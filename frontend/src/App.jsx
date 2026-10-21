import { useEffect, useRef, useState } from 'react'
import './App.css'
import Signup from "./assets/components/Signup.jsx";
import Login from "./assets/components/Login.jsx";
import DecryptPage from "./assets/components/DecryptPage";
import AnalyticsPage from './assets/components/AnalyticsPage'
import Settings from "./assets/components/Settings";
import HistoryPage from './assets/components/HistoryPage'

const API_URL = 'http://127.0.0.1:5000/api'

function App() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activePage, setActivePage] = useState('home')
  const [showDecryptVerification, setShowDecryptVerification] = useState(false)
  const [decryptPassword, setDecryptPassword] = useState('')
  const [decryptToken, setDecryptToken] = useState('')
  const [decryptVerifyLoading, setDecryptVerifyLoading] = useState(false)
  const [decryptVerifyError, setDecryptVerifyError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const searchInputRef = useRef(null)


const openDecryptVerification = () => {
  console.log('Opening decrypt verification modal')

  setDecryptPassword('')
  setDecryptVerifyError('')
  setShowDecryptVerification(true)
}


  const searchItems = [
  {
    title: 'Home',
    description: 'Go to dashboard and upload files',
    keywords: 'home dashboard upload file encryption',
    action: () => {
      document
        .querySelector('.hero')
        ?.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        })
    },
  },
  {
    title: 'Encrypt',
    description: 'Upload and encrypt a file',
    keywords: 'encrypt encryption upload secure file',
    action: () => {
      document
        .querySelector('.upload-section')
        ?.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        })
    },
  },
  {
  title: 'Decrypt',
  description: 'Decrypt a file after password verification',
  keywords: 'decrypt decryption secure file',
  action: openDecryptVerification,
},
  {
    title: 'History',
    description: 'View encryption and decryption history',
    keywords: 'history activity records encryption decryption',
    action: () => {
      const button = [...document.querySelectorAll('.nav-item')]
        .find((item) =>
          item.textContent
            ?.toLowerCase()
            .includes('history')
        )

      button?.click()
    },
  },
  {
    title: 'Analytics',
    description: 'View security and encryption analytics',
    keywords: 'analytics statistics charts security performance',
    action: () => {
      const button = [...document.querySelectorAll('.nav-item')]
        .find((item) =>
          item.textContent
            ?.toLowerCase()
            .includes('analytics')
        )

      button?.click()
    },
  },
  {
    title: 'Settings',
    description: 'Manage application settings',
    keywords: 'settings preferences security theme account support',
    action: () => {
      const button = [...document.querySelectorAll('.nav-item')]
        .find((item) =>
          item.textContent
            ?.toLowerCase()
            .includes('settings')
        )

      button?.click()
    },
  },
  {
    title: 'Documentation',
    description: 'Learn how to use Adaptive Encryption',
    keywords: 'documentation help guide user manual docs',
    action: () => {
      const button = [...document.querySelectorAll('.nav-item')]
        .find((item) =>
          item.textContent
            ?.toLowerCase()
            .includes('settings')
        )

      button?.click()

      setTimeout(() => {
        const documentationButton = [
          ...document.querySelectorAll('.support-row'),
        ].find((item) =>
          item.textContent
            ?.toLowerCase()
            .includes('documentation')
        )

        documentationButton?.click()
      }, 250)
    },
  },
  {
    title: 'Report an Issue',
    description: 'Report a system problem or bug',
    keywords: 'issue bug problem error report support',
    action: () => {
      const button = [...document.querySelectorAll('.nav-item')]
        .find((item) =>
          item.textContent
            ?.toLowerCase()
            .includes('settings')
        )

      button?.click()

      setTimeout(() => {
        const issueButton = [
          ...document.querySelectorAll('.support-row'),
        ].find((item) =>
          item.textContent
            ?.toLowerCase()
            .includes('report an issue')
        )

        issueButton?.click()
      }, 250)
    },
  },
  {
    title: 'Contact Support',
    description: 'Contact the support team',
    keywords: 'contact support help message assistance',
    action: () => {
      const button = [...document.querySelectorAll('.nav-item')]
        .find((item) =>
          item.textContent
            ?.toLowerCase()
            .includes('settings')
        )

      button?.click()

      setTimeout(() => {
        const supportButton = [
          ...document.querySelectorAll('.support-row'),
        ].find((item) =>
          item.textContent
            ?.toLowerCase()
            .includes('contact support')
        )

        supportButton?.click()
      }, 250)
    },
  },
]


