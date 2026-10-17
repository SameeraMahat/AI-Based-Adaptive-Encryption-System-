import { useEffect, useState } from 'react'
import './App.css'
import AuthPage from './AuthPage'
import DecryptPage from './DecryptPage'
import HistoryPage from './HistoryPage'
import AnalyticsPage from './AnalyticsPage'

const API_URL = 'http://127.0.0.1:5000/api'

function App() {
  const [activePage, setActivePage] = useState('home')
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [currentUser, setCurrentUser] = useState(null)
  const [authChecking, setAuthChecking] = useState(true)

  useEffect(() => {
    let cancelled = false

    const checkSession = async () => {
      try {
        const response = await fetch(`${API_URL}/auth/me`, {
          method: 'GET',
          credentials: 'include',
        })

        const data = await response.json()

        if (!cancelled && response.ok && data.authenticated) {
          setCurrentUser(data.user)
        }
      } catch (error) {
        console.error('Unable to check login session:', error)
      } finally {
        if (!cancelled) {
          setAuthChecking(false)
        }
      }
    }

    checkSession()

    return () => {
      cancelled = true
    }
  }, [])

  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      })
    } catch (error) {
      console.error('Logout request failed:', error)
    } finally {
      setCurrentUser(null)
      setActivePage('home')
      setFile(null)
      setResult(null)
      setError('')
    }
  }

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0]

    setFile(selectedFile || null)
    setResult(null)
    setError('')
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Upload failed.')
      }

      setResult(data)
    } catch (err) {
      setError(
        err.message ||
          'Unable to connect to the encryption backend.'
      )
    } finally {
      setLoading(false)
    }
  }

  const getSecurityClass = (level) => {
    if (!level) return ''

    const value = level.toLowerCase()

    if (value.includes('very')) return 'very-high'
    if (value.includes('high')) return 'high'
    if (value.includes('medium')) return 'medium'

    return 'standard'
  }

  const getPiiCount = () => {
    if (!result?.pii) return 0

    return Object.values(result.pii).reduce((total, value) => {
      if (Array.isArray(value)) return total + value.length
      if (typeof value === 'number') return total + value
      return total
    }, 0)
  }

  const formatBytes = (bytes) => {
    if (bytes === undefined || bytes === null || bytes === 0) {
      return '0 Bytes'
    }

    const units = ['Bytes', 'KB', 'MB', 'GB']
    const index = Math.floor(Math.log(bytes) / Math.log(1024))

    return `${(
      bytes / Math.pow(1024, index)
    ).toFixed(2)} ${units[index]}`
  }

  const formatPercent = (value) => {
    if (value === undefined || value === null) {
      return 'N/A'
    }

    return `${(value * 100).toFixed(1)}%`
  }

  const getSensitivityLevel = (score) => {
    if (score === undefined || score === null) {
      return 'N/A'
    }

    if (score >= 75) return 'Very High'
    if (score >= 50) return 'High'
    if (score >= 25) return 'Medium'

    return 'Low'
  }

  const recentFiles = [
    {
      name: 'research_paper.pdf',
      type: 'PDF',
      time: '2 min ago',
    },
    {
      name: 'data_analysis.xlsx',
      type: 'XLSX',
      time: '15 min ago',
    },
    {
      name: 'project_docs.zip',
      type: 'ZIP',
      time: '1 hour ago',
    },
    {
      name: 'image_sample.png',
      type: 'IMG',
      time: '2 hours ago',
    },
  ]

  // =====================================================
  // AUTHENTICATION GATE
  // =====================================================

  if (authChecking) {
    return (
      <div className="auth-loading">
        Checking your secure session...
      </div>
    )
  }

  if (!currentUser) {
    return <AuthPage onAuthenticated={setCurrentUser} />
  }

  return (
    <div className="app">

      {/* =====================================================
          SIDEBAR
          ===================================================== */}

      <aside className="sidebar">

        <div className="sidebar-brand">

          <div className="shield-logo">
            <span>◆</span>
          </div>

          <div className="brand-copy">
            <h1>Adaptive Encryption</h1>
            <p>AI-Powered Security System</p>
          </div>

        </div>

        <div className="sidebar-divider" />

        <nav className="navigation">

          <button
            className={`nav-item ${
              activePage === 'home' ? 'active' : ''
            }`}
            onClick={() => setActivePage('home')}
          >
            <span className="nav-icon">🏠</span>
            <span>Home</span>
          </button>

          <button
            className={`nav-item ${
              activePage === 'decrypt' ? 'active' : ''
            }`}
            onClick={() => setActivePage('decrypt')}
          >
            <span className="nav-icon">🔓</span>
            <span>Decrypt</span>
          </button>

          <button
            className={`nav-item ${
              activePage === 'history' ? 'active' : ''
            }`}
            onClick={() => setActivePage('history')}
          >
            <span className="nav-icon">🕘</span>
            <span>History</span>
          </button>

          <button
            className={`nav-item ${
              activePage === 'analytics' ? 'active' : ''
            }`}
            onClick={() => setActivePage('analytics')}
          >
            <span className="nav-icon">📊</span>
            <span>Analytics</span>
          </button>

          <button className="nav-item">
            <span className="nav-icon">⚙</span>
            <span>Settings</span>
          </button>

        </nav>
        <div className="sidebar-bottom">

          <div className="sidebar-message">
            <div className="message-line" />

            <strong>
              Security
              <br />
              Today.
              <br />
              Brighter
              <br />
              Tomorrows.
            </strong>
          </div>

          <div className="version">
            <span>v1.0.0</span>
            <span>© 2025 Adaptive Encryption</span>
            <span>All rights reserved.</span>
          </div>

        </div>

      </aside>


      {/* =====================================================
          MAIN AREA
          ===================================================== */}

      <div className="workspace">

        {/* TOP BAR */}

        <header className="topbar">

          <div className="search-box">

            <span className="search-icon">⌕</span>

            <input
             id="global-search"
             name="globalSearch"
             type="text"
             placeholder="Search files, history, or settings..."
             aria-label="Search files, history, or settings"
            />

            <kbd>Ctrl K</kbd>

          </div>

          <div className="topbar-actions">

            <button className="notification">
              !
            </button>

            <div className="backend-status">
              <span className="online-dot" />
              Backend Connected
            </div>

            <div className="profile" title={currentUser.email}>
              {currentUser.username?.charAt(0)?.toUpperCase() || 'U'}
            </div>

            <span className="current-user-name">
              {currentUser.username}
            </span>

            <button
              type="button"
              className="logout-button"
              onClick={handleLogout}
            >
              Sign out
            </button>

          </div>

        </header>


        {/* CONTENT */}

        <main className="content">

          {activePage === 'decrypt' ? (
            <DecryptPage onNavigate={setActivePage} />
          ) : activePage === 'history' ? (
            <HistoryPage onNavigate={setActivePage} />
          ) : activePage === 'analytics' ? (
            <AnalyticsPage onNavigate={setActivePage} />
          ) : (
            <>

              {/* HERO */}

              <section className="hero">

                <div className="hero-copy">

                  <p className="hero-eyebrow">
                    INTELLIGENT FILE PROTECTION
                  </p>

                  <h2>
                    Upload. Analyze.
                    <br />
                    <span>Encrypt Adaptively.</span>
                  </h2>

                  <p className="hero-description">
                    Our AI-driven encryption engine analyzes your file
                    and automatically selects the most suitable
                    encryption strategy based on sensitivity,
                    file characteristics and detected information.
                  </p>

                </div>

                <div className="hero-visual">

                  <div className="orbit orbit-one" />
                  <div className="orbit orbit-two" />
                  <div className="orbit orbit-three" />

                  <div className="hero-shield">

                    <div className="shield-inner">

                      <div className="lock">

                        <div className="lock-top" />

                        <div className="lock-body">
                          <span>•</span>
                        </div>

                      </div>

                    </div>

                  </div>

                  <div className="hero-side-text">

                    <span>PRIVACY</span>
                    <span>TODAY</span>
                    <span>SAFER</span>
                    <span>TOMORROW</span>

                    <i />

                  </div>

                </div>

              </section>


              {/* DASHBOARD GRID */}

              <section className="dashboard-grid">

                <div className="main-column">

                  {/* FEATURE CARDS */}

                  <div className="feature-grid">

                    <div className="feature-card">

                      <div className="feature-icon">
                        ✦
                      </div>

                      <div>
                        <h3>AI Analysis</h3>

                        <p>
                          Detects file sensitivity
                          <br />
                          and content type
                        </p>
                      </div>

                    </div>


                    <div className="feature-card">

                      <div className="feature-icon">
                        ⚙
                      </div>

                      <div>
                        <h3>Adaptive Encryption</h3>

                        <p>
                          Chooses the best algorithm
                          <br />
                          automatically
                        </p>
                      </div>

                    </div>


                    <div className="feature-card">

                      <div className="feature-icon">
                        🔒
                      </div>

                      <div>
                        <h3>Secure Output</h3>

                        <p>
                          Your data stays protected
                          <br />
                          and private
                        </p>
                      </div>

                    </div>

                  </div>


                  {/* UPLOAD */}

                  <section className="upload-card">

                    <div className="upload-heading">

                      <div className="upload-heading-icon">
                        ⇧
                      </div>

                      <div>
                        <h3>Upload & Analysis</h3>

                        <p>
                          Select a file to begin adaptive security analysis.
                        </p>
                      </div>

                    </div>


                    <label className="drop-zone">

                      <input
                        type="file"
                        onChange={handleFileChange}
                        accept=".pdf,.docx,.txt,.xlsx,.png,.jpg,.jpeg"
                      />

                      <div className="cloud-icon">
                        ⇧
                      </div>

                      {file ? (
                        <>
                          <strong>{file.name}</strong>
                          <span>{formatBytes(file.size)}</span>
                        </>
                      ) : (
                        <>
                          <strong>
                            Drag and drop your file here
                          </strong>

                          <span>
                            or click to browse
                          </span>
                        </>
                      )}

                      <div className="browse-row">

                        <span className="browse-button">
                          <span>□</span>
                          Choose File
                        </span>

                        {!file && (
                          <span className="no-file">
                            No file chosen
                          </span>
                        )}

                      </div>

                      <small>
                        Supported formats: PDF, DOCX, TXT, XLSX,
                        PNG, JPG (Max 100MB)
                      </small>

                    </label>


                    {file && (
                      <div className="selected-file">

                        <div>
                          <span>SELECTED FILE</span>

                          <strong>
                            {file.name}
                          </strong>
                        </div>

                        <span>
                          {formatBytes(file.size)}
                        </span>

                      </div>
                    )}


                    <button
                      className="analyze-button"
                      onClick={handleUpload}
                      disabled={!file || loading}
                    >
                      {loading
                        ? 'Analyzing & Encrypting...'
                        : 'Analyze & Encrypt File'}
                    </button>


                    {error && (
                      <div className="error-message">
                        <strong>Error:</strong> {error}
                      </div>
                    )}


                    {/* PROCESS */}

                    <div className="process-row">

                      <div className="process-step">

                        <div className="step-number">
                          1
                        </div>

                        <div>
                          <strong>AI Analysis</strong>
                          <span>
                            Scanning file content...
                          </span>
                        </div>

                      </div>

                      <div className="step-arrow">
                        →
                      </div>

                      <div className="process-step">

                        <div className="step-number">
                          2
                        </div>

                        <div>
                          <strong>Adaptive Encryption</strong>
                          <span>
                            Selecting best algorithm...
                          </span>
                        </div>

                      </div>

                      <div className="step-arrow">
                        →
                      </div>

                      <div className="process-step">

                        <div className="step-number">
                          3
                        </div>

                        <div>
                          <strong>Secure Output</strong>
                          <span>
                            Encrypting and finalizing...
                          </span>
                        </div>

                      </div>

                    </div>

                  </section>

                </div>


                {/* RECENT ACTIVITY */}

                <aside className="activity-card">

                  <div className="activity-header">

                    <h3>Recent Activity</h3>

                    <button>
                      View All
                    </button>

                  </div>

                  <div className="activity-list">

                    {recentFiles.map((item) => (

                      <div
                        className="activity-item"
                        key={item.name}
                      >

                        <div
                          className={`file-type ${item.type.toLowerCase()}`}
                        >
                          {item.type}
                        </div>

                        <div className="activity-info">

                          <strong>
                            {item.name}
                          </strong>

                          <span>
                            Encrypted • {item.time}
                          </span>

                        </div>

                        <div className="activity-check">
                          ✓
                        </div>

                      </div>

                    ))}

                  </div>

                </aside>

              </section>


              {/* =================================================
                  RESULTS
                  ================================================= */}

              {result && (

                <section className="results-section">

                  <div className="results-header">

                    <div>

                      <p className="result-eyebrow">
                        ANALYSIS COMPLETE
                      </p>

                      <h2>
                        Encryption Decision
                      </h2>

                    </div>

                    <div className="success-badge">
                      ✓ Encrypted Successfully
                    </div>

                  </div>


                  {/* RESULT GRID */}

                  <div className="result-grid">

                    <div className="result-card">

                      <span>FILE</span>

                      <h3>
                        {result.filename}
                      </h3>

                      <p>
                        File size:{' '}
                        {formatBytes(
                          result.system_features?.file_size_bytes ||
                          result.sensitivity?.file_size_bytes ||
                          file?.size
                        )}
                      </p>

                    </div>


                    <div className="result-card">

                      <span>CLASSIFICATION</span>

                      <h3>
                        {result.classification?.document_category ||
                          'General'}
                      </h3>

                      <p>
                        Confidence:{' '}

                        {result.classification?.category_confidence != null
                          ? `${(
                              result.classification.category_confidence * 100
                            ).toFixed(0)}%`
                          : 'N/A'}
                      </p>

                    </div>


                    <div className="result-card">

                      <span>PII DETECTED</span>

                      <h3>
                        {result.sensitivity?.pii_count ??
                          getPiiCount()}
                      </h3>

                      <p>
                        Sensitive information detected
                      </p>

                    </div>


                    <div className="result-card">

                      <span>SENSITIVITY</span>

                      <h3>
                        {getSensitivityLevel(
                          result.sensitivity?.sensitivity_score
                        )}
                      </h3>

                      <p>
                        Score:{' '}

                        {result.sensitivity?.sensitivity_score ??
                          'N/A'}
                        /100
                      </p>

                    </div>

                  </div>


                  {/* POLICY */}

                  <div className="policy-card">

                    <div className="policy-title">

                      <div className="policy-icon">
                        AI
                      </div>

                      <div>

                        <span>
                          ADAPTIVE POLICY
                        </span>

                        <h3>
                          Recommended Encryption
                        </h3>

                      </div>

                    </div>


                    <div className="policy-grid">

                      <div>

                        <small>
                          ALGORITHM
                        </small>

                        <strong>
                          {result.encryption?.algorithm ||
                            'Not available'}
                        </strong>

                      </div>


                      <div>

                        <small>
                          SECURITY LEVEL
                        </small>

                        <div
                          className={`security-badge ${getSecurityClass(
                            result.encryption?.security_level
                          )}`}
                        >
                          {result.encryption?.security_level ||
                            'Standard'}
                        </div>

                      </div>


                      <div>

                        <small>
                          AI MODEL PREDICTION
                        </small>

                        <strong>
                          {result.ml_prediction?.algorithm ||
                            'N/A'}
                        </strong>

                      </div>


                      <div>

                        <small>
                          MODEL CONFIDENCE
                        </small>

                        <strong>
                          {formatPercent(
                            result.ml_prediction?.confidence
                          )}
                        </strong>

                      </div>

                    </div>


                    <div className="reason-box">

                      <span>
                        Why this policy?
                      </span>

                      <p>
                        {result.encryption?.reason ||
                          'The adaptive AI engine selected this encryption strategy based on the analyzed file characteristics.'}
                      </p>

                    </div>

                  </div>


                  {/* DETAILS */}

                  <div className="details-grid">

                    <div className="details-card">

                      <h3>
                        Sensitivity Analysis
                      </h3>


                      <div className="detail-row">

                        <span>
                          PII Count
                        </span>

                        <strong>
                          {result.sensitivity?.pii_count ?? 0}
                        </strong>

                      </div>


                      <div className="detail-row">

                        <span>
                          Confidential Keywords
                        </span>

                        <strong>
                          {result.sensitivity
                            ?.confidential_keyword_count ?? 0}
                        </strong>

                      </div>


                      <div className="detail-row">

                        <span>
                          Confidential Marker
                        </span>

                        <strong>
                          {result.sensitivity
                            ?.confidential_marker || 'N/A'}
                        </strong>

                      </div>


                      <div className="detail-row">

                        <span>
                          Sensitivity Score
                        </span>

                        <strong>
                          {result.sensitivity
                            ?.sensitivity_score ?? 'N/A'}
                          /100
                        </strong>

                      </div>


                      <div className="detail-row">

                        <span>
                          File Size
                        </span>

                        <strong>
                          {formatBytes(
                            result.sensitivity
                              ?.file_size_bytes ??
                            file?.size
                          )}
                        </strong>

                      </div>


                      <div className="detail-row">

                        <span>
                          Extension
                        </span>

                        <strong>
                          {result.sensitivity
                            ?.file_extension || 'N/A'}
                        </strong>

                      </div>

                    </div>


                    <div className="details-card">

                      <h3>
                        Encryption Status
                      </h3>


                      <div className="encryption-success">

                        <div className="success-icon">
                          ✓
                        </div>

                        <div>

                          <strong>
                            File encrypted successfully
                          </strong>

                          <p>
                            {result.encryption?.algorithm}
                          </p>

                        </div>

                      </div>


                      <div className="encrypted-file">

                        <span>
                          Encrypted file
                        </span>

                        <strong>
                          {result.encryption?.encrypted_file}
                        </strong>

                      </div>


                      <div className="encrypted-file">

                        <span>
                          Key file
                        </span>

                        <strong>
                          {result.encryption?.key_file ||
                            'Managed securely by backend'}
                        </strong>

                      </div>

                    </div>

                  </div>


                  {/* PERFORMANCE */}

                  <div className="performance-card">

                    <div>

                      <span>
                        PERFORMANCE ANALYSIS
                      </span>

                      <h3>
                        Encryption Performance
                      </h3>

                    </div>


                    <div className="performance-grid">

                      <div>

                        <span>
                          Original Size
                        </span>

                        <strong>
                          {formatBytes(
                            result.performance
                              ?.original_size_bytes
                          )}
                        </strong>

                      </div>


                      <div>

                        <span>
                          Encrypted Size
                        </span>

                        <strong>
                          {formatBytes(
                            result.performance
                              ?.encrypted_size_bytes
                          )}
                        </strong>

                      </div>


                      <div>

                        <span>
                          Encryption Time
                        </span>

                        <strong>
                          {result.performance
                            ?.encryption_time_ms ?? 'N/A'} ms
                        </strong>

                      </div>


                      <div>

                        <span>
                          Size Overhead
                        </span>

                        <strong>
                          {result.performance
                            ?.size_overhead_percent ?? 'N/A'}%
                        </strong>

                      </div>

                    </div>

                  </div>


                  {/* PROBABILITIES */}

                  {result.ml_prediction?.probabilities && (

                    <div className="probability-card">

                      <span>
                        AI DECISION ANALYSIS
                      </span>

                      <h3>
                        Model Prediction Probabilities
                      </h3>


                      <div className="probability-list">

                        {Object.entries(
                          result.ml_prediction.probabilities
                        ).map(([algorithm, probability]) => (

                          <div
                            className="probability-row"
                            key={algorithm}
                          >

                            <span>
                              {algorithm}
                            </span>

                            <div className="probability-bar">

                              <div
                                className="probability-fill"
                                style={{
                                  width: `${probability * 100}%`,
                                }}
                              />

                            </div>

                            <strong>
                              {(probability * 100).toFixed(1)}%
                            </strong>

                          </div>

                        ))}

                      </div>

                    </div>

                  )}


                  {/* DOWNLOAD */}

                  {result.encryption?.encrypted_file && (

                    <a
                      className="download-button"
                      href={`${API_URL}/download/${encodeURIComponent(
                        result.encryption.encrypted_file
                      )}`}
                    >
                      ↓ Download Encrypted File
                    </a>

                  )}

                </section>

              )}

            </>
          )}

        </main>


        {/* FOOTER */}

        <footer className="footer">

          <span>
            AI-Based Adaptive Encryption System
          </span>

          <span>
            Intelligent security • Automated policy selection
          </span>

        </footer>

      </div>

    </div>
  )
}

export default App