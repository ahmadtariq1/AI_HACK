"""
Pydantic schemas for the Opportunity Inbox Copilot pipeline.

Covers:
  - EmailInput
  - StudentProfile (Nested structure matching sample_user_profile.json)
  - ClassificationResult (Matches local_ollama_flag_results.json)
  - ExtractedOpportunity (Matches local_ie_results_updated_dataset.json)
  - ScoredOpportunity
  - PipelineRequest
  - PipelineResponse
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Input schemas (Student Profile)
# ---------------------------------------------------------------------------

class AcademicProfile(BaseModel):
    degree_program: str = Field(..., example="BS Computer Science")
    university: str = Field(..., example="FAST NUCES LAHORE")
    semester: int = Field(..., ge=1, le=8)
    cgpa: float = Field(..., ge=0.0, le=4.0)

class TechnicalProfile(BaseModel):
    skills_and_interests: List[str]

class ExperienceItem(BaseModel):
    role: str
    context: str

class LogisticsProfile(BaseModel):
    preferred_opportunity_types: List[str]
    location_preference: List[str]
    financial_need: str

class StudentProfile(BaseModel):
    academic: AcademicProfile
    technical: TechnicalProfile
    experience: List[ExperienceItem]
    logistics: LogisticsProfile


class EmailInput(BaseModel):
    """A single raw email supplied by the user."""
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Full email body text")


# ---------------------------------------------------------------------------
# Stage I — Classification result (Matches local_ollama_flag_results.json)
# ---------------------------------------------------------------------------

class ClassificationResult(BaseModel):
    """Output of Stage I binary classifier."""
    is_opportunity: bool
    rationale: str
    confidence: float = Field(1.0, description="Confidence score")


# ---------------------------------------------------------------------------
# Stage II — Extracted Opportunity Schema (Matches local_ie_results.json)
# ---------------------------------------------------------------------------

class ApplicationOrContact(BaseModel):
    emails: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    instructions: Optional[str] = None

class ExtractedOpportunity(BaseModel):
    """
    Structured opportunity data extracted from a single email.
    """
    # Classification echo
    is_opportunity: bool
    confidence: float = 1.0
    classification_reason: str = Field(..., alias="rationale")

    # Core extraction fields (Stage II)
    opportunity_type: Optional[str] = None
    deadline: Optional[datetime] = None
    deadline_text: Optional[str] = None
    eligibility_conditions: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    application_or_contact: Optional[ApplicationOrContact] = None

    # Meta
    needs_manual_review: bool = Field(False)
    raw_subject: Optional[str] = None
    raw_body_snippet: Optional[str] = None


# ---------------------------------------------------------------------------
# Stage III — Scored Opportunity
# ---------------------------------------------------------------------------

class ScoreBreakdown(BaseModel):
    """Detailed breakdown of the three scoring components."""
    profile_fit: float = Field(..., description="Profile fit score 0–100 (60% weight)")
    urgency: float = Field(..., description="Urgency score 0–100 (25% weight)")
    completeness: float = Field(..., description="Completeness score 0–100 (15% weight)")
    total: float = Field(..., description="Weighted total score 0–100")
    is_eligible: bool = Field(..., description="False when student CGPA is below hard requirement")


class ScoredOpportunity(BaseModel):
    """An extracted opportunity enriched with scoring, reasoning, and action items."""
    rank: int = Field(..., description="Rank in the final sorted list (1 = best)")
    extracted: ExtractedOpportunity
    score: ScoreBreakdown
    why_text: str = Field(..., description="One concise paragraph explaining the ranking")
    why_bullets: List[str] = Field(..., description="Bullet-point evidence linked to the student profile")
    action_checklist: List[str] = Field(..., description="Auto-generated action items for this opportunity")


# ---------------------------------------------------------------------------
# API request / response wrappers
# ---------------------------------------------------------------------------

class PipelineRequest(BaseModel):
    """Full request body for POST /pipeline/process."""
    student_profile: StudentProfile
    emails: List[EmailInput] = Field(..., min_length=1, max_length=20)


class PipelineSummary(BaseModel):
    """High-level stats shown in the dashboard Summary Bar."""
    total_emails: int
    real_opportunities: int
    spam_filtered: int
    urgent_count: int
    top_deadline_days: Optional[int] = None


class PipelineResponse(BaseModel):
    """Full response from POST /pipeline/process."""
    summary: PipelineSummary
    ranked_opportunities: List[ScoredOpportunity]
    filtered_emails: List[ExtractedOpportunity]

