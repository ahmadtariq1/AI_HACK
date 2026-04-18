import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import ProfilePage from './components/ProfilePage'
import EmailPage from './components/EmailPage'
import ResultsPage from './components/ResultsPage'
import './App.css'

export default function App() {
  const [step, setStep]       = useState(1)
  const [profile, setProfile] = useState(null)
  const [emails, setEmails]   = useState([])
  const [theme, setTheme]     = useState('dark')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark')

  const handleProfileNext = (profileData) => {
    setProfile(profileData)
    setStep(2)
  }

  const handleAnalyse = (emailData) => {
    setEmails(emailData)
    setStep(3)
  }

  return (
    <>
      <Navbar step={step} onGoTo={setStep} theme={theme} toggleTheme={toggleTheme} />
      {step === 1 && <ProfilePage onNext={handleProfileNext} />}
      {step === 2 && <EmailPage onBack={() => setStep(1)} onAnalyse={handleAnalyse} />}
      {step === 3 && <ResultsPage emails={emails} profile={profile} key={emails.length} />}
    </>
  )
}
