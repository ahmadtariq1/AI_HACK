export default function Navbar({ step, onGoTo, theme, toggleTheme }) {
  const steps = [
    { n: 1, label: '01 / Profile' },
    { n: 2, label: '02 / Emails' },
    { n: 3, label: '03 / Results' },
  ]
  return (
    <nav className="nav">
      <div className="nav-brand">
        <div className="dot" />
        ALPHA MAIL EXTRACTOR
      </div>
      <div className="nav-steps">
        {steps.map(s => (
          <div
            key={s.n}
            className={`nav-step ${step === s.n ? 'active' : step > s.n ? 'completed' : ''}`}
            onClick={() => step > s.n && onGoTo(s.n)}
          >
            {s.label}
          </div>
        ))}
      </div>
      <button className="theme-toggle" onClick={toggleTheme}>
        <span className="theme-toggle-icon">{theme === 'dark' ? '☀️' : '🌙'}</span>
        {theme === 'dark' ? 'Light' : 'Dark'}
      </button>
    </nav>
  )
}
