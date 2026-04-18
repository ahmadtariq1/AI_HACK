"""
Stage II — Structured Opportunity Extractor  (REAL LLM IMPLEMENTATION)

Responsibility
--------------
Convert the raw text of a single email that has already passed Stage I
classification into a fully structured ExtractedOpportunity object.

Pipeline contract
-----------------
Input  : subject (str) + body (str) + classification result
Output : ExtractedOpportunity  (all fields present; unknown fields → null)

Key design decisions
--------------------
* Uses JSON mode via llm_client.complete_json() for strict output.
* Embeds the full Pydantic schema as a JSON Schema comment in the prompt
  so the model knows exactly which fields to fill.
* Normalizes relative dates (e.g. "this Friday", "next Monday") to ISO
  using the current date as the reference anchor.
* Handles multiple opportunities in one email by returning the most prominent
  one (the model is instructed to pick the main one).
* On any parsing or LLM error: sets needs_manual_review=True and populates
  only raw_subject / raw_body_snippet so the frontend can show a fallback.
"""

from __future__ import annotations

import glob
import logging
import os
from datetime import date, datetime
from typing import Optional

from app.schemas.opportunity import (
    ClassificationResult,
    EligibilityCriteria,
    ExtractedOpportunity,
)
from app.services.llm_client import llm_client

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Few-shot examples to anchor output format
# ---------------------------------------------------------------------------
_FEW_SHOT_EXAMPLES = """
--- EXAMPLE INPUT ---
Subject: Call for Proposals: NLP for Regional Languages
Body: The linguistics department is offering a micro-grant of $500 for undergraduate
engineering students. We need a script that can successfully tokenize Roman Urdu.
Submit a one-page methodology by Monday 20 April 2026. Contact: nlp-lab@uni.edu

--- EXAMPLE OUTPUT ---
{
  "opportunity_type": "Competition",
  "title": "NLP for Regional Languages Micro-Grant",
  "deadline": "2026-04-20",
  "deadline_relative": "in 2 days",
  "eligibility": {
    "min_cgpa": null,
    "target_semesters": null,
    "degree_programs": ["Engineering"],
    "other": ["Undergraduate students only"]
  },
  "required_documents": ["One-page methodology"],
  "links_contact": ["nlp-lab@uni.edu"],
  "stipend_funding": "$500 micro-grant",
  "organizer": "Linguistics Department"
}

--- EXAMPLE INPUT ---
Subject: CS Department Spring Update & Alumni News
Body: Google's local office has two unlisted summer internship slots for final-year
students. Send your resume to the department head by 5 PM today (April 18, 2026).

--- EXAMPLE OUTPUT ---
{
  "opportunity_type": "Internship",
  "title": "Google Summer Internship (Unlisted)",
  "deadline": "2026-04-18",
  "deadline_relative": "today",
  "eligibility": {
    "min_cgpa": null,
    "target_semesters": [7, 8],
    "degree_programs": ["Computer Science"],
    "other": ["Final-year students only"]
  },
  "required_documents": ["Resume"],
  "links_contact": null,
  "stipend_funding": null,
  "organizer": "Google (via CS Department)"
}
"""

# ---------------------------------------------------------------------------
# Main extraction prompt
# ---------------------------------------------------------------------------
_EXTRACT_PROMPT = """\
You are a precise data extraction assistant for a student opportunity ranking system.
Today's date is {today}.

Your task: extract structured information from the email below and return it as
strictly valid JSON matching the schema described.

=== RULES (read carefully) ===
1. Return ONLY the JSON object — no markdown fences, no explanation outside JSON.
2. If a field cannot be determined from the email text, set it to null — do NOT guess or hallucinate.
3. Deadline normalisation:
   - Convert relative dates ("this Friday", "next Monday", "by end of week") to absolute ISO dates
     using today ({today}) as the reference.
   - If a relative deadline is ambiguous (e.g. "soon"), set deadline to null.
   - deadline_relative must be human-readable: "today", "tomorrow", "in 5 days", "in 3 weeks", etc.
4. If the email contains MULTIPLE opportunities, extract only the MOST PROMINENT / MAIN one.
5. opportunity_type must be exactly one of: Internship | Scholarship | Competition |
   Fellowship | Admission | Research | Other
6. required_documents must be a list of strings (e.g. ["Resume", "Transcript", "CNIC"]).
7. links_contact must be a list of raw URLs and/or email addresses extracted verbatim.
8. eligibility sub-fields:
   - min_cgpa   : float or null
   - target_semesters : list of ints or null  (e.g. [6,7,8] for "junior/senior")
   - degree_programs  : list of strings or null
   - other            : list of free-text strings or null

=== OUTPUT JSON SCHEMA ===
{{
  "opportunity_type": "<string | null>",
  "title": "<string | null>",
  "deadline": "<YYYY-MM-DD | null>",
  "deadline_relative": "<string | null>",
  "eligibility": {{
    "min_cgpa": <float | null>,
    "target_semesters": [<int>, ...] | null,
    "degree_programs": ["<string>", ...] | null,
    "other": ["<string>", ...] | null
  }},
  "required_documents": ["<string>", ...] | null,
  "links_contact": ["<string>", ...] | null,
  "stipend_funding": "<string | null>",
  "organizer": "<string | null>"
}}

=== FEW-SHOT EXAMPLES ===
{examples}

=== EMAIL TO EXTRACT ===
Subject: {subject}
Body:
{body}
"""


