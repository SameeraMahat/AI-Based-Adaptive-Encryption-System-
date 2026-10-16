import { useCallback, useEffect, useRef, useState } from 'react'
import './HistoryPage.css'

const API_URL = 'http://127.0.0.1:5000/api'

const PAGE_SIZE = 10

const LIVE_REFRESH_MS = 15000

const TABS = [
  { key: 'all', label: 'All Activity' },
  { key: 'encryption', label: 'Encrypted' },
  { key: 'decryption', label: 'Decrypted' },
]

const RANGES = [
  { key: 'all', label: 'All time' },
  { key: '24h', label: 'Last 24 hours' },
  { key: '7d', label: 'Last 7 days' },
  { key: '30d', label: 'Last 30 days' },
  { key: '90d', label: 'Last 90 days' },
]

const prefersReducedMotion = () =>
  typeof window !== 'undefined' &&
  window.matchMedia &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

const formatDate = (value) => {
  if (!value) return '—'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return '—'

  return date.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const timeAgo = (value) => {
  if (!value) return ''

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return ''

  const minutes = Math.floor((Date.now() - date.getTime()) / 60000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} min ago`

  const hours = Math.floor(minutes / 60)

  if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`

  const days = Math.floor(hours / 24)

  if (days < 30) return `${days} day${days !== 1 ? 's' : ''} ago`

  return ''
}

const formatMs = (value) => {
  if (value === null || value === undefined) return '—'

  if (value >= 1000) return `${(value / 1000).toFixed(2)} s`

  return `${Number(value).toFixed(1)} ms`
}

const formatSize = (mb) => {
  if (mb === null || mb === undefined) return null

  if (mb < 1) return `${(mb * 1024).toFixed(0)} KB`

  return `${Number(mb).toFixed(2)} MB`
}

const levelClass = (level) => {
  if (!level) return ''

  return level.toLowerCase().replace(' ', '-')
}

const LEVEL_COLORS = {
  low: '#8a8a8a',
  medium: '#d7d7d7',
  high: '#ffc357',
  'very-high': '#ff5c5c',
}

// "Today", "Yesterday" or "Mon, 12 Oct" for the group headings
const dayKey = (value) => {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return 'unknown'

  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
}

const dayLabel = (value) => {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return 'Unknown date'

  const today = new Date()
  const yesterday = new Date()

  yesterday.setDate(today.getDate() - 1)

  if (dayKey(date) === dayKey(today)) return 'Today'
  if (dayKey(date) === dayKey(yesterday)) return 'Yesterday'

  return date.toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

// ------------------------------------------------------------
// Small helpers
// ------------------------------------------------------------

/** Number that rolls from its previous value to the new one. */
function Num({ value, duration = 900 }) {
  const [shown, setShown] = useState(0)
  const previous = useRef(0)

  useEffect(() => {
    const end = Number(value) || 0

    if (prefersReducedMotion()) {
      previous.current = end
      setShown(end)
      return undefined
    }

    const start = previous.current
    const startTime = performance.now()
    let frame

    const tick = (now) => {
      const progress = Math.min(1, (now - startTime) / duration)
      const eased = 1 - Math.pow(1 - progress, 4)
      const current = start + (end - start) * eased

      previous.current = current
      setShown(current)

      if (progress < 1) frame = requestAnimationFrame(tick)
    }

    frame = requestAnimationFrame(tick)

    return () => cancelAnimationFrame(frame)
  }, [value, duration])

  return <>{Math.round(shown).toLocaleString('en-IN')}</>
}

/** Bolds the part of `text` that matches what the user searched. */
function Highlight({ text, query }) {
  if (!query || !text) return <>{text}</>

  const lower = text.toLowerCase()
  const needle = query.toLowerCase()
  const parts = []

  let cursor = 0

  while (cursor < text.length) {
    const found = lower.indexOf(needle, cursor)

    if (found === -1) {
      parts.push(text.slice(cursor))
      break
    }

    if (found > cursor) parts.push(text.slice(cursor, found))

    parts.push(
      <mark key={found}>{text.slice(found, found + needle.length)}</mark>
    )

    cursor = found + needle.length
  }

  return <>{parts}</>
}

const spotlight = (event) => {
  const rect = event.currentTarget.getBoundingClientRect()

  event.currentTarget.style.setProperty('--mx', `${event.clientX - rect.left}px`)
  event.currentTarget.style.setProperty('--my', `${event.clientY - rect.top}px`)
}

function Meter({ value, max = 100, color, label }) {
  const [grown, setGrown] = useState(false)

  useEffect(() => {
    const frame = requestAnimationFrame(() => setGrown(true))

    return () => cancelAnimationFrame(frame)
  }, [])

  const percent = Math.max(0, Math.min(100, (value / max) * 100))

  return (
    <div className="hx-meter">
      <div className="hx-meter-top">
        <span>{label}</span>
        <strong>
          {max === 100 && label === 'Sensitivity'
            ? `${value}/100`
            : `${percent.toFixed(1)}%`}
        </strong>
      </div>

      <div className="hx-meter-track">
        <i
          style={{
            width: grown ? `${percent}%` : '0%',
            background: color,
          }}
        />
      </div>
    </div>
  )
}

function Details({ item }) {
  const facts = [
    ['Algorithm', item.algorithm],
    [item.type === 'encryption' ? 'Key size' : 'Key type', item.key_info],
    ['Category', item.document_category],
    ['File size', formatSize(item.file_size_mb)],
    ['Processing time', formatMs(item.processing_time_ms)],
    ['Security check', item.security_validation],
    ['PII found', item.pii_count],
    ['Completed', formatDate(item.created_at)],
  ].filter(
    ([, value]) => value !== null && value !== undefined && value !== '—'
  )

  const level = levelClass(item.sensitivity_level)

  return (
    <div className="hx-details">
      <dl className="hx-facts">
        {facts.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{String(value)}</dd>
          </div>
        ))}
      </dl>

      {(item.sensitivity_score !== null &&
        item.sensitivity_score !== undefined) ||
      item.ml_confidence != null ? (
        <div className="hx-meters">
          {item.sensitivity_score !== null &&
            item.sensitivity_score !== undefined && (
              <Meter
                label="Sensitivity"
                value={item.sensitivity_score}
                color={LEVEL_COLORS[level] || '#8a8a8a'}
              />
            )}

          {item.ml_confidence != null && (
            <Meter
              label="AI model confidence"
              value={item.ml_confidence * 100}
              color="var(--green)"
            />
          )}

          {item.ml_algorithm && (
            <p className="hx-ai-note">
              <span>✦</span> The AI model suggested{' '}
              <strong>{item.ml_algorithm}</strong>
            </p>
          )}
        </div>
      ) : null}
    </div>
  )
}

