import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import ScanProgress from '../components/ScanProgress'
import ResultCard   from '../components/ResultCard'
import RiskBadge    from '../components/RiskBadge'
import client       from '../api/client'

function StatsRow({ stats }) {
  const items = [
    { label: 'Total Scans',      value: stats.total },
    { label: 'Phishing Caught',  value: stats.phishing_caught, color: 'text-red-400' },
    { label: 'Safe URLs',        value: stats.safe,            color: 'text-emerald-400' },
    { label: 'Avg Score',        value: stats.avg_score?.toFixed(1) ?? '—' },
  ]
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
      {items.map(({ label, value, color }) => (
        <div key={label} className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
          <div className={`text-2xl font-bold ${color || 'text-white'}`}>{value ?? '—'}</div>
          <div className="text-xs text-slate-400 mt-1">{label}</div>
        </div>
      ))}
    </div>
  )
}

export default function Dashboard() {
  const { user }      = useAuth()
  const [url, setUrl] = useState('')
  const [scanning, setScanning] = useState(false)
  const [step, setStep]         = useState(null)
  const [result, setResult]     = useState(null)
  const [scanId, setScanId]     = useState(null)
  const [error, setError]       = useState('')
  const [stats, setStats]       = useState(null)
  const [recent, setRecent]     = useState([])

  useEffect(() => {
    client.get('/api/scans/stats').then(r => setStats(r.data)).catch(() => {})
    client.get('/api/scans?limit=5').then(r => setRecent(r.data.items || [])).catch(() => {})
  }, [])

  const handleScan = async e => {
    e.preventDefault()
    if (!url.trim()) return
    setScanning(true); setResult(null); setScanId(null); setError(''); setStep('dns')

    const token = sessionStorage.getItem('access_token')

    // Use fetch + ReadableStream for POST with auth header (EventSource doesn't support custom headers)
    try {
      const resp = await fetch('/api/scan', {
        method:  'POST',
        headers: {
          'Content-Type':  'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ url: url.trim() }),
      })

      const reader  = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer    = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()           // keep incomplete line

        for (let i = 0; i < lines.length; i++) {
          if (lines[i].startsWith('event: ')) {
            const event    = lines[i].slice(7).trim()
            const dataLine = lines[i + 1]
            if (dataLine?.startsWith('data: ')) {
              const data = JSON.parse(dataLine.slice(6))
              if (event === 'progress' || event === 'cached') setStep(data.step || 'ml')
              if (event === 'done') {
                setResult(data)
                setScanId(data.id)
                setScanning(false)
                setStep(null)
                client.get('/api/scans/stats').then(r => setStats(r.data)).catch(() => {})
                client.get('/api/scans?limit=5').then(r => setRecent(r.data.items || [])).catch(() => {})
              }
              i++ // skip the consumed data line
            }
          }
        }
      }
    } catch (err) {
      setError('Scan failed. Please try again.')
      setScanning(false)
      setStep(null)
    }
  }

  return (
    <div className="space-y-8">
      {stats && <StatsRow stats={stats} />}

      {/* URL input */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Analyze a URL</h2>
        <form onSubmit={handleScan} className="flex gap-3">
          <input
            value={url} onChange={e => setUrl(e.target.value)}
            placeholder="https://example.com/path"
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5
                       text-white text-sm focus:outline-none focus:border-blue-500 transition"
            disabled={scanning}
          />
          <button
            type="submit" disabled={scanning || !url.trim()}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50
                       text-white rounded-lg text-sm font-medium transition whitespace-nowrap"
          >
            {scanning ? 'Scanning…' : 'Scan URL'}
          </button>
        </form>

        {scanning && (
          <div className="mt-4">
            <ScanProgress currentStep={step} done={false} />
          </div>
        )}

        {error && (
          <div className="mt-4 text-red-400 text-sm bg-red-900/20 border border-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
      </div>

      {/* Result */}
      {result && <ResultCard result={result} scanId={scanId} />}

      {/* Recent scans */}
      {recent.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-white">Recent Scans</h2>
            <Link to="/history" className="text-sm text-blue-400 hover:underline">View all</Link>
          </div>
          <div className="space-y-2">
            {recent.map(s => (
              <Link key={s.id} to={`/scan/${s.id}`}
                className="flex items-center justify-between bg-slate-900 border border-slate-800
                           hover:border-slate-600 rounded-xl px-5 py-3 transition group">
                <span className="text-sm text-slate-300 truncate max-w-xs group-hover:text-white">
                  {s.url}
                </span>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-sm text-slate-400">{s.score.toFixed(1)}</span>
                  <RiskBadge level={s.risk_level} />
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
