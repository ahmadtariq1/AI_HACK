"""
Pipeline API endpoint — POST /api/v1/pipeline/process

Routes
------
POST /process   : Run the full 3-stage pipeline on a batch of emails.
GET  /demo      : Return a pre-built demo payload (15 emails + student profile).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.opportunity import (
    EmailInput,
    PipelineRequest,
    PipelineResponse,
    StudentProfile,
)
from app.services.demo_data import DEMO_EMAILS, DEMO_PROFILE
from app.services.pipeline import run_pipeline

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /process
# ---------------------------------------------------------------------------


@router.post(
    "/process",
    response_model=PipelineResponse,
    summary="Run the full AI pipeline on a batch of emails",
    description=(
        "Accepts a student profile and a list of emails. "
        "Runs Stage I (binary classification), Stage II (structured extraction), "
        "and Stage III (deterministic scoring). Returns a ranked list of opportunities."
    ),
)
async def process_emails(request: PipelineRequest) -> PipelineResponse:
    """Run the 3-stage pipeline and return ranked opportunities."""
    try:
        return await run_pipeline(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# GET /demo
# ---------------------------------------------------------------------------


@router.get(
    "/demo",
    response_model=PipelineResponse,
    summary="Run the pipeline on demo data",
    description=(
        "Loads the pre-built demo inbox (15 emails from better_dataset.txt) "
        "and a sample CS student profile, then runs the full pipeline. "
        "Use this endpoint to quickly validate the system without supplying data."
    ),
)
async def run_demo() -> PipelineResponse:
    """Run the pipeline on the built-in demo dataset."""
    try:
        profile = StudentProfile(**DEMO_PROFILE)
        emails = [EmailInput(**e) for e in DEMO_EMAILS]
        request = PipelineRequest(profile=profile, emails=emails)
        return await run_pipeline(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
