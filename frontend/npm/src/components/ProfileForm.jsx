import { useState } from 'react'

const DEGREE_OPTIONS = ['BS Computer Science','BS Software Engineering','BS Electrical Engineering','BS Data Science','BBA','BS Business Administration','BS Economics','BS Mathematics','BS Physics','BS Bioinformatics','Other']
const LOC_OPTIONS    = ['No Preference','Remote','Lahore','Karachi','Islamabad','Rawalpindi','Peshawar','Quetta']
const OPP_TYPES      = ['Internship','Scholarship','Competition','Hackathon','Research','Fellowship','Exchange Program','Volunteer']

export default function ProfileForm({ onSubmit }) {
  const [form, setForm] = useState({
    degree_program: 'BS Computer Science',
    semester: '5',
    cgpa: '3.8',
    skills_interests: ['Python', 'Machine Learning', 'Data Structures', 'React'],
    pref_opp_types: ['Internship', 'Scholarship', 'Competition'],
    financial_need: true,
    location_pref: 'Remote',
    past_experience: ['Web Dev Intern — StartupXYZ', 'ML Research Assistant — University Lab'],
  })
  const [skillInput, setSkillInput]     = useState('')
  const [expInput, setExpInput]         = useState('')
  const [errors, setErrors]             = useState({})

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const addSkill = () => {
    const s = skillInput.trim()
    if (s && !form.skills_interests.includes(s)) set('skills_interests', [...form.skills_interests, s])
    setSkillInput('')
  }
  const addExp = () => {
    const s = expInput.trim()
    if (s && !form.past_experience.includes(s)) set('past_experience', [...form.past_experience, s])
    setExpInput('')
  }
  const removeTag = (key, val) => set(key, form[key].filter(x => x !== val))
  const toggleOpp = (type) => {
    const cur = form.pref_opp_types
    set('pref_opp_types', cur.includes(type) ? cur.filter(x => x !== type) : [...cur, type])
  }

  const validate = () => {
    const e = {}
    if (!form.degree_program) e.degree_program = 'Required'
    if (!form.semester || +form.semester < 1 || +form.semester > 8) e.semester = '1–8'
    if (!form.cgpa || +form.cgpa < 0 || +form.cgpa > 4) e.cgpa = '0.0–4.0'
    if (!form.location_pref) e.location_pref = 'Required'
    if (form.skills_interests.length === 0) e.skills_interests = 'Add at least one skill'
    if (form.pref_opp_types.length === 0) e.pref_opp_types = 'Select at least one'
    return e
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    onSubmit({ ...form, semester: +form.semester, cgpa: +form.cgpa })
  }

  return (
    <div style={S.wrap}>
      <div style={S.container}>
        {/* Header */}
        <div style={S.header}>
          <span style={S.stage}>STAGE 0 / PROFILE SETUP</span>
          <h1 style={S.title}>AGENT PROFILE</h1>
          <p style={S.sub}>Your profile is the scoring key. Fill it accurately — it determines what ranks #1.</p>
        </div>

        <form onSubmit={handleSubmit} noValidate>
          <div style={S.grid}>
            {/* Degree */}
            <div style={S.fieldWrap}>
              <label style={S.label}>DEGREE PROGRAM</label>
              <select id="degree-select" style={{ ...S.input, ...(errors.degree_program ? S.inputErr : {}) }}
                value={form.degree_program} onChange={e => set('degree_program', e.target.value)}>
                <option value="">Select program...</option>
                {DEGREE_OPTIONS.map(d => <option key={d}>{d}</option>)}
              </select>
              {errors.degree_program && <span style={S.err}>{errors.degree_program}</span>}
            </div>

            {/* Semester */}
            <div style={S.fieldWrap}>
              <label style={S.label}>CURRENT SEMESTER</label>
              <input id="semester-input" type="number" min="1" max="8" placeholder="e.g. 5"
                style={{ ...S.input, ...(errors.semester ? S.inputErr : {}) }}
                value={form.semester} onChange={e => set('semester', e.target.value)} />
              {errors.semester && <span style={S.err}>{errors.semester}</span>}
            </div>

            {/* CGPA */}
            <div style={S.fieldWrap}>
              <label style={S.label}>CGPA</label>
              <input id="cgpa-input" type="number" min="0" max="4" step="0.01" placeholder="e.g. 3.75"
                style={{ ...S.input, ...(errors.cgpa ? S.inputErr : {}) }}
                value={form.cgpa} onChange={e => set('cgpa', e.target.value)} />
              {errors.cgpa && <span style={S.err}>{errors.cgpa}</span>}
            </div>

            {/* Location */}
            <div style={S.fieldWrap}>
              <label style={S.label}>LOCATION PREFERENCE</label>
              <select id="location-select" style={{ ...S.input, ...(errors.location_pref ? S.inputErr : {}) }}
                value={form.location_pref} onChange={e => set('location_pref', e.target.value)}>
                <option value="">Select location...</option>
                {LOC_OPTIONS.map(l => <option key={l}>{l}</option>)}
              </select>
              {errors.location_pref && <span style={S.err}>{errors.location_pref}</span>}
            </div>
          </div>

          {/* Skills */}
          <div style={{ ...S.fieldWrap, marginTop: '20px' }}>
            <label style={S.label}>SKILLS & INTERESTS {errors.skills_interests && <span style={S.err}> — {errors.skills_interests}</span>}</label>
            <div style={S.tagInput}>
              <input id="skill-input" placeholder="e.g. Python, Machine Learning..." style={S.tagInner}
                value={skillInput}
                onChange={e => setSkillInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addSkill())} />
              <button type="button" style={S.addBtn} onClick={addSkill}>+ ADD</button>
            </div>
            <div style={S.tags}>
              {form.skills_interests.map(s => (
                <span key={s} style={S.tag}>{s} <button type="button" onClick={() => removeTag('skills_interests', s)} style={S.tagX}>×</button></span>
              ))}
            </div>
          </div>

          {/* Past Experience */}
          <div style={{ ...S.fieldWrap, marginTop: '20px' }}>
            <label style={S.label}>PAST EXPERIENCE <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional tags)</span></label>
            <div style={S.tagInput}>
              <input id="exp-input" placeholder="e.g. MERN Stack Intern, ML Research Assistant..." style={S.tagInner}
                value={expInput}
                onChange={e => setExpInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addExp())} />
              <button type="button" style={S.addBtn} onClick={addExp}>+ ADD</button>
            </div>
            <div style={S.tags}>
              {form.past_experience.map(s => (
                <span key={s} style={S.tag}>{s} <button type="button" onClick={() => removeTag('past_experience', s)} style={S.tagX}>×</button></span>
              ))}
            </div>
          </div>

          {/* Opportunity Types */}
          <div style={{ ...S.fieldWrap, marginTop: '20px' }}>
            <label style={S.label}>PREFERRED OPPORTUNITY TYPES {errors.pref_opp_types && <span style={S.err}> — {errors.pref_opp_types}</span>}</label>
            <div style={S.oppGrid}>
              {OPP_TYPES.map(t => (
                <button key={t} type="button" id={`opp-type-${t.toLowerCase()}`}
                  style={{ ...S.oppBtn, ...(form.pref_opp_types.includes(t) ? S.oppBtnActive : {}) }}
                  onClick={() => toggleOpp(t)}>
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Financial Need */}
          <div style={{ ...S.fieldWrap, marginTop: '20px' }}>
            <label style={S.label}>FINANCIAL AID NEEDED?</label>
            <div style={S.toggleRow}>
              <span style={{ fontFamily: 'var(--font-body)', fontSize: '15px', color: 'var(--text-secondary)' }}>
                Flag scholarships and stipended opportunities higher in results
              </span>
              <button type="button" id="financial-need-toggle"
                style={{ ...S.toggle, background: form.financial_need ? 'var(--amber)' : 'var(--bg-elevated)' }}
                onClick={() => set('financial_need', !form.financial_need)}>
                <span style={{ ...S.toggleThumb, transform: form.financial_need ? 'translateX(22px)' : 'translateX(2px)' }} />
              </button>
            </div>
          </div>

          <div style={{ marginTop: '36px', display: 'flex', justifyContent: 'flex-end' }}>
            <button id="submit-profile-btn" type="submit" style={S.submitBtn}
              onMouseEnter={e => { e.target.style.background = 'var(--amber)'; e.target.style.color = '#000' }}
              onMouseLeave={e => { e.target.style.background = 'transparent'; e.target.style.color = 'var(--amber)' }}>
              TRANSMIT PROFILE →
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const S = {
  wrap: { minHeight: '100vh', padding: '40px 20px', display: 'flex', alignItems: 'flex-start', justifyContent: 'center' },
  container: { width: '100%', maxWidth: '760px', animation: 'fadeUp 0.6s var(--ease-out) both' },
  header: { marginBottom: '36px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '24px' },
  stage: { fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.12em' },
  title: { fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 'clamp(2rem, 6vw, 3.5rem)', color: 'var(--text-bright)', letterSpacing: '-0.02em', margin: '8px 0 12px' },
  sub: { fontFamily: 'var(--font-body)', fontSize: '16px', color: 'var(--text-secondary)', lineHeight: 1.6 },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' },
  fieldWrap: { display: 'flex', flexDirection: 'column', gap: '8px' },
  label: { fontFamily: 'var(--font-mono)', fontSize: '11px', letterSpacing: '0.1em', color: 'var(--text-muted)', fontWeight: 500 },
  input: {
    fontFamily: 'var(--font-display)', fontSize: '15px', color: 'var(--text-bright)',
    background: 'var(--bg-input)', border: '1px solid var(--border-normal)', borderRadius: '4px',
    padding: '12px 16px', outline: 'none', width: '100%',
    transition: 'border-color 0.2s',
  },
  inputErr: { borderColor: 'var(--red)' },
  err: { fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--red)' },
  tagInput: { display: 'flex', gap: '8px', border: '1px solid var(--border-normal)', borderRadius: '4px', background: 'var(--bg-input)', overflow: 'hidden' },
  tagInner: { flex: 1, padding: '12px 16px', background: 'transparent', border: 'none', outline: 'none', fontFamily: 'var(--font-display)', fontSize: '15px', color: 'var(--text-bright)' },
  addBtn: { padding: '0 18px', background: 'var(--amber-dim)', border: 'none', borderLeft: '1px solid var(--border-normal)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--amber)', letterSpacing: '0.08em', fontWeight: 500 },
  tags: { display: 'flex', flexWrap: 'wrap', gap: '8px', minHeight: '28px' },
  tag: { display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 12px', background: 'var(--amber-dim)', border: '1px solid var(--amber-border)', borderRadius: '2px', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--amber)' },
  tagX: { background: 'none', border: 'none', cursor: 'pointer', color: 'var(--amber)', fontSize: '16px', lineHeight: 1, padding: 0 },
  oppGrid: { display: 'flex', flexWrap: 'wrap', gap: '8px' },
  oppBtn: { padding: '8px 18px', border: '1px solid var(--border-normal)', borderRadius: '2px', background: 'transparent', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)', transition: 'all 0.15s' },
  oppBtnActive: { background: 'var(--amber-dim)', border: '1px solid var(--amber-border)', color: 'var(--amber)' },
  toggleRow: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' },
  toggle: { width: '48px', height: '26px', borderRadius: '13px', border: '1px solid var(--border-normal)', cursor: 'pointer', position: 'relative', transition: 'background 0.25s', flexShrink: 0, padding: 0 },
  toggleThumb: { position: 'absolute', top: '3px', width: '18px', height: '18px', borderRadius: '50%', background: '#fff', transition: 'transform 0.25s var(--ease-out)', display: 'block' },
  submitBtn: { fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '15px', letterSpacing: '0.12em', color: 'var(--amber)', border: '2px solid var(--amber-border)', borderRadius: '2px', padding: '14px 36px', background: 'transparent', cursor: 'pointer', transition: 'all 0.2s var(--ease-out)' },
}
