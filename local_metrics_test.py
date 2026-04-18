"""Local-only script: compute U/E/F metrics for each opportunity.

Inputs:
- local_ie_results_updated_dataset.json (structured extraction)
- dataset/updated_dataset/email_*.txt (for Received-Date)
- sample_user_profile.json

Outputs:
- local_metrics_results_updated_dataset.json

Rules:
- Urgency (U): computed deterministically from (deadline_date - received_date) in days.
- Eligibility (E): LLM score in [0,1]
- Profile Fit (F): LLM score in [0,1]

Testing only; do not push.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


IE_PATH = Path("local_ie_results_updated_dataset.json")
PROFILE_PATH = Path("sample_user_profile.json")
EMAIL_DIR = Path("dataset/updated_dataset")

LMSTUDIO_BASE_URL = os.environ.get("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234")
MODEL = os.environ.get("LMSTUDIO_MODEL", "qwen3-4b-instruct-2507-mlx")
TEMPERATURE = float(os.environ.get("LMSTUDIO_TEMPERATURE", "0"))
TIMEOUT_S = int(os.environ.get("LMSTUDIO_TIMEOUT_S", "180"))
RETRIES = int(os.environ.get("LMSTUDIO_RETRIES", "1"))

RECEIVED_DATE_RE = re.compile(r"^Received-Date:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


@dataclass
class MetricsResult:
    file: str
    received_date: str
    deadline: str | None
    days_remaining: int | None
    urgency_U: float
    eligibility_E: float
    profile_fit_F: float
    rationale: str
    model: str
    created_at: str


PROMPT = """You are a strict scoring assistant.
Given a STUDENT_PROFILE_JSON and EXTRACTED_OPPORTUNITY_JSON, output ONLY valid JSON:
{{
  "eligibility_E": number,   // 0..1
  "profile_fit_F": number,   // 0..1
  "rationale": string        // 1-2 sentences, mention key constraints/fit signals
}}

Rules:
- eligibility_E should be 0 if there is an explicit hard constraint the student fails (e.g., degree mismatch, requires 10+ years, CGPA minimum higher than student).
- If there are no explicit constraints, default eligibility_E to a high value (e.g., 0.6-1.0).
- profile_fit_F should reflect overlap with the student's skills/interests and preferred opportunity types/location.
- Return numbers as decimals between 0 and 1.

STUDENT_PROFILE_JSON:
{student_profile}

