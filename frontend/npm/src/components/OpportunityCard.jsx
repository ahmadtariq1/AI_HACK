import { useState } from 'react'

const TYPE_COLORS = {
  Internship:  { bg: 'rgba(168,199,250,0.08)', border: 'rgba(168,199,250,0.25)', text: '#A8C7FA' },
  Scholarship: { bg: 'rgba(240,180,41,0.08)',  border: 'rgba(240,180,41,0.25)',  text: '#F0B429' },
  Competition: { bg: 'rgba(20,184,166,0.08)',  border: 'rgba(20,184,166,0.25)',  text: '#14B8A6' },
  Fellowship:  { bg: 'rgba(168,199,250,0.08)', border: 'rgba(168,199,250,0.25)', text: '#A8C7FA' },
  FILTERED:    { bg: 'rgba(239,68,68,0.06)',   border: 'rgba(239,68,68,0.2)',    text: '#EF4444' },
}

const URGENCY_COLOR = (days) => {
  if (days === null) return 'var(--text-muted)'
  if (days <= 7)  return 'var(--red)'
  if (days <= 14) return '#FB923C'
  return 'var(--teal)'
}

function ScoreRing({ score, size = 64 }) {
  const r = (size / 2) - 6
  const circ = 2 * Math.PI * r
  const dash = (score / 100) * circ
  const color = score >= 80 ? 'var(--teal)' : score >= 55 ? 'var(--amber)' : 'var(--red)'

  return (
    <svg width={size} height={size} style={{ transform: 'rotate(-90deg)', flexShrink: 0 }}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="var(--border-subtle)" strokeWidth="5" />
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="5"
        strokeDasharray={`${dash} ${circ - dash}`}
        strokeLinecap="round"
        style={{ transition: 'stroke-dasharray 1.2s var(--ease-out)' }}
      />
      <text x={size/2} y={size/2} textAnchor="middle" dominantBaseline="central"
        style={{ transform: 'rotate(90deg)', transformOrigin: `${size/2}px ${size/2}px`,
          fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 500, fill: color }}>
        {score}
      </text>
    </svg>
  )
}