const filteredSearchItems = searchItems.filter((item) => {
  const query = searchQuery.trim().toLowerCase()

  if (!query) {
    return false
  }

  const title = String(item.title || '').toLowerCase()
  const description = String(item.description || '').toLowerCase()
  const keywords = String(item.keywords || '').toLowerCase()

  return (
    title.includes(query) ||
    description.includes(query) ||
    keywords.includes(query)
  )
})


const handleSearchSelect = (item) => {
  setSearchQuery('')
  item.action()
}


const handleDecryptVerification = async (event) => {
  event.preventDefault()
  setDecryptVerifyError('')

  let user = null

  try {
    user = JSON.parse(localStorage.getItem('user') || 'null')
  } catch {
    user = null
  }

  if (!user?.email) {
    setDecryptVerifyError(
      'Logged-in user email not found. Please log in again.'
    )
    return
  }

  if (!decryptPassword) {
    setDecryptVerifyError('Please enter your password.')
    return
  }

  setDecryptVerifyLoading(true)

  try {
    const response = await fetch(
      `${API_URL}/auth/verify-decrypt`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: user.email,
          password: decryptPassword,
        }),
      }
    )

    const data = await response.json()

    if (!response.ok || !data.decrypt_token) {
      throw new Error(
        data.message || 'Password verification failed.'
      )
    }

    setDecryptToken(data.decrypt_token)
    setShowDecryptVerification(false)
    setDecryptPassword('')
    setActivePage('decrypt')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (error) {
    setDecryptVerifyError(
      error.message || 'Unable to verify password.'
    )
  } finally {
    setDecryptVerifyLoading(false)
  }
}


useEffect(() => {
  const handleKeyboardShortcut = (event) => {
    if (
      (event.ctrlKey || event.metaKey) &&
      event.key.toLowerCase() === 'k'
    ) {
      event.preventDefault()
      searchInputRef.current?.focus()
    }

    if (event.key === 'Escape') {
      setSearchQuery('')
      searchInputRef.current?.blur()
    }
  }

  window.addEventListener(
    'keydown',
    handleKeyboardShortcut
  )

  return () => {
    window.removeEventListener(
      'keydown',
      handleKeyboardShortcut
    )
  }
}, [])

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
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Upload failed.')
      }

      setResult(data)

