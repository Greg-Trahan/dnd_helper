import { useEffect, useState } from 'react'
import { getHealth } from '../services/dashboard/dashboardService'
import '../styles/global.css'

type View = 'dashboard' | 'characters' | 'campaigns' | 'compendium' | 'settings'

const navigation: { id: View; label: string; icon: string }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '⌂' },
  { id: 'characters', label: 'Characters', icon: '♙' },
  { id: 'campaigns', label: 'Campaigns', icon: '⚑' },
  { id: 'compendium', label: 'Compendium', icon: '▤' },
  { id: 'settings', label: 'Settings', icon: '⚙' },
]

const viewDescriptions: Record<View, string> = {
  dashboard: 'Your adventures start here.',
  characters: 'Create, manage, and explore your character builds.',
  campaigns: 'Keep your adventures and party organized.',
  compendium: 'Explore creatures, spells, equipment, and more.',
  settings: 'Manage your D&D Helper preferences.',
}

function App() {
  const [activeView, setActiveView] = useState<View>('dashboard')
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking')

  useEffect(() => {
    let mounted = true

    getHealth()
      .then((data) => {
        if (mounted) {
          setApiStatus(
            data.status === 'healthy' && data.database === 'connected'
              ? 'connected'
              : 'disconnected',
          )
        }
      })
      .catch(() => {
        if (mounted) {
          setApiStatus('disconnected')
        }
      })

    return () => {
      mounted = false
    }
  }, [])

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">D</div>
          <div>
            <div className="brand-name">D&D Helper</div>
            <div className="brand-subtitle">ADVENTURE COMPANION</div>
          </div>
        </div>

        <div className="nav-heading">WORKSPACE</div>
        <nav className="main-nav" aria-label="Main navigation">
          {navigation.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activeView === item.id ? 'active' : ''}`}
              onClick={() => setActiveView(item.id)}
              aria-current={activeView === item.id ? 'page' : undefined}
            >
              <span className="nav-icon" aria-hidden="true">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="connection-card">
            <div className="connection-heading">SYSTEM STATUS</div>
            <div className="connection-line">
              <span className={`status-dot ${apiStatus}`} />
              <span>
                {apiStatus === 'checking'
                  ? 'Checking connection'
                  : apiStatus === 'connected'
                    ? 'Database connected'
                    : 'Connection unavailable'}
              </span>
            </div>
          </div>
          <div className="sidebar-version">D&D Helper · Version 1.0</div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">D&D HELPER <span>/</span> {activeView.toUpperCase()}</div>
          <div className="topbar-label">YOUR ADVENTURE STARTS HERE</div>
        </header>

        <div className="page-content">
          {activeView === 'dashboard' ? (
            <>
              <section className="welcome-section">
                <div className="eyebrow">WELCOME, ADVENTURER</div>
                <h1>Your next adventure<br />begins here.</h1>
                <p>
                  Build heroes, organize campaigns, and explore the
                  world of Dungeons & Dragons.
                </p>
                <button
                  className="primary-button"
                  onClick={() => setActiveView('characters')}
                >
                  <span aria-hidden="true">＋</span> Create a character
                </button>
                <div className="welcome-decoration" aria-hidden="true">✧</div>
              </section>

              <section className="section-block">
                <div className="section-heading">
                  <div>
                    <div className="eyebrow">YOUR WORKSPACE</div>
                    <h2>Adventure tools</h2>
                  </div>
                </div>

                <div className="tool-grid">
                  <button
                    className="tool-card"
                    onClick={() => setActiveView('characters')}
                  >
                    <div className="tool-icon character-icon">♙</div>
                    <div className="tool-card-title">Character Builder</div>
                    <p>Create and customize your next hero.</p>
                    <span className="tool-link">Explore characters →</span>
                  </button>

                  <button
                    className="tool-card"
                    onClick={() => setActiveView('campaigns')}
                  >
                    <div className="tool-icon campaign-icon">⚑</div>
                    <div className="tool-card-title">Campaign Manager</div>
                    <p>Organize your campaigns and parties.</p>
                    <span className="tool-link">Explore campaigns →</span>
                  </button>

                  <button
                    className="tool-card"
                    onClick={() => setActiveView('compendium')}
                  >
                    <div className="tool-icon compendium-icon">▤</div>
                    <div className="tool-card-title">Compendium</div>
                    <p>Browse the D&D reference library.</p>
                    <span className="tool-link">Explore compendium →</span>
                  </button>
                </div>
              </section>

              <section className="section-block getting-started">
                <div className="eyebrow">THE JOURNEY AWAITS</div>
                <h2>Make this world your own.</h2>
                <p>
                  Your tools are taking shape. Start with a character,
                  build a party, and prepare for adventure.
                </p>
              </section>
            </>
          ) : (
            <section className="placeholder-section">
              <div className="eyebrow">D&D HELPER WORKSPACE</div>
              <h1>{navigation.find((item) => item.id === activeView)?.label}</h1>
              <p>{viewDescriptions[activeView]}</p>
              <div className="placeholder-card">
                <div className="placeholder-icon">✧</div>
                <h2>Coming soon</h2>
                <p>
                  We're building this part of your adventure.
                  The foundation is in place; functionality will be added next.
                </p>
                <button
                  className="secondary-button"
                  onClick={() => setActiveView('dashboard')}
                >
                  Return to dashboard
                </button>
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
