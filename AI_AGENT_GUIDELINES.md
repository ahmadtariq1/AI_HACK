# 📑 AI Agent Guidelines: Opportunity Inbox Copilot

## 1. Project Overview
**Objective:** Build an AI-powered system to parse opportunity emails, extract structured data, and rank them using a deterministic engine based on a student’s unique profile.
**Target Goal:** A working MVP capable of processing 5–15 emails within a 6-hour development window.
**Core Objective:** Turn a messy inbox + student profile → ranked, evidence-backed action list in <15 seconds.
**MVP Success:** End-to-end demo works with 5–15 realistic English emails, showing which are real opportunities vs spam, extracting clean structured data, personalizing rankings, and providing a one-click action checklist.

## 2. Functional Requirements & Data Schemas

### A. Input Module & Student Profile Schema (Required Input)
* **Email Ingestion:** Drag-and-drop or “Paste all emails” textarea (supports raw text, EML, copied Gmail/Outlook body, or a JSON list containing `subject` and `body` fields for each email).
* **Batch Size:** 5–15 emails (auto-split by “-----” or new line if pasted).
* **Demo Data:** Pre-loaded “Ignored Inbox” button (8 sample emails: 5 real + 3 spam) is required.

The AI must use this structured profile to evaluate fit. Do not use free-text for the profile. Required fields:

| Field | Data Type | Description |
| :--- | :--- | :--- |
| `degree_program` | String | e.g., BS Computer Science, BBA. |
| `semester` | Integer | Current semester (1–8). |
| `cgpa` | Float | Current CGPA (0.0 – 4.0). |
| `skills_interests` | List[String] | Keywords (multi-select): "Python", "Machine Learning", "Public Speaking". |
| `pref_opp_types` | List[String] | Checkboxes: Scholarship, Internship, Fellowship, Competition, Admission, Other. |
| `financial_need` | String | Yes/No + level: High/Medium/Low. |
| `location_pref` | String | e.g., "Pakistan", "International", "Remote". |
| `past_experience` | List[String] | Brief tags of previous roles or projects (3-5 tags). |

### B. Extracted Opportunity Schema (LLM Output)
The AI Agent must extract these fields from "messy" natural language emails (all mandatory where present):
* **Opportunity Type:** Classification (Internship, Scholarship, Competition, etc.).
* **Title / Short Description:** Name of the opportunity.
* **Deadline:** ISO date (YYYY-MM-DD format) + relative "in X days".
* **Eligibility Criteria:** Structured list (Min CGPA, Target Semesters, Degree).
* **Required Documents:** List of docs (Resume, Transcript, CNIC).
* **Links/Contact:** Direct application URL, email address, or portal.
* **Stipend / Funding:** Details if mentioned.
* **Organizer / Source:** Who is hosting or providing the opportunity.

## 3. The Three-Stage Pipeline

### Stage I: Binary Classification
* **Task:** Filter the inbox.
* **Logic:** Identify if the email contains a specific, actionable opportunity.
* **Method:** LLM prompt (zero-shot) + confidence score > 0.7.
* **Discard:** Newsletters, generic university announcements, or marketing spam.

### Stage II: Structured Extraction (LLM)
* **Task:** Convert text to JSON.
* **Constraint:** Use Pydantic or strict prompting (JSON mode + few-shot examples) to ensure the output matches the Extracted Opportunity Schema.
* **Normalization:** Convert relative dates (e.g., "this Friday") into absolute dates based on the current date (April 18, 2026).

### Stage III: Deterministic Scoring (Python Logic)
* **Task:** Rank opportunities without LLM hallucinations.
* **Formula:** `Total Score = (0.6 * Fit) + (0.25 * Urgency) + (0.15 * Completeness)`

## 4. Scoring Engine Logic
To ensure the ranking is evidence-backed, use the following logic weights (Three independent scores 0-100):

* **Profile Fit (60% weight):**
  * Weighted sum of CGPA match, skill overlap, type preference, location, financial need.
  * **Hard Filter:** If `student_cgpa < required_cgpa`, the opportunity is flagged as "Ineligible" (Score: 0).
* **Urgency (25% weight):**
  * Score is 100 if deadline < 7 days.
  * Linear decay to 0 at 90+ days.
* **Completeness (15% weight):**
  * % of required documents/eligibility the student already satisfies.

*(Note: Final score sorts descending to create the ranked list.)*

## 5. Output Requirements (The "Actionable" Checklist)
The final UI must display:
* **Summary Dashboard:** E.g., “Out of 12 emails → 7 real opportunities”, “Top 3 have deadlines < 14 days”. Quick filters for Urgent, High Fit, or Scholarships only.
* **Priority Rank Cards (expandable):** A sorted list from highest to lowest score. Header includes Rank #, Title, Deadline badge (red/yellow/green), Score badge.
* **The "Why":** A concise explanation (e.g., "Top Match: Matches your interest in AI and your 3.8 CGPA exceeds the 3.0 requirement.") with bullet evidence linked to the profile.
* **Extracted Fields:** Clean table view of the structured data.
* **Action Checklist:** Auto-generated, clickable list:
  * [ ] Update Resume for [Opportunity Name / skill]
  * [ ] Gather Transcript (due in 3 days)
  * [ ] Submit via Google Form link

