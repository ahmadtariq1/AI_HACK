import { useState, useEffect } from 'react'
import { buildWhyText, getDaysRemaining, formatDeadline, extractRequirements, runPipeline } from '../utils/scoring'

function ResultCard({ item, rank, profile }) {
  const [open, setOpen]       = useState(false)
  const [checks, setChecks]   = useState({})
  const { opp, scoring, email } = item

  const days    = getDaysRemaining(opp.deadline)
  const reqs    = extractRequirements(email.body)
  const why     = buildWhyText(opp, scoring, profile || {})
  const linkM   = email.body.match(/https?:\/\/[^\s]+/)
  const emailM  = email.body.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/)
  const applyLink = linkM ? linkM[0] : (emailM ? emailM[0] : null)

  const toggleCheck = (k) => setChecks(c => ({ ...c, [k]: !c[k] }))

  const checkItems = [
    ...reqs,
    ...(applyLink ? ['Submit application'] : []),
    ...(opp.deadline ? [`Apply by ${formatDeadline(opp.deadline)}`] : []),
  ]

  return (
    <div className={`result-card ${rank === 1 ? 'rank-1' : ''} ${!scoring.eligible ? 'ineligible-card' : ''}`}>
      <div className="result-card-header" onClick={() => setOpen(o => !o)}>
        <div className="rank-badge">
          <div className="rank-num">{String(rank).padStart(2, '0')}</div>
          <div className="rank-label">Rank</div>
        </div>

        <div className="card-main">
          <div className="card-title">{email.subject || opp.oppType}</div>
          <div className="card-meta-row">
            <span className="pill pill-type">{opp.oppType}</span>
            {scoring.eligible
              ? <span className="pill pill-eligible">Eligible</span>
              : <span className="pill pill-ineligible">Ineligible — CGPA</span>
            }
            {days !== null && days <= 10 && scoring.eligible &&
              <span className="pill pill-urgent">{days}d left</span>
            }
          </div>
        </div>

        <div className="score-block">
          <div className="score-num">{scoring.score}</div>
          <div className="score-max">/ 100</div>
          <div className="score-bar-wrap">
            <div className="score-bar" style={{ width: `${scoring.score}%` }} />
          </div>
        </div>
      </div>

      {open && (
        <div className="card-body">
          {/* Why */}
          <div style={{ gridColumn: '1 / -1' }}>
            <div className="section-label">Why this score</div>
            <div className="why-box" dangerouslySetInnerHTML={{ __html: why }} />
          </div>

          {/* Score breakdown */}
          <div>
            <div className="section-label">Score breakdown</div>
            <div className="score-breakdown">
              {[
                { label: 'Fit 50%',     val: scoring.sFit,     color: 'var(--amber)' },
                { label: 'Urgency 30%', val: scoring.sUrgency, color: 'var(--info)' },
                { label: 'Pref 20%',    val: scoring.sPref,    color: 'var(--success)' },
              ].map(row => (
                <div key={row.label} className="score-row">
                  <div className="score-row-label">{row.label}</div>
                  <div className="score-row-bar">
                    <div className="score-row-fill" style={{ width: `${row.val}%`, background: row.color }} />
                  </div>
                  <div className="score-row-val">{row.val}</div>
                </div>
              ))}
            </div>

            <div className="section-label" style={{ marginTop: '12px' }}>Details</div>
            <div className="info-rows">
              <div className="info-row"><span className="info-key">Deadline</span><span className="info-val">{formatDeadline(opp.deadline)}</span></div>
              <div className="info-row"><span className="info-key">Min CGPA</span><span className="info-val">{opp.minCgpa > 0 ? opp.minCgpa.toFixed(1) : 'Not stated'}</span></div>
              <div className="info-row"><span className="info-key">Location</span><span className="info-val">{opp.location}</span></div>
              {applyLink && (
                <div className="info-row">
                  <span className="info-key">Apply</span>
                  <span className="info-val" style={{ color: 'var(--info)', fontSize: '11px', wordBreak: 'break-all' }}>{applyLink}</span>
                </div>
              )}
            </div>
          </div>

          {/* Action checklist */}
          <div>
            <div className="section-label">Action checklist</div>
            <div className="checklist">
              {checkItems.map((item, i) => (
                <div key={i} className="check-item" onClick={() => toggleCheck(i)} style={{ cursor: 'pointer' }}>
                  <div className={`check-box ${checks[i] ? 'checked' : ''}`}>
                    {checks[i] && <span style={{ fontSize: '10px', color: '#fff' }}>✓</span>}
                  </div>
                  <span style={{ textDecoration: checks[i] ? 'line-through' : 'none', opacity: checks[i] ? 0.5 : 1 }}>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ProcessingState({ stage }) {
  const steps = [
    'Stage I — Filtering spam & newsletters',
    'Stage II — Extracting structured data',
    'Stage III — Computing match scores',
  ]
  return (
    <div className="processing-state">
      <div className="spinner" />
      <div className="processing-label">Analysing your inbox...</div>
      <div className="processing-steps">
        {steps.map((s, i) => (
          <div key={i} className={`proc-step ${stage === i ? 'active' : stage > i ? 'done' : ''}`}>
            <div className="proc-dot" />
            {s}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function ResultsPage({ emails, profile }) {
  const [stage, setStage]     = useState(0)
  const [done, setDone]       = useState(false)
  const [results, setResults] = useState({ parsed: [], filtered: [] })

  useEffect(() => {
    let s = 0
    const iv = setInterval(() => {
      if (s < 2) { setStage(s + 1); s++ }
      else {
        clearInterval(iv)
        setTimeout(() => {
          const res = runPipeline(emails, profile || {})
          setResults(res)
          setDone(true)
        }, 400)
      }
    }, 900)
    return () => clearInterval(iv)
  }, [])

  const eligible = results.parsed.filter(p => p.scoring.eligible)
  const urgent   = results.parsed.filter(p => {
    if (!p.opp.deadline) return false
    const days = Math.ceil((p.opp.deadline - new Date('2026-04-18')) / 86400000)
    return days <= 10 && p.scoring.eligible
  })

  return (
    <div className="page">
      <div className="page-hero">
        <div className="page-tag">Step 03</div>
        <h1 className="page-title">Ranked Opportunities</h1>
        <p className="page-sub">Sorted by fit, urgency, and preference.</p>
      </div>

      <div className="results-layout">
        {!done ? (
          <ProcessingState stage={stage} />
        ) : (
          <>
            <div className="summary-bar">
              {[
                { num: emails.length,          label: 'Total Parsed' },
                { num: eligible.length,         label: 'Eligible' },
                { num: urgent.length,           label: 'Due Soon' },
                { num: results.filtered.length, label: 'Filtered Out' },
              ].map(c => (
                <div key={c.label} className="summary-cell">
                  <div className="summary-num">{c.num}</div>
                  <div className="summary-label">{c.label}</div>
                </div>
              ))}
            </div>

            <div className="results-header">
              <div className="results-title">Your Ranked Opportunities</div>
              <div className="results-meta">
                Analysed {emails.length} emails · {new Date('2026-04-18').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
              </div>
            </div>

            <div className="result-cards">
              {results.parsed.map((item, i) => (
                <ResultCard key={i} item={item} rank={i + 1} profile={profile} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
