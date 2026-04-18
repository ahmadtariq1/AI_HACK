import { useState } from 'react'

const PLACEHOLDER = `Paste a raw opportunity email here...`

const DUMMY_EMAILS = [
  `Subject: Google Summer of Code 2026 — Applications Now Open

Dear Students,

We are thrilled to announce that Google Summer of Code 2026 is officially open for applications. GSoC is a global program focused on bringing student developers into open source software development.

Eligibility:
- Currently enrolled in a BS/MS/PhD program (CS, Software Engineering, or related field)
- Minimum CGPA: 3.0/4.0
- Strong programming skills required
- Open to students in any country

Requirements:
- Updated Resume / CV
- Project Proposal (600-800 words)
- GitHub profile showing open source contributions
- Cover Letter

Stipend: USD $3,000 – $6,600 depending on your country
Duration: May – August 2026
Mode: Fully Remote

Deadline: April 25, 2026

Apply here: summerofcode.withgoogle.com
Questions: gsoc-support@google.com`,

  `Subject: HEC Need-Based Scholarship 2026 — Applications Invited

Dear Student,

The Higher Education Commission (HEC) of Pakistan is pleased to invite applications for its Need-Based Scholarship Programme 2026-27. This programme aims to support talented but financially disadvantaged students pursuing higher education.

Eligibility Criteria:
- Enrolled in a recognized Pakistani university (Semester 1–8)
- Minimum CGPA: 2.5/4.0
- Monthly family income must not exceed PKR 45,000
- Must demonstrate genuine financial need

Documents Required:
- Official Transcript (from Registrar)
- CNIC copy (attested)
- Family Income Certificate (from Union Council or employer)
- Domicile Certificate
- Recent Photograph

Scholarship Amount: PKR 25,000 per month
Duration: Full academic year (renewable)

Last Date to Apply: May 10, 2026

Submit applications at: hec.gov.pk/scholarships
Helpline: 051-111-119-432`,

  `Subject: LUMS National Computing Olympiad 2026 — Register Now!

Greetings from LUMS!

The Lahore University of Management Sciences (LUMS) is organizing the 8th National Computing Olympiad (NCO) 2026. This prestigious competition brings together the brightest computer science minds from across Pakistan.

Who Can Participate?
- Undergraduate students enrolled in CS, Software Engineering, or IT programs
- CGPA requirement: 3.2/4.0 or above
- Teams of 2–3 members allowed
- Individual participation also accepted

Competition Format:
- Online Qualifier Round: April 22, 2026
- On-site Finals at LUMS Campus: May 5, 2026
- Problem domains: Algorithms, Data Structures, Dynamic Programming, Graph Theory

Required Documents:
- Current University ID / Enrollment Letter
- Resume (1 page)
- Team registration form

Prize Pool:
- 1st Place: PKR 150,000
- 2nd Place: PKR 75,000
- 3rd Place: PKR 40,000

Registration Deadline: April 30, 2026

Register at: lums.edu.pk/nco2026
Contact: nco@lums.edu.pk`,

  `Subject: The Weekly Startup Digest — Issue #214

Hi there,

Welcome to this week's Startup Digest! Here's what's trending in the Pakistani startup ecosystem:

📰 Airlift raises Series B funding of $85M
📰 10 productivity tools every founder should know
📰 How to network effectively at tech events
📰 Top 5 co-working spaces in Lahore 2026

Plus: Our sponsor this week is RemoteDesk — the best way to find remote jobs.

Unsubscribe | Manage Preferences | View in Browser

© 2026 Startup Digest Media, All rights reserved.`
]

