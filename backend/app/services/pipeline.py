"""
Pipeline Orchestrator — chains Stage I → Stage II → Stage III

run_pipeline()  is the single public entry point consumed by both:
  1. The FastAPI endpoint  (POST /api/v1/pipeline/process)
  2. The manual test harness in main.py  (asyncio.run(run_pipeline(...)))

Parallelism
-----------
All Stage I (classification) calls run concurrently via asyncio.gather().
Stage II (extraction) calls also run concurrently, but only for emails that
passed Stage I.  Stage III (scoring) is synchronous / in-process.

Error isolation
---------------
A failure in one email's processing never crashes the whole batch.
Errors are caught per-email and surfaced as needs_manual_review=True items.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date
from typing import List

from app.schemas.opportunity import (
    EmailInput,
    ExtractedOpportunity,
    PipelineRequest,
    PipelineResponse,
    PipelineSummary,
    ScoredOpportunity,
    StudentProfile,
)
from app.services.classifier import classify_email
from app.services.extractor import extract_opportunity
from app.services.scorer import score_opportunity

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _process_single_email(
    email: EmailInput,
    profile: StudentProfile,
) -> tuple[ExtractedOpportunity | None, ExtractedOpportunity | None]:
    """
    Process one email through Stage I → Stage II.

    Returns
    -------
    (opportunity, filtered)
      opportunity : ExtractedOpportunity if is_opportunity=True, else None
      filtered    : ExtractedOpportunity with minimal fields if spam, else None
    """
    # Stage I — classify
    classification = await classify_email(email.subject, email.body)

    if not classification.is_opportunity:
        # Build a lightweight spam record for the filtered list
        spam_record = ExtractedOpportunity(
            is_opportunity=False,
            confidence=classification.confidence,
            classification_reason=classification.rationale,
            needs_manual_review=False,
            raw_subject=email.subject,
            raw_body_snippet=email.body[:300],
        )
        return None, spam_record

    # Stage II — extract structured data
    extracted = await extract_opportunity(email.subject, email.body, classification)
    return extracted, None


# ---------------------------------------------------------------------------
# Public orchestrator
# ---------------------------------------------------------------------------


async def run_pipeline(request: PipelineRequest) -> PipelineResponse:
    """
    Run the full 3-stage pipeline on a batch of emails.

    Parameters
    ----------
    request : PipelineRequest containing StudentProfile + List[EmailInput]

    Returns
    -------
    PipelineResponse with ranked opportunities and summary stats.
    """
    logger.info("Pipeline started | emails=%d", len(request.emails))

    # ------------------------------------------------------------------ #
    # Stage I + II  (concurrent per email)                                #
    # ------------------------------------------------------------------ #
    tasks = [
        _process_single_email(email, request.student_profile)
        for email in request.emails
    ]
    results: list[tuple] = await asyncio.gather(*tasks, return_exceptions=True)

    opportunities: list[ExtractedOpportunity] = []
    filtered: list[ExtractedOpportunity] = []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Per-email error → add a manual-review placeholder
            email = request.emails[i]
            logger.error("Pipeline error for email %d (%r): %s", i, email.subject[:60], result)
            placeholder = ExtractedOpportunity(
                is_opportunity=True,
                confidence=0.5,
                classification_reason=f"Processing error: {result}",
                needs_manual_review=True,
                raw_subject=email.subject,
                raw_body_snippet=email.body[:300],
            )
            opportunities.append(placeholder)
        else:
            opp, spam = result
            if opp is not None:
                opportunities.append(opp)
            if spam is not None:
                filtered.append(spam)

    # ------------------------------------------------------------------ #
    # Stage III  (synchronous — pure Python)                              #
    # ------------------------------------------------------------------ #
    scored: list[ScoredOpportunity] = [
        score_opportunity(opp, request.student_profile, rank=0)
        for opp in opportunities
    ]

    # Sort descending by total score; ineligible items go to the bottom
    scored.sort(
        key=lambda s: (s.score.is_eligible, s.score.total),
        reverse=True,
    )

    # Assign final ranks (1-based)
    for i, item in enumerate(scored, start=1):
        item.rank = i

    # ------------------------------------------------------------------ #
    # Summary stats                                                        #
    # ------------------------------------------------------------------ #
    urgent_count = sum(
        1 for s in scored
        if s.extracted.deadline
        and (s.extracted.deadline.date() - date.today()).days <= 14
        and s.score.is_eligible
    )

    nearest_days: int | None = None
    deadline_items = [
        s for s in scored
        if s.extracted.deadline and s.score.is_eligible
    ]
    if deadline_items:
        nearest_days = min(
            (s.extracted.deadline.date() - date.today()).days
            for s in deadline_items
        )

    summary = PipelineSummary(
        total_emails=len(request.emails),
        real_opportunities=len(opportunities),
        spam_filtered=len(filtered),
        urgent_count=urgent_count,
        top_deadline_days=nearest_days,
    )

    logger.info(
        "Pipeline complete | real=%d | spam=%d | urgent=%d",
        len(opportunities),
        len(filtered),
        urgent_count,
    )

    return PipelineResponse(
        summary=summary,
        ranked_opportunities=scored,
        filtered_emails=filtered,
    )
