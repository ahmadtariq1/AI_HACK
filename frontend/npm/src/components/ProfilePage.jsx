import { useState, useRef } from 'react'

const PREF_TYPES = ['Internship', 'Scholarship', 'Hackathon', 'Competition', 'Research', 'Fellowship', 'Workshop']

function TagInput({ tags, onAdd, onRemove, inputId, placeholder }) {
  const [val, setVal] = useState('')
  const ref = useRef()

  const add = () => {
    const v = val.replace(',', '').trim()
    if (v && !tags.includes(v)) onAdd(v)
    setVal('')
  }

  return (
    <div className="tag-wrapper" onClick={() => ref.current?.focus()}>
      {tags.map(t => (
        <div key={t} className="tag">
          {t}
          <button className="tag-remove" onClick={() => onRemove(t)}>×</button>
        </div>
      ))}
      <input
        ref={ref}
        id={inputId}
        className="tag-input"
        placeholder={placeholder}
        value={val}
        onChange={e => setVal(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); add() } }}
      />
    </div>
  )
}

export default function ProfilePage({ onNext }) {
  const [degree, setDegree] = useState('BS Computer Science')
  const [semester, setSemester] = useState(5)
  const [cgpa, setCgpa] = useState(3.40)
  const [locPref, setLocPref] = useState('Lahore')
  const [skills, setSkills] = useState(['Python', 'Machine Learning', 'Data Analysis'])
  const [prefTypes, setPrefTypes] = useState(['Internship', 'Hackathon'])
  const [experience, setExperience] = useState(['Web Dev Project', 'Research Assistant'])
  const [finNeed, setFinNeed] = useState(false)

  const togglePref = (t) => setPrefTypes(p => p.includes(t) ? p.filter(x => x !== t) : [...p, t])

  const handleSubmit = () => {
    onNext({
      degree_program: degree,
      semester,
      cgpa,
      location_pref: locPref,
      skills_interests: skills,
      pref_opp_types: prefTypes,
      past_experience: experience,
      financial_need: finNeed,
    })
  }

  return (
    <div className="page">
      <div className="page-hero">
        <div className="page-tag">Step 01</div>
        <h1 className="page-title">Your <em>Profile</em></h1>
        <p className="page-sub">Define your academic identity. The scoring engine uses this data to evaluate every opportunity against your exact situation.</p>
      </div>

      <div className="form-body">
        <div className="form-grid">

          <div className="form-group">
            <label htmlFor="degree">Degree Program</label>
            <input id="degree" type="text" placeholder="e.g. BS Computer Science"
              value={degree} onChange={e => setDegree(e.target.value)} />
          </div>

          <div className="form-group">
            <label>Current Semester</label>
            <div className="range-row">
              <input type="range" min="1" max="8" step="1" value={semester}
                onChange={e => setSemester(+e.target.value)} />
              <div className="range-val">{semester}</div>
            </div>
          </div>

          <div className="form-group">
            <label>CGPA</label>
            <div className="range-row">
              <input type="range" min="0" max="4" step="0.01" value={cgpa}
                onChange={e => setCgpa(parseFloat(e.target.value))} />
              <div className="range-val">{cgpa.toFixed(2)}</div>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="locPref">Location Preference</label>
            <select id="locPref" value={locPref} onChange={e => setLocPref(e.target.value)}>
              <option>No Preference</option>
              <option>Lahore</option>
              <option>Karachi</option>
              <option>Islamabad</option>
              <option>Remote</option>
            </select>
          </div>

          <div className="form-group full">
            <label>Skills &amp; Interests — press Enter or comma to add</label>
            <TagInput
              tags={skills} inputId="skillInput" placeholder="Add skill..."
              onAdd={v => setSkills(s => [...s, v])}
              onRemove={v => setSkills(s => s.filter(x => x !== v))}
            />
          </div>

          <div className="form-group full">
            <label>Preferred Opportunity Types</label>
            <div className="check-group">
              {PREF_TYPES.map(t => (
                <div key={t} className={`check-btn ${prefTypes.includes(t) ? 'selected' : ''}`}
                  onClick={() => togglePref(t)}>
                  {t}
                </div>
              ))}
            </div>
          </div>

          <div className="form-group full">
            <label>Past Experience Tags — press Enter or comma to add</label>
            <TagInput
              tags={experience} inputId="expInput" placeholder="Add experience..."
              onAdd={v => setExperience(s => [...s, v])}
              onRemove={v => setExperience(s => s.filter(x => x !== v))}
            />
          </div>

          <div className="form-group full">
            <label>Financial Need</label>
            <div className="toggle-row">
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Requires financial assistance — boosts stipended opportunities</span>
              <div className={`toggle-track ${finNeed ? 'on' : ''}`} onClick={() => setFinNeed(f => !f)}>
                <div className="toggle-thumb" />
              </div>
            </div>
          </div>

        </div>

        <div className="form-footer">
          <button className="btn btn-primary" onClick={handleSubmit}>Continue to Emails →</button>
        </div>
      </div>
    </div>
  )
}
