"""
Main entry point for the FastAPI application.

Manual testing
--------------
Run from the backend/ directory:

    python main.py

This loads all 15 demo emails + a sample student profile, runs the full
3-stage pipeline, and pretty-prints the ranked results to stdout.
No API server is needed.
"""

import asyncio
import json
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS — allow the React dev server (and production domain) to talk to the API
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
async def root():
    """Root health-check endpoint."""
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


# ===========================================================================
# MANUAL TEST HARNESS
# Run with:  python main.py  (from the backend/ directory)
# ===========================================================================

def _separator(char: str = "─", width: int = 70) -> str:
    return char * width


def _print_summary(response_dict: dict) -> None:
    """Print a human-readable summary of the pipeline response."""
    summary = response_dict["summary"]
    ranked = response_dict["ranked_opportunities"]
    filtered = response_dict["filtered_emails"]

    print(_separator("═"))
    print("  OPPORTUNITY INBOX COPILOT — PIPELINE RESULTS")
    print(_separator("═"))
    print(f"  📧  Total emails processed : {summary['total_emails']}")
    print(f"  ✅  Real opportunities      : {summary['real_opportunities']}")
    print(f"  🗑️   Spam / noise filtered  : {summary['spam_filtered']}")
    print(f"  🔥  Urgent (≤14 days)      : {summary['urgent_count']}")
    if summary.get("top_deadline_days") is not None:
        print(f"  ⏰  Nearest deadline        : in {summary['top_deadline_days']} day(s)")
    print()

    if not ranked:
        print("  No real opportunities found in this inbox.\n")
        return

    print(f"  {'RANK':<5} {'TITLE':<40} {'TYPE':<14} {'SCORE':<7} {'DEADLINE'}")
    print(_separator())
    for item in ranked:
        ext = item["extracted"]
        sc = item["score"]
        title = (ext.get("title") or ext.get("raw_subject") or "Untitled")[:38]
        opp_type = (ext.get("opportunity_type") or "—")[:12]
        score = f"{sc['total']:.1f}"
        deadline = str(ext.get("deadline") or "—")
        eligible = "" if sc["is_eligible"] else " ⛔ INELIGIBLE"
        print(f"  #{item['rank']:<4} {title:<40} {opp_type:<14} {score:<7} {deadline}{eligible}")

    print()
    print(_separator())
    print("  TOP OPPORTUNITY DETAIL")
    print(_separator())

    top = ranked[0]
    ext = top["extracted"]
    sc = top["score"]

    print(f"  Title      : {ext.get('title') or ext.get('raw_subject')}")
    print(f"  Type       : {ext.get('opportunity_type') or '—'}")
    print(f"  Organizer  : {ext.get('organizer') or '—'}")
    print(f"  Deadline   : {ext.get('deadline') or '—'} ({ext.get('deadline_relative') or '—'})")
    print(f"  Funding    : {ext.get('stipend_funding') or '—'}")
    print(f"  Score      : {sc['total']:.1f}  "
          f"(Fit={sc['profile_fit']:.0f} | Urgency={sc['urgency']:.0f} | "
          f"Completeness={sc['completeness']:.0f})")
    print()
    print("  Why this ranks #1:")
    for bullet in top.get("why_bullets", [])[:6]:
        print(f"    {bullet}")
    print()
    print("  Action Checklist:")
    for action in top.get("action_checklist", [])[:5]:
        print(f"    ☐ {action}")

    print()
    print(_separator())
    print(f"  FILTERED EMAILS ({len(filtered)} spam/noise)")
    print(_separator())
    for f in filtered:
        subj = f.get("raw_subject") or "—"
        reason = f.get("classification_reason") or "—"
        print(f"  ✗ {subj[:55]:<55} | {reason[:50]}")

    print(_separator("═"))
    print()


async def _run_manual_test() -> None:
    """Entry point for manual pipeline testing."""
    from app.schemas.opportunity import EmailInput, PipelineRequest, StudentProfile
    from app.services.demo_data import DEMO_PROFILE
    from app.services.pipeline import run_pipeline
    import glob

    # Read emails from the updated_dataset
    dataset_path = "/Users/Hassaan/PycharmProjects/AI_HACK/dataset/updated_dataset"
    email_files = sorted(glob.glob(os.path.join(dataset_path, "email_*.txt")))

    # Configurable number of outputs
    NUM_EMAILS_TO_TEST = 1
    to_process_files = email_files[:NUM_EMAILS_TO_TEST]

    emails = []
    for fpath in to_process_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            subject = "Unknown Subject"
            body = content
            for line in content.splitlines():
                if line.startswith("Subject:"):
                    subject = line.replace("Subject:", "").strip()
                elif line.startswith("Body:"):
                    body = line.replace("Body:", "").strip()
            emails.append(EmailInput(subject=subject, body=body))

    print()
    print(f"  Loading demo profile + {len(emails)} emails from updated_dataset …")
    print(f"  LLM Provider : {settings.LLM_PROVIDER.upper()}")
    if settings.LLM_PROVIDER == "google":
        print(f"  Model        : {settings.GEMINI_MODEL}")
    else:
        print(f"  Model        : {settings.OLLAMA_MODEL}")
    print()

    profile = StudentProfile(**DEMO_PROFILE)
    request = PipelineRequest(student_profile=profile, emails=emails)

    print("  Running pipeline …\n")
    response = await run_pipeline(request)

    # Convert to dict for display
    response_dict = json.loads(response.model_dump_json())
    _print_summary(response_dict)

    # Dump full JSON for further inspection
    output_path = os.path.join(os.path.dirname(__file__), "pipeline_output.json")
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(response_dict, fh, indent=2, default=str)
    print(f"  Full JSON saved to: {output_path}")
    print()


if __name__ == "__main__":
    # Ensure the backend/ directory is on sys.path so relative imports resolve
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(name)s | %(message)s",
    )

    asyncio.run(_run_manual_test())