## 6. MVP Constraints & Guardrails
* **Volume:** Optimize for 5–15 emails.
* **Speed:** The whole pipeline (extraction and scoring) should complete in under **15 seconds** for the entire batch.
* **Accuracy:** If the AI is unsure of a deadline, it must return `null` rather than a "hallucinated" date.
* **Tech Stack:** 
  * **Frontend:** React (replacing Streamlit).
  * **Backend:** Python + LangChain / LlamaIndex or raw OpenAI/Groq/Claude API.
  * **LLM:** Fast/cheap JSON mode capable models like Groq (Llama-3.3-70B) or OpenAI GPT-4o-mini (No training, no vector DB needed).
* **Privacy:** Everything runs in-memory or via API keys (no data stored).
* **Mobile-friendly:** A bonus requirement.

## 7. Edge Cases & Error Handling
* **Missing Deadlines:** Handle explicitly → default urgency to medium, but rank primarily by fit.
* **Multiple Opportunities:** Handle emails containing more than one opportunity.
* **Messy Formatting:** Ignore non-text elements (tables, images, etc.).
* **Language Mix:** Target primarily English, but robust against Urdu/English mix where possible.
* **Fallback:** Graceful fallback if extraction fails → show raw text + “manual review needed”.

## 8. 6-Hour Architecture Plan (Suggested)
| Time | Task | Owner |
| :--- | :--- | :--- |
| **0–30 min** | Setup React App + Backend API + pre-load demo emails | All |
| **30–90 min** | Profile form + email input UI | Frontend |
| **90–150 min** | Classifier + Extraction prompts (JSON mode) | AI |
| **150–210 min** | Scoring engine + ranking logic (pure Python) | Backend |
| **210–270 min** | Output cards + action checklist generator | Full |
| **270–300 min** | Polish UI, add loading animations, demo script | All |
| **300–360 min** | Testing with 3 different student profiles + edge cases | QA |

## 9. React Frontend Guidelines (Hackathon Blueprint)

### A. Tech Stack (Fastest for Hackathon)
* React 18 + Vite (JS)
* Tailwind CSS + Shadcn/ui (for beautiful cards, forms, badges, tables, progress bars)
* Lucide React (lightweight icons)
* React Hook Form + Zod (for profile validation)
* TanStack Query (or native fetch + loading states) for API calls
* Zustand (tiny state store for profile and results slices)
* Responsive by default; no auth required.

### B. App Structure (Single-Page Flow)
A multi-step wizard style state machine:
1. **Step 1:** Profile Form + "Next" button.
2. **Step 2:** Email Uploader + “Process Inbox” button.
3. **Step 3:** Results Dashboard + “Start Over” button.

### C. Color Scheme & Branding
* **Primary:** Fast tech feel (e.g., Sky Blue).
* **Accent:** Violet/Purple.
* **Background:** Dark mode by default (Neutral slate) for a modern, premium look.
* **Status Colors:**
  * **Success/High Match:** Emerald Green.
  * **Warning/Medium Match/Soon Deadline:** Amber/Yellow.
  * **Danger/Low Match/Urgent Deadline:** Rose/Red.
* Consistent rounded corners, slight shadows, and subtle borders everywhere.

### D. Step 1: Profile Form
* Two-column layout on desktop.
* Real-time validation.
* Must include a “Load Demo Profile” button to instantly pre-fill for a target student (e.g., a CS major).
* Save the validated profile to the state store and proceed to step 2.

### E. Step 2: Email Uploader
* Drag & Drop zone with clear accent borders.
* Accept JSON files (a list of emails including `subject` and `body`) or direct paste into a textarea (raw text, EML, etc.).
* Show a preview of "X emails loaded".
* Include a “Load Sample Inbox” button (representing a mix of real opportunities and spam).
* Distinct "Process Inbox" call-to-action that triggers a full-screen processing overlay (spinner/animation).

### F. Step 3: Results Dashboard
* **Summary Bar (Sticky):** Show metrics like “12 emails scanned → 7 real opportunities”, “3 urgent”. Quick filters for Urgent, High Fit, or Scholarships.
* **Ranked List:** Vertical stack of expandable Opportunity Cards.
* **Opportunity Card Design:**
  * Header showing Rank #, Title, exact Score, Type pill, and color-coded Urgency badge.
  * **The "Why":** A dedicated section explaining the fit (e.g., matching degree, CGPA, skills) using bullet points linked back to the profile data.
  * **Extracted Data Table:** Clean presentation of deadline, eligibility, required docs, and links.
  * **Action Checklist:** Auto-generated interactive checkboxes (e.g., "Prepare transcript", "Update resume with ML project").
  * A prominent "Open Application Link" button.

### G. Extra Polish (Judges Love These)
* Loading skeleton cards while processing AI tasks.
* Confetti effects upon successful results load.
* A dark-mode-only premium aesthetic.
* Mobile-perfect responsive design where cards stack cleanly.
* Keyboard shortcuts (e.g., Ctrl+K to start over).
* Optional "Export as PDF" or print friendly view.

> **Note to Agents:** Prioritize Reliability over Creativity. The student depends on the accuracy of these deadlines and eligibility criteria.
