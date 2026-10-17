import { useEffect, useMemo, useRef, useState } from 'react'
import './AnalyticsPage.css'

const API_URL = 'http://127.0.0.1:5000/api'

const LIVE_REFRESH_MS = 15000

const RANGES = [
  { key: '7d', label: '7 days' },
  { key: '30d', label: '30 days' },
  { key: '90d', label: '90 days' },
  { key: 'all', label: 'All time' },
]

const DONUT_COLORS = ['#35e890', '#f5f5f5', '#8a8a8a', '#4f4f4f', '#2b9e66']

const LEVEL_COLORS = {
  Low: '#8a8a8a',
  Medium: '#d7d7d7',
  High: '#ffc357',
  'Very High': '#ff5c5c',
}

const prefersReducedMotion = () =>
  typeof window !== 'undefined' &&
  window.matchMedia &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

const formatMs = (value) => {
  if (!value) return '0 ms'

  if (value >= 1000) return `${(value / 1000).toFixed(2)} s`

  return `${value.toFixed(1)} ms`
}

const formatDay = (isoDate) => {
  const [year, month, day] = isoDate.split('-').map(Number)

  return new Date(year, month - 1, day).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
  })
}

const formatDayLong = (isoDate) => {
  const [year, month, day] = isoDate.split('-').map(Number)

  return new Date(year, month - 1, day).toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  })
}

// ------------------------------------------------------------
// Small hooks
// ------------------------------------------------------------

/**
 * Counts from the previous value to `target` (so numbers "roll"
 * when the range changes instead of jumping).
 */
function useCountUp(target, duration = 1000) {
  const [value, setValue] = useState(0)
  const previous = useRef(0)

  useEffect(() => {
    const end = Number(target) || 0

    if (prefersReducedMotion()) {
      previous.current = end
      setValue(end)
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
      setValue(current)

      if (progress < 1) frame = requestAnimationFrame(tick)
    }

    frame = requestAnimationFrame(tick)

    return () => cancelAnimationFrame(frame)
  }, [target, duration])

  return value
}

/**
 * false for one frame, then true: lets CSS transitions play
 * (bars growing, donut drawing) every time `trigger` changes.
 */
function useGrown(trigger) {
  const [grown, setGrown] = useState(false)

  useEffect(() => {
    setGrown(false)

    const frame = requestAnimationFrame(() =>
      requestAnimationFrame(() => setGrown(true))
    )

    return () => cancelAnimationFrame(frame)
  }, [trigger])

  return grown
}

// soft light that follows the mouse across a card
const spotlight = (event) => {
  const rect = event.currentTarget.getBoundingClientRect()

  event.currentTarget.style.setProperty('--mx', `${event.clientX - rect.left}px`)
  event.currentTarget.style.setProperty('--my', `${event.clientY - rect.top}px`)
}

// ------------------------------------------------------------
// Small chart components (no chart library needed)
// ------------------------------------------------------------

function smoothPath(points) {
  if (points.length < 2) return ''

  let path = `M ${points[0][0]} ${points[0][1]}`

  for (let i = 0; i < points.length - 1; i += 1) {
    const p0 = points[i - 1] || points[i]
    const p1 = points[i]
    const p2 = points[i + 1]
    const p3 = points[i + 2] || p2

    const c1x = p1[0] + (p2[0] - p0[0]) / 6
    const c1y = p1[1] + (p2[1] - p0[1]) / 6
    const c2x = p2[0] - (p3[0] - p1[0]) / 6
    const c2y = p2[1] - (p3[1] - p1[1]) / 6

    path += ` C ${c1x} ${c1y}, ${c2x} ${c2y}, ${p2[0]} ${p2[1]}`
  }

  return path
}

function Sparkline({ values }) {
  if (!values || values.length < 2) return null

  const max = Math.max(1, ...values)

  const points = values.map((value, index) => [
    (index / (values.length - 1)) * 100,
    92 - (value / max) * 80,
  ])

  const line = smoothPath(points)
  const area = `${line} L 100 100 L 0 100 Z`

  return (
    <svg
      className="ax-spark"
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="ax-spark-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#35e890" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#35e890" stopOpacity="0" />
        </linearGradient>
      </defs>

      <path d={area} fill="url(#ax-spark-fill)" className="ax-spark-area" />

      <path
        d={line}
        pathLength="1"
        className="ax-spark-line"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  )
}

