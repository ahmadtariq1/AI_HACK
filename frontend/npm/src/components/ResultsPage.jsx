import { useState, useEffect } from 'react'

function formatDeadline(d) {
  if (!d) return 'Not stated'
  return new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

function ResultCard({ item }) {
  const [open, setOpen] = useState(false)
  const [checks, setChecks] = useState({})
  
  const { rank, extracted, score, why_text, why_bullets, action_checklist } = item
  
  const toggleCheck = (k) => setChecks(c => ({ ...c, [k]: !c[k] }))

  return (
    <div className={`result-card ${rank === 1 ? 'rank-1' : ''} ${!score.is_eligible ? 'ineligible-card' : ''}`}>
      <div className="result-card-header" onClick={() => setOpen(o => !o)}>
        <div className="rank-badge">
          <div className="rank-num">{String(rank).padStart(2, '0')}</div>
          <div className="rank-label">Rank</div>
        </div>

        <div className="card-main">
          <div className="card-title">{extracted.title || extracted.opportunity_type || extracted.raw_subject || 'Opportunity'}</div>
          <div className="card-meta-row">
            <span className="pill pill-type">{extracted.opportunity_type || 'Opportunity'}</span>
            {score.is_eligible
              ? <span className="pill pill-eligible">Eligible</span>
              : <span className="pill pill-ineligible">Ineligible — CGPA</span>
            }
          </div>
        </div>

        <div className="score-block">
          <div className="score-num">{score.total}</div>
          <div className="score-max">/ 100</div>
          <div className="score-bar-wrap">
            <div className="score-bar" style={{ width: `${score.total}%` }} />
          </div>
        </div>
      </div>

      {open && (
        <div className="card-body">
          {/* Why */}
          <div style={{ gridColumn: '1 / -1' }}>
            <div className="section-label">Why this score</div>
            <div className="why-box">
              <p>{why_text}</p>
              <ul style={{ paddingLeft: '20px', marginTop: '8px' }}>
                {why_bullets.map((b, i) => <li key={i} style={{ marginBottom: '4px' }}>{b}</li>)}
              </ul>
            </div>
          </div>

          {/* Score breakdown */}
          <div>
            <div className="section-label">Score breakdown</div>
            <div className="score-breakdown">
              {[
                { label: 'Fit 60%',     val: score.profile_fit,  color: 'var(--amber)' },
                { label: 'Urgency 25%', val: score.urgency,      color: 'var(--info)' },
                { label: 'Completeness 15%', val: score.completeness, color: 'var(--success)' },
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
              <div className="info-row"><span className="info-key">Deadline</span><span className="info-val">{formatDeadline(extracted.deadline)}</span></div>
              {extracted.application_or_contact?.urls?.length > 0 && (
                <div className="info-row">
                  <span className="info-key">Apply URL</span>
                  <span className="info-val" style={{ color: 'var(--info)', fontSize: '11px', wordBreak: 'break-all' }}>{extracted.application_or_contact.urls[0]}</span>
                </div>
              )}
              {extracted.application_or_contact?.emails?.length > 0 && (
                <div className="info-row">
                  <span className="info-key">Contact</span>
                  <span className="info-val" style={{ color: 'var(--info)', fontSize: '11px', wordBreak: 'break-all' }}>{extracted.application_or_contact.emails[0]}</span>
                </div>
              )}
            </div>
          </div>

          {/* Action checklist */}
          <div>
            <div className="section-label">Action checklist</div>
            <div className="checklist">
              {action_checklist.map((item, i) => (
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

function ProcessingState() {
  return (
    <div className="processing-state">
      <div className="spinner" />
      <div className="processing-label">Analysing your inbox...</div>
      <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '12px' }}>
        Calling LLM classification and extraction models via FastAPI...
      </p>
    </div>
  )
}

export default function ResultsPage({ emails, profile }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [data, setData] = useState(null)

  useEffect(() => {
    const processEmails = async () => {
      try {
        const payload = {
          student_profile: profile,
          emails: emails.map(e => ({ subject: e.subject || 'No Subject', body: e.body }))
        }
        
        const res = await fetch('http://localhost:8000/api/v1/pipeline/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        
        if (!res.ok) {
          throw new Error(`API returned ${res.status}`)
        }
        
        const json = await res.json()
        setData(json)
      } catch (err) {
        console.error(err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    
    processEmails()
  }, [emails, profile])

  return (
    <div className="page">
      <div className="page-hero">
        <div className="page-tag">Step 03</div>
        <h1 className="page-title">Ranked <em>Opportunities</em></h1>
        <p className="page-sub">Sorted by fit, urgency, and preference via deterministic engine.</p>
      </div>

      <div className="results-layout">
        {loading ? (
          <ProcessingState />
        ) : error ? (
          <div style={{ color: 'var(--danger)', padding: '2rem', textAlign: 'center' }}>
            <h2>Processing Failed</h2>
            <p>{error}</p>
            <p>Ensure the FastAPI backend is running on port 8000.</p>
          </div>
        ) : (
          <>
            <div className="summary-bar">
              {[
                { num: data.summary.total_emails,          label: 'Total Parsed' },
                { num: data.summary.real_opportunities,    label: 'Valid Opps' },
                { num: data.summary.urgent_count,          label: 'Due Soon' },
                { num: data.summary.spam_filtered,         label: 'Spam Filtered' },
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
                Analysed {data.summary.total_emails} emails
              </div>
            </div>

            <div className="result-cards">
              {data.ranked_opportunities.map((item, i) => (
                <ResultCard key={i} item={item} />
              ))}
            </div>
            
            {data.filtered_emails?.length > 0 && (
              <div style={{ marginTop: '3rem' }}>
                <div className="results-header">
                  <div className="results-title" style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Filtered Noise & Spam ({data.filtered_emails.length})</div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {data.filtered_emails.map((spam, i) => (
                    <div key={i} style={{ padding: '12px', background: 'var(--surface2)', borderRadius: '6px', fontSize: '12px', color: 'var(--text-muted)' }}>
                      <strong>{spam.raw_subject}</strong> — {spam.classification_reason || spam.rationale}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

