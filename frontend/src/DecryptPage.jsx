import { useEffect, useRef, useState } from 'react'
import './DecryptPage.css'

const API_URL = 'http://127.0.0.1:5000/api'

function DecryptPage({ onNavigate }) {
  const [encryptedFile, setEncryptedFile] = useState(null)
  const [keyFile, setKeyFile] = useState(null)

  const [keySource, setKeySource] = useState('stored')

  const [metadata, setMetadata] = useState(null)
  const [metadataLoading, setMetadataLoading] = useState(false)

  const [decrypting, setDecrypting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(null)

  const [recentActivity, setRecentActivity] = useState([])

  const fileInputRef = useRef(null)
  const keyInputRef = useRef(null)


  // ============================================================
  // FORMAT HELPERS
  // ============================================================

  const formatBytes = (bytes) => {
    if (
      bytes === undefined ||
      bytes === null ||
      Number.isNaN(bytes)
    ) {
      return 'N/A'
    }

    if (bytes === 0) {
      return '0 Bytes'
    }

    const units = [
      'Bytes',
      'KB',
      'MB',
      'GB',
    ]

    const index = Math.floor(
      Math.log(bytes) / Math.log(1024)
    )

    const safeIndex = Math.min(
      index,
      units.length - 1
    )

    return `${(
      bytes / Math.pow(1024, safeIndex)
    ).toFixed(2)} ${units[safeIndex]}`
  }


  const getFileType = (filename) => {
    if (!filename) {
      return 'N/A'
    }

    const cleanFilename = filename
      .toLowerCase()
      .endsWith('.enc')
      ? filename.slice(0, -4)
      : filename

    const extension = cleanFilename
      .split('.')
      .pop()
      ?.toUpperCase()

    if (!extension) {
      return 'N/A'
    }

    return extension
  }


  const formatActivityTime = (dateValue) => {
    if (!dateValue) {
      return ''
    }

    const date = new Date(dateValue)

    if (Number.isNaN(date.getTime())) {
      return ''
    }

    const difference =
      Date.now() - date.getTime()

    const minutes = Math.floor(
      difference / 60000
    )

    if (minutes < 1) {
      return 'Just now'
    }

    if (minutes < 60) {
      return `${minutes} min ago`
    }

    const hours = Math.floor(
      minutes / 60
    )

    if (hours < 24) {
      return `${hours} hour${hours !== 1 ? 's' : ''} ago`
    }

    const days = Math.floor(
      hours / 24
    )

    return `${days} day${days !== 1 ? 's' : ''} ago`
  }


  // ============================================================
  // LOAD DECRYPTION HISTORY
  // ============================================================

  const loadRecentActivity = async () => {
    try {
      const response = await fetch(
        `${API_URL}/decrypt/history`
      )

      const data = await response.json()

      if (!response.ok || !data.success) {
        return
      }

      setRecentActivity(
        Array.isArray(data.history)
          ? data.history.slice(0, 5)
          : []
      )

    } catch {
      // History is supplementary.
      // Do not block the decryption page.
    }
  }


  // ============================================================
  // INITIAL LOAD
  // ============================================================

  useEffect(() => {
    loadRecentActivity()
  }, [])


  // ============================================================
  // FETCH ACTUAL ENCRYPTION METADATA
  // ============================================================

  const fetchMetadata = async (file) => {
    if (!file) {
      return
    }

    setMetadata(null)
    setMetadataLoading(true)

    try {
      const response = await fetch(
        `${API_URL}/dashboard/encryption/${encodeURIComponent(
          file.name.slice(0, -4)
        )}`
      )

      const data = await response.json()

      if (!response.ok || !data.success) {
        setMetadata(null)

        setError(
          data.error ||
          'Encryption metadata not found for this file.'
        )

        return
      }

      setMetadata(data.metadata)
      setError('')

    } catch {
      setMetadata(null)

      setError(
        'Unable to retrieve encryption metadata from the backend.'
      )

    } finally {
      setMetadataLoading(false)
    }
  }


  // ============================================================
  // RESET KEY FILE
  // ============================================================

  const resetKeyFile = () => {
    setKeyFile(null)

    if (keyInputRef.current) {
      keyInputRef.current.value = ''
    }
  }


  // ============================================================
  // FILE SELECTION
  // ============================================================

  const processEncryptedFile = async (selectedFile) => {
    setError('')
    setSuccess(null)
    setMetadata(null)

    if (!selectedFile) {
      setEncryptedFile(null)
      return
    }

    if (
      !selectedFile.name
        .toLowerCase()
        .endsWith('.enc')
    ) {
      setEncryptedFile(null)

      setError(
        'Unsupported encrypted file.'
      )

      return
    }

    setEncryptedFile(selectedFile)

    // A new encrypted file means the previous uploaded
    // key may no longer correspond to it.
    resetKeyFile()

    // Stored key is the default and is server-managed.
    setKeySource('stored')

    await fetchMetadata(selectedFile)
  }


  const handleEncryptedFileChange = async (
    event
  ) => {
    const selectedFile =
      event.target.files?.[0]

    await processEncryptedFile(
      selectedFile
    )
  }


  // ============================================================
  // KEY FILE SELECTION
  // ============================================================

  const handleKeyFileChange = (event) => {
    const selectedKey =
      event.target.files?.[0]

    setError('')
    setSuccess(null)

    if (!selectedKey) {
      setKeyFile(null)
      return
    }

    setKeyFile(selectedKey)
  }


  // ============================================================
  // DROP HANDLER
  // ============================================================

  const handleDrop = async (event) => {
    event.preventDefault()

    const droppedFile =
      event.dataTransfer.files?.[0]

    if (!droppedFile) {
      return
    }

    await processEncryptedFile(
      droppedFile
    )
  }


  const handleDragOver = (event) => {
    event.preventDefault()
  }


  // ============================================================
  // CLEAR ENCRYPTED FILE
  // ============================================================

  const clearEncryptedFile = () => {
    setEncryptedFile(null)
    setMetadata(null)
    setSuccess(null)
    setError('')

    resetKeyFile()

    setKeySource('stored')

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }


  // ============================================================
  // CLEAR KEY FILE
  // ============================================================

  const clearKeyFile = () => {
    resetKeyFile()

    setSuccess(null)
    setError('')
  }


  // ============================================================
  // SELECT STORED KEY
  // ============================================================

  const selectStoredKey = () => {
    setKeySource('stored')

    resetKeyFile()

    setError('')
    setSuccess(null)
  }


  // ============================================================
  // SELECT UPLOAD KEY
  // ============================================================

  const selectUploadKey = () => {
    setKeySource('upload')

    setError('')
    setSuccess(null)
  }


  // ============================================================
  // DECRYPT FILE
  // ============================================================

  const handleDecrypt = async () => {
    setError('')
    setSuccess(null)

    // ----------------------------------------------------------
    // Encrypted file validation
    // ----------------------------------------------------------

    if (!encryptedFile) {
      setError(
        'Please select an encrypted file.'
      )

      return
    }


    // ----------------------------------------------------------
    // Uploaded key validation
    // ----------------------------------------------------------

    if (
      keySource === 'upload' &&
      !keyFile
    ) {
      setError(
        'Please provide the required decryption key.'
      )

      return
    }


    setDecrypting(true)


    const formData = new FormData()

    // ----------------------------------------------------------
    // Always send encrypted file
    // ----------------------------------------------------------

    formData.append(
      'file',
      encryptedFile
    )


    // ----------------------------------------------------------
    // Tell backend where the key should come from
    // ----------------------------------------------------------

    formData.append(
      'key_source',
      keySource
    )


    // ----------------------------------------------------------
    // Upload-key mode
    // ----------------------------------------------------------

    if (
      keySource === 'upload' &&
      keyFile
    ) {
      formData.append(
        'key',
        keyFile
      )
    }


    try {

      const response = await fetch(
        `${API_URL}/decrypt`,
        {
          method: 'POST',
          body: formData,
        }
      )


      // ========================================================
      // ERROR RESPONSE
      // ========================================================

      if (!response.ok) {

        let backendMessage =
          'Decryption failed.'

        try {

          const data =
            await response.json()

          if (data?.error) {
            backendMessage =
              data.error
          }

        } catch {
          // Response was not JSON.
        }

        setError(
          backendMessage
        )

        return
      }


      // ========================================================
      // SUCCESS RESPONSE
      // ========================================================

      const decryptedBlob =
        await response.blob()


      if (
        !decryptedBlob ||
        decryptedBlob.size === 0
      ) {
        setError(
          'Decryption failed. The decrypted file is empty.'
        )

        return
      }


      // ========================================================
      // READ ACTUAL BACKEND HEADERS
      // ========================================================

      const algorithm =
        response.headers.get(
          'X-Decryption-Algorithm'
        ) ||
        metadata?.encryption_algorithm ||
        'Not available'


      const originalFilename =
        response.headers.get(
          'X-Original-Filename'
        ) ||
        (
          encryptedFile.name
            .toLowerCase()
            .endsWith('.enc')
            ? encryptedFile.name.slice(
                0,
                -4
              )
            : encryptedFile.name
        )


      // ========================================================
      // CREATE DOWNLOAD
      // ========================================================

      const blobUrl =
        window.URL.createObjectURL(
          decryptedBlob
        )


      const downloadLink =
        document.createElement('a')


      downloadLink.href =
        blobUrl


      downloadLink.download =
        originalFilename


      document.body.appendChild(
        downloadLink
      )


      downloadLink.click()

      downloadLink.remove()


      // Release the browser object URL
      // after initiating the download.

      window.setTimeout(() => {
        window.URL.revokeObjectURL(
          blobUrl
        )
      }, 1000)


      // ========================================================
      // SUCCESS UI
      // ========================================================

      setSuccess({
        filename:
          originalFilename,

        algorithm:
          algorithm,

        status:
          'Successfully decrypted',
      })


      // ========================================================
      // REFRESH DECRYPTION ACTIVITY
      // ========================================================

      await loadRecentActivity()

    } catch (err) {

      setError(
        err?.message ||
        'Unable to connect to the decryption backend.'
      )

    } finally {

      setDecrypting(false)
    }
  }


  // ============================================================
  // DECRYPT BUTTON STATE
  // ============================================================

  const canDecrypt =
    Boolean(encryptedFile) &&
    (
      keySource === 'stored' ||
      Boolean(keyFile)
    ) &&
    !metadataLoading &&
    !decrypting


  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="decrypt-page">

      {/* ======================================================
          HEADER
          ====================================================== */}

      <section className="decrypt-header">

        <div className="decrypt-header-icon">
          🔓
        </div>

        <div>
          <p className="decrypt-eyebrow">
            SECURE FILE RECOVERY
          </p>

          <h1>
            Decrypt Your File
          </h1>

          <p>
            Recover your original file securely
            using the required encryption key.
          </p>
        </div>

      </section>


      {/* ======================================================
          MAIN GRID
          ====================================================== */}

      <div className="decrypt-layout">

        <div className="decrypt-main">

          {/* ==================================================
              ENCRYPTED FILE
              ================================================== */}

          <section className="decrypt-card">

            <div className="decrypt-card-heading">

              <div className="section-icon">
                🔓
              </div>

              <div>
                <h2>
                  Encrypted File
                </h2>

                <p>
                  Select the encrypted file you want to recover.
                </p>
              </div>

            </div>


            <div
              className={`decrypt-drop-zone ${
                encryptedFile
                  ? 'has-file'
                  : ''
              }`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={() =>
                fileInputRef.current?.click()
              }
            >

              <input
                ref={fileInputRef}
                type="file"
                accept=".enc"
                onChange={
                  handleEncryptedFileChange
                }
                hidden
              />


              {!encryptedFile ? (
                <>
                  <div className="drop-icon">
                    🔓
                  </div>

                  <strong>
                    Drop encrypted file here
                  </strong>

                  <span>
                    or click to browse
                  </span>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={(event) => {
                      event.stopPropagation()

                      fileInputRef.current?.click()
                    }}
                  >
                    Choose Encrypted File
                  </button>
                </>
              ) : (
                <div className="selected-encrypted-file">

                  <div className="selected-file-icon">
                    ENC
                  </div>

                  <div className="selected-file-info">

                    <strong>
                      {encryptedFile.name}
                    </strong>

                    <span>
                      {formatBytes(
                        encryptedFile.size
                      )}{' '}
                      •{' '}
                      {getFileType(
                        encryptedFile.name
                      )}
                    </span>

                    <small>
                      ✓ Ready for decryption
                    </small>

                  </div>

                  <button
                    type="button"
                    className="remove-file-button"
                    onClick={(event) => {
                      event.stopPropagation()
                      clearEncryptedFile()
                    }}
                    aria-label="Remove encrypted file"
                  >
                    ×
                  </button>

                </div>
              )}

            </div>

          </section>


          {/* ==================================================
              ENCRYPTION DETAILS
              ================================================== */}

          {encryptedFile && (
            <section className="decrypt-card">

              <div className="decrypt-card-heading">

                <div className="section-icon">
                  🛡️
                </div>

                <div>
                  <h2>
                    Encryption Details
                  </h2>

                  <p>
                    Metadata retrieved from the encryption backend.
                  </p>
                </div>

              </div>


              {metadataLoading ? (

                <div className="metadata-loading">
                  Loading actual encryption metadata...
                </div>

              ) : metadata ? (

                <div className="metadata-grid">

                  <div className="metadata-item">

                    <span>
                      ALGORITHM
                    </span>

                    <strong>
                      {metadata.encryption_algorithm ||
                        'Not available'}
                    </strong>

                  </div>


                  <div className="metadata-item">

                    <span>
                      FILE TYPE
                    </span>

                    <strong>
                      {metadata.file_type ||
                        getFileType(
                          encryptedFile.name
                        )}
                    </strong>

                  </div>


                  <div className="metadata-item">

                    <span>
                      ENCRYPTED SIZE
                    </span>

                    <strong>
                      {formatBytes(
                        encryptedFile.size
                      )}
                    </strong>

                  </div>

                </div>

              ) : (

                <div className="metadata-unavailable">

                  <span>
                    !
                  </span>

                  <div>

                    <strong>
                      Encryption metadata unavailable
                    </strong>

                    <p>
                      The selected encrypted file was not
                      found in the encryption history.
                    </p>

                  </div>

                </div>
              )}

            </section>
          )}


          {/* ==================================================
              DECRYPTION KEY
              ================================================== */}

          <section className="decrypt-card">

            <div className="decrypt-card-heading">

              <div className="section-icon">
                🔑
              </div>

              <div>
                <h2>
                  Decryption Key
                </h2>

                <p>
                  Provide the key required to recover the original file.
                </p>
              </div>

            </div>


            <div className="key-options">

              {/* ==================================================
                  STORED KEY
                  ================================================== */}

              <label
                className={`key-option ${
                  keySource === 'stored'
                    ? 'selected'
                    : ''
                }`}
              >

                <input
                  type="radio"
                  name="key-source"
                  value="stored"
                  checked={
                    keySource === 'stored'
                  }
                  onChange={
                    selectStoredKey
                  }
                />

                <span className="radio-circle" />

                <span className="key-option-copy">

                  <strong>
                    Use stored key
                  </strong>

                  <small>
                    Use the key managed securely by the backend.
                  </small>

                </span>

              </label>


              {/* ==================================================
                  UPLOAD KEY
                  ================================================== */}

              <label
                className={`key-option ${
                  keySource === 'upload'
                    ? 'selected'
                    : ''
                }`}
              >

                <input
                  type="radio"
                  name="key-source"
                  value="upload"
                  checked={
                    keySource === 'upload'
                  }
                  onChange={
                    selectUploadKey
                  }
                />

                <span className="radio-circle" />

                <span className="key-option-copy">

                  <strong>
                    Upload key file
                  </strong>

                  <small>
                    Select the corresponding key file.
                  </small>

                </span>

              </label>

            </div>


            {/* ==================================================
                UPLOAD KEY AREA
                ================================================== */}

            {keySource === 'upload' && (

              <div className="key-upload">

                <input
                  ref={keyInputRef}
                  type="file"
                  onChange={
                    handleKeyFileChange
                  }
                  hidden
                />

                <button
                  type="button"
                  className="key-select-button"
                  onClick={() =>
                    keyInputRef.current?.click()
                  }
                >
                  🔑 Select / Enter Key
                </button>


                {keyFile && (

                  <div className="key-selected">

                    <span className="key-file-symbol">
                      🔐
                    </span>

                    <div>

                      <strong>
                        {keyFile.name}
                      </strong>

                      <small>
                        Key file selected securely
                      </small>

                    </div>

                    <button
                      type="button"
                      onClick={
                        clearKeyFile
                      }
                      aria-label="Remove key file"
                    >
                      ×
                    </button>

                  </div>
                )}

              </div>
            )}


            {/* ==================================================
                STORED KEY NOTICE
                ================================================== */}

            {keySource === 'stored' && (

              <div className="stored-key-notice">

                <span>
                  🔐
                </span>

                <div>

                  <strong>
                    Backend-managed key
                  </strong>

                  <p>
                    The correct decryption key remains on
                    the server and is never exposed in the browser.
                  </p>

                </div>

              </div>
            )}

          </section>


          {/* ==================================================
              ERROR
              ================================================== */}

          {error && (

            <div className="decrypt-error">

              <span className="error-icon">
                !
              </span>

              <div>

                <strong>
                  Decryption failed
                </strong>

                <p>
                  {error}
                </p>

              </div>

            </div>
          )}


          {/* ==================================================
              PROCESSING
              ================================================== */}

          {decrypting && (

            <div className="decrypt-processing">

              <div className="processing-spinner" />

              <div>

                <strong>
                  Decrypting...
                </strong>

                <p>
                  Please wait while the file is being processed.
                </p>

              </div>

            </div>
          )}


          {/* ==================================================
              DECRYPT BUTTON
              ================================================== */}

          <button
            type="button"
            className="decrypt-button"
            disabled={!canDecrypt}
            onClick={handleDecrypt}
          >

            🔓{' '}

            {decrypting
              ? 'Decrypting...'
              : 'Decrypt File'}

          </button>


          {/* ==================================================
              SUCCESS RESULT
              ================================================== */}

          {success && (

            <section className="decrypt-success">

              <div className="success-check">
                ✓
              </div>

              <div className="success-content">

                <p className="success-eyebrow">
                  DECRYPTION COMPLETE
                </p>

                <h2>
                  Decryption Successful
                </h2>

                <div className="success-details">

                  <div>

                    <span>
                      ORIGINAL FILE
                    </span>

                    <strong>
                      {success.filename}
                    </strong>

                  </div>


                  <div>

                    <span>
                      ALGORITHM
                    </span>

                    <strong>
                      {success.algorithm}
                    </strong>

                  </div>


                  <div>

                    <span>
                      STATUS
                    </span>

                    <strong>
                      {success.status}
                    </strong>

                  </div>

                </div>

                <p className="download-note">
                  Your decrypted file has been downloaded.
                </p>

              </div>

            </section>
          )}

        </div>


        {/* ====================================================
            RIGHT SIDE — RECENT ACTIVITY
            ==================================================== */}

        <aside className="decrypt-activity-card">

          <div className="decrypt-activity-header">

            <div>

              <p>
                RECENT ACTIVITY
              </p>

              <h2>
                Recent Decryption Activity
              </h2>

            </div>

            <button
              type="button"
              onClick={() =>
                onNavigate?.('history')
              }
            >
              View All
            </button>

          </div>


          <div className="decrypt-activity-list">

            {recentActivity.length > 0 ? (

              recentActivity.map(
                (item, index) => (

                  <div
                    className="decrypt-activity-item"
                    key={
                      item.id ||
                      `${item.filename}-${index}`
                    }
                  >

                    <div className="activity-file-icon">
                      {getFileType(
                        item.filename
                      )}
                    </div>

                    <div className="decrypt-activity-info">

                      <strong>
                        {item.filename}
                      </strong>

                      <span>
                        Decrypted •{' '}
                        {formatActivityTime(
                          item.created_at
                        )}
                      </span>

                    </div>

                    <div className="activity-success">
                      ✓
                    </div>

                  </div>

                )
              )

            ) : (

              <div className="empty-activity">

                <span>
                  🔓
                </span>

                <p>
                  No decryption activity yet.
                </p>

              </div>
            )}

          </div>


          <button
            type="button"
            className="activity-view-all"
            onClick={() =>
              onNavigate?.('history')
            }
          >

            View All Decryption History

            <span>
              →
            </span>

          </button>

        </aside>

      </div>

    </div>
  )
}

export default DecryptPage