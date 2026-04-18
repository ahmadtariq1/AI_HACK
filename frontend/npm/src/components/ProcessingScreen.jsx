import { useState, useEffect } from 'react'

const STAGES = [
  {
    id: 'I',
    label: 'BINARY CLASSIFICATION',
    desc: 'Filtering inbox for actionable opportunity signals',
    logs: [
      '✓ Email 1: OPPORTUNITY DETECTED — Internship (confidence 98%)',
      '✓ Email 2: OPPORTUNITY DETECTED — Scholarship (confidence 95%)',
      '✗ Email 3: FILTERED OUT — Generic newsletter, no actionable content',
      '✓ Email 4: OPPORTUNITY DETECTED — Competition (confidence 91%)',
      '✓ Email 5: OPPORTUNITY DETECTED — Internship (confidence 87%)',
      '→ Stage I complete. 4 signals extracted, 1 discarded.',
    ],
    duration: 1600,
  },
  {
    id: 'II',
    label: 'STRUCTURED EXTRACTION',
    desc: 'Converting natural language to structured JSON via LLM',
    logs: [
      '→ Dispatching Email 1 to extraction model...',
      '→ Parsing deadline: "April 25" → 2026-04-25 ✓',
      '→ Extracting eligibility: Min CGPA 3.0, CS/Engineering ✓',
      '→ Parsing requirements: [Resume, Cover Letter, Code Sample] ✓',
      '→ Repeating for Emails 2, 4, 5...',
      '→ Stage II complete. All fields normalized.',
    ],
    duration: 1800,
  },
  {
    id: 'III',
    label: 'DETERMINISTIC SCORING',
    desc: 'Computing fit, urgency & preference scores without hallucination',
    logs: [
      '→ Computing Fit Score (50% weight)...',
      '→ CGPA 3.8 ≥ required 3.0 — ELIGIBLE ✓',
      '→ Skill match: Python, ML → 95% overlap ✓',
      '→ Computing Urgency Score (30% weight)...',
      '→ 7 days remaining — urgency: HIGH ⚡',
      '→ Computing Preference Score (20% weight)...',
      '→ Location: Remote ✓ — Type: Internship ✓',
      '→ Ranking 4 opportunities by total score...',
      '✓ Analysis complete. Intelligence brief ready.',
    ],
    duration: 1800,
  },
]

