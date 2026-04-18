"""
Stage III — Deterministic Scoring Engine

Responsibility
--------------
Rank extracted opportunities without any LLM calls.

Scoring formula (from guidelines):
    Total = (0.60 × ProfileFit) + (0.25 × Urgency) + (0.15 × Completeness)

Each component is a score in [0, 100].

Hard filter
-----------
If student CGPA < required min CGPA  →  is_eligible = False, Total = 0.

Profile Fit (60%)
-----------------
Sub-components (each 0–100), averaged with fixed weights:
  • CGPA buffer    (25 pts max) : how much above the minimum the student is
  • Skill overlap  (30 pts max) : fraction of opportunity-relevant skills matched
  • Type match     (20 pts max) : preferred_opp_types contains this type?
  • Location match (15 pts max) : location_pref matches opportunity location
  • Financial need (10 pts max) : student financial need + funded opportunity

Urgency (25%)
-------------
  deadline_days < 7  → 100
  deadline_days < 30 → linear 70–99
  deadline_days < 90 → linear 10–69
  deadline_days ≥ 90 → 0
  No deadline        → 40 (medium urgency)

Completeness (15%)
------------------
Fraction of known required documents / eligibility criteria the student
plausibly satisfies, based on their profile data.

Action Checklist
----------------
Auto-generated per opportunity based on required docs and deadline urgency.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import List, Optional

from app.schemas.opportunity import (
    ExtractedOpportunity,
    ScoreBreakdown,
    ScoredOpportunity,
    StudentProfile,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Keywords extracted from opportunity type labels → relevant skills
_TYPE_SKILL_MAP: dict[str, list[str]] = {
    "internship": ["python", "java", "sql", "machine learning", "data", "software",
                   "web", "django", "flask", "react", "communication"],
    "scholarship": ["leadership", "public speaking", "research", "academic"],
    "competition": ["python", "machine learning", "data science", "ai", "algorithms",
                    "competitive programming", "hackathon", "web3", "blockchain"],
    "fellowship": ["research", "leadership", "writing", "public speaking"],
    "admission": ["gre", "gmat", "ielts", "toefl", "research"],
    "research": ["python", "ml", "nlp", "data", "research", "statistics"],
    "other": [],
}


def _normalise(text: str) -> str:
    return text.lower().strip()

def _extract_min_cgpa(conditions: list[str]) -> Optional[float]:
    """Naively extract a CGPA requirement from flat strings."""
    for cond in conditions:
        if "cgpa" in cond.lower() or "gpa" in cond.lower():
            match = re.search(r"(\d\.\d+)", cond)
            if match:
                return float(match.group(1))
    return None

# ---------------------------------------------------------------------------
# Component scorers
# ---------------------------------------------------------------------------


def _score_profile_fit(opp: ExtractedOpportunity, profile: StudentProfile) -> tuple[float, list[str]]:
    """Return (fit_score 0-100, list of bullet evidence strings)."""
    bullets: list[str] = []
    total = 0.0

    # 1. CGPA buffer (25 pts)
    min_cgpa = _extract_min_cgpa(opp.eligibility_conditions)
    if min_cgpa is not None:
        if profile.academic.cgpa >= min_cgpa:
            buffer = min(profile.academic.cgpa - min_cgpa, 1.5)  # cap at 1.5 above
            cgpa_score = (buffer / 1.5) * 25
            bullets.append(
                f"✅ Your CGPA {profile.academic.cgpa:.2f} meets the {min_cgpa:.1f} requirement "
                f"(+{profile.academic.cgpa - min_cgpa:.2f} buffer)"
            )
        else:
            cgpa_score = 0.0
            bullets.append(
                f"❌ Your CGPA {profile.academic.cgpa:.2f} is below the {min_cgpa:.1f} requirement"
            )
    else:
        cgpa_score = 15.0  # neutral — no CGPA requirement stated
        bullets.append("ℹ️ No CGPA requirement specified")
    total += cgpa_score

    # 2. Skill overlap (30 pts)
    opp_type_key = _normalise(opp.opportunity_type or "other")
    relevant_skills = _TYPE_SKILL_MAP.get(opp_type_key, [])
    student_skills_lower = [_normalise(s) for s in profile.technical.skills_and_interests]

    if relevant_skills:
        matched = [s for s in relevant_skills if any(s in sk for sk in student_skills_lower)]
        overlap_ratio = len(matched) / len(relevant_skills)
        skill_score = overlap_ratio * 30
        if matched:
            bullets.append(f"✅ Matching skills: {', '.join(matched[:4])}")
        else:
            bullets.append("⚠️ No directly matching skills detected")
    else:
        skill_score = 15.0  # neutral
    total += skill_score

    # 3. Type preference match (20 pts)
    pref_types_lower = [_normalise(t) for t in profile.logistics.preferred_opportunity_types]
    opp_type_norm = _normalise(opp.opportunity_type or "")
    if opp_type_norm and opp_type_norm in pref_types_lower:
        type_score = 20.0
        bullets.append(f"✅ Matches your preferred opportunity type: {opp.opportunity_type}")
    else:
        type_score = 0.0
        bullets.append(f"ℹ️ Type '{opp.opportunity_type}' not in your preferences")
    total += type_score

    # 4. Location match (15 pts)
    # Give benefit of doubt for Pakistan since it's the primary context
    loc_prefs = [_normalise(lp) for lp in profile.logistics.location_preference]
    location_score = 0.0
    if "international" in loc_prefs or "remote" in loc_prefs or "any" in loc_prefs:
        location_score = 15.0
        bullets.append("✅ Matches your international/remote preference")
    elif "pakistan" in loc_prefs or "lahore" in loc_prefs:
        location_score = 12.0
        bullets.append("✅ Likely within Pakistan (matches location preference)")
    else:
        location_score = 7.0  # neutral
    total += location_score

    # 5. Financial need alignment (10 pts)
    fin_need = _normalise(profile.logistics.financial_need)
    fin_score = 0.0
    # No direct funding field in the new ExtractedOpportunity, so we give neutral
    if "stipend" in fin_need:
        fin_score = 8.0
    else:
        fin_score = 4.0
    total += fin_score

    return min(total, 100.0), bullets


def _score_urgency(opp: ExtractedOpportunity) -> float:
    """Return urgency score 0–100 based on deadline proximity."""
    if opp.deadline is None:
        return 40.0  # no deadline → medium urgency per guidelines

    # ExtractedOpportunity deadline is a datetime now.
    days = (opp.deadline.date() - date.today()).days

    if days < 0:
        return 5.0  # past deadline — still show but very low urgency
    if days < 7:
        return 100.0
    if days < 30:
        # Linear from 70 (at 7 days) → 50 at 30
        return 70.0 - ((days - 7) / 23) * 20
    if days < 90:
        return 40.0 - ((days - 30) / 60) * 30
    return 5.0


def _score_completeness(opp: ExtractedOpportunity, profile: StudentProfile) -> tuple[float, list[str]]:
    """Return completeness score 0–100 and additional bullets."""
    bullets: list[str] = []
    criteria_count = 0
    satisfied_count = 0

    # Required documents
    std_docs = {_normalise(d) for d in (opp.required_documents or [])}
    student_likely_has = {"resume", "cv", "transcript", "cnic"}  # typical student items

    if std_docs:
        criteria_count += len(std_docs)
        have = std_docs & student_likely_has
        satisfied_count += len(have)
        missing = std_docs - student_likely_has
        if have:
            bullets.append(f"📄 Documents you likely have: {', '.join(have)}")
        if missing:
            bullets.append(f"📋 Documents to prepare: {', '.join(missing)}")

    # Eligibility criteria (we do a naive match since it's a flat list now)
    if opp.eligibility_conditions:
        prog_lower = _normalise(profile.academic.degree_program)
        for cond in opp.eligibility_conditions:
            criteria_count += 1
            if "cgpa" in cond.lower() or "gpa" in cond.lower():
                min_cgpa = _extract_min_cgpa([cond])
                if min_cgpa and profile.academic.cgpa >= min_cgpa:
                    satisfied_count += 1
            elif "semester" in cond.lower() or "year" in cond.lower():
                # naive assumption they meet it
                satisfied_count += 1
                bullets.append("✅ Semester/Year requirement likely met")
            elif "cs" in cond.lower() or "computer" in cond.lower() or prog_lower in cond.lower():
                satisfied_count += 1
                bullets.append(f"✅ Your program ({profile.academic.degree_program}) matches eligibility")
            else:
                # default assume they might not meet it
                pass

    if criteria_count == 0:
        return 60.0, bullets  # neutral when no criteria known

    ratio = satisfied_count / criteria_count
    return round(ratio * 100, 1), bullets


# ---------------------------------------------------------------------------
# Action checklist generator
# ---------------------------------------------------------------------------


def _generate_action_checklist(
    opp: ExtractedOpportunity,
    deadline_days: Optional[int],
) -> List[str]:
    """Build an auto-generated action checklist for this opportunity."""
    actions: list[str] = []
    title = opp.title or opp.opportunity_type or "this opportunity"

    # Link / portal action
    if opp.application_or_contact:
        if opp.application_or_contact.emails:
            actions.append(f"📧 Email application to {opp.application_or_contact.emails[0]}")
        elif opp.application_or_contact.urls:
            actions.append(f"🔗 Open application link: {opp.application_or_contact.urls[0]}")
        
        if opp.application_or_contact.instructions:
            actions.append(f"📝 {opp.application_or_contact.instructions}")
    else:
        actions.append(f"🔍 Find the application portal for '{title}'")

    # Documents
    for doc in (opp.required_documents or []):
        if "resume" in doc.lower() or "cv" in doc.lower():
            actions.append(f"📝 Update your Resume/CV for {title}")
        elif "transcript" in doc.lower():
            actions.append("📄 Request official Transcript from the Registrar")
        elif "cnic" in doc.lower():
            actions.append("🪪 Prepare a scanned copy of your CNIC")
        elif "sop" in doc.lower() or "statement" in doc.lower():
            actions.append(f"✍️ Write Statement of Purpose for {title}")
        elif "letter" in doc.lower() or "recommendation" in doc.lower():
            actions.append("📩 Request a Recommendation Letter from a professor")
        else:
            actions.append(f"📋 Prepare: {doc}")

    # Deadline urgency
    if deadline_days is not None:
        formatted_date = opp.deadline.date().isoformat()
        if deadline_days <= 3:
            actions.insert(0, f"🚨 URGENT: Submit by {formatted_date} — only {deadline_days} day(s) left!")
        elif deadline_days <= 7:
            actions.insert(0, f"⏰ Submit before {formatted_date} ({deadline_days} days remaining)")
        else:
            actions.append(f"📅 Mark deadline {formatted_date} in your calendar")
    else:
        actions.append("📅 Clarify deadline — not found in email")

    return actions


# ---------------------------------------------------------------------------
# Public scoring function
# ---------------------------------------------------------------------------


def score_opportunity(
    opp: ExtractedOpportunity,
    profile: StudentProfile,
    rank: int = 0,
) -> ScoredOpportunity:
    """
    Stage III — score and annotate a single extracted opportunity.
    """
    # --- Hard eligibility check ---
    min_cgpa = _extract_min_cgpa(opp.eligibility_conditions)
    is_eligible = True
    if min_cgpa is not None and profile.academic.cgpa < min_cgpa:
        is_eligible = False

    # --- Component scores ---
    if not is_eligible:
        fit_score = 0.0
        fit_bullets = [
            f"❌ Ineligible: your CGPA {profile.academic.cgpa:.2f} < required {min_cgpa:.1f}"
        ]
    else:
        fit_score, fit_bullets = _score_profile_fit(opp, profile)

    urgency_score = _score_urgency(opp)
    completeness_score, comp_bullets = _score_completeness(opp, profile)

    all_bullets = fit_bullets + comp_bullets

    # --- Weighted total ---
    if not is_eligible:
        total = 0.0
    else:
        total = round(
            (0.60 * fit_score) + (0.25 * urgency_score) + (0.15 * completeness_score),
            2,
        )

    score = ScoreBreakdown(
        profile_fit=round(fit_score, 2),
        urgency=round(urgency_score, 2),
        completeness=round(completeness_score, 2),
        total=total,
        is_eligible=is_eligible,
    )

    # --- Why text summary ---
    if not is_eligible:
        why_text = (
            f"Ineligible: your CGPA ({profile.academic.cgpa:.2f}) is below "
            f"the required {min_cgpa:.1f}. Consider applying if your CGPA improves."
        )
    else:
        why_text = (
            f"Ranked with a score of {total:.1f}/100. "
            f"Profile fit: {fit_score:.0f}/100 — "
            f"Urgency: {urgency_score:.0f}/100 — "
            f"Completeness: {completeness_score:.0f}/100."
        )

    # --- Deadline days for checklist ---
    deadline_days: Optional[int] = None
    if opp.deadline:
        deadline_days = (opp.deadline.date() - date.today()).days

    action_checklist = _generate_action_checklist(opp, deadline_days)

    logger.info(
        "score_opportunity | subject=%r | total=%.1f | eligible=%s",
        opp.raw_subject or opp.title or "?",
        total,
        is_eligible,
    )

    return ScoredOpportunity(
        rank=rank,
        extracted=opp,
        score=score,
        why_text=why_text,
        why_bullets=all_bullets,
        action_checklist=action_checklist,
    )
