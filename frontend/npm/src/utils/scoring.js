const TODAY = new Date('2026-04-18')

export function classifyEmail(email) {
  const text = (email.subject + ' ' + email.body).toLowerCase()
  const spamTerms = ['newsletter', 'digest', 'unsubscribe', 'weekly', 'subscribe', 'forward to a friend', 'this week in']
  return !spamTerms.some(t => text.includes(t))
}

export function extractOpportunity(email) {
  const text = email.body + ' ' + email.subject
  const lower = text.toLowerCase()

  const typeMap = {
    'hackathon': 'Hackathon', 'competition': 'Competition',
    'internship': 'Internship', 'scholarship': 'Scholarship',
    'fellowship': 'Fellowship', 'research': 'Research',
    'workshop': 'Workshop', 'bootcamp': 'Workshop'
  }
  let oppType = 'Other'
  for (const [k, v] of Object.entries(typeMap)) {
    if (lower.includes(k)) { oppType = v; break }
  }

  // Deadline extraction
  const deadlinePatterns = [
    /deadline[:\s]+([A-Za-z]+ \d{1,2},?\s*\d{4})/i,
    /apply by[:\s]+([A-Za-z]+ \d{1,2},?\s*\d{4})/i,
    /due[:\s]+([A-Za-z]+ \d{1,2},?\s*\d{4})/i,
    /(April|May|June|July|August)\s+(\d{1,2}),?\s*(2026)/i
  ]
  let deadline = null
  for (const p of deadlinePatterns) {
    const m = text.match(p)
    if (m) {
      try {
        const d = new Date(m[1] || m[0])
        if (!isNaN(d)) { deadline = d; break }
      } catch (e) {}
    }
  }

  // Min CGPA
  const cgpaM = text.match(/CGPA[:\s≥>=]+(\d+\.?\d*)/i)
  const minCgpa = cgpaM ? parseFloat(cgpaM[1]) : 0

  // Location
  let location = 'Unspecified'
  if (lower.includes('lahore')) location = 'Lahore'
  else if (lower.includes('remote')) location = 'Remote'
  else if (lower.includes('karachi')) location = 'Karachi'
  else if (lower.includes('islamabad')) location = 'Islamabad'

  return { oppType, deadline, minCgpa, location, text, subject: email.subject, from: email.from }
}

export function scoreOpportunity(opp, profile) {
  // Hard filter: CGPA
  if (opp.minCgpa > 0 && profile.cgpa < opp.minCgpa) {
    return { score: 0, eligible: false, sFit: 0, sUrgency: 0, sPref: 0 }
  }

  // Fit score (50%)
  const lower = opp.text.toLowerCase()
  const matchedSkills = profile.skills_interests.filter(s => lower.includes(s.toLowerCase()))
  const skillMatch = profile.skills_interests.length > 0 ? matchedSkills.length / profile.skills_interests.length : 0
  const sFit = Math.min(100, Math.round(skillMatch * 100))

  // Urgency score (30%) — formula: 100 / (days + 1)
  let sUrgency = 20
  if (opp.deadline) {
    const days = Math.max(0, Math.ceil((opp.deadline - TODAY) / 86400000))
    sUrgency = Math.min(100, Math.round(100 / (days + 1) * 10))
  }

  // Preference score (20%)
  const typeMatch = profile.pref_opp_types.includes(opp.oppType) ? 60 : 0
  const locMatch = (profile.location_pref === 'No Preference' || opp.location === profile.location_pref || opp.location === 'Remote') ? 40 : 0
  const sPref = typeMatch + locMatch

  const score = Math.round(0.5 * sFit + 0.3 * sUrgency + 0.2 * sPref)
  return { score, eligible: true, sFit, sUrgency, sPref }
}

export function buildWhyText(opp, scoring, profile) {
  const parts = []
  if (scoring.sFit > 60) parts.push(`Strong skill alignment (${scoring.sFit}% match)`)
  if (profile.pref_opp_types.includes(opp.oppType)) parts.push(`matches your preferred type (${opp.oppType})`)
  if (opp.location === profile.location_pref) parts.push(`located in ${opp.location}`)
  if (opp.deadline) {
    const days = Math.ceil((opp.deadline - TODAY) / 86400000)
    if (days <= 10) parts.push(`<strong>deadline in ${days} days</strong> — act fast`)
  }
  if (opp.minCgpa > 0) parts.push(`your CGPA ${Number(profile.cgpa).toFixed(2)} exceeds the ${opp.minCgpa} requirement`)
  return parts.length ? parts.join(' · ') : 'Moderate alignment with your profile.'
}

export function getDaysRemaining(deadline) {
  if (!deadline) return null
  return Math.ceil((deadline - TODAY) / 86400000)
}

export function formatDeadline(deadline) {
  if (!deadline) return 'Not specified'
  return deadline.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

export function extractRequirements(emailBody) {
  const lower = emailBody.toLowerCase()
  const reqs = []
  if (lower.includes('resume') || lower.includes(' cv')) reqs.push('Resume / CV')
  if (lower.includes('transcript')) reqs.push('Official Transcript')
  if (lower.includes('cnic')) reqs.push('CNIC Copy')
  if (lower.includes('statement of purpose') || lower.includes(' sop')) reqs.push('Statement of Purpose')
  if (lower.includes('reference') || lower.includes('recommendation')) reqs.push('Reference Letter')
  if (lower.includes('bank statement')) reqs.push('Bank Statement')
  if (lower.includes('income certificate')) reqs.push('Income Certificate')
  return reqs
}

export function runPipeline(emails, profile) {
  const parsed = []
  const filtered = []

  for (const em of emails) {
    if (!classifyEmail(em)) { filtered.push(em); continue }
    const opp = extractOpportunity(em)
    const scoring = scoreOpportunity(opp, profile)
    parsed.push({ opp, scoring, email: em })
  }

  parsed.sort((a, b) => b.scoring.score - a.scoring.score)
  return { parsed, filtered }
}