export default function ProcessingScreen() {
  const [stageIdx, setStageIdx]     = useState(0)
  const [logIdx, setLogIdx]         = useState(0)
  const [stagesDone, setStagesDone] = useState([])
  const [progress, setProgress]     = useState(0)

  useEffect(() => {
    let cancelled = false
    let totalElapsed = 0

    const runStages = async () => {
      for (let s = 0; s < STAGES.length; s++) {
        if (cancelled) return
        setStageIdx(s)
        setLogIdx(0)

        const stage = STAGES[s]
        const logDelay = stage.duration / (stage.logs.length + 1)

        for (let l = 0; l < stage.logs.length; l++) {
          if (cancelled) return
          await delay(logDelay)
          setLogIdx(l + 1)
        }

        await delay(300)
        setStagesDone(d => [...d, s])
        totalElapsed += stage.duration + 300
        setProgress(Math.round(((s + 1) / STAGES.length) * 100))
      }
    }

    runStages()
    return () => { cancelled = true }
  }, [])

  const currentStage = STAGES[stageIdx]

  return (
    <div style={S.wrap}>
      <div style={S.container}>
        <div style={S.header}>
          <span style={S.stage}>PROCESSING / THREE-STAGE PIPELINE</span>
          <h1 style={S.title}>ANALYZING DISPATCHES</h1>
        </div>

        {/* Progress bar */}
        <div style={S.progressOuter}>
          <div style={{ ...S.progressBar, width: `${progress}%` }} />
        </div>
        <div style={S.progressLabel}>
          <span style={S.mono}>{progress}% COMPLETE</span>
          <span style={{ ...S.mono, color: 'var(--amber)', animation: 'blink 1s step-end infinite' }}>█</span>
        </div>

        {/* Stage cards */}
        <div style={S.stagesRow}>
          {STAGES.map((st, i) => {
            const done    = stagesDone.includes(i)
            const active  = stageIdx === i && !done
            const pending = !done && !active
            return (
              <div key={st.id} style={{ ...S.stageCard, ...(active ? S.stageActive : done ? S.stageDone : S.stagePending) }}>
                <div style={S.stageNum}>
                  {done
                    ? <span style={{ color: 'var(--teal)', fontSize: '18px' }}>✓</span>
                    : active
                      ? <div style={S.spinner} />
                      : <span style={{ color: 'var(--text-muted)' }}>○</span>
                  }
                </div>
                <div>
                  <div style={S.stageId}>STAGE {st.id}</div>
                  <div style={{ ...S.stageLabel, color: active ? 'var(--text-bright)' : done ? 'var(--teal)' : 'var(--text-muted)' }}>{st.label}</div>
                  <div style={S.stageDesc}>{st.desc}</div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Live log */}
        <div style={S.logBox}>
          <div style={S.logHeader}>
            <span style={{ color: 'var(--amber)', letterSpacing: '0.1em' }}>LIVE OUTPUT — STAGE {currentStage.id}</span>
            <span style={{ color: 'var(--text-muted)' }}>// {currentStage.label}</span>
          </div>
          <div style={S.logBody}>
            {currentStage.logs.slice(0, logIdx).map((line, i) => (
              <div key={i} style={{ ...S.logLine, animationDelay: `${i * 0.05}s` }}>
                <span style={{ color: line.startsWith('✓') ? 'var(--teal)' : line.startsWith('✗') ? 'var(--red)' : 'var(--text-secondary)' }}>
                  {line}
                </span>
              </div>
            ))}
            {logIdx < currentStage.logs.length && (
              <div style={{ ...S.logLine, color: 'var(--amber)' }}>
                <span style={{ animation: 'blink 0.8s step-end infinite' }}>█</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

const delay = (ms) => new Promise(r => setTimeout(r, ms))

const S = {
  wrap: { minHeight: '100vh', padding: '40px 20px', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  container: { width: '100%', maxWidth: '780px', animation: 'fadeUp 0.5s var(--ease-out) both' },
  header: { marginBottom: '32px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '20px' },
  stage: { fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.12em' },
  title: { fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 'clamp(2rem, 5vw, 3rem)', color: 'var(--text-bright)', margin: '8px 0 0' },
  progressOuter: { height: '3px', background: 'var(--bg-elevated)', borderRadius: '2px', overflow: 'hidden', marginBottom: '8px' },
  progressBar: { height: '100%', background: 'linear-gradient(90deg, var(--amber), var(--amber-bright))', borderRadius: '2px', transition: 'width 0.8s var(--ease-out)', boxShadow: '0 0 12px var(--amber-glow)' },
  progressLabel: { display: 'flex', justifyContent: 'space-between', marginBottom: '28px' },
  mono: { fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.1em' },
  stagesRow: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '12px', marginBottom: '24px' },
  stageCard: { display: 'flex', alignItems: 'flex-start', gap: '14px', padding: '18px', borderRadius: '6px', border: '1px solid', transition: 'all 0.3s var(--ease-out)' },
  stageActive:  { background: 'var(--bg-elevated)', borderColor: 'var(--amber-border)', boxShadow: '0 0 20px var(--amber-dim)' },
  stageDone:    { background: 'var(--teal-dim)', borderColor: 'rgba(20,184,166,0.25)' },
  stagePending: { background: 'var(--bg-card)', borderColor: 'var(--border-subtle)' },
  stageNum: { width: '24px', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', paddingTop: '2px' },
  spinner: { width: '18px', height: '18px', border: '2px solid var(--amber-border)', borderTopColor: 'var(--amber)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' },
  stageId: { fontFamily: 'var(--font-mono)', fontSize: '10px', letterSpacing: '0.12em', color: 'var(--text-muted)', marginBottom: '4px' },
  stageLabel: { fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '13px', letterSpacing: '0.04em', marginBottom: '4px', transition: 'color 0.3s' },
  stageDesc: { fontFamily: 'var(--font-body)', fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5 },
  logBox: { border: '1px solid var(--border-normal)', borderRadius: '6px', overflow: 'hidden', background: 'var(--bg-void)' },
  logHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 16px', borderBottom: '1px solid var(--border-subtle)', fontFamily: 'var(--font-mono)', fontSize: '11px', background: 'var(--bg-card)' },
  logBody: { padding: '16px', minHeight: '180px', fontFamily: 'var(--font-mono)', fontSize: '12px', lineHeight: 1.8, display: 'flex', flexDirection: 'column', gap: '2px' },
  logLine: { animation: 'logAppear 0.3s var(--ease-out) both' },
}
