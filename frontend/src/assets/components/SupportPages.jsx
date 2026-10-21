import { useState } from 'react'
import './SupportPages.css'

const API_URL = 'http://127.0.0.1:5000/api'

const documentationSections = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    icon: '▶',
    content: (
      <>
        <h2>Getting Started</h2>
        <p>
          Adaptive Encryption is an AI-powered security system designed to
          protect files by analyzing their content and selecting an appropriate
          encryption method.
        </p>

        <h3>Basic workflow</h3>

        <div className="documentation-flow">
          <span>Upload File</span>
          <span>→</span>
          <span>Analyze</span>
          <span>→</span>
          <span>Detect PII</span>
          <span>→</span>
          <span>Calculate Sensitivity</span>
          <span>→</span>
          <span>Select Encryption</span>
          <span>→</span>
          <span>Encrypt</span>
        </div>

        <p>
          Start from the Home page and choose the operation you want to
          perform. The system processes the selected file and displays the
          relevant result after processing.
        </p>
      </>
    ),
  },

  {
    id: 'encrypt',
    title: 'Encrypt a File',
    icon: '🔒',
    content: (
      <>
        <h2>Encrypt a File</h2>

        <p>
          Use the encryption workflow when you want to protect a file with
          adaptive encryption.
        </p>

        <h3>Steps</h3>

        <ol>
          <li>Open the Home or Encrypt workflow.</li>
          <li>Select the file you want to protect.</li>
          <li>Start the encryption process.</li>
          <li>
            The system analyzes the file and evaluates its sensitivity.
          </li>
          <li>
            The adaptive encryption system selects a suitable encryption
            algorithm.
          </li>
          <li>Review the encryption result.</li>
          <li>Download or save the encrypted output.</li>
        </ol>

        <div className="documentation-note">
          <strong>Note:</strong>
          <span>
            Keep the generated encryption key safe. A key may be required to
            decrypt the protected file later.
          </span>
        </div>
      </>
    ),
  },

  {
    id: 'decrypt',
    title: 'Decrypt a File',
    icon: '🔓',
    content: (
      <>
        <h2>Decrypt a File</h2>

        <p>
          The Decrypt workflow is used to recover the original content from an
          encrypted file.
        </p>

        <h3>Steps</h3>

        <ol>
          <li>Open the Decrypt page.</li>
          <li>Select the encrypted file.</li>
          <li>Provide the required encryption key.</li>
          <li>Start the decryption process.</li>
          <li>Wait for the decryption result.</li>
          <li>Download or access the recovered file.</li>
        </ol>

        <div className="documentation-warning">
          <strong>Important:</strong>
          <span>
            Decryption requires the correct key and compatible encrypted
            data. Keep your encryption keys secure.
          </span>
        </div>
      </>
    ),
  },

  {
    id: 'ai',
    title: 'AI Adaptive Encryption',
    icon: '◉',
    content: (
      <>
        <h2>AI Adaptive Encryption</h2>

        <p>
          The system does not simply apply one fixed encryption algorithm to
          every file. It analyzes the file and uses the resulting security
          information to determine the encryption approach.
        </p>

        <h3>Processing flow</h3>

        <div className="documentation-step-list">
          <div>
            <strong>1. Content Analysis</strong>
            <span>The uploaded file is analyzed for relevant content.</span>
          </div>

          <div>
            <strong>2. PII Detection</strong>
            <span>
              Personally identifiable information can be detected when PII
              detection is enabled.
            </span>
          </div>

          <div>
            <strong>3. Document Classification</strong>
            <span>
              The system evaluates the type and characteristics of the
              document.
            </span>
          </div>

          <div>
            <strong>4. Sensitivity Calculation</strong>
            <span>
              Security-related characteristics are used to calculate a
              sensitivity level.
            </span>
          </div>

          <div>
            <strong>5. ML Prediction</strong>
            <span>
              The machine-learning component evaluates the available features
              and predicts an encryption strategy.
            </span>
          </div>

          <div>
            <strong>6. Encryption</strong>
            <span>
              The selected encryption method is applied to protect the file.
            </span>
          </div>
        </div>

        <h3>Supported encryption methods</h3>

        <div className="documentation-algorithms">
          <div>
            <strong>AES-256-GCM</strong>
            <span>Authenticated symmetric encryption.</span>
          </div>

          <div>
            <strong>ChaCha20-Poly1305</strong>
            <span>Authenticated modern symmetric encryption.</span>
          </div>

          <div>
            <strong>Hybrid Encryption</strong>
            <span>
              Combines RSA-2048 with AES-256-GCM for key protection and data
              encryption.
            </span>
          </div>
        </div>
      </>
    ),
  },

  {
    id: 'history',
    title: 'History & Analytics',
    icon: '▤',
    content: (
      <>
        <h2>History & Analytics</h2>

        <p>
          History and Analytics help you review previous encryption and
          decryption activity.
        </p>

        <h3>History</h3>

        <ul>
          <li>Review previous operations.</li>
          <li>Check encryption and decryption activity.</li>
          <li>Review available operation details.</li>
        </ul>

        <h3>Analytics</h3>

        <ul>
          <li>Review encryption-related statistics.</li>
          <li>Inspect available algorithm usage information.</li>
          <li>Review sensitivity and confidence information when available.</li>
        </ul>
      </>
    ),
  },

  {
    id: 'settings',
    title: 'Settings',
    icon: '⚙',
    content: (
      <>
        <h2>Settings</h2>

        <p>
          The Settings page lets you configure application preferences,
          security options, AI settings, and data-storage behavior.
        </p>

        <h3>Important settings</h3>

        <ul>
          <li>
            <strong>Theme:</strong> Choose Dark, Light, or System appearance.
          </li>

          <li>
            <strong>Key Storage:</strong> Configure the selected key-storage
            option.
          </li>

          <li>
            <strong>Key Expiry:</strong> Configure the key validity period.
          </li>

          <li>
            <strong>Session Timeout:</strong> Configure automatic session
            timeout.
          </li>

          <li>
            <strong>PII Detection:</strong> Enable or disable PII detection.
          </li>

          <li>
            <strong>Sensitivity Threshold:</strong> Configure the sensitivity
            threshold used by the application.
          </li>

          <li>
            <strong>Store History:</strong> Control whether operation history
            is retained.
          </li>

          <li>
            <strong>Auto Delete Downloads:</strong> Configure downloaded-file
            cleanup behavior.
          </li>
        </ul>

        <p>
          After changing settings, use <strong>Save All Changes</strong> to
          persist the configuration.
        </p>
      </>
    ),
  },

  {
    id: 'security',
    title: 'Security & Privacy',
    icon: '🛡',
    content: (
      <>
        <h2>Security & Privacy</h2>

        <p>
          The application provides encryption and security-related controls
          intended to protect processed data.
        </p>

        <h3>Recommended practices</h3>

        <ul>
          <li>Use strong account credentials.</li>
          <li>Keep encryption keys private and secure.</li>
          <li>Do not share encryption keys unnecessarily.</li>
          <li>Review your security and storage settings regularly.</li>
          <li>Use the application only with files you are authorized to process.</li>
        </ul>

        <div className="documentation-warning">
          <strong>Important:</strong>
          <span>
            Encryption protects data only when the associated keys and
            credentials are also handled securely.
          </span>
        </div>
      </>
    ),
  },

  {
    id: 'troubleshooting',
    title: 'Troubleshooting',
    icon: '⚠',
    content: (
      <>
        <h2>Troubleshooting</h2>

        <h3>Backend is not connected</h3>
        <p>
          Make sure the Flask backend is running on
          <code> http://127.0.0.1:5000</code>.
        </p>

        <h3>File upload is not working</h3>
        <ul>
          <li>Check that the backend is running.</li>
          <li>Check that the selected file is accessible.</li>
          <li>Try refreshing the application.</li>
        </ul>

        <h3>Encryption failed</h3>
        <ul>
          <li>Check the backend console for the error.</li>
          <li>Try the operation again.</li>
          <li>Make sure the required input file is valid.</li>
        </ul>

        <h3>Decryption failed</h3>
        <ul>
          <li>Check that the correct encrypted file was selected.</li>
          <li>Check that the required key is available.</li>
          <li>Make sure the key matches the encrypted file.</li>
        </ul>

        <h3>Still having a problem?</h3>
        <p>
          Use <strong>Report an Issue</strong> from About &amp; Support to
          send the problem to the application support backend.
        </p>
      </>
    ),
  },
]


