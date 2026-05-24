import { useState } from 'react'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [copied, setCopied] = useState(false)

  const lines = query.split('\n').filter(line => line.trim() !== '')
  const gartnerLinks = lines.map(
    line => `https://www.gartner.com/mysearch/all?g=${encodeURIComponent(line.trim())}`
  )

  const handleCopy = async () => {
    if (gartnerLinks.length === 0) return
    const textToCopy = gartnerLinks.join('\n')
    try {
      await navigator.clipboard.writeText(textToCopy)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      const ta = document.createElement('textarea')
      ta.value = textToCopy
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="app">
      <div className="card">
        <div className="logo-area">
          <div className="logo-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </div>
          <h1>Gartner Search</h1>
          <p className="subtitle">Generate search links for Gartner research — one per line</p>
        </div>

        <div className="input-group">
          <textarea
            id="search-input"
            placeholder={"Enter search terms, one per line...\ne.g.\nCloud Security\nAI Strategy\nERP Solutions"}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={5}
            autoFocus
          />
          <div className="input-glow" />
        </div>

        {gartnerLinks.length > 0 && (
          <div className="result-area">
            <div className="link-preview">
              <span className="link-label">
                Generated {gartnerLinks.length === 1 ? 'Link' : `Links (${gartnerLinks.length})`}
              </span>
              <div className="links-list">
                {gartnerLinks.map((url, idx) => (
                  <div className="link-row" key={idx}>
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="link-term-link"
                    >
                      {lines[idx]}
                    </a>
                  </div>
                ))}
              </div>
            </div>

            <button
              id="copy-button"
              className={`copy-btn ${copied ? 'copied' : ''}`}
              onClick={handleCopy}
            >
              {copied ? (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                  Copied {gartnerLinks.length} {gartnerLinks.length === 1 ? 'link' : 'links'}!
                </>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                  </svg>
                  Copy {gartnerLinks.length === 1 ? 'Link' : `All ${gartnerLinks.length} Links`}
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
