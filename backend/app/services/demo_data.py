"""
Demo data module — all 15 emails from better_dataset.txt + a sample student profile.

Exports
-------
DEMO_EMAILS   : List of {"subject": str, "body": str} dicts
DEMO_PROFILE  : Dict matching StudentProfile schema

Use in tests / main.py:
    from app.services.demo_data import DEMO_EMAILS, DEMO_PROFILE
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# All 15 emails from better_dataset.txt
# 7 real opportunities (Emails 1–7) + 8 spam/negatives (Emails 8–15)
# ---------------------------------------------------------------------------

DEMO_EMAILS: list[dict] = [
    # --- Ambiguous Positives (real, but tricky) ---
    {
        "subject": "CS Department Spring Update & Alumni News",
        "body": (
            "Welcome back to the Spring semester. We are proud to announce that "
            "Dr. Ahmed's paper was accepted at NeurIPS. Also, a reminder that the "
            "library closes at 8 PM on Fridays now. Finally, Google's local office "
            "reached out to us this morning; they have two unlisted summer internship "
            "slots for final-year students. Send your resume to the department head "
            "by 5 PM today if you want the referral."
        ),
    },
    {
        "subject": "Invite: Tech Leaders Mixer",
        "body": (
            "Join us this Thursday at the local tech park. We are hosting CTOs from "
            "five top software houses. There are no formal presentations, just coffee "
            "and conversation. We highly recommend bringing a few copies of your "
            "resume, as several of these companies are looking to bypass standard "
            "technical interviews for immediate hires."
        ),
    },
    {
        "subject": "Fwd: Fwd: Please share with seniors",
        "body": (
            "See below.\n"
            "--- Forwarded message ---\n"
            "Systems Ltd is doing an on-campus drive. Form closes midnight. "
            "Link: bit.ly/sys-drive-2026. Only fast-nu emails accepted."
        ),
    },
    {
        "subject": "Med-Tech Innovation Challenge",
        "body": (
            "The Medical College is hosting its annual hardware design challenge. "
            "We have several teams of medical students who have great ideas but no "
            "ability to code. We are opening up 10 slots for CS students to join as "
            "technical co-founders. Top prize is a 500k PKR grant."
        ),
    },
    {
        "subject": "Update on Summer Fellowship 2026",
        "body": (
            "Thank you to everyone who applied. The primary application window closed "
            "yesterday. However, due to a high volume of incomplete applications, we "
            "are opening a 24-hour waitlist form. Waitlisted candidates will be "
            "reviewed if spots open up."
        ),
    },
    {
        "subject": "Build on Web3 - Global Virtual Hackathon",
        "body": (
            "Join the Solana developer ecosystem this weekend. No prior blockchain "
            "experience required. We provide the API and RPC endpoints. Connect your "
            "wallet to register and join the main Discord channel to find a team. "
            "Bounties total $50k USD."
        ),
    },
    {
        "subject": "Call for Proposals: NLP for Regional Languages",
        "body": (
            "The linguistics department is offering a micro-grant of $500 for "
            "undergraduate engineering students. We need a script that can successfully "
            "tokenize Roman Urdu with high accuracy. Submit a one-page methodology "
            "by Monday."
        ),
    },
    # ---- Ambiguous Negatives (spam / noise) ---
    {
        "subject": "You have been selected! Global Youth Tech Summit",
        "body": (
            "Congratulations! Based on your GitHub profile, you have been selected "
            "to attend the Global Youth Tech Summit in Dubai as a student delegate. "
            "This is a premier networking fellowship. To secure your spot and receive "
            "your visa letter, please pay the $850 registration and processing fee "
            "by Friday."
        ),
    },
    {
        "subject": "Final Project: AI Hackathon Logistics",
        "body": (
            "For your final project in CS405, we will be simulating a hackathon "
            "environment. You have 48 hours to build your model. The team with the "
            "highest accuracy score on the test set will receive a 5% bonus on their "
            "final grade. Attendance in the lab is mandatory for the duration of the "
            "\"event\"."
        ),
    },
    {
        "subject": "Become a Red Bull Campus Ambassador",
        "body": (
            "Want to build your resume and gain marketing experience? Apply to be "
            "our campus ambassador. Your duties will include handing out samples "
            "during exam weeks, posting on your personal social media twice a week, "
            "and organizing campus events. Unpaid, but you get free merchandise and "
            "a certificate of participation."
        ),
    },
    {
        "subject": "Merit Scholarship Funds Ready for Deposit",
        "body": (
            "Dear Student, the financial aid office has approved a $2,000 merit "
            "scholarship for your upcoming semester based on your recent transcript. "
            "To process the direct deposit, please click the link below and verify "
            "your university portal login credentials and bank routing number within "
            "24 hours."
        ),
    },
    {
        "subject": "Now Hiring: Principal Data Architect",
        "body": (
            "We are expanding our data engineering team. We are looking for a "
            "Principal Data Architect with 10+ years of experience managing distributed "
            "Kafka clusters and enterprise-level Hadoop ecosystems. Competitive salary "
            "and stock options. Apply via our portal."
        ),
    },
    {
        "subject": "Tell us about your coding habits!",
        "body": (
            "We are conducting research on how IDEs are used by university students. "
            "Please take 15 minutes to fill out this detailed survey about your coding "
            "environment. Everyone who completes the survey will be entered into a "
            "raffle to win one of three $50 Amazon gift cards."
        ),
    },
    {
        "subject": "Nominations open for Debate Club Treasurer",
        "body": (
            "The current executive board is stepping down next month. If you are "
            "interested in running for the Treasurer position, you must submit a "
            "nomination form with 10 signatures from active club members by Thursday. "
            "Speeches will be held next Tuesday."
        ),
    },
    {
        "subject": "Looking for a tech wizard for the next Uber!",
        "body": (
            "I am a business major with an incredible idea that will disrupt the "
            "logistics industry. I just need a coder to build the app, set up the "
            "backend, and handle the AI integration. I can't pay you right now, but "
            "I am offering 5% equity in the company once we launch and secure funding. "
            "Let's meet at the cafe to discuss."
        ),
    },
]


# ---------------------------------------------------------------------------
# Demo student profile — a typical CS student
# ---------------------------------------------------------------------------

DEMO_PROFILE: dict = {
    "academic": {
        "degree_program": "BS Computer Science",
        "university": "FAST NUCES LAHORE",
        "semester": 6,
        "cgpa": 3.6
    },
    "technical": {
        "skills_and_interests": [
            "Python",
            "Machine Learning",
            "NLP",
            "Public Speaking",
            "Web Development",
            "Django"
        ]
    },
    "experience": [
        {
            "role": "Software Engineering Intern",
            "context": "Django intern (3 months)"
        },
        {
            "role": "Research Assistant",
            "context": "ML Research Assistant"
        },
        {
            "role": "Competitive Programmer",
            "context": "ICPC participant"
        }
    ],
    "logistics": {
        "preferred_opportunity_types": ["Internship", "Scholarship", "Competition", "Research"],
        "location_preference": ["Pakistan"],
        "financial_need": "stipend_required"
    }
}