function getStoredUser() {
  try {
    const storedUser =
      localStorage.getItem('user') ||
      sessionStorage.getItem('adaptiveEncryptionUser');

    return storedUser ? JSON.parse(storedUser) : null;
  } catch (error) {
    console.error('Unable to read logged-in user:', error);
    return null;
  }
}


function getUserEmail() {
  const user = getStoredUser();

  return (
    user?.email ||
    user?.work_email ||
    user?.organization_email ||
    localStorage.getItem('adaptiveEncryptionEmail') ||
    ''
  ).trim().toLowerCase();
}

function SupportPages({ initialPage = 'documentation', onBack }) {
  const [activePage, setActivePage] = useState(initialPage)

  const [activeDocumentation, setActiveDocumentation] = useState(
    'getting-started'
  )

  const [documentationSearch, setDocumentationSearch] = useState('')

  const [issueForm, setIssueForm] = useState({
    title: '',
    description: '',
    severity: 'Medium',
    page: 'Settings',
  })

  const [contactForm, setContactForm] = useState({
    subject: '',
    message: '',
  })

  const [submitting, setSubmitting] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')


  const filteredDocumentation = documentationSections.filter(
    (section) =>
      section.title
        .toLowerCase()
        .includes(documentationSearch.trim().toLowerCase())
  )


  const currentDocumentation =
    documentationSections.find(
      (section) => section.id === activeDocumentation
    ) || documentationSections[0]


  const openPage = (page) => {
    setActivePage(page)
    setSuccessMessage('')
    setErrorMessage('')
  }


  const handleIssueSubmit = async (event) => {
    event.preventDefault()

    setSuccessMessage('')
    setErrorMessage('')

    const email = getUserEmail()

    if (!email) {
      setErrorMessage('No logged-in user email was found.')
      return
    }

    if (!issueForm.title.trim()) {
      setErrorMessage('Please enter an issue title.')
      return
    }

    if (!issueForm.description.trim()) {
      setErrorMessage('Please describe the issue.')
      return
    }

    try {
      setSubmitting(true)

      const response = await fetch(
        `${API_URL}/support/issues`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            title: issueForm.title.trim(),
            description: issueForm.description.trim(),
            severity: issueForm.severity,
            page: issueForm.page,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || 'Unable to report the issue.'
        )
      }

      setSuccessMessage(
        `Issue reported successfully. Reference ID: ${data.issue_id}`
      )

      setIssueForm({
        title: '',
        description: '',
        severity: 'Medium',
        page: 'Settings',
      })
    } catch (error) {
      setErrorMessage(
        error.message || 'Unable to report the issue.'
      )
    } finally {
      setSubmitting(false)
    }
  }


  const handleContactSubmit = async (event) => {
    event.preventDefault()

    setSuccessMessage('')
    setErrorMessage('')

    const email = getUserEmail()

    if (!email) {
      setErrorMessage('No logged-in user email was found.')
      return
    }

    if (!contactForm.subject.trim()) {
      setErrorMessage('Please enter a subject.')
      return
    }

    if (!contactForm.message.trim()) {
      setErrorMessage('Please enter your message.')
      return
    }

    try {
      setSubmitting(true)

      const response = await fetch(
        `${API_URL}/support/contact`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            subject: contactForm.subject.trim(),
            message: contactForm.message.trim(),
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || 'Unable to contact support.'
        )
      }

      setSuccessMessage(
        `Message sent successfully. Reference ID: ${data.message_id}`
      )

      setContactForm({
        subject: '',
        message: '',
      })
    } catch (error) {
      setErrorMessage(
        error.message || 'Unable to contact support.'
      )
    } finally {
      setSubmitting(false)
    }
  }


  return (
    <div className="support-pages">

      {/* Header */}
      <header className="support-pages-header">

        <button
          type="button"
          className="support-back-button"
          onClick={onBack}
        >
          ← Back to Settings
        </button>

        <div className="support-header-title">
          <div className="support-header-icon">
            {activePage === 'documentation'
              ? '▣'
              : activePage === 'issue'
                ? '⚠'
                : '✉'}
          </div>

          <div>
            <h1>
              {activePage === 'documentation'
                ? 'Documentation'
                : activePage === 'issue'
                  ? 'Report an Issue'
                  : 'Contact Support'}
            </h1>

            <p>
              {activePage === 'documentation'
                ? 'Learn how to use Adaptive Encryption.'
                : activePage === 'issue'
                  ? 'Tell us about a problem you encountered.'
                  : 'Send a message to the support team.'}
            </p>
          </div>
        </div>

      </header>


      {/* Global message */}
      {(successMessage || errorMessage) && (
        <div
          className={`support-alert ${
            successMessage
              ? 'success'
              : 'error'
          }`}
        >
          {successMessage || errorMessage}
        </div>
      )}


      {/* =====================================================
          DOCUMENTATION
      ====================================================== */}

      {activePage === 'documentation' && (
        <div className="documentation-layout">

          <aside className="documentation-sidebar">

            <div className="documentation-search">
              <span>⌕</span>

              <input
                type="text"
                value={documentationSearch}
                onChange={(event) =>
                  setDocumentationSearch(event.target.value)
                }
                placeholder="Search documentation..."
              />
            </div>


            <div className="documentation-nav">

              {filteredDocumentation.map((section) => (
                <button
                  type="button"
                  key={section.id}
                  className={
                    activeDocumentation === section.id
                      ? 'active'
                      : ''
                  }
                  onClick={() =>
                    setActiveDocumentation(section.id)
                  }
                >
                  <span>{section.icon}</span>
                  <span>{section.title}</span>
                </button>
              ))}

              {filteredDocumentation.length === 0 && (
                <div className="documentation-no-results">
                  No documentation found.
                </div>
              )}

            </div>

          </aside>


          <article className="documentation-content">

            <div className="documentation-content-header">
              <span className="documentation-badge">
                USER GUIDE
              </span>

              <h1>{currentDocumentation.title}</h1>
            </div>

            <div className="documentation-body">
              {currentDocumentation.content}
            </div>

          </article>

        </div>
      )}


      {/* =====================================================
          REPORT AN ISSUE
      ====================================================== */}

      {activePage === 'issue' && (
        <div className="support-form-page">

          <div className="support-form-card">

            <div className="support-form-intro">
              <div className="large-support-icon">
                ⚠
              </div>

              <div>
                <h2>Report a System Issue</h2>

                <p>
                  Found something that is not working correctly?
                  Describe the problem and the support team can
                  investigate it.
                </p>
              </div>
            </div>


            <form onSubmit={handleIssueSubmit}>

              <div className="support-form-grid">

                <div className="support-form-group full">
                  <label>Issue Title</label>

                  <input
                    type="text"
                    value={issueForm.title}
                    onChange={(event) =>
                      setIssueForm((previous) => ({
                        ...previous,
                        title: event.target.value,
                      }))
                    }
                    placeholder="Example: Encryption failed for PDF file"
                  />
                </div>


                <div className="support-form-group">
                  <label>Severity</label>

                  <select
                    value={issueForm.severity}
                    onChange={(event) =>
                      setIssueForm((previous) => ({
                        ...previous,
                        severity: event.target.value,
                      }))
                    }
                  >
                    <option>Low</option>
                    <option>Medium</option>
                    <option>High</option>
                    <option>Critical</option>
                  </select>
                </div>


                <div className="support-form-group">
                  <label>Current Page</label>

                  <select
                    value={issueForm.page}
                    onChange={(event) =>
                      setIssueForm((previous) => ({
                        ...previous,
                        page: event.target.value,
                      }))
                    }
                  >
                    <option>Home</option>
                    <option>Encrypt</option>
                    <option>Decrypt</option>
                    <option>History</option>
                    <option>Analytics</option>
                    <option>Settings</option>
                  </select>
                </div>


                <div className="support-form-group full">
                  <label>Description</label>

                  <textarea
                    value={issueForm.description}
                    onChange={(event) =>
                      setIssueForm((previous) => ({
                        ...previous,
                        description: event.target.value,
                      }))
                    }
                    placeholder="Explain what happened, what you expected, and any error message you saw..."
                    rows="8"
                  />
                </div>

              </div>


              <div className="support-form-actions">

                <button
                  type="button"
                  className="support-secondary-button"
                  onClick={() => openPage('documentation')}
                >
                  View Documentation
                </button>

                <button
                  type="submit"
                  className="support-primary-button"
                  disabled={submitting}
                >
                  {submitting
                    ? 'Submitting...'
                    : 'Submit Issue'}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}


      {/* =====================================================
          CONTACT SUPPORT
      ====================================================== */}

      {activePage === 'contact' && (
        <div className="support-form-page">

          <div className="support-form-card">

            <div className="support-form-intro">
              <div className="large-support-icon">
                ✉
              </div>

              <div>
                <h2>Contact Support</h2>

                <p>
                  Have a question or need assistance? Send a
                  message to the support team.
                </p>
              </div>
            </div>


            <form onSubmit={handleContactSubmit}>

              <div className="support-form-group">
                <label>Email</label>

                <input
                  type="email"
                  value={getUserEmail()}
                  disabled
                />
              </div>


              <div className="support-form-group">
                <label>Subject</label>

                <input
                  type="text"
                  value={contactForm.subject}
                  onChange={(event) =>
                    setContactForm((previous) => ({
                      ...previous,
                      subject: event.target.value,
                    }))
                  }
                  placeholder="What do you need help with?"
                />
              </div>


              <div className="support-form-group">
                <label>Message</label>

                <textarea
                  value={contactForm.message}
                  onChange={(event) =>
                    setContactForm((previous) => ({
                      ...previous,
                      message: event.target.value,
                    }))
                  }
                  placeholder="Write your message here..."
                  rows="10"
                />
              </div>


              <div className="support-form-actions">

                <button
                  type="button"
                  className="support-secondary-button"
                  onClick={() => openPage('documentation')}
                >
                  View Documentation
                </button>

                <button
                  type="submit"
                  className="support-primary-button"
                  disabled={submitting}
                >
                  {submitting
                    ? 'Sending...'
                    : 'Send Message'}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

    </div>
  )
}


export default SupportPages