function KpiCard({ card, index }) {
  const animated = useCountUp(card.raw)

  return (
    <div
      className="ax-kpi ax-reveal"
      style={{ '--d': `${index * 70}ms` }}
      onMouseMove={spotlight}
    >
      <span>{card.label}</span>

      {card.trend !== null && card.trend !== undefined && (
        <em
          className={`ax-trend ${
            card.trend > 0 ? 'up' : card.trend < 0 ? 'down' : ''
          }`}
          title="Later half of this period vs the earlier half"
        >
          {card.trend > 0 ? '▲' : card.trend < 0 ? '▼' : '–'}{' '}
          {Math.abs(card.trend)}%
        </em>
      )}

      <strong>{card.format(animated)}</strong>

      <small>{card.hint}</small>

      <Sparkline values={card.spark} />
    </div>
  )
}

function Insights({ items }) {
  if (!items.length) return null

  return (
    <div className="ax-insights ax-reveal" style={{ '--d': '420ms' }}>
      <div className="ax-insights-title">
        <span>✦</span>
        <strong>Key takeaways</strong>
      </div>

      <div className="ax-insights-list">
        {items.map((item, index) => (
          <div
            className="ax-insight"
            key={item.title}
            style={{ '--d': `${520 + index * 90}ms` }}
          >
            <i>{item.icon}</i>

            <div>
              <small>{item.title}</small>
              <strong>{item.text}</strong>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function Donut({ data }) {
  const [active, setActive] = useState(null)

  const signature = data.map((item) => `${item.name}:${item.count}`).join('|')
  const grown = useGrown(signature)

  const total = data.reduce((sum, item) => sum + item.count, 0)

  // Where each slice starts (12 o'clock = 25 on this 100-unit circle).
  const segments = data.map((item, index) => {
    const before = data
      .slice(0, index)
      .reduce((sum, previous) => sum + previous.count, 0)

    return {
      ...item,
      percentOfCircle: (item.count / total) * 100,
      offset: 25 - (before / total) * 100,
    }
  })

  const focus = active !== null ? segments[active] : null

  return (
    <div className="ax-donut-wrap">
      <svg
        viewBox="0 0 42 42"
        className="ax-donut"
        role="img"
        onMouseLeave={() => setActive(null)}
      >
        <circle
          cx="21"
          cy="21"
          r="15.9155"
          fill="none"
          stroke="#1c1c1c"
          strokeWidth="5"
        />

        {segments.map((item, index) => {
          const gap = segments.length > 1 ? 0.6 : 0
          const length = Math.max(0, item.percentOfCircle - gap)

          return (
            <circle
              key={item.name}
              className={`ax-donut-slice ${
                active === index ? 'is-active' : ''
              } ${active !== null && active !== index ? 'is-dim' : ''}`}
              cx="21"
              cy="21"
              r="15.9155"
              fill="none"
              stroke={DONUT_COLORS[index % DONUT_COLORS.length]}
              strokeWidth={active === index ? 6.4 : 5}
              strokeDasharray={
                grown ? `${length} ${100 - length}` : '0 100'
              }
              strokeDashoffset={item.offset}
              style={{ transitionDelay: grown ? `${index * 120}ms` : '0ms' }}
              onMouseEnter={() => setActive(index)}
            >
              <title>{`${item.name}: ${item.count} (${item.percent}%)`}</title>
            </circle>
          )
        })}

        <text x="21" y="20.5" textAnchor="middle" className="ax-donut-number">
          {focus ? `${focus.percent}%` : total}
        </text>

        <text x="21" y="26" textAnchor="middle" className="ax-donut-label">
          {focus
            ? focus.name.length > 14
              ? `${focus.name.slice(0, 13)}…`
              : focus.name
            : 'files'}
        </text>
      </svg>

      <ul className="ax-legend">
        {data.map((item, index) => (
          <li
            key={item.name}
            className={`${active === index ? 'is-active' : ''} ${
              active !== null && active !== index ? 'is-dim' : ''
            }`}
            style={{ '--d': `${index * 80}ms` }}
            onMouseEnter={() => setActive(index)}
            onMouseLeave={() => setActive(null)}
          >
            <i
              style={{
                background: DONUT_COLORS[index % DONUT_COLORS.length],
              }}
            />

            <span>{item.name}</span>

            <strong>
              {item.count}
              <small>{item.percent}%</small>
            </strong>
          </li>
        ))}
      </ul>
    </div>
  )
}

function Bars({ data, colors }) {
  const max = Math.max(1, ...data.map((item) => item.count))
  const total = data.reduce((sum, item) => sum + item.count, 0)

  const signature = data.map((item) => `${item.name}:${item.count}`).join('|')
  const grown = useGrown(signature)

  return (
    <div className="ax-bars">
      {data.map((item, index) => (
        <div className="ax-bar-row" key={item.name}>
          <span className="ax-bar-name" title={item.name}>
            {item.name}
          </span>

          <div className="ax-bar-track">
            <div
              className="ax-bar-fill"
              style={{
                width: grown ? `${(item.count / max) * 100}%` : '0%',
                background: colors?.[item.name],
                transitionDelay: grown ? `${index * 90}ms` : '0ms',
              }}
            />
          </div>

          <strong>
            {item.count}
            <em>{total ? Math.round((item.count / total) * 100) : 0}%</em>
          </strong>
        </div>
      ))}
    </div>
  )
}

function Timeline({ data, mode, show }) {
  const [hover, setHover] = useState(null)
  const plotRef = useRef(null)

  const count = data.length

  const peak = Math.max(
    1,
    ...data.map((day) =>
      Math.max(
        show.enc ? day.encryptions : 0,
        show.dec ? day.decryptions : 0
      )
    )
  )

  // round the top of the scale to a tidy number
  const top = peak <= 4 ? peak : Math.ceil(peak / 4) * 4

  const ticks = [top, (top * 3) / 4, top / 2, top / 4, 0].map((tick) =>
    Math.round(tick * 10) / 10
  )

  const middle = Math.floor(count / 2)

  const pointsFor = (key) =>
    data.map((day, index) => [
      ((index + 0.5) / count) * 100,
      100 - (day[key] / top) * 100,
    ])

  const encLine = smoothPath(pointsFor('encryptions'))
  const decLine = smoothPath(pointsFor('decryptions'))

  const handleMove = (event) => {
    const rect = plotRef.current.getBoundingClientRect()
    const ratio = (event.clientX - rect.left) / rect.width

    setHover(Math.max(0, Math.min(count - 1, Math.floor(ratio * count))))
  }

  const hovered = hover !== null ? data[hover] : null

  // keep the tooltip inside the card
  const tipSide = hover !== null && hover > count * 0.65 ? 'left' : 'right'

  return (
    <div className="ax-timeline">
      <div className="ax-timeline-axis">
        {ticks.map((tick, index) => (
          <span key={index}>{Number.isInteger(tick) ? tick : ''}</span>
        ))}
      </div>

      <div className="ax-timeline-main">
        <div
          className="ax-timeline-plot"
          ref={plotRef}
          onPointerMove={handleMove}
          onPointerLeave={() => setHover(null)}
        >
          <div className="ax-gridlines">
            {ticks.map((_, index) => (
              <i key={index} />
            ))}
          </div>

          {/* hover guide */}

          {hovered && (
            <div
              className="ax-guide"
              style={{ left: `${((hover + 0.5) / count) * 100}%` }}
            />
          )}

          {/* BAR MODE */}

          <div className={`ax-columns ${mode === 'bars' ? '' : 'is-hidden'}`}>
            {data.map((day, index) => (
              <div
                className={`ax-column ${hover === index ? 'is-hover' : ''}`}
                key={day.date}
              >
                <div
                  className="ax-column-bar enc"
                  style={{
                    height: show.enc
                      ? `${(day.encryptions / top) * 100}%`
                      : '0%',
                    animationDelay: `${Math.min(index * 18, 700)}ms`,
                  }}
                />

                <div
                  className="ax-column-bar dec"
                  style={{
                    height: show.dec
                      ? `${(day.decryptions / top) * 100}%`
                      : '0%',
                    animationDelay: `${Math.min(index * 18 + 40, 740)}ms`,
                  }}
                />
              </div>
            ))}
          </div>

          {/* LINE MODE */}

          {mode === 'line' && count > 1 && (
            <>
              <svg
                className="ax-lines"
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
                aria-hidden="true"
              >
                <defs>
                  <linearGradient id="ax-enc-fill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#35e890" stopOpacity="0.32" />
                    <stop offset="100%" stopColor="#35e890" stopOpacity="0" />
                  </linearGradient>
                </defs>

                {show.enc && (
                  <path
                    d={`${encLine} L ${((count - 0.5) / count) * 100} 100 L ${
                      (0.5 / count) * 100
                    } 100 Z`}
                    fill="url(#ax-enc-fill)"
                    className="ax-line-area"
                  />
                )}

                {show.dec && (
                  <path
                    d={decLine}
                    pathLength="1"
                    className="ax-line dec"
                    vectorEffect="non-scaling-stroke"
                  />
                )}

                {show.enc && (
                  <path
                    d={encLine}
                    pathLength="1"
                    className="ax-line enc"
                    vectorEffect="non-scaling-stroke"
                  />
                )}
              </svg>

              {hovered && show.enc && (
                <i
                  className="ax-dot enc"
                  style={{
                    left: `${((hover + 0.5) / count) * 100}%`,
                    top: `${100 - (hovered.encryptions / top) * 100}%`,
                  }}
                />
              )}

              {hovered && show.dec && (
                <i
                  className="ax-dot dec"
                  style={{
                    left: `${((hover + 0.5) / count) * 100}%`,
                    top: `${100 - (hovered.decryptions / top) * 100}%`,
                  }}
                />
              )}
            </>
          )}

          {/* TOOLTIP */}

          {hovered && (
            <div
              className={`ax-tip ${tipSide}`}
              style={{ left: `${((hover + 0.5) / count) * 100}%` }}
            >
              <strong>{formatDayLong(hovered.date)}</strong>

              <span>
                <i className="enc" /> Encrypted
                <b>{hovered.encryptions}</b>
              </span>

              <span>
                <i className="dec" /> Decrypted
                <b>{hovered.decryptions}</b>
              </span>
            </div>
          )}
        </div>

        <div className="ax-timeline-dates">
          <span>{formatDay(data[0].date)}</span>

          {count > 2 && <span>{formatDay(data[middle].date)}</span>}

          <span>{formatDay(data[count - 1].date)}</span>
        </div>
      </div>
    </div>
  )
}

function PerformanceTable({ rows }) {
  const [sort, setSort] = useState({ key: 'count', dir: 'desc' })

  const sorted = useMemo(() => {
    const list = [...rows]

    list.sort((a, b) => {
      const left = a[sort.key]
      const right = b[sort.key]

      const result =
        typeof left === 'string'
          ? left.localeCompare(right)
          : left - right

      return sort.dir === 'asc' ? result : -result
    })

    return list
  }, [rows, sort])

  const maxTime = Math.max(1, ...rows.map((row) => row.avg_time_ms))

  const fastest =
    rows.length > 1
      ? rows.reduce((best, row) =>
          row.avg_time_ms < best.avg_time_ms ? row : best
        ).name
      : null

  const columns = [
    { key: 'name', label: 'Algorithm' },
    { key: 'count', label: 'Files' },
    { key: 'avg_time_ms', label: 'Avg Encryption Time' },
    { key: 'avg_confidence_percent', label: 'Avg Model Confidence' },
  ]

  const toggle = (key) =>
    setSort((current) => ({
      key,
      dir: current.key === key && current.dir === 'desc' ? 'asc' : 'desc',
    }))

  const grown = useGrown(rows.map((row) => row.name).join('|'))

  return (
    <div className="ax-table-wrap">
      <table className="ax-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>
                <button
                  className={sort.key === column.key ? 'is-sorted' : ''}
                  onClick={() => toggle(column.key)}
                >
                  {column.label}
                  <span>
                    {sort.key === column.key
                      ? sort.dir === 'asc'
                        ? '▲'
                        : '▼'
                      : '↕'}
                  </span>
                </button>
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {sorted.map((row, index) => (
            <tr key={row.name} style={{ '--d': `${index * 70}ms` }}>
              <td>
                {row.name}
                {row.name === fastest && (
                  <em className="ax-pill">⚡ Fastest</em>
                )}
              </td>

              <td>{row.count}</td>

              <td>
                <div className="ax-cell-bar">
                  <span>{formatMs(row.avg_time_ms)}</span>

                  <div>
                    <i
                      style={{
                        width: grown
                          ? `${(row.avg_time_ms / maxTime) * 100}%`
                          : '0%',
                      }}
                    />
                  </div>
                </div>
              </td>

              <td>
                <div className="ax-cell-bar">
                  <span>{row.avg_confidence_percent}%</span>

                  <div>
                    <i
                      className="conf"
                      style={{
                        width: grown ? `${row.avg_confidence_percent}%` : '0%',
                      }}
                    />
                  </div>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const WEEKDAYS_LONG = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
]

// later half of the period vs the earlier half
function trendOf(values) {
  if (!values || values.length < 4) return null

  const half = Math.floor(values.length / 2)
  const earlier = values.slice(0, half).reduce((a, b) => a + b, 0)
  const later = values.slice(values.length - half).reduce((a, b) => a + b, 0)

  if (!earlier) return null

  return Math.round(((later - earlier) / earlier) * 100)
}

function Gauge({ label, value, max = 100, color, caption, suffix = '' }) {
  const grown = useGrown(value)
  const shown = useCountUp(value, 1200)

  const length = Math.PI * 40
  const filled = (Math.max(0, Math.min(value, max)) / max) * length

  return (
    <div className="ax-gauge">
      <svg viewBox="0 0 100 62" aria-hidden="true">
        <path d="M 10 52 A 40 40 0 0 1 90 52" className="ax-gauge-track" />

        <path
          d="M 10 52 A 40 40 0 0 1 90 52"
          className="ax-gauge-fill"
          style={{
            stroke: color,
            strokeDasharray: `${grown ? filled : 0} ${length}`,
            filter: `drop-shadow(0 0 3px ${color})`,
          }}
        />
      </svg>

      <div className="ax-gauge-value">
        {shown.toFixed(1)}
        {suffix}
      </div>

      <strong>{label}</strong>
      <small style={{ color }}>{caption}</small>
    </div>
  )
}

function WeekdayChart({ timeline }) {
  const totals = WEEKDAYS.map(() => 0)

  timeline.forEach((day) => {
    const [year, month, date] = day.date.split('-').map(Number)
    const index = (new Date(year, month - 1, date).getDay() + 6) % 7

    totals[index] += day.encryptions + day.decryptions
  })

  const max = Math.max(1, ...totals)
  const best = totals.indexOf(Math.max(...totals))
  const grown = useGrown(totals.join(','))

  return (
    <>
      <div className="ax-weekdays">
        {totals.map((total, index) => (
          <div
            className={`ax-weekday ${index === best && total ? 'is-top' : ''}`}
            key={WEEKDAYS[index]}
            title={`${WEEKDAYS_LONG[index]}: ${total} operations`}
          >
            <b>{total}</b>

            <div className="ax-weekday-track">
              <i
                style={{
                  height: grown ? `${(total / max) * 100}%` : '0%',
                  transitionDelay: `${index * 70}ms`,
                }}
              />
            </div>

            <span>{WEEKDAYS[index]}</span>
          </div>
        ))}
      </div>

      <p className="ax-caption">
        {totals[best]
          ? `${WEEKDAYS_LONG[best]} is the busiest day of the week.`
          : 'No activity yet.'}
      </p>
    </>
  )
}

function exportCsv(data) {
  const rows = [
    ['Adaptive Encryption - Analytics report'],
    ['Range', data.range],
    ['Generated', new Date().toLocaleString('en-IN')],
    [],
    ['SUMMARY'],
    ...Object.entries(data.kpis).map(([key, value]) => [key, value]),
    [],
    ['ALGORITHMS', 'Files', 'Percent'],
    ...data.algorithms.map((a) => [a.name, a.count, a.percent]),
    [],
    ['SENSITIVITY', 'Files'],
    ...data.sensitivity.map((a) => [a.name, a.count]),
    [],
    ['CATEGORIES', 'Files', 'Percent'],
    ...data.categories.map((a) => [a.name, a.count, a.percent]),
    [],
    ['FILE TYPES', 'Files', 'Percent'],
    ...data.file_types.map((a) => [a.name, a.count, a.percent]),
    [],
    ['ALGORITHM PERFORMANCE', 'Files', 'Avg time (ms)', 'Avg confidence (%)'],
    ...data.algorithm_performance.map((a) => [
      a.name,
      a.count,
      a.avg_time_ms,
      a.avg_confidence_percent,
    ]),
    [],
    ['DATE', 'Encrypted', 'Decrypted'],
    ...data.timeline.map((d) => [d.date, d.encryptions, d.decryptions]),
  ]

  const csv = rows
    .map((row) =>
      row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')
    )
    .join('\r\n')

  const url = URL.createObjectURL(
    new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
  )

  const link = document.createElement('a')

  link.href = url
  link.download = `analytics-${data.range}-${new Date()
    .toISOString()
    .slice(0, 10)}.csv`

  link.click()

  URL.revokeObjectURL(url)
}

function Skeleton() {
  return (
    <div className="ax-body" aria-busy="true" aria-label="Loading analytics">
      <div className="ax-kpis">
        {Array.from({ length: 6 }).map((_, index) => (
          <div className="ax-kpi ax-skel ax-skel-kpi" key={index} />
        ))}
      </div>

      <div className="ax-card ax-skel ax-skel-chart" />

      <div className="ax-grid">
        <div className="ax-card ax-skel ax-skel-box" />
        <div className="ax-card ax-skel ax-skel-box" />
      </div>
    </div>
  )
}

// ------------------------------------------------------------
// Page
// ------------------------------------------------------------

function AnalyticsPage({ onNavigate }) {
  const [range, setRange] = useState('30d')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)

  const [live, setLive] = useState(false)
  const [updatedAt, setUpdatedAt] = useState(null)
  const silentRef = useRef(false)

  const [chartMode, setChartMode] = useState('bars')
  const [show, setShow] = useState({ enc: true, dec: true })

  useEffect(() => {
    const controller = new AbortController()

    const load = async () => {
      const silent = silentRef.current
      silentRef.current = false

      if (!silent) setLoading(true)
      setError('')

      // minutes the user's clock is ahead of UTC, so days line up
      const offset = -new Date().getTimezoneOffset()

      try {
        const response = await fetch(
           `${API_URL}/analytics?range=${range}&tz_offset=${offset}`,
            {
              signal: controller.signal,
              credentials: 'include',
            }
  )

        const json = await response.json()

        if (!response.ok || !json.success) {
          throw new Error(json.error || 'Unable to load analytics.')
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
  }, [range, reloadKey])

  // optional auto-refresh
  useEffect(() => {
    if (!live) return undefined

    const timer = setInterval(() => {
      silentRef.current = true
      setReloadKey((key) => key + 1)
    }, LIVE_REFRESH_MS)

    return () => clearInterval(timer)
  }, [live])

  const kpis = data?.kpis
  const isEmpty = kpis && kpis.total_operations === 0

  const encSpark = data?.timeline.map((day) => day.encryptions)
  const decSpark = data?.timeline.map((day) => day.decryptions)
  const opsSpark = data?.timeline.map(
    (day) => day.encryptions + day.decryptions
  )

  const cards = kpis
    ? [
        {
          label: 'Files Encrypted',
          raw: kpis.files_encrypted,
          format: (v) => Math.round(v).toLocaleString('en-IN'),
          hint: `${kpis.total_size_mb} MB processed`,
          spark: encSpark,
          trend: trendOf(encSpark),
        },
        {
          label: 'Files Decrypted',
          raw: kpis.files_decrypted,
          format: (v) => Math.round(v).toLocaleString('en-IN'),
          hint: `${kpis.total_operations} operations total`,
          spark: decSpark,
          trend: trendOf(decSpark),
        },
        {
          label: 'Success Rate',
          raw: kpis.success_rate,
          format: (v) => `${v.toFixed(1)}%`,
          hint: 'Encrypt + decrypt',
          spark: opsSpark,
        },
        {
          label: 'Avg Encryption Time',
          raw: kpis.avg_encryption_ms,
          format: (v) => formatMs(v),
          hint: `Decrypt: ${formatMs(kpis.avg_decryption_ms)}`,
        },
        {
          label: 'Avg Sensitivity',
          raw: kpis.avg_sensitivity,
          format: (v) => `${v.toFixed(1)}/100`,
          hint: `Model confidence ${kpis.avg_confidence_percent}%`,
        },
        {
          label: 'PII Detected',
          raw: kpis.total_pii,
          format: (v) => Math.round(v).toLocaleString('en-IN'),
          hint: 'Across all encrypted files',
        },
      ]
    : []

  // plain-English takeaways, built from the same data
  const insights = useMemo(() => {
    if (!data || data.kpis.total_operations === 0) return []

    const items = []

    if (data.algorithms.length) {
      const top = data.algorithms[0]

      items.push({
        icon: '🛡',
        title: 'Most used algorithm',
        text: `${top.name} · ${top.percent}% of files`,
      })
    }

    const busiest = data.timeline.reduce(
      (best, day) =>
        day.encryptions + day.decryptions >
        best.encryptions + best.decryptions
          ? day
          : best,
      data.timeline[0]
    )

    if (busiest && busiest.encryptions + busiest.decryptions > 0) {
      items.push({
        icon: '📅',
        title: 'Busiest day',
        text: `${formatDay(busiest.date)} · ${
          busiest.encryptions + busiest.decryptions
        } operations`,
      })
    }

    const sensitivityTotal = data.sensitivity.reduce(
      (sum, level) => sum + level.count,
      0
    )

    if (sensitivityTotal) {
      const risky = data.sensitivity
        .filter((level) => level.name === 'High' || level.name === 'Very High')
        .reduce((sum, level) => sum + level.count, 0)

      items.push({
        icon: '⚠',
        title: 'High-risk files',
        text: `${Math.round((risky / sensitivityTotal) * 100)}% rated High or Very High`,
      })
    }

    if (data.categories.length) {
      items.push({
        icon: '📂',
        title: 'Top document type',
        text: `${data.categories[0].name} · ${data.categories[0].count} files`,
      })
    }

    return items
  }, [data])

  const totalEnc = data?.timeline.reduce((sum, day) => sum + day.encryptions, 0)
  const totalDec = data?.timeline.reduce((sum, day) => sum + day.decryptions, 0)

  const toggleSeries = (key) =>
    setShow((current) => {
      const next = { ...current, [key]: !current[key] }

      // never allow both to be hidden
      return next.enc || next.dec ? next : current
    })

  const refresh = () => setReloadKey((key) => key + 1)

  return (
    <div className="ax-page">
      {/* HEADER */}

      <div className="ax-header">
        <div className="ax-header-main">
          <div className="ax-header-icon">📊</div>

          <div>
            <p className="ax-eyebrow">INSIGHTS</p>
            <h1>Analytics</h1>
            <p className="ax-subtitle">
              How the adaptive engine is protecting your files: algorithms
              chosen, sensitivity levels and performance.
            </p>
          </div>
        </div>

        <div className="ax-header-actions">
          <div className="ax-range">
            {RANGES.map((item) => (
              <button
                key={item.key}
                className={range === item.key ? 'active' : ''}
                onClick={() => setRange(item.key)}
              >
                {item.label}
              </button>
            ))}
          </div>

          <button
            className="ax-refresh"
            onClick={() => data && exportCsv(data)}
            disabled={!data}
            title="Download these numbers as a spreadsheet (CSV)"
          >
            ⤓ Export
          </button>

          <button
            className={`ax-refresh ax-live ${live ? 'is-on' : ''}`}
            onClick={() => setLive((value) => !value)}
            title={`Refresh automatically every ${LIVE_REFRESH_MS / 1000} seconds`}
          >
            <i /> Live
          </button>

          <button
            className={`ax-refresh ${loading ? 'is-spinning' : ''}`}
            onClick={refresh}
            disabled={loading}
          >
            <span className="ax-refresh-icon">⟳</span> Refresh
          </button>
        </div>
      </div>

      {updatedAt && !error && (
        <p className="ax-updated">
          Updated{' '}
          {updatedAt.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          })}
          {live && ` · refreshing every ${LIVE_REFRESH_MS / 1000}s`}
        </p>
      )}

      {error ? (
        <section className="ax-card ax-state ax-state-error">
          <strong>Could not load analytics</strong>
          <p>{error}</p>

          <button className="ax-refresh" onClick={refresh}>
            Try again
          </button>
        </section>
      ) : !data ? (
        <Skeleton />
      ) : (
        <div
          className={loading ? 'ax-body is-loading' : 'ax-body'}
          key={data.range}
        >
          {/* KPI CARDS */}

          <div className="ax-kpis">
            {cards.map((card, index) => (
              <KpiCard card={card} index={index} key={card.label} />
            ))}
          </div>

          {isEmpty ? (
            <section className="ax-card ax-state ax-reveal">
              <div className="ax-state-icon">📈</div>
              <strong>No activity in this period</strong>
              <p>
                Encrypt or decrypt a file and your charts will appear here.
                Try a longer time range if you have older files.
              </p>

              <button
                className="ax-refresh ax-primary"
                onClick={() => onNavigate?.('home')}
              >
                Encrypt a file
              </button>
            </section>
          ) : (
            <>
              <Insights items={insights} />

              {/* TIMELINE */}

              <section
                className="ax-card ax-reveal"
                style={{ '--d': '300ms' }}
                onMouseMove={spotlight}
              >
                <div className="ax-card-head">
                  <div>
                    <span>ACTIVITY</span>
                    <h3>Operations Over Time</h3>
                  </div>

                  <div className="ax-card-tools">
                    <div className="ax-key">
                      <button
                        className={show.enc ? '' : 'is-off'}
                        onClick={() => toggleSeries('enc')}
                        title="Click to show or hide"
                      >
                        <i className="enc" /> Encrypted
                        <b>{totalEnc}</b>
                      </button>

                      <button
                        className={show.dec ? '' : 'is-off'}
                        onClick={() => toggleSeries('dec')}
                        title="Click to show or hide"
                      >
                        <i className="dec" /> Decrypted
                        <b>{totalDec}</b>
                      </button>
                    </div>

                    <div className="ax-switch">
                      <button
                        className={chartMode === 'bars' ? 'active' : ''}
                        onClick={() => setChartMode('bars')}
                      >
                        Bars
                      </button>

                      <button
                        className={chartMode === 'line' ? 'active' : ''}
                        onClick={() => setChartMode('line')}
                      >
                        Line
                      </button>
                    </div>
                  </div>
                </div>

                <Timeline data={data.timeline} mode={chartMode} show={show} />
              </section>

              {/* GRID */}

              <div className="ax-grid">
                <section
                  className="ax-card ax-reveal"
                  style={{ '--d': '380ms' }}
                  onMouseMove={spotlight}
                >
                  <div className="ax-card-head">
                    <div>
                      <span>ADAPTIVE ENGINE</span>
                      <h3>Algorithms Selected</h3>
                    </div>
                  </div>

                  {data.algorithms.length ? (
                    <Donut data={data.algorithms} />
                  ) : (
                    <p className="ax-none">No encrypted files yet.</p>
                  )}
                </section>

                <section
                  className="ax-card ax-reveal"
                  style={{ '--d': '450ms' }}
                  onMouseMove={spotlight}
                >
                  <div className="ax-card-head">
                    <div>
                      <span>RISK</span>
                      <h3>Sensitivity Levels</h3>
                    </div>
                  </div>

                  <Bars data={data.sensitivity} colors={LEVEL_COLORS} />
                </section>

                <section
                  className="ax-card ax-reveal"
                  style={{ '--d': '520ms' }}
                  onMouseMove={spotlight}
                >
                  <div className="ax-card-head">
                    <div>
                      <span>CONTENT</span>
                      <h3>Document Categories</h3>
                    </div>
                  </div>

                  {data.categories.length ? (
                    <Bars data={data.categories} />
                  ) : (
                    <p className="ax-none">No data.</p>
                  )}
                </section>

                <section
                  className="ax-card ax-reveal"
                  style={{ '--d': '590ms' }}
                  onMouseMove={spotlight}
                >
                  <div className="ax-card-head">
                    <div>
                      <span>FORMAT</span>
                      <h3>File Types</h3>
                    </div>
                  </div>

                  {data.file_types.length ? (
                    <Bars data={data.file_types} />
                  ) : (
                    <p className="ax-none">No data.</p>
                  )}
                </section>
              </div>

              {/* HEALTH + WEEKDAYS */}

              <div className="ax-grid">
                <section
                  className="ax-card ax-reveal"
                  style={{ '--d': '630ms' }}
                  onMouseMove={spotlight}
                >
                  <div className="ax-card-head">
                    <div>
                      <span>AT A GLANCE</span>
                      <h3>System Health</h3>
                    </div>
                  </div>

                  <div className="ax-gauges">
                    <Gauge
                      label="Success rate"
                      value={kpis.success_rate}
                      suffix="%"
                      color="#35e890"
                      caption={
                        kpis.success_rate >= 95
                          ? 'Excellent'
                          : kpis.success_rate >= 80
                            ? 'Good'
                            : 'Needs attention'
                      }
                    />

                    <Gauge
                      label="Avg sensitivity"
                      value={kpis.avg_sensitivity}
                      color={
                        LEVEL_COLORS[
                          kpis.avg_sensitivity >= 75
                            ? 'Very High'
                            : kpis.avg_sensitivity >= 50
                              ? 'High'
                              : kpis.avg_sensitivity >= 25
                                ? 'Medium'
                                : 'Low'
                        ]
                      }
                      caption={
                        kpis.avg_sensitivity >= 75
                          ? 'Very High risk'
                          : kpis.avg_sensitivity >= 50
                            ? 'High risk'
                            : kpis.avg_sensitivity >= 25
                              ? 'Medium risk'
                              : 'Low risk'
                      }
                    />
                  </div>
                </section>

                <section
                  className="ax-card ax-reveal"
                  style={{ '--d': '700ms' }}
                  onMouseMove={spotlight}
                >
                  <div className="ax-card-head">
                    <div>
                      <span>PATTERN</span>
                      <h3>Busiest Weekdays</h3>
                    </div>
                  </div>

                  <WeekdayChart timeline={data.timeline} />
                </section>
              </div>

              {/* PERFORMANCE */}

              <section
                className="ax-card ax-reveal"
                style={{ '--d': '770ms' }}
                onMouseMove={spotlight}
              >
                <div className="ax-card-head">
                  <div>
                    <span>PERFORMANCE</span>
                    <h3>Algorithm Performance</h3>
                  </div>

                  <small className="ax-hint">Click a heading to sort</small>
                </div>

                <PerformanceTable rows={data.algorithm_performance} />
              </section>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default AnalyticsPage
