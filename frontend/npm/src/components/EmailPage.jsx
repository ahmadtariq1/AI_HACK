import { useState } from 'react'
import { sampleEmails } from '../data/sampleEmails'

function EmailCard({ email, index, onRemove, onUpdate }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className={`email-card ${expanded ? 'editing' : ''}`}>
      <button className="email-remove" onClick={() => onRemove(index)}>×</button>
      <div className="email-card-header">
        <span className="email-from">{email.from || 'Unknown Sender'}</span>
      </div>
      <div className="email-subject">{email.subject || 'No Subject'}</div>
      <div className="email-preview">{(email.body || '').substring(0, 140)}...</div>
      <div style={{ marginTop: '6px' }}>
        <button className="edit-toggle-btn" onClick={() => setExpanded(e => !e)}>
          {expanded ? 'Hide full text ↑' : 'Edit full text ↓'}
        </button>
      </div>
      {expanded && (
        <div className="email-body-expand">
          <textarea
            value={email.body}
            onChange={e => onUpdate(index, e.target.value)}
            placeholder="Paste full email text here..."
          />
        </div>
      )}
    </div>
  )
}

export default function EmailPage({ onBack, onAnalyse }) {
  const [emails, setEmails] = useState(sampleEmails.map(e => ({ ...e })))

  const loadSamples = () => setEmails(sampleEmails.map(e => ({ ...e })))
  const addEmail    = () => setEmails(e => [...e, { from: '', subject: '', body: '' }])
  const removeEmail = (i) => setEmails(e => e.filter((_, j) => j !== i))
  const updateBody  = (i, val) => setEmails(e => e.map((x, j) => j === i ? { ...x, body: val } : x))

  return (
    <div className="page">
      <div className="page-hero">
        <div className="page-tag">Step 02</div>
        <h1 className="page-title"><em>Paste Your Emails</em></h1>
        <p className="page-sub">Add emails to find opportunity</p>
      </div>

      <div className="email-toolbar">
        <div className="email-toolbar-left">
          <button className="btn-back" onClick={onBack}>← Back</button>
          <span className="email-count"><span>{emails.length}</span> emails queued</span>
        </div>
        <button className="btn btn-ghost" onClick={loadSamples}>Load Sample Emails</button>
      </div>

      <div className="email-list">
        {emails.map((em, i) => (
          <EmailCard key={i} email={em} index={i} onRemove={removeEmail} onUpdate={updateBody} />
        ))}
      </div>

      {emails.length < 15 && (
        <button className="add-email-btn" onClick={addEmail}>+ Add another email</button>
      )}

      <div className="form-footer">
        <button className="btn btn-primary" onClick={() => onAnalyse(emails)}>
          Analyse &amp; Rank →
        </button>
      </div>
    </div>
  )
}