function Skeleton() {
  return (
    <div className="hx-skeleton" aria-busy="true" aria-label="Loading history">
      {Array.from({ length: 6 }).map((_, index) => (
        <div className="hx-skel-row" key={index}>
          <i />
          <div>
            <b />
            <b />
          </div>
          <b />
          <b />
          <b />
        </div>
      ))}
    </div>
  )
}

// ------------------------------------------------------------
// Page
// ------------------------------------------------------------

function HistoryPage({ onNavigate }) {
  const [tab, setTab] = useState('all')
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [algorithm, setAlgorithm] = useState('all')
  const [status, setStatus] = useState('all')
  const [range, setRange] = useState('all')
  const [sort, setSort] = useState('newest')
  const [page, setPage] = useState(1)

  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)

  const [expanded, setExpanded] = useState(null)
  const [live, setLive] = useState(false)
  const [updatedAt, setUpdatedAt] = useState(null)

  const silentRef = useRef(false)
  const searchRef = useRef(null)

  // Wait until the user stops typing before searching.
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput.trim())
      setPage(1)
    }, 300)

    return () => clearTimeout(timer)
  }, [searchInput])

  // press "/" anywhere to jump to the search box
  useEffect(() => {
    const onKey = (event) => {
      const tag = (event.target.tagName || '').toLowerCase()

      if (
        event.key === '/' &&
        !['input', 'textarea', 'select'].includes(tag)
      ) {
        event.preventDefault()
        searchRef.current?.focus()
      }
    }

    window.addEventListener('keydown', onKey)

    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const buildParams = useCallback(
    (includePaging) => {
      const params = new URLSearchParams({
        type: tab,
        algorithm,
        status,
        range,
        sort,
      })

      if (search) params.set('search', search)

      if (includePaging) {
        params.set('page', String(page))
        params.set('page_size', String(PAGE_SIZE))
      }

      return params
    },
    [tab, algorithm, status, range, sort, search, page]
  )

  useEffect(() => {
    const controller = new AbortController()

    const load = async () => {
      const silent = silentRef.current
      silentRef.current = false

      if (!silent) setLoading(true)
      setError('')

      try {
        const response = await fetch(
          `${API_URL}/history?${buildParams(true)}`,
          { signal: controller.signal }
        )

        const json = await response.json()

        if (!response.ok || !json.success) {
          throw new Error(json.error || 'Unable to load history.')
        }

        setData(json)
        setUpdatedAt(new Date())
      } catch (err) {
        if (err.name === 'AbortError') return

        setError(
          err.message === 'Failed to fetch'
            ? 'Unable to connect to the backend. Make sure the Flask server is running.'
            : err.message
        )
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }

    load()

    return () => controller.abort()
  }, [buildParams, reloadKey])

  // optional auto-refresh
  useEffect(() => {
    if (!live) return undefined

    const timer = setInterval(() => {
      silentRef.current = true
      setReloadKey((key) => key + 1)
    }, LIVE_REFRESH_MS)

    return () => clearInterval(timer)
  }, [live])

  const changeFilter = (setter) => (event) => {
    setter(event.target.value)
    setPage(1)
    setExpanded(null)
  }

  const changeTab = (key) => {
    setTab(key)
    setPage(1)
    setExpanded(null)
  }

  const goToPage = (next) => {
    setPage(next)
    setExpanded(null)
  }

  const resetFilters = () => {
    setSearchInput('')
    setSearch('')
    setAlgorithm('all')
    setStatus('all')
    setRange('all')
    setSort('newest')
    setPage(1)
    setExpanded(null)
  }

  const hasFilters =
    search || algorithm !== 'all' || status !== 'all' || range !== 'all'

  const items = data?.items ?? []
  const counts = data?.counts ?? { all: 0, encryption: 0, decryption: 0 }
  const totalPages = data?.total_pages ?? 1

  const firstShown = data && data.total ? (data.page - 1) * PAGE_SIZE + 1 : 0
  const lastShown = data ? firstShown + items.length - (items.length ? 1 : 0) : 0

  // removable chips for whatever is filtering the list
  const chips = [
    search && {
      key: 'search',
      label: `“${search}”`,
      clear: () => {
        setSearchInput('')
        setSearch('')
        setPage(1)
      },
    },
    algorithm !== 'all' && {
      key: 'algorithm',
      label: algorithm,
      clear: () => setAlgorithm('all'),
    },
    status !== 'all' && {
      key: 'status',
      label: status === 'success' ? 'Success' : 'Failed',
      clear: () => setStatus('all'),
    },
    range !== 'all' && {
      key: 'range',
      label: RANGES.find((item) => item.key === range)?.label,
      clear: () => setRange('all'),
    },
  ].filter(Boolean)

  const encShare = counts.all ? (counts.encryption / counts.all) * 100 : 0

  const stats = [
    { label: 'Total records', value: counts.all, icon: '🗂' },
    { label: 'Encrypted', value: counts.encryption, icon: '🔒' },
    { label: 'Decrypted', value: counts.decryption, icon: '🔓' },
    {
      label: hasFilters || tab !== 'all' ? 'Matching filters' : 'Showing now',
      value: data?.total ?? 0,
      icon: '🎯',
    },
  ]

  // rows + a heading whenever the day changes
  const rows = []
  let lastDay = null

  items.forEach((item) => {
    const key = dayKey(item.created_at)

    if (key !== lastDay) {
      lastDay = key

      rows.push({
        kind: 'day',
        key: `day-${key}-${item.id}`,
        label: dayLabel(item.created_at),
        count: items.filter((other) => dayKey(other.created_at) === key)
          .length,
      })
    }

    rows.push({ kind: 'item', key: `${item.type}-${item.id}`, item })
  })

  // changes when a different set of rows arrives, so rows animate in again
  const rowsKey = `${tab}|${data?.page}|${data?.total}|${items[0]?.id}`

  let rowIndex = 0

  const toggleRow = (id) =>
    setExpanded((current) => (current === id ? null : id))

  return (
    <div className="hx-page">
      {/* HEADER */}

      <div className="hx-header">
        <div className="hx-header-main">
          <div className="hx-header-icon">🕘</div>

          <div>
            <p className="hx-eyebrow">ACTIVITY LOG</p>
            <h1>History</h1>
            <p className="hx-subtitle">
              Every file you encrypted or decrypted, with the algorithm and
              analysis behind it.
            </p>
          </div>
        </div>

        <div className="hx-header-actions">
          <button
            className={`hx-button hx-live ${live ? 'is-on' : ''}`}
            onClick={() => setLive((value) => !value)}
            title={`Refresh automatically every ${LIVE_REFRESH_MS / 1000} seconds`}
          >
            <i /> Live
          </button>

          <button
            className={`hx-button ${loading ? 'is-spinning' : ''}`}
            onClick={() => setReloadKey((key) => key + 1)}
            disabled={loading}
          >
            <span className="hx-refresh-icon">⟳</span> Refresh
          </button>

          <a
            className="hx-button hx-button-primary"
            href={`${API_URL}/history/export?${buildParams(false)}`}
          >
            ↓ Export CSV
          </a>
        </div>
      </div>

      {/* STAT TILES */}

      <div className="hx-stats">
        {stats.map((stat, index) => (
          <div
            className="hx-stat hx-reveal"
            key={stat.label}
            style={{ '--d': `${index * 70}ms` }}
            onMouseMove={spotlight}
          >
            <i>{stat.icon}</i>

            <div>
              <span>{stat.label}</span>
              <strong>
                <Num value={stat.value} />
              </strong>
            </div>
          </div>
        ))}
      </div>

      {counts.all > 0 && (
        <div
          className="hx-split hx-reveal"
          style={{ '--d': '300ms' }}
          title={`${counts.encryption} encrypted · ${counts.decryption} decrypted`}
        >
          <i style={{ width: `${encShare}%` }} />
        </div>
      )}

      {/* TABS */}

      <div className="hx-tabs">
        {TABS.map((item) => (
          <button
            key={item.key}
            className={`hx-tab ${tab === item.key ? 'active' : ''}`}
            onClick={() => changeTab(item.key)}
          >
            {item.label}
            <span>{counts[item.key] ?? 0}</span>
          </button>
        ))}
      </div>

      {/* FILTERS */}

      <div className="hx-filters">
        <div className="hx-search">
          <span>⌕</span>

          <input
            ref={searchRef}
            type="text"
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            placeholder="Search by file name, algorithm or category..."
          />

          {searchInput ? (
            <button
              className="hx-clear"
              onClick={() => setSearchInput('')}
              aria-label="Clear search"
            >
              ✕
            </button>
          ) : (
            <kbd>/</kbd>
          )}
        </div>

        <select value={algorithm} onChange={changeFilter(setAlgorithm)}>
          <option value="all">All algorithms</option>

          {(data?.algorithms ?? []).map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>

        <select value={status} onChange={changeFilter(setStatus)}>
          <option value="all">All statuses</option>
          <option value="success">Success</option>
          <option value="failed">Failed</option>
        </select>

        <select value={range} onChange={changeFilter(setRange)}>
          {RANGES.map((item) => (
            <option key={item.key} value={item.key}>
              {item.label}
            </option>
          ))}
        </select>

        <select value={sort} onChange={changeFilter(setSort)}>
          <option value="newest">Newest first</option>
          <option value="oldest">Oldest first</option>
        </select>

        {hasFilters && (
          <button className="hx-link" onClick={resetFilters}>
            Reset filters
          </button>
        )}
      </div>

      {chips.length > 0 && (
        <div className="hx-chips">
          {chips.map((chip) => (
            <button
              className="hx-chip"
              key={chip.key}
              onClick={chip.clear}
              title="Remove this filter"
            >
              {chip.label} <span>✕</span>
            </button>
          ))}
        </div>
      )}

      {updatedAt && !error && (
        <p className="hx-updated">
          Updated{' '}
          {updatedAt.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          })}
          {live && ` · refreshing every ${LIVE_REFRESH_MS / 1000}s`}
        </p>
      )}

      {/* TABLE */}

      <section className="hx-card">
        {loading && data && <div className="hx-progress" />}

        {error ? (
          <div className="hx-state hx-state-error">
            <strong>Could not load history</strong>
            <p>{error}</p>

            <button
              className="hx-button"
              onClick={() => setReloadKey((key) => key + 1)}
            >
              Try again
            </button>
          </div>
        ) : loading && !data ? (
          <Skeleton />
        ) : items.length === 0 ? (
          <div className="hx-state">
            <div className="hx-state-icon">🗂</div>

            <strong>
              {hasFilters || tab !== 'all'
                ? 'No activity matches your filters'
                : 'No activity yet'}
            </strong>

            <p>
              {hasFilters || tab !== 'all'
                ? 'Try a different search or reset the filters.'
                : 'Files you encrypt or decrypt will appear here.'}
            </p>

            {hasFilters || tab !== 'all' ? (
              <button
                className="hx-button"
                onClick={() => {
                  resetFilters()
                  setTab('all')
                }}
              >
                Reset filters
              </button>
            ) : (
              <button
                className="hx-button hx-button-primary"
                onClick={() => onNavigate?.('home')}
              >
                Encrypt a file
              </button>
            )}
          </div>
        ) : (
          <div className={`hx-table-wrap ${loading ? 'is-loading' : ''}`}>
            <table className="hx-table">
              <thead>
                <tr>
                  <th>File</th>
                  <th>Operation</th>
                  <th>Algorithm</th>
                  <th>Sensitivity</th>
                  <th>PII</th>
                  <th>Time</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>

              <tbody key={rowsKey}>
                {rows.map((row) => {
                  if (row.kind === 'day') {
                    return (
                      <tr className="hx-day" key={row.key}>
                        <td colSpan={8}>
                          <span>{row.label}</span>
                          <small>
                            {row.count} operation{row.count !== 1 ? 's' : ''}
                          </small>
                        </td>
                      </tr>
                    )
                  }

                  const { item } = row
                  const open = expanded === row.key
                  const failed = (item.status || '').toLowerCase() !== 'success'
                  const delay = `${Math.min(rowIndex++ * 45, 500)}ms`

                  return [
                    <tr
                      key={row.key}
                      className={`hx-row ${open ? 'is-open' : ''} ${
                        failed ? 'is-failed' : ''
                      }`}
                      style={{ '--d': delay }}
                      tabIndex={0}
                      aria-expanded={open}
                      onClick={() => toggleRow(row.key)}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter' || event.key === ' ') {
                          event.preventDefault()
                          toggleRow(row.key)
                        }
                      }}
                    >
                      <td>
                        <div className="hx-file">
                          <span className="hx-chevron" aria-hidden="true">
                            ›
                          </span>

                          <div className="hx-file-type">{item.file_type}</div>

                          <div className="hx-file-info">
                            <strong title={item.filename}>
                              <Highlight text={item.filename} query={search} />
                            </strong>

                            <span>
                              <Highlight
                                text={
                                  item.document_category ||
                                  item.key_info ||
                                  '—'
                                }
                                query={search}
                              />
                            </span>
                          </div>
                        </div>
                      </td>

                      <td>
                        <span className={`hx-pill ${item.type}`}>
                          {item.type === 'encryption'
                            ? '🔒 Encrypted'
                            : '🔓 Decrypted'}
                        </span>
                      </td>

                      <td className="hx-algorithm">
                        <Highlight text={item.algorithm || '—'} query={search} />
                      </td>

                      <td>
                        {item.sensitivity_level ? (
                          <div className="hx-sensitivity">
                            <span
                              className={`hx-level ${levelClass(
                                item.sensitivity_level
                              )}`}
                            >
                              {item.sensitivity_level}
                            </span>

                            <small>{item.sensitivity_score}/100</small>
                          </div>
                        ) : (
                          <span className="hx-muted">—</span>
                        )}
                      </td>

                      <td>
                        {item.pii_count === null ||
                        item.pii_count === undefined ? (
                          <span className="hx-muted">—</span>
                        ) : (
                          item.pii_count
                        )}
                      </td>

                      <td>{formatMs(item.processing_time_ms)}</td>

                      <td>
                        <span
                          className={`hx-status ${(
                            item.status || ''
                          ).toLowerCase()}`}
                        >
                          {(item.status || '').toLowerCase() === 'success'
                            ? '✓ '
                            : '✕ '}
                          {item.status}
                        </span>
                      </td>

                      <td>
                        <div className="hx-date">
                          <span>{formatDate(item.created_at)}</span>
                          <small>{timeAgo(item.created_at)}</small>
                        </div>
                      </td>
                    </tr>,

                    open && (
                      <tr className="hx-detail-row" key={`${row.key}-detail`}>
                        <td colSpan={8}>
                          <Details item={item} />
                        </td>
                      </tr>
                    ),
                  ]
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* PAGINATION */}

        {data && data.total > 0 && !error && (
          <div className="hx-pagination">
            <span>
              Showing {firstShown}–{lastShown} of {data.total}
              <em className="hx-tip"> · click a row for details</em>
            </span>

            <div>
              <button
                className="hx-button"
                onClick={() => goToPage(Math.max(1, page - 1))}
                disabled={page <= 1 || loading}
              >
                ← Previous
              </button>

              <div className="hx-pages">
                {pageWindow(data.page, totalPages).map((entry, index) =>
                  entry === '…' ? (
                    <span className="hx-dots" key={`dots-${index}`}>
                      …
                    </span>
                  ) : (
                    <button
                      key={entry}
                      className={entry === data.page ? 'active' : ''}
                      onClick={() => goToPage(entry)}
                      disabled={loading}
                    >
                      {entry}
                    </button>
                  )
                )}
              </div>

              <button
                className="hx-button"
                onClick={() => goToPage(Math.min(totalPages, page + 1))}
                disabled={page >= totalPages || loading}
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}

// 1 … 4 5 [6] 7 8 … 20
function pageWindow(current, total) {
  if (total <= 7) {
    return Array.from({ length: total }, (_, index) => index + 1)
  }

  const pages = new Set([1, total, current, current - 1, current + 1])

  if (current <= 3) [2, 3, 4].forEach((value) => pages.add(value))
  if (current >= total - 2) {
    ;[total - 1, total - 2, total - 3].forEach((value) => pages.add(value))
  }

  const sorted = [...pages]
    .filter((value) => value >= 1 && value <= total)
    .sort((a, b) => a - b)

  const result = []

  sorted.forEach((value, index) => {
    if (index > 0 && value - sorted[index - 1] > 1) result.push('…')

    result.push(value)
  })

  return result
}

export default HistoryPage
