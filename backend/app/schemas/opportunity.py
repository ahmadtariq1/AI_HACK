"""
Pydantic schemas for the Opportunity Inbox Copilot pipeline.

Covers:
  - EmailInput          : raw email from the user
  - StudentProfile      : structured student profile (Stage I / III input)
  - EligibilityCriteria : sub-object inside ExtractedOpportunity
  - ExtractedOpportunity: LLM output schema (Stage II output)
  - ClassificationResult: Stage I output
  - ScoredOpportunity   : Stage III output (adds all scoring fields)
  - PipelineRequest     : full API request body
  - PipelineResponse    : full API response
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class EmailInput(BaseModel):
    """A single raw email supplied by the user."""

    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Full email body text")


class StudentProfile(BaseModel):
    """Structured student profile used for personalised ranking."""

    degree_program: str = Field(
        ..., example="BS Computer Science", description="e.g. BS Computer Science, BBA"
    )
    semester: int = Field(..., ge=1, le=8, description="Current semester (1–8)")
    cgpa: float = Field(..., ge=0.0, le=4.0, description="Current CGPA (0.0–4.0)")
    skills_interests: List[str] = Field(
        ...,
        example=["Python", "Machine Learning", "Public Speaking"],
        description="Skill/interest keywords",
    )
    pref_opp_types: List[str] = Field(
        ...,
        example=["Scholarship", "Internship", "Fellowship"],
        description="Preferred opportunity types",
    )
    financial_need: str = Field(
        ...,
        example="Medium",
        description="Yes/No + level: High | Medium | Low  (e.g. 'Yes - High')",
    )
    location_pref: str = Field(
        ...,
        example="Pakistan",
        description="e.g. Pakistan | International | Remote",
    )
    past_experience: List[str] = Field(
        ...,
        example=["Django intern", "ML Research Assistant", "Competitive programming"],
        description="3–5 brief role/project tags",
    )


# ---------------------------------------------------------------------------
# Stage II — Extracted Opportunity Schema (LLM output)
# ---------------------------------------------------------------------------


class EligibilityCriteria(BaseModel):
    """Structured eligibility sub-object extracted from the email."""

    min_cgpa: Optional[float] = Field(None, description="Minimum CGPA requirement")
    target_semesters: Optional[List[int]] = Field(
        None, description="Eligible semesters, e.g. [6,7,8]"
    )
    degree_programs: Optional[List[str]] = Field(
        None, description="Eligible degree programs"
    )
    other: Optional[List[str]] = Field(
        None, description="Any other eligibility requirements as free-text bullets"
    )


class ExtractedOpportunity(BaseModel):
    """
    Structured opportunity data extracted from a single email.

    All fields are optional (LLM must return null rather than hallucinate).
    `needs_manual_review` is set True when extraction confidence is low.
    """

    # Classification echo
    is_opportunity: bool = Field(
        ..., description="Whether the email contains a real opportunity"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Classifier confidence score"
    )
    classification_reason: str = Field(
        ..., description="One-sentence reason for the classification decision"
    )

    # Core extraction fields
    opportunity_type: Optional[str] = Field(
        None,
        description="Internship | Scholarship | Competition | Fellowship | Admission | Other",
    )
    title: Optional[str] = Field(None, description="Short name/title of the opportunity")
    deadline: Optional[date] = Field(
        None, description="Application deadline in ISO format (YYYY-MM-DD)"
    )
    deadline_relative: Optional[str] = Field(
        None, description="Human-readable relative deadline e.g. 'in 5 days'"
    )
    eligibility: Optional[EligibilityCriteria] = Field(
        None, description="Structured eligibility criteria"
    )
    required_documents: Optional[List[str]] = Field(
        None, description="e.g. ['Resume', 'Transcript', 'CNIC']"
    )
    links_contact: Optional[List[str]] = Field(
        None, description="Application URLs, email addresses, or portal links"
    )
    stipend_funding: Optional[str] = Field(
        None, description="Stipend or funding details if mentioned"
    )
    organizer: Optional[str] = Field(
        None, description="Host/organiser of the opportunity"
    )

    # Meta
    needs_manual_review: bool = Field(
        False,
        description="True when extraction failed or confidence is low – show raw email",
    )
    raw_subject: Optional[str] = Field(None, description="Original email subject")
    raw_body_snippet: Optional[str] = Field(
        None, description="First 300 chars of email body for fallback display"
    )


# ---------------------------------------------------------------------------
# Stage I — Classification result (intermediate, also embedded in Extracted)
# ---------------------------------------------------------------------------


class ClassificationResult(BaseModel):
    """Output of Stage I binary classifier."""

    is_opportunity: bool
    confidence: float
    reason: str


# ---------------------------------------------------------------------------
# Stage III — Scored Opportunity (pipeline final output per email)
# ---------------------------------------------------------------------------


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of the three scoring components."""

    profile_fit: float = Field(..., description="Profile fit score 0–100 (60% weight)")
    urgency: float = Field(..., description="Urgency score 0–100 (25% weight)")
    completeness: float = Field(
        ..., description="Completeness score 0–100 (15% weight)"
    )
    total: float = Field(..., description="Weighted total score 0–100")
    is_eligible: bool = Field(
        ..., description="False when student CGPA is below hard requirement"
    )


class ScoredOpportunity(BaseModel):
    """An extracted opportunity enriched with scoring, reasoning, and action items."""

    rank: int = Field(..., description="Rank in the final sorted list (1 = best)")
    extracted: ExtractedOpportunity
    score: ScoreBreakdown
    why_text: str = Field(
        ...,
        description="One concise paragraph explaining the ranking",
    )
    why_bullets: List[str] = Field(
        ..., description="Bullet-point evidence linked to the student profile"
    )
    action_checklist: List[str] = Field(
        ..., description="Auto-generated action items for this opportunity"
    )


# ---------------------------------------------------------------------------
# API request / response wrappers
# ---------------------------------------------------------------------------


class PipelineRequest(BaseModel):
    """Full request body for POST /pipeline/process."""

    profile: StudentProfile
    emails: List[EmailInput] = Field(
        ..., min_length=1, max_length=20, description="1–20 emails to process"
    )


class PipelineSummary(BaseModel):
    """High-level stats shown in the dashboard Summary Bar."""

    total_emails: int
    real_opportunities: int
    spam_filtered: int
    urgent_count: int = Field(
        ..., description="Opportunities with deadline within 14 days"
    )
    top_deadline_days: Optional[int] = Field(
        None, description="Days until the single most urgent deadline"
    )


class PipelineResponse(BaseModel):
    """Full response from POST /pipeline/process."""

    summary: PipelineSummary
    ranked_opportunities: List[ScoredOpportunity]
    filtered_emails: List[ExtractedOpportunity] = Field(
        ..., description="Emails classified as non-opportunities (spam/noise)"
    )
