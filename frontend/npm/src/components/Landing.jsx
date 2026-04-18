import { useEffect, useState } from 'react'

const BG_SNIPPETS = [
  'Subject: Internship — Google Summer of Code 2026 applications now open...',
  'Dear Student, HEC Need-Based Scholarship invites applications from enrolled...',
  'LUMS National Computing Olympiad — Registration deadline April 30th...',
  'Microsoft Research Fellowship — Min CGPA 3.5, CS/EE programs only...',
  'Unilever Future Leaders Programme — Apply before May 15, 2026...',
  'Aga Khan Foundation International Scholarship 2026 applications open...',
  'Hackathon Registration — $10,000 in prizes, fully remote participation...',
  'Re: Research Assistantship — Join our ML lab, stipend PKR 35,000/month...',
]

const STATUS_CYCLE = [
  'SCANNING INBOX FOR SIGNALS...',
  'RUNNING BINARY CLASSIFICATION...',
  'EXTRACTING STRUCTURED DATA...',
  'COMPUTING FIT SCORES...',
  'GENERATING INTELLIGENCE BRIEF...',
]

export default function Landing({ onStart }) {
  const [statusIdx, setStatusIdx] = useState(0)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    setVisible(true)
    const t = setInterval(() => setStatusIdx(i => (i + 1) % STATUS_CYCLE.length), 2200)
    return () => clearInterval(t)
  }, [])

  return (
    <div style={styles.wrap}>
      {/* Floating background email snippets */}
      <div style={styles.bgLayer} aria-hidden="true">
        {BG_SNIPPETS.map((s, i) => (
          <div key={i} style={{ ...styles.bgSnippet, animationDelay: `${i * 1.4}s`, top: `${10 + i * 10}%`, left: `${(i % 2 === 0 ? 5 : 55)}%` }}>
            {s}
          </div>
        ))}
      </div>

      {/* Scanline sweep */}
      <div style={styles.scanline} aria-hidden="true" />

      {/* Main content */}
      <div style={{ ...styles.content, opacity: visible ? 1 : 0, transition: 'opacity 0.6s' }}>
        <div style={{ ...styles.badge, animationDelay: '0.1s' }}>
          <span style={styles.dot} />
          SIGNAL INTELLIGENCE SYSTEM v2.6
        </div>

        <h1 style={styles.headline}>
          <span style={{ display: 'block', animation: 'fadeUp 0.8s var(--ease-out) 0.2s both' }}>
            OPPORTUNITY
          </span>
          <span style={{ display: 'block', color: 'var(--amber)', animation: 'fadeUp 0.8s var(--ease-out) 0.35s both' }}>
            INBOX
          </span>
          <span style={{ display: 'block', fontSize: 'clamp(1.2rem, 4vw, 2.2rem)', color: 'var(--text-secondary)', fontWeight: 600, letterSpacing: '0.25em', animation: 'fadeUp 0.8s var(--ease-out) 0.5s both' }}>
            COPILOT
          </span>
        </h1>

        <p style={{ ...styles.sub, animation: 'fadeUp 0.8s var(--ease-out) 0.65s both' }}>
          Paste your inbox. Our AI parses every email, extracts deadlines &amp; eligibility, and ranks what actually matters — for <em>your</em> profile.
        </p>

        <div style={{ ...styles.statusLine, animation: 'fadeUp 0.8s var(--ease-out) 0.8s both' }}>
          <span style={styles.statusLabel}>STATUS</span>
          <span style={styles.statusText} key={statusIdx}>{STATUS_CYCLE[statusIdx]}</span>
          <span style={styles.cursor}>█</span>
        </div>

        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', justifyContent: 'center', animation: 'fadeUp 0.8s var(--ease-out) 1s both' }}>
          <button id="start-analysis-btn" style={styles.ctaBtn} onClick={onStart}
            onMouseEnter={e => { e.target.style.background = 'var(--amber)'; e.target.style.color = '#000'; e.target.style.transform = 'translateY(-2px)' }}
            onMouseLeave={e => { e.target.style.background = 'transparent'; e.target.style.color = 'var(--amber)'; e.target.style.transform = 'translateY(0)' }}>
            INITIATE ANALYSIS →
          </button>
        </div>

        <div style={{ ...styles.statsRow, animation: 'fadeUp 0.8s var(--ease-out) 1.2s both' }}>
          {[['3', 'STAGE PIPELINE'], ['< 30s', 'PROCESSING TIME'], ['5–15', 'EMAILS PER BATCH']].map(([v, l]) => (
            <div key={l} style={styles.stat}>
              <span style={styles.statVal}>{v}</span>
              <span style={styles.statLabel}>{l}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

const styles = {
  wrap: {
    minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
    position: 'relative', overflow: 'hidden', padding: '40px 20px',
  },
  bgLayer: {
    position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden',
  },
  bgSnippet: {
    position: 'absolute', fontFamily: 'var(--font-mono)', fontSize: '11px',
    color: 'var(--text-muted)', whiteSpace: 'nowrap', animation: 'drift 12s linear infinite',
    maxWidth: '40vw', overflow: 'hidden', textOverflow: 'ellipsis',
  },
  scanline: {
    position: 'absolute', left: 0, right: 0, height: '1px',
    background: 'linear-gradient(90deg, transparent, var(--amber-glow), transparent)',
    animation: 'scanline 6s linear infinite', pointerEvents: 'none',
  },
  content: {
    display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center',
    gap: '28px', maxWidth: '720px', position: 'relative', zIndex: 1,
  },
  badge: {
    display: 'inline-flex', alignItems: 'center', gap: '8px',
    fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: 500,
    color: 'var(--amber)', letterSpacing: '0.12em',
    border: '1px solid var(--amber-border)', borderRadius: '2px',
    padding: '6px 14px', background: 'var(--amber-dim)',
    animation: 'fadeUp 0.8s var(--ease-out) 0s both',
  },
  dot: {
    width: '6px', height: '6px', borderRadius: '50%',
    background: 'var(--amber)', animation: 'blink 1.4s ease-in-out infinite',
    display: 'inline-block',
  },
  headline: {
    fontFamily: 'var(--font-display)', fontWeight: 800,
    fontSize: 'clamp(2.4rem, 8vw, 5.5rem)', lineHeight: 1.0, letterSpacing: '-0.02em',
    color: 'var(--text-bright)', width: '100%',
  },
  sub: {
    fontFamily: 'var(--font-body)', fontSize: 'clamp(1rem, 2vw, 1.2rem)',
    color: 'var(--text-secondary)', lineHeight: 1.7, maxWidth: '520px',
  },
  statusLine: {
    display: 'flex', alignItems: 'center', gap: '12px',
    fontFamily: 'var(--font-mono)', fontSize: '12px',
    border: '1px solid var(--border-normal)', borderRadius: '2px',
    padding: '10px 18px', background: 'var(--bg-card)',
  },
  statusLabel: { color: 'var(--text-muted)', letterSpacing: '0.1em' },
  statusText: { color: 'var(--teal)', letterSpacing: '0.08em', animation: 'fadeIn 0.4s ease' },
  cursor: { color: 'var(--amber)', animation: 'blink 1s step-end infinite' },
  ctaBtn: {
    fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '15px',
    letterSpacing: '0.12em', color: 'var(--amber)',
    border: '2px solid var(--amber-border)', borderRadius: '2px',
    padding: '16px 40px', background: 'transparent', cursor: 'pointer',
    transition: 'all 0.2s var(--ease-out)',
  },
  statsRow: {
    display: 'flex', gap: '40px', flexWrap: 'wrap', justifyContent: 'center',
    borderTop: '1px solid var(--border-subtle)', paddingTop: '28px', width: '100%',
  },
  stat: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' },
  statVal: { fontFamily: 'var(--font-mono)', fontSize: '22px', fontWeight: 500, color: 'var(--text-bright)' },
  statLabel: { fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.12em' },
}
