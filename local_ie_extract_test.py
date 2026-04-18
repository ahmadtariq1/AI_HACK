"""Local-only test script: extract structured opportunity info via LM Studio.

Inputs:
- local_ollama_flag_results.json (filter is_opportunity=true)
- dataset/updated_dataset/email_*.txt

Output:
- local_ie_results_updated_dataset.json

Testing only; do not push.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


FLAGS_PATH = Path("local_ollama_flag_results.json")
EMAIL_DIR = Path("dataset/updated_dataset")

LMSTUDIO_BASE_URL = os.environ.get("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234")
MODEL = os.environ.get("LMSTUDIO_MODEL", "qwen3-4b-instruct-2507-mlx")
TEMPERATURE = float(os.environ.get("LMSTUDIO_TEMPERATURE", "0"))
TIMEOUT_S = int(os.environ.get("LMSTUDIO_TIMEOUT_S", "180"))
RETRIES = int(os.environ.get("LMSTUDIO_RETRIES", "2"))


@dataclass
class ExtractionResult:
    file: str
    extraction: dict[str, Any]
    model: str
    created_at: str


PROMPT = """You are an information extraction system.
Extract structured fields from the email below.

Return ONLY valid JSON with this schema:
{
  "opportunity_type": string,                 // e.g. internship, job, hackathon, competition, fellowship, research_grant, networking
  "deadline": string | null,                  // ISO-8601 date if possible (YYYY-MM-DD). If unknown, null.
  "deadline_text": string | null,             // exact phrase from email (e.g. "by Monday", "closes midnight")
  "eligibility_conditions": [string],         // bullet list
  "required_documents": [string],             // e.g. resume, transcript
  "application_or_contact": {
    "emails": [string],
    "urls": [string],
    "instructions": string | null
  }
}

Rules:
- If the email has relative time ("by Monday"), put null in deadline, and fill deadline_text.
- Prefer copying exact constraints as strings.
- If a field is not mentioned, return empty list / null as appropriate.

EMAIL:
"""


RECEIVED_DATE_RE = re.compile(r"^Received-Date:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def parse_received_date(email_text: str) -> datetime:
    """Parse YYYY-MM-DD from a `Received-Date:` line in the email.

    Returns a timezone-aware UTC datetime at midnight.
    """
    m = RECEIVED_DATE_RE.search(email_text)
    if not m:
        raise ValueError("Email missing Received-Date: YYYY-MM-DD header")
    return datetime.fromisoformat(m.group(1)).replace(tzinfo=UTC)


WEEKDAY_TO_INT = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def resolve_relative_weekday(received_date: datetime, deadline_text: str | None) -> str | None:
    """Resolve 'by Monday'/'next Tuesday' into YYYY-MM-DD based on received_date.

    Heuristics (deterministic):
    - If contains 'next <weekday>', choose the weekday in the *next* week (>= 7 days ahead).
    - Else if contains '<weekday>', choose the next occurrence including the same day.
    """
    if not deadline_text:
        return None

    s = deadline_text.strip().lower()
    # Extract weekday name
    weekday = None
    for name in WEEKDAY_TO_INT.keys():
        if re.search(rf"\b{name}\b", s):
            weekday = name
            break
    if weekday is None:
        return None

    target = WEEKDAY_TO_INT[weekday]
    cur = received_date.weekday()
    days_ahead = (target - cur) % 7

    if "next" in s:
        # Ensure at least 7 days ahead
        days_ahead = days_ahead + 7 if days_ahead != 0 else 7

    resolved = received_date + timedelta(days=days_ahead)
    return resolved.date().isoformat()


def _extract_json(text: str) -> dict[str, Any]:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError(f"No JSON object found in response: {text[:400]}")
    return json.loads(match.group(0))


def call_lmstudio(email_text: str) -> dict[str, Any]:
    import urllib.error
    import urllib.request

    url = f"{LMSTUDIO_BASE_URL.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "messages": [{"role": "user", "content": PROMPT + email_text}],
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    last_err: Exception | None = None
    for attempt in range(RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                resp_text = resp.read().decode("utf-8", errors="replace")
            data = json.loads(resp_text)
            raw = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            return _extract_json(raw)
        except urllib.error.HTTPError as e:
            last_err = RuntimeError(
                f"LM Studio HTTPError {e.code}: {e.read().decode('utf-8', errors='replace')}"
            )
        except (urllib.error.URLError, TimeoutError) as e:
            last_err = RuntimeError(f"LM Studio request failed: {e}")
        except json.JSONDecodeError as e:
            last_err = RuntimeError(f"LM Studio returned non-JSON response: {e}")

        if attempt < RETRIES:
            continue

    assert last_err is not None
    raise last_err


def main() -> None:
    if not FLAGS_PATH.exists():
        raise SystemExit(f"Missing flags file: {FLAGS_PATH}")

    flags = json.loads(FLAGS_PATH.read_text(encoding="utf-8"))
    positives = [f for f in flags if f.get("is_opportunity") is True]

    results: list[ExtractionResult] = []
    created_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    for item in positives:
        file_path = Path(item["file"])
        if not file_path.exists():
            # Try resolving by filename in EMAIL_DIR
            file_path = EMAIL_DIR / Path(item["file"]).name

        email_text = file_path.read_text(encoding="utf-8")
        received_date = parse_received_date(email_text)
        extraction = call_lmstudio(email_text)

        # Deterministic post-processing: resolve relative weekday deadlines using Received-Date
        deadline = extraction.get("deadline")
        deadline_text = extraction.get("deadline_text")
        if (deadline is None) and isinstance(deadline_text, str):
            resolved = resolve_relative_weekday(received_date, deadline_text)
            if resolved is not None:
                extraction["deadline"] = resolved
        results.append(
            ExtractionResult(
                file=str(file_path),
                extraction=extraction,
                model=MODEL,
                created_at=created_at,
            )
        )

    out_path = Path("local_ie_results_updated_dataset.json")
    out_path.write_text(
        json.dumps([r.__dict__ for r in results], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Extracted {len(results)} opportunities -> {out_path}")


if __name__ == "__main__":
    main()