addRecentActivity(
  data.filename || file.name
)
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
  if (
    score === undefined ||
    score === null ||
    score === ''
  ) {
    return 'N/A';
  }

  const value = Number(score);

  if (!Number.isFinite(value)) {
    return 'N/A';
  }

  if (value <= 20) return 'Low';
  if (value <= 50) return 'Medium';
  if (value <= 75) return 'High';

  return 'Very High';
};

  const getStoredRecentFiles = () => {
  try {
    const stored = localStorage.getItem(
      'adaptiveEncryptionRecentFiles'
    )

    if (!stored) {
      return []
    }

    const parsed = JSON.parse(stored)

    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}


const [recentFiles, setRecentFiles] = useState(
  getStoredRecentFiles
)


const getFileType = (filename) => {
  const extension = filename
    ?.split('.')
    .pop()
    ?.toLowerCase()

  if (extension === 'pdf') return 'PDF'
  if (extension === 'xlsx' || extension === 'xls') return 'XLSX'
  if (extension === 'zip') return 'ZIP'
  if (
    extension === 'png' ||
    extension === 'jpg' ||
    extension === 'jpeg'
  ) {
    return 'IMG'
  }
  if (extension === 'docx') return 'DOCX'
  if (extension === 'txt') return 'TXT'

  return extension
    ? extension.toUpperCase().slice(0, 4)
    : 'FILE'
}


const formatActivityTime = (timestamp) => {
  if (!timestamp) {
    return 'Just now'
  }

  const difference =
    Date.now() - new Date(timestamp).getTime()

  const seconds = Math.max(
    0,
    Math.floor(difference / 1000)
  )

  if (seconds < 60) {
    return 'Just now'
  }

  const minutes = Math.floor(seconds / 60)

  if (minutes < 60) {
    return `${minutes} min ago`
  }

  const hours = Math.floor(minutes / 60)

  if (hours < 24) {
    return `${hours} hour${hours === 1 ? '' : 's'} ago`
  }

  const days = Math.floor(hours / 24)

  return `${days} day${days === 1 ? '' : 's'} ago`
}


const addRecentActivity = (filename) => {
  if (!filename) {
    return
  }

  const activity = {
    id: `${Date.now()}-${filename}`,
    name: filename,
    type: getFileType(filename),
    time: new Date().toISOString(),
  }

  setRecentFiles((previous) => {
    const updated = [
      activity,
      ...previous.filter(
        (item) => item.name !== filename
      ),
    ].slice(0, 10)

    localStorage.setItem(
      'adaptiveEncryptionRecentFiles',
      JSON.stringify(updated)
    )

    return updated
  })
}
  // Signup page condition

const currentPath = window.location.pathname;

if (currentPath === "/signup") {
  return <Signup />;
}

if (currentPath === "/login") {
  return <Login />;
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
    className={`nav-item ${activePage === 'home' ? 'active' : ''}`}
    onClick={() => {
      setActivePage('home')
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }}
  >
    <span className="nav-icon">🏠</span>
    <span>Home</span>
  </button>

  

 
<button
  type="button"
  className={`nav-item ${activePage === 'decrypt' ? 'active' : ''}`}
  onClick={() => {
    

    const savedUser = localStorage.getItem('user');

    if (!savedUser) {
 
  window.location.href = '/login';
  return;
}

    let user;

    try {
      user = JSON.parse(savedUser);
    } catch {
      user = null;
    }

    if (!user?.email) {
      window.location.href = '/login';
      return;
    }


openDecryptVerification();
  }}
>
  <span className="nav-icon">🔓</span>
  <span>Decrypt</span>
</button>




  
<button
  className={`nav-item ${activePage === 'history' ? 'active' : ''}`}
  onClick={() => {
    setActivePage('history')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }}
>
  <span className="nav-icon">🕘</span>
  <span>History</span>
</button>

<button
  className={`nav-item ${activePage === 'analytics' ? 'active' : ''}`}
  onClick={() => {
    setActivePage('analytics')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }}
>
  <span className="nav-icon">📊</span>
  <span>Analytics</span>
</button>


  <button
  className={`nav-item ${activePage === 'settings' ? 'active' : ''}`}
  onClick={() => {
    setActivePage('settings')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }}
>
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

        {activePage !== 'settings' && (
  <header className="topbar">

    <div className="global-search">

  <div className="search-box">

    <span className="search-icon">⌕</span>

    <input
      ref={searchInputRef}
      type="text"
      value={searchQuery}
      onChange={(event) =>
        setSearchQuery(event.target.value)
      }
      onFocus={() => {
        if (searchQuery.trim()) {
          setSearchQuery(searchQuery)
        }
      }}
      placeholder="Search files, history, or settings..."
      aria-label="Search"
    />

    <kbd>Ctrl K</kbd>

  </div>


  {searchQuery.trim() && (
    <div className="search-results">

      {filteredSearchItems.length > 0 ? (
        filteredSearchItems.map((item) => (
          <button
            type="button"
            className="search-result-item"
            key={item.title}
            onClick={() =>
              handleSearchSelect(item)
            }
          >

            <span className="search-result-icon">
              {item.title === 'Home' && '⌂'}
              {item.title === 'Encrypt' && '🔒'}
              {item.title === 'Decrypt' && '🔓'}
              {item.title === 'History' && '◷'}
              {item.title === 'Analytics' && '▥'}
              {item.title === 'Settings' && '⚙'}
              {item.title === 'Documentation' && '▣'}
              {item.title === 'Report an Issue' && '⚠'}
              {item.title === 'Contact Support' && '✉'}
            </span>


            <span className="search-result-content">

              <strong>
                {item.title}
              </strong>

              <small>
                {item.description}
              </small>

            </span>


            <span className="search-result-arrow">
              →
            </span>

          </button>
        ))
      ) : (
        <div className="search-no-results">
          <strong>No results found</strong>
          <span>
            Try searching for Home, Encrypt, Decrypt,
            History, Analytics, Settings, or Support.
          </span>
        </div>
      )}

    </div>
  )}

</div>

    <div className="topbar-actions">

      <button className="notification">
        !
      </button>

      <div className="backend-status">
        <span className="online-dot" />
        Backend Connected
      </div>

      <div className="profile">
        U
      </div>

    </div>

  </header>
)}

        {/* CONTENT */}

      {activePage === 'settings' ? (
  <Settings />
) : activePage === 'decrypt' ? (
  <DecryptPage
    decryptToken={decryptToken}
    onNavigate={(page) => setActivePage(page)}
  />
) : activePage === 'history' ? (
  <HistoryPage
    onNavigate={(page) => setActivePage(page)}
  />
) : activePage === 'analytics' ? (
  <AnalyticsPage
    onNavigate={(page) => setActivePage(page)}
  />
) : (
  <main className="content">

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

                <button
  type="button"
  onClick={() => {
    const historyButton = [
      ...document.querySelectorAll('.nav-item'),
    ].find((item) =>
      item.textContent
        ?.toLowerCase()
        .includes('history')
    )

    historyButton?.click()
  }}
>
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
                      Encrypted • {formatActivityTime(item.time)}
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

        </main>
        )}

        
{/* DECRYPT PASSWORD VERIFICATION MODAL */}

{/* DECRYPT PASSWORD VERIFICATION MODAL */}
{showDecryptVerification && (
  <div
    className="decrypt-modal-overlay"
    onClick={(event) => {
      if (event.target === event.currentTarget) {
        setShowDecryptVerification(false)
        setDecryptPassword('')
        setDecryptVerifyError('')
      }
    }}
  >
    <div
      className="decrypt-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="decrypt-modal-title"
    >
      <div className="decrypt-modal-icon">🔐</div>

      <h2 id="decrypt-modal-title">
        Verify Your Password
      </h2>

      <p>
        Re-enter your account password to access secure decryption.
      </p>

      <form onSubmit={handleDecryptVerification}>
        <label htmlFor="decrypt-password">
          Account Password
        </label>

        <input
          id="decrypt-password"
          type="password"
          value={decryptPassword}
          onChange={(event) =>
            setDecryptPassword(event.target.value)
          }
          placeholder="Enter your password"
          autoComplete="current-password"
          required
        />

        {decryptVerifyError && (
          <div className="error-message" role="alert">
            {decryptVerifyError}
          </div>
        )}

        <div className="decrypt-modal-actions">
          <button
            type="button"
            onClick={() => {
              setShowDecryptVerification(false)
              setDecryptPassword('')
              setDecryptVerifyError('')
            }}
            disabled={decryptVerifyLoading}
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={decryptVerifyLoading}
          >
            {decryptVerifyLoading
              ? 'Verifying...'
              : 'Verify & Continue'}
          </button>
        </div>
      </form>
    </div>
  </div>
)}



{/* DECRYPT PASSWORD VERIFICATION MODAL */}


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