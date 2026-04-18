"""Local-only test script: use LM Studio (OpenAI-compatible API) to flag opportunity emails.

Inputs:
- Emails: dataset/updated_dataset/email_*.txt
- Student profile: sample_user_profile.json

Output:
- local_ollama_flag_results.json

This is for *testing only* and shouldn't be pushed.
"""

from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


UPDATED_DATASET_DIR = Path("dataset/updated_dataset")
PROFILE_PATH = Path("sample_user_profile.json")
LMSTUDIO_BASE_URL = os.environ.get("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234")
MODEL = os.environ.get("LMSTUDIO_MODEL", "qwen3-4b-instruct-2507-mlx")
TEMPERATURE = float(os.environ.get("LMSTUDIO_TEMPERATURE", "0"))
MAX_WORKERS = int(os.environ.get("OLLAMA_MAX_WORKERS", "3"))
TIMEOUT_S = int(os.environ.get("OLLAMA_TIMEOUT_S", "180"))


@dataclass
class FlagResult:
    file: str
    is_opportunity: bool
    rationale: str
    model: str
    created_at: str


PROMPT = """You are an email classifier.
Task: Decide if the email describes a genuine opportunity for a university CS student AND whether it does NOT violate the student's profile.

Generation settings: temperature={temperature}.

Rule 1: WHAT COUNTS AS AN OPPORTUNITY (is_opportunity=true)
- Internships, job openings, hackathons, competitions, fellowships, scholarships, or research grants.
- Waitlists, deadline extensions, or secondary application pathways for legitimate programs.
- Networking mixers, tech talks, or informal events if the text implies attendees can bypass interviews, meet CTOs, or submit resumes directly.

Rule 2: WHAT IS NOT AN OPPORTUNITY (is_opportunity=false)
- Spam, scams, phishing, or pay-to-play (where a fee is required).
- Standard university announcements, class logistics, or department newsletters.
- Unpaid marketing/ambassador labor or vague "idea pitches" lacking structure.
- Surveys, raffles, or internal club elections.

Rule 3: APPLICABILITY EXCLUSION (Only reject on hard evidence)
- DO NOT reject an opportunity just because it lacks specific details, explicit eligibility criteria, or exact alignment with the profile. Assume it is applicable unless proven otherwise.
- ONLY set is_opportunity=false if the email EXPLICITLY states a hard constraint the student fails (e.g., requires 10+ years experience, requires a Medical degree, etc.).

Return ONLY valid JSON with this exact schema:
{{
    "is_opportunity": boolean,
    "rationale": string
}}
Keep rationale to 1-2 sentences. No markdown.

STUDENT_PROFILE_JSON:
{student_profile_json}

EMAIL:
"""


def _extract_json(text: str) -> dict[str, Any]:
    """Best-effort extraction of the first JSON object from a model response."""
    # Sometimes models wrap JSON in text; grab the first {...} block.
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError(f"No JSON object found in response: {text[:400]}")
    return json.loads(match.group(0))


def classify_email(email_text: str, student_profile_json: str) -> tuple[bool, str, str]:
    """Call LM Studio's OpenAI-compatible endpoint and return (is_opportunity, rationale, raw_text)."""
    # Local import so this stays a single-file script without extra deps.
    import urllib.error
    import urllib.request

    url = f"{LMSTUDIO_BASE_URL.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "messages": [
            {
                "role": "user",
                "content": PROMPT.format(
                    temperature=TEMPERATURE,
                    student_profile_json=student_profile_json,
                )
                + email_text,
            }
        ],
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            resp_text = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"LM Studio HTTPError {e.code}: {e.read().decode('utf-8', errors='replace')}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"LM Studio URLError: {e}")

    data = json.loads(resp_text)
    raw = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )
    extracted = _extract_json(raw)
    is_opp = bool(extracted.get("is_opportunity"))
    rationale = str(extracted.get("rationale", "")).strip()
    return is_opp, rationale, raw


def main() -> None:
    if not UPDATED_DATASET_DIR.exists():
        raise SystemExit(f"Missing folder: {UPDATED_DATASET_DIR}")

    files = sorted(UPDATED_DATASET_DIR.glob("email_*.txt"))
    if not files:
        raise SystemExit(f"No email_*.txt files found in {UPDATED_DATASET_DIR}")

    if not PROFILE_PATH.exists():
        raise SystemExit(f"Missing student profile: {PROFILE_PATH}")

    # Keep profile as explicit JSON text to reduce ambiguity.
    student_profile_obj = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    student_profile_json = json.dumps(student_profile_obj, ensure_ascii=False, indent=2)

    results: list[FlagResult] = []
    created_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    def _work(fp: Path) -> FlagResult:
        text = fp.read_text(encoding="utf-8")
        is_opp, rationale, _raw = classify_email(text, student_profile_json)
        return FlagResult(
            file=str(fp),
            is_opportunity=is_opp,
            rationale=rationale,
            model=MODEL,
            created_at=created_at,
        )

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(_work, fp): fp for fp in files}
        for fut in as_completed(futures):
            results.append(fut.result())

    # Stable ordering in output
    results.sort(key=lambda r: r.file)

    out_path = Path("local_ollama_flag_results.json")
    out_path.write_text(
        json.dumps([r.__dict__ for r in results], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    positives = sum(1 for r in results if r.is_opportunity)
    negatives = len(results) - positives
    print(f"Done. {positives} positive, {negatives} negative. Wrote {out_path}")


if __name__ == "__main__":
    main()