# ---------------------------------------------------------------------------
# Date normalisation helper
# ---------------------------------------------------------------------------

def _compute_relative_label(deadline: date) -> str:
    """Return a human-readable relative label for a deadline date."""
    delta = (deadline - date.today()).days
    if delta < 0:
        return "past deadline"
    if delta == 0:
        return "today"
    if delta == 1:
        return "tomorrow"
    if delta <= 14:
        return f"in {delta} days"
    weeks = round(delta / 7)
    return f"in {weeks} week{'s' if weeks != 1 else ''}"


# ---------------------------------------------------------------------------
# Public extraction function
# ---------------------------------------------------------------------------

async def extract_opportunity(
    subject: str,
    body: str,
    classification: Optional[ClassificationResult] = None,
) -> ExtractedOpportunity:
    """
    Stage II — extract structured data from a single classified email.

    Parameters
    ----------
    subject        : Email subject line.
    body           : Full email body text.
    classification : Result from Stage I (passed through into the output).
                     Defaults to is_opportunity=True if not provided.

    Returns
    -------
    ExtractedOpportunity with all extractable fields populated,
    and needs_manual_review=True on any failure.
    """
    # Build classification echo (defaults if not provided)
    is_opp = classification.is_opportunity if classification else True
    confidence = classification.confidence if classification else 1.0
    cl_reason = classification.reason if classification else "Pre-classified as opportunity."

    prompt = _EXTRACT_PROMPT.format(
        today=date.today().isoformat(),
        examples=_FEW_SHOT_EXAMPLES,
        subject=subject,
        body=body[:4000],  # trim very long emails
    )

    try:
        data = await llm_client.complete_json(prompt)

        # --- Parse deadline ---
        raw_deadline = data.get("deadline")
        parsed_deadline: Optional[date] = None
        deadline_relative: Optional[str] = data.get("deadline_relative")

        if raw_deadline:
            try:
                parsed_deadline = datetime.strptime(str(raw_deadline), "%Y-%m-%d").date()
                # Always compute the relative label ourselves for consistency
                deadline_relative = _compute_relative_label(parsed_deadline)
            except ValueError:
                logger.warning("Could not parse deadline '%s' for subject=%r", raw_deadline, subject[:60])
                parsed_deadline = None

        # --- Parse eligibility sub-object ---
        elig_raw = data.get("eligibility") or {}
        eligibility: Optional[EligibilityCriteria] = None
        if elig_raw:
            eligibility = EligibilityCriteria(
                min_cgpa=elig_raw.get("min_cgpa"),
                target_semesters=elig_raw.get("target_semesters"),
                degree_programs=elig_raw.get("degree_programs"),
                other=elig_raw.get("other"),
            )

        # --- Build the final object ---
        result = ExtractedOpportunity(
            is_opportunity=is_opp,
            confidence=confidence,
            classification_reason=cl_reason,
            opportunity_type=data.get("opportunity_type"),
            title=data.get("title"),
            deadline=parsed_deadline,
            deadline_relative=deadline_relative,
            eligibility=eligibility,
            required_documents=data.get("required_documents"),
            links_contact=data.get("links_contact"),
            stipend_funding=data.get("stipend_funding"),
            organizer=data.get("organizer"),
            needs_manual_review=False,
            raw_subject=subject,
            raw_body_snippet=body[:300],
        )

        logger.info(
            "extract_opportunity | subject=%r | type=%s | deadline=%s",
            subject[:60],
            result.opportunity_type,
            result.deadline,
        )
        return result

    except Exception as exc:  # noqa: BLE001
        logger.error(
            "extract_opportunity failed for subject=%r: %s", subject[:60], exc
        )
        # Graceful fallback — return minimal object for manual review
        return ExtractedOpportunity(
            is_opportunity=is_opp,
            confidence=confidence,
            classification_reason=cl_reason,
            needs_manual_review=True,
            raw_subject=subject,
            raw_body_snippet=body[:300],
        )


# ---------------------------------------------------------------------------
# Test extractor on dataset
# ---------------------------------------------------------------------------

async def test_extractor_on_dataset(num_emails: int = 5):
    """
    Test helper to run the extractor on real files from the dataset.
    """
    dataset_path = "/Users/Hassaan/PycharmProjects/AI_HACK/dataset/updated_dataset"
    email_files = sorted(glob.glob(os.path.join(dataset_path, "email_*.txt")))

    to_process = email_files[:num_emails]
    print(f"\n--- Testing Extractor on {len(to_process)} emails ---\n")

    for fpath in to_process:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # Basic parsing of the provided format:
        # Subject: <subj>
        # Body: <body>
        subject = "Unknown Subject"
        body = content

        for line in content.splitlines():
            if line.startswith("Subject:"):
                subject = line.replace("Subject:", "").strip()
            elif line.startswith("Body:"):
                body = line.replace("Body:", "").strip()

        print(f"Processing File: {os.path.basename(fpath)}")
        print(f"Subject: {subject}")

        result = await extract_opportunity(subject, body)

        print(f"Extracted Title: {result.title}")
        print(f"Type: {result.opportunity_type}")
        print(f"Deadline: {result.deadline} ({result.deadline_relative})")
        print(f"Organizer: {result.organizer}")
        print(f"Manual Review Needed: {result.needs_manual_review}")
        print("-" * 40)


async def main():
    # Configure number of emails to test here
    await test_extractor_on_dataset(num_emails=3)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

