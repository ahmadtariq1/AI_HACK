"""
Stage I — Binary Email Classifier

Responsibility
--------------
Determine whether an email contains a specific, actionable opportunity
(internship, scholarship, competition, fellowship, etc.) or is noise
(newsletter, spam, marketing, internal announcement, pay-to-play scam).

Pipeline contract
-----------------
Input  : subject (str) + body (str)
Output : ClassificationResult(is_opportunity, confidence, reason)

Decision rule: is_opportunity = True  iff  confidence > 0.7
"""

from __future__ import annotations

import logging
from datetime import date

from app.schemas.opportunity import ClassificationResult
from app.services.llm_client import llm_client

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Few-shot examples — drawn from better_dataset.txt to ground the model
# ---------------------------------------------------------------------------
_FEW_SHOT_EXAMPLES = """
EXAMPLE 1 (REAL — hidden opportunity)
Subject: CS Department Spring Update & Alumni News
Body: ...Google's local office reached out; they have two unlisted summer internship
      slots for final-year students. Send your resume to the department head by 5 PM today.
Output: {"is_opportunity": true, "confidence": 0.92, "reason": "Contains a real, time-bound internship offer with a specific action step."}

EXAMPLE 2 (SPAM — pay-to-play scam)
Subject: You have been selected! Global Youth Tech Summit
Body: ...To secure your spot, please pay the $850 registration and processing fee by Friday.
Output: {"is_opportunity": false, "confidence": 0.97, "reason": "Requires upfront payment to participate — classic pay-to-play scam, not a legitimate opportunity."}

EXAMPLE 3 (SPAM — unpaid ambassador / free labour)
Subject: Become a Red Bull Campus Ambassador
Body: Unpaid, but you get free merchandise and a certificate of participation.
Output: {"is_opportunity": false, "confidence": 0.88, "reason": "Unpaid ambassador role with no career value; essentially free marketing labour."}

EXAMPLE 4 (REAL — niche research grant)
Subject: Call for Proposals: NLP for Regional Languages
Body: The linguistics department is offering a micro-grant of $500 for undergraduate
      engineering students. Submit a one-page methodology by Monday.
Output: {"is_opportunity": true, "confidence": 0.91, "reason": "Specific funded grant with a clear deliverable and deadline for undergraduate students."}

EXAMPLE 5 (SPAM — mandatory coursework disguised as competition)
Subject: Final Project: AI Hackathon Logistics
Body: For your final project in CS405, we will be simulating a hackathon environment...
      Attendance in the lab is mandatory.
Output: {"is_opportunity": false, "confidence": 0.95, "reason": "Compulsory academic assignment framed as a competition — not an external opportunity."}
"""

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------
_CLASSIFY_PROMPT = """\
You are an expert email classifier for a student opportunity system.
Today's date is {today}.

Your task: classify the email below as a REAL OPPORTUNITY or NOT.

--- DEFINITIONS ---
REAL OPPORTUNITY: A specific, external, actionable chance for a student to gain
  a scholarship, internship, fellowship, competition entry, research grant, or
  admission. Must have at least one of: deadline, application link, or clear
  next step. Implied hiring / networking events count if directly actionable.

NOT AN OPPORTUNITY: Newsletters, generic announcements, mandatory coursework,
  pay-to-play schemes requiring upfront fees, unpaid labour framed as
  "experience", phishing/scam emails, internal club elections, raffle surveys.

--- RULES ---
1. Return ONLY valid JSON — no markdown, no explanation outside JSON.
2. confidence must be a float in [0.0, 1.0].
3. reason must be a single sentence ≤ 25 words.
4. If the email has ANY red flag (fee required, no actionable step, mandatory
   academic work), set is_opportunity to false.

--- FEW-SHOT EXAMPLES ---
{examples}

--- EMAIL TO CLASSIFY ---
Subject: {subject}
Body:
{body}

--- REQUIRED OUTPUT FORMAT ---
{{
  "is_opportunity": <true|false>,
  "confidence": <0.0–1.0>,
  "reason": "<single sentence>"
}}
"""


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------


async def classify_email(subject: str, body: str) -> ClassificationResult:
    """
    Stage I — classify a single email.

    Returns a ClassificationResult. `is_opportunity` will be False if the
    model's confidence is ≤ 0.7, regardless of the raw label.

    Never raises — on any error returns a safe fallback result flagged for
    manual review.
    """

    # return dummy true for now
    return ClassificationResult(
        is_opportunity=True,
        confidence=0.8,
        reason="Dummy True.",
    )