EXTRACTED_OPPORTUNITY_JSON:
{opportunity}
"""


def parse_received_date(email_text: str) -> datetime:
    m = RECEIVED_DATE_RE.search(email_text)
    if not m:
        raise ValueError("Email missing Received-Date: YYYY-MM-DD")
    return datetime.fromisoformat(m.group(1)).replace(tzinfo=UTC)


def parse_deadline_date(deadline: str | None) -> datetime | None:
    if not deadline:
        return None
    # Accept YYYY-MM-DD or full ISO-ish strings; use date portion.
    s = str(deadline).strip()
    date_part = s[:10] if len(s) >= 10 else s
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_part):
        return None
    return datetime.fromisoformat(date_part).replace(tzinfo=UTC)


def compute_urgency(received: datetime, deadline_dt: datetime | None) -> tuple[int | None, float]:
    """Return (days_remaining, U) using bounded linear decay capped at 30 days.

    Formula (for known deadlines):
        U = max(0, 1 - DaysRemaining/30)

    Notes:
    - If deadline missing: days_remaining=None, U=0.5
    - If deadline is today or already passed: DaysRemaining<=0 -> U=0.0 (score should be 0 as well)
    - If DaysRemaining>=30 -> U=0.0
    """
    if deadline_dt is None:
        return None, 0.5

    days_remaining = (deadline_dt.date() - received.date()).days

    if days_remaining <= 0:
        return days_remaining, 0.0

    if days_remaining >= 30:
        return days_remaining, 0.0

    u = 1.0 - (float(days_remaining) / 30.0)
    return days_remaining, max(0.0, u)


def _extract_json(text: str) -> dict[str, Any]:
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError(f"No JSON found in response: {text[:400]}")
    return json.loads(m.group(0))


def score_with_lmstudio(student_profile: dict[str, Any], opportunity: dict[str, Any]) -> dict[str, Any]:
    import urllib.error
    import urllib.request

    url = f"{LMSTUDIO_BASE_URL.rstrip('/')}/v1/chat/completions"

    # Keep payload reasonably sized to reduce long stalls on some local servers.
    # (Safe: deterministic truncation; scoring doesn't need full verbosity.)
    student_profile_json = json.dumps(student_profile, ensure_ascii=False)
    opportunity_json = json.dumps(opportunity, ensure_ascii=False)
    if len(student_profile_json) > 12_000:
        student_profile_json = student_profile_json[:12_000] + "…"
    if len(opportunity_json) > 20_000:
        opportunity_json = opportunity_json[:20_000] + "…"

    content = PROMPT.format(
        student_profile=student_profile_json,
        opportunity=opportunity_json,
    )
    payload = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "messages": [{"role": "user", "content": content}],
    }

    # Important: build a *fresh* Request each attempt. Reusing a Request object can
    # lead to confusing hangs with some urllib/http.client code paths.
    def _build_req() -> urllib.request.Request:
        return urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Connection": "close"},
            method="POST",
        )

    last_err: Exception | None = None
    for attempt in range(RETRIES + 1):
        try:
            with urllib.request.urlopen(_build_req(), timeout=TIMEOUT_S) as resp:
                resp_text = resp.read().decode("utf-8", errors="replace")
            data = json.loads(resp_text)
            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return _extract_json(raw)
        except Exception as e:
            last_err = e
            if attempt >= RETRIES:
                break
            continue

    raise RuntimeError(
        "LM Studio scoring failed after retries. "
        f"base_url={LMSTUDIO_BASE_URL!r} model={MODEL!r} timeout_s={TIMEOUT_S} retries={RETRIES}. "
        f"last_error={type(last_err).__name__}: {last_err}"
    )


def clamp01(x: Any) -> float:
    try:
        v = float(x)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, v))


def main() -> None:
    if not IE_PATH.exists():
        raise SystemExit(f"Missing IE results: {IE_PATH}")
    if not PROFILE_PATH.exists():
        raise SystemExit(f"Missing profile: {PROFILE_PATH}")

    ie_items = json.loads(IE_PATH.read_text(encoding="utf-8"))
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

    created_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    out: list[MetricsResult] = []

    for item in ie_items:
        file_path = Path(item["file"])
        if not file_path.exists():
            file_path = EMAIL_DIR / Path(item["file"]).name

        email_text = file_path.read_text(encoding="utf-8")
        received_dt = parse_received_date(email_text)

        extraction = item.get("extraction", {})
        deadline_str = extraction.get("deadline")
        deadline_dt = parse_deadline_date(deadline_str)
        days_remaining, U = compute_urgency(received_dt, deadline_dt)

        scores = score_with_lmstudio(profile, extraction)
        E = clamp01(scores.get("eligibility_E"))
        F = clamp01(scores.get("profile_fit_F"))
        rationale = str(scores.get("rationale", "")).strip()

        out.append(
            MetricsResult(
                file=str(file_path),
                received_date=received_dt.date().isoformat(),
                deadline=deadline_dt.date().isoformat() if deadline_dt else None,
                days_remaining=days_remaining,
                urgency_U=U,
                eligibility_E=E,
                profile_fit_F=F,
                rationale=rationale,
                model=MODEL,
                created_at=created_at,
            )
        )

    out_path = Path("local_metrics_results_updated_dataset.json")
    out_path.write_text(
        json.dumps([o.__dict__ for o in out], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Deterministic ranking (no LLM calls):
    # Score = ((30 * U) + (70 * F)) * E
    ranked = []
    for o in out:
        # Hard rule: if deadline is today/past (days_remaining <= 0), score must be 0.
        if o.days_remaining is not None and int(o.days_remaining) <= 0:
            score = 0.0
        else:
            score = ((30.0 * float(o.urgency_U)) + (70.0 * float(o.profile_fit_F))) * float(o.eligibility_E)
        ranked.append({"file": o.file, "score": score, **o.__dict__})
    ranked.sort(key=lambda r: float(r["score"]), reverse=True)

    ranking_path = Path("local_ranked_results_updated_dataset.json")
    ranking_path.write_text(json.dumps(ranked, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    positive_ranked = [r for r in ranked if float(r.get("score", 0.0)) > 0.0]
    positive_ranking_path = Path("local_ranked_results_updated_dataset_positive_only.json")
    positive_ranking_path.write_text(
        json.dumps(positive_ranked, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("\nRanking (desc):")
    for i, r in enumerate(ranked, start=1):
        m = re.search(r"email_(\d+)\.txt$", str(r.get("file", "")))
        eid = int(m.group(1)) if m else str(r.get("file"))
        print(
            f"{i:02d}. Email {eid}: score={r['score']:.4f} "
            f"(U={r['urgency_U']:.4f}, F={r['profile_fit_F']:.4f}, E={r['eligibility_E']:.4f}, days={r['days_remaining']})"
        )

    print(f"\nScored {len(out)} opportunities -> {out_path}")
    print(f"Wrote ranking -> {ranking_path}")
    print(f"Wrote positive-only ranking ({len(positive_ranked)}) -> {positive_ranking_path}")


if __name__ == "__main__":
    main()
