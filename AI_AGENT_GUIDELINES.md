# 📑 AI Agent Guidelines: Opportunity Inbox Copilot

## 1. Project Overview
**Objective:** Build an AI-powered system to parse opportunity emails, extract structured data, and rank them using a deterministic engine based on a student’s unique profile.
**Target Goal:** A working MVP capable of processing 5–15 emails within a 6-hour development window.

## 2. Data Schemas (Input/Output)

### A. Student Profile Schema (Required Input)
The AI must use this structured profile to evaluate fit. Do not use free-text for the profile.

| Field | Data Type | Description |
| :--- | :--- | :--- |
| `degree_program` | String | e.g., BS Computer Science, BBA. |
| `semester` | Integer | Current semester (1–8). |
| `cgpa` | Float | Current CGPA (0.0 – 4.0). |
| `skills_interests` | List[String] | Keywords: "Python", "Machine Learning", "Public Speaking". |
| `pref_opp_types` | List[String] | e.g., ["Internship", "Scholarship", "Hackathon"]. |
| `financial_need` | Boolean | True if the student requires financial aid. |
| `location_pref` | String | e.g., "Lahore", "Remote", "No Preference". |
| `past_experience` | List[String] | Brief tags of previous roles or projects. |

### B. Extracted Opportunity Schema (LLM Output)
The AI Agent must extract these fields from "messy" natural language emails:
* **Opportunity Type:** Classification (Internship, Scholarship, Competition, etc.).
* **Deadline:** Standardized YYYY-MM-DD.
* **Eligibility Criteria:** Structured (Min CGPA, Target Semesters, Degree).
* **Requirements:** List of docs (Resume, Transcript, CNIC).
* **Links/Contact:** Direct application URL or email address.

## 3. The Three-Stage Pipeline

### Stage I: Binary Classification
* **Task:** Filter the inbox.
* **Logic:** Identify if the email contains a specific, actionable opportunity.
* **Discard:** Newsletters, generic university announcements, or marketing spam.

### Stage II: Structured Extraction (LLM)
* **Task:** Convert text to JSON.
* **Constraint:** Use Pydantic or strict prompting to ensure the output matches the Extracted Opportunity Schema.
* **Normalization:** Convert relative dates (e.g., "this Friday") into absolute dates based on the current date (April 18, 2026).

### Stage III: Deterministic Scoring (Python Logic)
* **Task:** Rank opportunities without LLM hallucinations.
* **Formula:** `Total Score = (W_fit * S_fit) + (W_urgency * S_urgency) + (W_pref * S_pref)`

## 4. Scoring Engine Logic
To ensure the ranking is evidence-backed, use the following logic weights:

* **Fit Score (S_fit) - 50%:**
  * **Hard Filter:** If `student_cgpa < required_cgpa`, the opportunity is flagged as "Ineligible" (Score: 0).
  * **Skill Match:** Percentage of `skills_interests` matching the opportunity keywords.
* **Urgency Score (S_urgency) - 30%:**
  * Exponentially increase the score as the deadline approaches.
  * **Formula suggestion:** `100 / (Days Remaining + 1)`.
* **Preference Score (S_pref) - 20%:**
  * Bonus points if the Opportunity Type matches the student's `pref_opp_types`.
  * Bonus points if `location_pref` matches the opportunity location.

## 5. Output Requirements (The "Actionable" Checklist)
The final UI must display:
* **Priority Rank:** A sorted list from highest to lowest score.
* **The "Why":** A concise explanation (e.g., "Top Match: Matches your interest in AI and your 3.8 CGPA exceeds the 3.0 requirement.")
* **Action Checklist:** 
  * [ ] Update Resume for [Opportunity Name]
  * [ ] Request Transcript (Required)
  * [ ] Apply by [Deadline Date]

## 6. MVP Constraints & Guardrails
* **Volume:** Optimize for 5–15 emails.
* **Speed:** The extraction and scoring should complete in under 30 seconds for the entire batch.
* **Accuracy:** If the AI is unsure of a deadline, it must return `null` rather than a "hallucinated" date.
* **Tech Stack:** Use Streamlit for the UI and LangChain/OpenAI/Gemini for the core extraction.

> **Note to Agents:** Prioritize Reliability over Creativity. The student depends on the accuracy of these deadlines and eligibility criteria.