export default function EmailInput({ onSubmit, profile }) {
  const [emails, setEmails] = useState(DUMMY_EMAILS)

  const updateEmail = (i, v) => setEmails(e => e.map((x, j) => j === i ? v : x))
  const addEmail    = () => emails.length < 15 && setEmails(e => [...e, ''])
  const removeEmail = (i) => emails.length > 1 && setEmails(e => e.filter((_, j) => j !== i))

  const handleSubmit = () => {
    const filled = emails.filter(e => e.trim().length > 20)
    if (filled.length === 0) return
    onSubmit(filled)
  }

  return (
    <div style={S.wrap}>
      <div style={S.container}>
        {/* Header */}
        <div style={S.header}>
          <span style={S.stage}>STAGE I / EMAIL INPUT</span>
          <h1 style={S.title}>UPLOAD DISPATCHES</h1>
          <p style={S.sub}>Paste raw opportunity emails below. Include the full body — subjects, deadlines, eligibility, links. The AI handles the rest.</p>
        </div>

        {/* Profile summary chip */}
        {profile && (
          <div style={S.profileChip}>
            <span style={S.mono}>AGENT PROFILE LOADED</span>
            <span style={S.chipDivider} />
            <span style={S.chipVal}>{profile.degree_program}</span>
            <span style={S.chipDivider} />
            <span style={S.chipVal}>CGPA {profile.cgpa}</span>
            <span style={S.chipDivider} />
            <span style={S.chipVal}>SEM {profile.semester}</span>
          </div>
        )}

        {/* Email textareas */}
        <div style={S.emailList}>
          {emails.map((email, i) => (
            <div key={i} style={{ ...S.emailBlock, animation: `fadeUp 0.4s var(--ease-out) ${i * 0.05}s both` }}>
              <div style={S.emailHeader}>
                <span style={S.dispatchLabel}>
                  <span style={S.dispatchDot} />
                  DISPATCH #{String(i + 1).padStart(3, '0')}
                </span>
                {emails.length > 1 && (
                  <button type="button" style={S.removeBtn} onClick={() => removeEmail(i)}>
                    REMOVE ×
                  </button>
                )}
              </div>
              <textarea
                id={`email-input-${i}`}
                style={S.textarea}
                placeholder={PLACEHOLDER}
                value={email}
                onChange={e => updateEmail(i, e.target.value)}
              />
              <div style={S.charCount}>
                {email.length > 0 ? `${email.length} CHARS` : 'AWAITING INPUT'}
              </div>
            </div>
          ))}
        </div>

        {/* Controls */}
        <div style={S.controls}>
          <div style={S.leftControls}>
            {emails.length < 15 && (
              <button id="add-dispatch-btn" type="button" style={S.addBtn} onClick={addEmail}
                onMouseEnter={e => e.target.style.borderColor = 'var(--amber)'}
                onMouseLeave={e => e.target.style.borderColor = 'var(--border-normal)'}>
                + ADD DISPATCH
              </button>
            )}
            <span style={S.counter}>
              {emails.filter(e => e.trim().length > 20).length} / 15 READY
            </span>
          </div>

          <button id="analyze-emails-btn" type="button" style={S.submitBtn}
            onClick={handleSubmit}
            onMouseEnter={e => { e.target.style.background = 'var(--amber)'; e.target.style.color = '#000' }}
            onMouseLeave={e => { e.target.style.background = 'transparent'; e.target.style.color = 'var(--amber)' }}>
            RUN ANALYSIS →
          </button>
        </div>

        <p style={S.hint}>
          ⚡ Tip: You can paste multiple emails in one box, separated by "---" dividers, or use the Add Dispatch button to process them individually.
        </p>
      </div>
    </div>
  )
}

const S = {
  wrap: { minHeight: '100vh', padding: '40px 20px', display: 'flex', justifyContent: 'center' },
  container: { width: '100%', maxWidth: '820px', animation: 'fadeUp 0.6s var(--ease-out) both' },
  header: { marginBottom: '28px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '24px' },
  stage: { fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.12em' },
  title: { fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 'clamp(2rem, 6vw, 3.5rem)', color: 'var(--text-bright)', letterSpacing: '-0.02em', margin: '8px 0 12px' },
  sub: { fontFamily: 'var(--font-body)', fontSize: '16px', color: 'var(--text-secondary)', lineHeight: 1.6 },
  profileChip: { display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap', padding: '10px 16px', background: 'var(--teal-dim)', border: '1px solid rgba(20,184,166,0.25)', borderRadius: '4px', marginBottom: '24px' },
  mono: { fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--teal)', letterSpacing: '0.1em' },
  chipDivider: { width: '1px', height: '14px', background: 'rgba(20,184,166,0.3)', flexShrink: 0 },
  chipVal: { fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)' },
  emailList: { display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' },
  emailBlock: { border: '1px solid var(--border-normal)', borderRadius: '6px', overflow: 'hidden', background: 'var(--bg-card)' },
  emailHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 16px', borderBottom: '1px solid var(--border-subtle)', background: 'var(--bg-elevated)' },
  dispatchLabel: { display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--amber)', letterSpacing: '0.1em' },
  dispatchDot: { width: '6px', height: '6px', borderRadius: '50%', background: 'var(--amber)', flexShrink: 0 },
  removeBtn: { fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer', letterSpacing: '0.08em', padding: '2px 8px' },
  textarea: { width: '100%', minHeight: '160px', padding: '16px', background: 'transparent', border: 'none', outline: 'none', resize: 'vertical', fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.7 },
  charCount: { padding: '6px 16px', fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.1em', borderTop: '1px solid var(--border-subtle)', textAlign: 'right' },
  controls: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' },
  leftControls: { display: 'flex', alignItems: 'center', gap: '20px' },
  addBtn: { fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)', border: '1px solid var(--border-normal)', borderRadius: '2px', padding: '10px 20px', background: 'transparent', cursor: 'pointer', letterSpacing: '0.08em', transition: 'border-color 0.2s' },
  counter: { fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-muted)', letterSpacing: '0.1em' },
  submitBtn: { fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '15px', letterSpacing: '0.12em', color: 'var(--amber)', border: '2px solid var(--amber-border)', borderRadius: '2px', padding: '14px 36px', background: 'transparent', cursor: 'pointer', transition: 'all 0.2s var(--ease-out)' },
  hint: { marginTop: '20px', fontFamily: 'var(--font-body)', fontStyle: 'italic', fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.6 },
}
