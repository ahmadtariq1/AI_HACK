import { useState, useRef } from 'react'

const PREF_TYPES = ['Internship', 'Scholarship', 'Hackathon', 'Competition', 'Research', 'Fellowship', 'Workshop']
const LOC_TYPES = ['Lahore', 'Karachi', 'Islamabad', 'Remote', 'Any']

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

function ExperienceInput({ experience, setExperience }) {
  const [role, setRole] = useState('')
  const [context, setContext] = useState('')

  const add = () => {
    if (role.trim() && context.trim()) {
      setExperience([...experience, { role: role.trim(), context: context.trim() }])
      setRole('')
      setContext('')
    }
  }

  const remove = (idx) => {
    setExperience(experience.filter((_, i) => i !== idx))
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {experience.map((exp, idx) => (
        <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', background: 'var(--surface2)', padding: '8px 12px', borderRadius: '4px', border: '1px solid var(--border)' }}>
          <div>
            <div style={{ fontWeight: 600, color: 'var(--text)' }}>{exp.role}</div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{exp.context}</div>
          </div>
          <button className="tag-remove" style={{ alignSelf: 'center', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }} onClick={() => remove(idx)}>×</button>
        </div>
      ))}
      <div style={{ display: 'flex', gap: '8px' }}>
        <input 
          className="tag-input" style={{ flex: 1, padding: '8px', background: 'var(--surface2)', border: '1px solid var(--border)', color: 'var(--text)', borderRadius: '4px' }} 
          placeholder="Role (e.g. Intern)" value={role} onChange={e => setRole(e.target.value)} 
        />
        <input 
          className="tag-input" style={{ flex: 2, padding: '8px', background: 'var(--surface2)', border: '1px solid var(--border)', color: 'var(--text)', borderRadius: '4px' }} 
          placeholder="Context (e.g. 3 months at Tech Corp)" value={context} onChange={e => setContext(e.target.value)} 
          onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
        />
        <button className="btn btn-primary" style={{ padding: '0 12px' }} onClick={add}>Add</button>
      </div>
    </div>
  )
}

export default function ProfilePage({ onNext }) {
  const [degree, setDegree] = useState('BS Computer Science')
  const [university, setUniversity] = useState('FAST NUCES LAHORE')
  const [semester, setSemester] = useState(6)
  const [cgpa, setCgpa] = useState(3.60)
  const [locPref, setLocPref] = useState(['Lahore', 'Remote'])
  const [skills, setSkills] = useState(['Python', 'Machine Learning', 'NLP', 'Django'])
  const [prefTypes, setPrefTypes] = useState(['Internship', 'Scholarship'])
  const [experience, setExperience] = useState([
    { role: "Software Engineering Intern", context: "Django intern (3 months)" }
  ])
  const [finNeed, setFinNeed] = useState(false)

  const togglePref = (t) => setPrefTypes(p => p.includes(t) ? p.filter(x => x !== t) : [...p, t])
  const toggleLoc = (l) => setLocPref(p => p.includes(l) ? p.filter(x => x !== l) : [...p, l])

  const handleSubmit = () => {
    onNext({
      academic: {
        degree_program: degree,
        university: university,
        semester: semester,
        cgpa: cgpa
      },
      technical: {
        skills_and_interests: skills
      },
      experience: experience,
      logistics: {
        preferred_opportunity_types: prefTypes,
        location_preference: locPref.length > 0 ? locPref : ["Any"],
        financial_need: finNeed ? "stipend_required" : "none"
      }
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
            <label htmlFor="university">University</label>
            <input id="university" type="text" placeholder="e.g. FAST NUCES LAHORE"
              value={university} onChange={e => setUniversity(e.target.value)} />
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

          <div className="form-group full">
            <label>Skills &amp; Interests — press Enter or comma to add</label>
            <TagInput
              tags={skills} inputId="skillInput" placeholder="Add skill..."
              onAdd={v => setSkills(s => [...s, v])}
              onRemove={v => setSkills(s => s.filter(x => x !== v))}
            />
          </div>

          <div className="form-group full">
            <label>Past Experience</label>
            <ExperienceInput experience={experience} setExperience={setExperience} />
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
            <label>Location Preference</label>
            <div className="check-group">
              {LOC_TYPES.map(l => (
                <div key={l} className={`check-btn ${locPref.includes(l) ? 'selected' : ''}`}
                  onClick={() => toggleLoc(l)}>
                  {l}
                </div>
              ))}
            </div>
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