function ScoreBar({ label, value, color }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-muted)', width: '80px', flexShrink: 0 }}>{label}</span>
      <div style={{ flex: 1, height: '4px', background: 'var(--bg-elevated)', borderRadius: '2px', overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${value}%`, background: color, borderRadius: '2px', transition: 'width 1.2s var(--ease-out)' }} />
      </div>
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color, width: '30px', textAlign: 'right' }}>{value}</span>
    </div>
  )
}

export default function OpportunityCard({ opp, delay = 0 }) {
  const [checkList, setCheckList] = useState(opp.checklist.map(t => ({ text: t, done: false })))
  const [expanded, setExpanded]   = useState(false)

  const typeStyle = TYPE_COLORS[opp.type] || TYPE_COLORS.FILTERED
  const isFiltered = opp.type === 'FILTERED'

  const toggleCheck = (i) => setCheckList(c => c.map((x, j) => j === i ? { ...x, done: !x.done } : x))

  return (
    <div style={{ ...S.card, ...(isFiltered ? S.cardFiltered : {}), animationDelay: `${delay}s` }}>
      {/* Rank bar */}
      {!isFiltered && (
        <div style={S.rankBar}>
          <span style={S.rankNum}>#{opp.rank}</span>
          <div style={{ flex: 1, height: '2px', background: `linear-gradient(90deg, var(--amber-border), transparent)` }} />
        </div>
      )}

      {/* Header row */}
      <div style={S.cardHeader}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={S.metaRow}>
            <span style={{ ...S.typeBadge, background: typeStyle.bg, border: `1px solid ${typeStyle.border}`, color: typeStyle.text }}>
              {opp.type}
            </span>
            {opp.daysRemaining !== null && (
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: URGENCY_COLOR(opp.daysRemaining) }}>
                {opp.daysRemaining <= 7 ? '⚡ ' : ''}{opp.daysRemaining}D LEFT
              </span>
            )}
            {isFiltered && <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--red)' }}>✗ DISCARDED</span>}
          </div>

          <h2 style={{ ...S.cardTitle, color: isFiltered ? 'var(--text-muted)' : 'var(--text-bright)', textDecoration: isFiltered ? 'line-through' : 'none' }}>
            {opp.title}
          </h2>
          <div style={S.orgRow}>
            <span style={S.org}>{opp.organization}</span>
            {opp.location && <span style={S.dot}>·</span>}
            {opp.location && <span style={S.org}>{opp.location}</span>}
            {opp.stipend && <span style={S.dot}>·</span>}
            {opp.stipend && <span style={{ ...S.org, color: 'var(--teal)' }}>{opp.stipend}</span>}
          </div>
        </div>

        {!isFiltered && (
          <div style={S.scoreWrap}>
            <ScoreRing score={opp.totalScore} />
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>SCORE</span>
          </div>
        )}
      </div>

      {/* "Why" reasoning */}
      <div style={S.why}>
        <span style={S.whyLabel}>WHY THIS {isFiltered ? 'WAS FILTERED' : 'MATCHES'}</span>
        <p style={S.whyText}>{opp.why}</p>
      </div>

      {!isFiltered && (
        <>
          {/* Score breakdown */}
          <div style={S.scoreBreakdown}>
            <ScoreBar label="FIT (50%)"     value={opp.fitScore}     color="var(--teal)" />
            <ScoreBar label="URGENCY (30%)" value={opp.urgencyScore} color="var(--amber)" />
            <ScoreBar label="PREF (20%)"    value={opp.prefScore}    color="var(--ice)" />
          </div>

          {/* Deadline + requirements */}
          <div style={S.infoRow}>
            {opp.deadline && (
              <div style={S.infoChip}>
                <span style={S.infoLabel}>DEADLINE</span>
                <span style={{ ...S.infoVal, color: URGENCY_COLOR(opp.daysRemaining) }}>{opp.deadline}</span>
              </div>
            )}
            {opp.requiredCGPA && (
              <div style={S.infoChip}>
                <span style={S.infoLabel}>MIN CGPA</span>
                <span style={S.infoVal}>{opp.requiredCGPA}</span>
              </div>
            )}
            {opp.requirements?.length > 0 && (
              <div style={S.infoChip}>
                <span style={S.infoLabel}>DOCS NEEDED</span>
                <span style={S.infoVal}>{opp.requirements.join(', ')}</span>
              </div>
            )}
          </div>

          {/* Expand toggle */}
          <button style={S.expandBtn} onClick={() => setExpanded(e => !e)}
            onMouseEnter={e => e.target.style.color = 'var(--amber)'}
            onMouseLeave={e => e.target.style.color = 'var(--text-muted)'}>
            {expanded ? '▲ HIDE CHECKLIST' : '▼ SHOW ACTION CHECKLIST'}
          </button>

          {/* Action checklist */}
          {expanded && (
            <div style={S.checklist}>
              <div style={S.checkHeader}>ACTION CHECKLIST</div>
              {checkList.map((item, i) => (
                <div key={i} style={S.checkItem} onClick={() => toggleCheck(i)}>
                  <div style={{ ...S.checkbox, ...(item.done ? S.checkboxDone : {}) }}>
                    {item.done && <span style={{ color: '#000', fontSize: '12px', lineHeight: 1 }}>✓</span>}
                  </div>
                  <span style={{ ...S.checkText, textDecoration: item.done ? 'line-through' : 'none', color: item.done ? 'var(--text-muted)' : 'var(--text-primary)' }}>
                    {item.text}
                  </span>
                </div>
              ))}
              {opp.link && (
                <a href={`https://${opp.link}`} target="_blank" rel="noopener noreferrer" style={S.applyLink}>
                  APPLY NOW → {opp.link}
                </a>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

const S = {
  card: {
    background: 'var(--bg-card)', border: '1px solid var(--border-normal)', borderRadius: '8px',
    overflow: 'hidden', animation: 'fadeUp 0.6s var(--ease-out) both',
    transition: 'border-color 0.2s, box-shadow 0.2s',
  },
  cardFiltered: { opacity: 0.55, borderColor: 'var(--border-subtle)' },
  rankBar: { display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 20px 0', height: '28px' },
  rankNum: { fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--amber)', letterSpacing: '0.12em', flexShrink: 0 },
  cardHeader: { display: 'flex', alignItems: 'flex-start', gap: '16px', padding: '16px 20px 16px' },
  metaRow: { display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', marginBottom: '8px' },
  typeBadge: { fontFamily: 'var(--font-mono)', fontSize: '10px', letterSpacing: '0.1em', padding: '3px 10px', borderRadius: '2px', fontWeight: 500 },
  cardTitle: { fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 'clamp(1rem, 2.5vw, 1.25rem)', lineHeight: 1.3, marginBottom: '8px' },
  orgRow: { display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' },
  org: { fontFamily: 'var(--font-body)', fontSize: '14px', color: 'var(--text-secondary)' },
  dot: { color: 'var(--text-muted)' },
  scoreWrap: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', flexShrink: 0 },
  why: { padding: '14px 20px', borderTop: '1px solid var(--border-subtle)', background: 'rgba(255,255,255,0.012)' },
  whyLabel: { fontFamily: 'var(--font-mono)', fontSize: '10px', letterSpacing: '0.12em', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' },
  whyText: { fontFamily: 'var(--font-body)', fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.7 },
  scoreBreakdown: { display: 'flex', flexDirection: 'column', gap: '8px', padding: '14px 20px', borderTop: '1px solid var(--border-subtle)' },
  infoRow: { display: 'flex', flexWrap: 'wrap', gap: '8px', padding: '12px 20px', borderTop: '1px solid var(--border-subtle)' },
  infoChip: { display: 'flex', flexDirection: 'column', gap: '2px', background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '8px 14px' },
  infoLabel: { fontFamily: 'var(--font-mono)', fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.12em' },
  infoVal: { fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-primary)' },
  expandBtn: { width: '100%', padding: '12px', background: 'none', border: 'none', borderTop: '1px solid var(--border-subtle)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.1em', transition: 'color 0.15s', textAlign: 'center' },
  checklist: { padding: '16px 20px 20px', borderTop: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '10px' },
  checkHeader: { fontFamily: 'var(--font-mono)', fontSize: '10px', letterSpacing: '0.12em', color: 'var(--text-muted)', marginBottom: '4px' },
  checkItem: { display: 'flex', alignItems: 'flex-start', gap: '12px', cursor: 'pointer', userSelect: 'none' },
  checkbox: { width: '18px', height: '18px', border: '1px solid var(--border-normal)', borderRadius: '3px', flexShrink: 0, marginTop: '1px', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.15s' },
  checkboxDone: { background: 'var(--amber)', borderColor: 'var(--amber)' },
  checkText: { fontFamily: 'var(--font-body)', fontSize: '14px', lineHeight: 1.5, transition: 'color 0.2s' },
  applyLink: { display: 'inline-flex', alignItems: 'center', gap: '6px', marginTop: '8px', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--amber)', textDecoration: 'none', padding: '10px 16px', border: '1px solid var(--amber-border)', borderRadius: '4px', background: 'var(--amber-dim)', letterSpacing: '0.06em' },
}
