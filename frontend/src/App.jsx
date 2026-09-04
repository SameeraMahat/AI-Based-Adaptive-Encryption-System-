import { useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:5000/api'

function App() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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

    if (value.includes('very')) {
      return 'very-high'
    }

    if (value.includes('high')) {
      return 'high'
    }

    if (value.includes('medium')) {
      return 'medium'
    }

    return 'standard'
  }

  const getPiiCount = () => {
    if (!result?.pii) return 0

    return Object.values(result.pii).reduce(
      (total, value) => {
        if (Array.isArray(value)) {
          return total + value.length
        }

        if (typeof value === 'number') {
          return total + value
        }

        return total
      },
      0
    )
  }

  const formatBytes = (bytes) => {
    if (bytes === undefined || bytes === null || bytes === 0) {
      return '0 Bytes'
    }

    const units = [
      'Bytes',
      'KB',
      'MB',
      'GB'
    ]

    const index = Math.floor(
      Math.log(bytes) / Math.log(1024)
    )

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

    if (score >= 75) {
      return 'Very High'
    }

    if (score >= 50) {
      return 'High'
    }

    if (score >= 25) {
      return 'Medium'
    }

    return 'Low'
  }

  return (
    <div className="app">

      {/* HEADER */}

      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            🔐
          </div>

          <div>
            <h1>
              Adaptive Encryption
            </h1>

            <span>
              AI-Powered Security System
            </span>
          </div>

        </div>

        <div className="status">

          <span className="status-dot"></span>

          Backend Connected

        </div>

      </header>


      {/* MAIN */}

      <main className="main">

        {/* HERO */}

        <section className="hero-section">

          <div>

            <p className="eyebrow">
              INTELLIGENT FILE PROTECTION
            </p>

            <h2>
              Upload. Analyze.
              <br />
              <span>Encrypt Adaptively.</span>
            </h2>

            <p className="hero-text">
              Our AI-driven encryption engine analyzes
              your file and automatically selects the
              most suitable encryption strategy based
              on sensitivity, file characteristics and
              detected information.
            </p>

          </div>

        </section>


        {/* UPLOAD CARD */}

        <section className="upload-card">

          <div className="section-title">

            <div className="section-icon">
              ↑
            </div>

            <div>

              <h3>
                Upload & Analysis
              </h3>

              <p>
                Select a file to begin adaptive security analysis.
              </p>

            </div>

          </div>


          <label className="drop-zone">

            <input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
            />

            <div className="upload-icon">
              ↑
            </div>

            {file ? (
              <>
                <strong>
                  {file.name}
                </strong>

                <span>
                  {formatBytes(file.size)}
                </span>
              </>
            ) : (
              <>
                <strong>
                  Choose a file to encrypt
                </strong>

                <span>
                  PDF, DOCX, TXT, PNG, JPG or JPEG
                </span>
              </>
            )}

          </label>


          {file && (
            <div className="selected-file">

              <div>

                <span className="file-label">
                  Selected file
                </span>

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

              <strong>
                Error:
              </strong>{' '}

              {error}

            </div>
          )}

        </section>


        {/* RESULTS */}

        {result && (
          <section className="results-section">

            {/* RESULTS HEADER */}

            <div className="results-header">

              <div>

                <p className="eyebrow">
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


            {/* ANALYSIS CARDS */}

            <div className="result-grid">

              {/* FILE */}

              <div className="result-card">

                <span className="card-label">
                  FILE
                </span>

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


              {/* CLASSIFICATION */}

              <div className="result-card">

                <span className="card-label">
                  CLASSIFICATION
                </span>

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


              {/* PII */}

              <div className="result-card">

                <span className="card-label">
                  PII DETECTED
                </span>

                <h3>
                  {result.sensitivity?.pii_count ??
                    getPiiCount()}
                </h3>

                <p>
                  Sensitive information detected
                </p>

              </div>


              {/* SENSITIVITY */}

              <div className="result-card">

                <span className="card-label">
                  SENSITIVITY
                </span>

                <h3>
                  {getSensitivityLevel(
                    result.sensitivity?.sensitivity_score
                  )}
                </h3>

                <p>
                  Score:{' '}
                  {result.sensitivity?.sensitivity_score ?? 'N/A'}
                  /100
                </p>

              </div>

            </div>


            {/* AI DECISION */}

            <div className="policy-card">

              <div className="policy-heading">

                <div className="policy-icon">
                  AI
                </div>

                <div>

                  <span className="card-label">
                    ADAPTIVE POLICY
                  </span>

                  <h3>
                    Recommended Encryption
                  </h3>

                </div>

              </div>


              <div className="algorithm">

                <div>

                  <span className="small-label">
                    ALGORITHM
                  </span>

                  <strong>
                    {result.encryption?.algorithm ||
                      'Not available'}
                  </strong>

                </div>


                <div>

                  <span className="small-label">
                    SECURITY LEVEL
                  </span>

                  <div
                    className={`security-badge ${getSecurityClass(
                      result.encryption?.security_level
                    )}`}
                  >
                    {result.encryption?.security_level ||
                      'Standard'}
                  </div>

                </div>

              </div>


              {/* ML CONFIDENCE */}

              <div className="ml-confidence">

                <div>

                  <span className="small-label">
                    AI MODEL PREDICTION
                  </span>

                  <strong>
                    {result.ml_prediction?.algorithm ||
                      'N/A'}
                  </strong>

                </div>

                <div>

                  <span className="small-label">
                    MODEL CONFIDENCE
                  </span>

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


            {/* SENSITIVITY + ENCRYPTION STATUS */}

            <div className="details-grid">

              {/* SENSITIVITY */}

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


              {/* ENCRYPTION STATUS */}

              <div className="details-card">

                <h3>
                  Encryption Status
                </h3>

                <div className="encryption-status">

                  <div className="check-circle">
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

              <div className="performance-heading">

                <div>

                  <span className="card-label">
                    PERFORMANCE ANALYSIS
                  </span>

                  <h3>
                    Encryption Performance
                  </h3>

                </div>

                <div className="performance-icon">
                  ⚡
                </div>

              </div>


              <div className="performance-grid">

                <div className="performance-item">

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


                <div className="performance-item">

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


                <div className="performance-item">

                  <span>
                    Encryption Time
                  </span>

                  <strong>
                    {result.performance
                      ?.encryption_time_ms ?? 'N/A'} ms
                  </strong>

                </div>


                <div className="performance-item">

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


            {/* ML PROBABILITIES */}

            {result.ml_prediction?.probabilities && (
              <div className="probability-card">

                <div>

                  <span className="card-label">
                    AI DECISION ANALYSIS
                  </span>

                  <h3>
                    Model Prediction Probabilities
                  </h3>

                </div>


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
                            width: `${probability * 100}%`
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


            {/* FAKE HISTORY */}

            <div className="history-card">

              <div className="history-heading">

                <div>

                  <span className="card-label">
                    ENCRYPTION HISTORY
                  </span>

                  <h3>
                    Recent Encryption Activity
                  </h3>

                </div>

                <span className="demo-badge">
                  DEMO
                </span>

              </div>


              <div className="history-table">

                <div className="history-row history-header">

                  <span>
                    File
                  </span>

                  <span>
                    Algorithm
                  </span>

                  <span>
                    Security
                  </span>

                </div>


                <div className="history-row">

                  <span>
                    test_frontend.txt
                  </span>

                  <span>
                    AES-256-GCM
                  </span>

                  <span className="history-security high-text">
                    High
                  </span>

                </div>


                <div className="history-row">

                  <span>
                    grocery.txt
                  </span>

                  <span>
                    ChaCha20
                  </span>

                  <span className="history-security standard-text">
                    Standard
                  </span>

                </div>


                <div className="history-row">

                  <span>
                    large_hr.txt
                  </span>

                  <span>
                    Hybrid
                  </span>

                  <span className="history-security very-high-text">
                    Very High
                  </span>

                </div>

              </div>

              <p className="history-note">
                History shown here is currently a static demonstration.
                Database-backed encryption history will be implemented later.
              </p>

            </div>

          </section>
        )}

      </main>


      {/* FOOTER */}

      <footer>

        <span>
          AI-Based Adaptive Encryption System
        </span>

        <span>
          Intelligent security • Automated policy selection
        </span>

      </footer>

    </div>
  )
}

export default App