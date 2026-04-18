import OpportunityCard from './OpportunityCard'

export default function ResultsBoard({ results, profile, onReset }) {
  const ranked   = results.filter(r => r.type !== 'FILTERED').sort((a, b) => b.totalScore - a.totalScore)
  const filtered = results.filter(r => r.type === 'FILTERED')
  const eligible = ranked.filter(r => r.eligible)
  const urgent   = ranked.filter(r => r.daysRemaining !== null && r.daysRemaining <= 7)

  return (
    <div style={S.wrap}>
      <div style={S.container}>

        {/* Header */}
        <div style={S.header}>
          <div>
            <span style={S.stage}>INTELLIGENCE BRIEF / RESULTS</span>
            <h1 style={S.title}>YOUR OPPORTUNITY BRIEF</h1>
            {profile && (
              <p style={S.sub}>
                Ranked for <strong style={{ color: 'var(--text-bright)' }}>{profile.degree_program}</strong>, Semester {profile.semester}, CGPA {profile.cgpa} — {profile.location_pref}
              </p>
            )}
          </div>
          <button id="reset-btn" style={S.resetBtn} onClick={onReset}
            onMouseEnter={e => e.target.style.borderColor = 'var(--amber)'}
            onMouseLeave={e => e.target.style.borderColor = 'var(--border-normal)'}>
            ↩ NEW ANALYSIS
          </button>
        </div>

        {/* Stats bar */}
        <div style={S.statsBar}>
          {[
            { v: results.length,    l: 'EMAILS PROCESSED' },
            { v: ranked.length,     l: 'OPPORTUNITIES FOUND' },
            { v: filtered.length,   l: 'FILTERED OUT' },
            { v: eligible.length,   l: 'ELIGIBLE MATCHES' },
            { v: urgent.length,     l: 'URGENT (≤7 DAYS)', red: true },
          ].map(({ v, l, red }) => (
            <div key={l} style={S.stat}>
              <span style={{ ...S.statVal, color: red && v > 0 ? 'var(--red)' : 'var(--text-bright)' }}>{v}</span>
              <span style={S.statLabel}>{l}</span>
            </div>
          ))}
        </div>

        {/* Urgent callout */}
        {urgent.length > 0 && (
          <div style={S.urgentBanner}>
            <span style={{ animation: 'blink 1s step-end infinite' }}>⚡</span>
            <span style={S.urgentText}>
              <strong>{urgent.length} opportunity{urgent.length > 1 ? 'ies' : 'y'}</strong> closing within 7 days — act now.
            </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
              {urgent.map(u => u.title).join(' · ')}
            </span>
          </div>
        )}

        {/* Ranked results */}
        {ranked.length > 0 && (
          <section style={S.section}>
            <h2 style={S.sectionTitle}>RANKED OPPORTUNITIES</h2>
            <div style={S.cardList}>
              {ranked.map((opp, i) => (
                <OpportunityCard key={opp.id} opp={opp} delay={i * 0.1} />
              ))}
            </div>
          </section>
        )}

        {/* Filtered */}
        {filtered.length > 0 && (
          <section style={{ ...S.section, marginTop: '40px' }}>
            <h2 style={{ ...S.sectionTitle, color: 'var(--text-muted)' }}>
              DISCARDED DISPATCHES
              <span style={{ fontFamily: 'var(--font-body)', fontSize: '14px', fontWeight: 400, marginLeft: '12px', fontStyle: 'italic' }}>
                — filtered in Stage I as non-actionable
              </span>
            </h2>
            <div style={S.cardList}>
              {filtered.map((opp, i) => (
                <OpportunityCard key={opp.id} opp={opp} delay={i * 0.08} />
              ))}
            </div>
          </section>
        )}

        {/* Footer note */}
        <div style={S.footer}>
          <span style={S.footerMono}>SCORING ENGINE</span>
          <span style={S.footerDivider} />
          <span style={S.footerText}>Fit 50% · Urgency 30% · Preference 20% · No LLM hallucination in scoring</span>
          <span style={S.footerDivider} />
          <span style={S.footerMono}>GENERATED {new Date().toLocaleDateString('en-PK', { day: '2-digit', month: 'short', year: 'numeric' }).toUpperCase()}</span>
        </div>
      </div>
    </div>
  )
}

const S = {
  wrap: { minHeight: '100vh', padding: '40px 20px', display: 'flex', justifyContent: 'center' },
  container: { width: '100%', maxWidth: '860px', animation: 'fadeUp 0.5s var(--ease-out) both' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '20px', flexWrap: 'wrap', marginBottom: '28px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '24px' },
  stage: { fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.12em' },
  title: { fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 'clamp(2rem, 5vw, 3.2rem)', color: 'var(--text-bright)', letterSpacing: '-0.02em', margin: '8px 0 8px' },
  sub: { fontFamily: 'var(--font-body)', fontSize: '15px', color: 'var(--text-secondary)', lineHeight: 1.6 },
  resetBtn: { fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)', border: '1px solid var(--border-normal)', borderRadius: '2px', padding: '10px 20px', background: 'transparent', cursor: 'pointer', letterSpacing: '0.08em', transition: 'border-color 0.2s', flexShrink: 0 },
  statsBar: { display: 'flex', gap: '0', marginBottom: '24px', border: '1px solid var(--border-normal)', borderRadius: '6px', overflow: 'hidden' },
  stat: { flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '16px 8px', gap: '4px', borderRight: '1px solid var(--border-subtle)', background: 'var(--bg-card)', ':last-child': { borderRight: 'none' } },
  statVal: { fontFamily: 'var(--font-mono)', fontSize: '22px', fontWeight: 500, lineHeight: 1 },
  statLabel: { fontFamily: 'var(--font-mono)', fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.1em', textAlign: 'center' },
  urgentBanner: { display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap', padding: '14px 20px', marginBottom: '24px', background: 'var(--red-dim)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: '6px', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--red)', letterSpacing: '0.04em' },
  urgentText: { flex: 1, color: 'var(--text-primary)', fontFamily: 'var(--font-body)', fontSize: '14px' },
  section: {},
  sectionTitle: { fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '13px', letterSpacing: '0.1em', color: 'var(--text-secondary)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '0' },
  cardList: { display: 'flex', flexDirection: 'column', gap: '16px' },
  footer: { display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap', justifyContent: 'center', marginTop: '48px', paddingTop: '24px', borderTop: '1px solid var(--border-subtle)' },
  footerMono: { fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.12em' },
  footerDivider: { width: '1px', height: '14px', background: 'var(--border-subtle)', flexShrink: 0 },
  footerText: { fontFamily: 'var(--font-body)', fontSize: '13px', color: 'var(--text-muted)' },
}
