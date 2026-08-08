import { useState } from 'react'
import { Link } from 'react-router-dom'
import RiskBadge from '../components/RiskBadge'
import client    from '../api/client'

function ResultRow({ item }) {
  if (item.error) {
    return (
      <div className="flex items-center gap-4 px-5 py-3 bg-slate-900 border border-slate-800 rounded-xl">
        <span className="text-red-400 text-sm shrink-0">Error</span>
        <span className="text-slate-400 text-sm truncate flex-1">{item.url}</span>
        <span className="text-slate-500 text-xs">{item.error}</span>
      </div>
    )
  }

  return (
    <Link
      to={`/scan/${item.id}`}
      className="flex items-center gap-4 px-5 py-3 bg-slate-900 border border-slate-800
                 hover:border-slate-600 rounded-xl transition group"
    >
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-300 group-hover:text-white truncate">{item.url}</p>
      </div>
      <div className="flex items-center gap-4 shrink-0">
        <span className="text-sm font-mono text-slate-300">{item.score?.toFixed(1)}</span>
        <RiskBadge level={item.risk_level} />
        <span className="text-xs text-slate-500 hidden sm:block">{item.verdict}</span>
      </div>
    </Link>
  )
}

export default function BulkScan() {
  const [raw,     setRaw]     = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  const urls = raw.split('\n').map(s => s.trim()).filter(Boolean)
  const tooMany = urls.length > 10

  const handleScan = async e => {
    e.preventDefault()
    if (!urls.length || tooMany) return
    setLoading(true)
    setResults([])
    setError('')
    try {
      const { data } = await client.post('/api/scan/bulk', { urls })
      setResults(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Bulk scan failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const summary = results.reduce((acc, r) => {
    if (!r.error) acc[r.risk_level] = (acc[r.risk_level] || 0) + 1
    return acc
  }, {})

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white">Bulk URL Scan</h1>
        <p className="text-sm text-slate-400 mt-1">Scan up to 10 URLs simultaneously.</p>
      </div>

      {/* Input form */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <form onSubmit={handleScan} className="space-y-4">
          <div>
            <label className="text-sm text-slate-300 block mb-2">
              URLs <span className="text-slate-500">(one per line, max 10)</span>
            </label>
            <textarea
              rows={8}
              value={raw}
              onChange={e => setRaw(e.target.value)}
              placeholder={"https://example.com\nhttps://another.site/path\nhttps://..."}
              disabled={loading}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3
                         text-white text-sm font-mono focus:outline-none focus:border-blue-500
                         transition resize-none"
            />
            <div className="flex items-center justify-between mt-1">
              <span className={`text-xs ${tooMany ? 'text-red-400' : 'text-slate-500'}`}>
                {urls.length} / 10 URLs
              </span>
              {tooMany && (
                <span className="text-xs text-red-400">Maximum 10 URLs allowed</span>
              )}
            </div>
          </div>

          {error && (
            <div className="bg-red-900/20 border border-red-800 text-red-400 text-sm px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div className="flex items-center gap-3">
            <button
              type="submit" disabled={loading || !urls.length || tooMany}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50
                         text-white rounded-lg text-sm font-medium transition"
            >
              {loading ? 'Scanning…' : `Scan ${urls.length || ''} URL${urls.length !== 1 ? 's' : ''}`}
            </button>
            {loading && (
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                Running ML analysis on all URLs in parallel…
              </div>
            )}
          </div>
        </form>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          {/* Summary bar */}
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white">
              Results <span className="text-slate-400 font-normal text-sm">({results.length} URLs)</span>
            </h2>
            <div className="flex items-center gap-3 flex-wrap">
              {Object.entries(summary).map(([level, count]) => (
                <div key={level} className="flex items-center gap-1.5">
                  <RiskBadge level={level} />
                  <span className="text-sm text-slate-400">×{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Risk summary banner if any phishing detected */}
          {(summary.High || summary.Critical) && (
            <div className="bg-red-900/20 border border-red-800 rounded-xl px-5 py-3 flex items-center gap-3">
              <span className="text-red-400 font-medium text-sm">
                {(summary.Critical || 0) + (summary.High || 0)} high-risk URL(s) detected — do not visit these sites.
              </span>
            </div>
          )}

          <div className="space-y-2">
            {results.map((item, i) => (
              <ResultRow key={i} item={item} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
