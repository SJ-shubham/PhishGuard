import { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import RiskBadge from '../components/RiskBadge'
import client    from '../api/client'

const LEVELS = ['All', 'Low', 'Medium', 'High', 'Critical']

export default function History() {
  const navigate = useNavigate()
  const [items,   setItems]   = useState([])
  const [total,   setTotal]   = useState(0)
  const [pages,   setPages]   = useState(1)
  const [page,    setPage]    = useState(1)
  const [loading, setLoading] = useState(true)
  const [filter,  setFilter]  = useState('All')
  const [sortBy,  setSortBy]  = useState('timestamp')
  const [search,  setSearch]  = useState('')
  const [query,   setQuery]   = useState('')
  const [deleting, setDeleting] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        page,
        limit: 20,
        sort_by: sortBy,
        order: 'desc',
        ...(filter !== 'All' && { risk_level: filter }),
        ...(query && { search: query }),
      })
      const { data } = await client.get(`/api/scans?${params}`)
      setItems(data.items  || [])
      setTotal(data.total  || 0)
      setPages(data.pages  || 1)
    } finally {
      setLoading(false)
    }
  }, [page, filter, sortBy, query])

  useEffect(() => { load() }, [load])

  const handleDelete = async (id, e) => {
    e.stopPropagation()
    if (!confirm('Delete this scan?')) return
    setDeleting(id)
    try {
      await client.delete(`/api/scans/${id}`)
      setItems(prev => prev.filter(i => i.id !== id))
      setTotal(t => t - 1)
    } finally {
      setDeleting(null)
    }
  }

  const fmt = ts => new Date(ts).toLocaleString()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white">
          Scan History <span className="text-slate-400 text-base font-normal">({total})</span>
        </h1>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <input
          value={search} onChange={e => setSearch(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') { setPage(1); setQuery(search) } }}
          placeholder="Search URL…"
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm
                     text-white focus:outline-none focus:border-blue-500 transition w-60"
        />
        <select
          value={filter} onChange={e => { setFilter(e.target.value); setPage(1) }}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
        >
          {LEVELS.map(l => <option key={l}>{l}</option>)}
        </select>
        <select
          value={sortBy} onChange={e => { setSortBy(e.target.value); setPage(1) }}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
        >
          <option value="timestamp">Sort: Date</option>
          <option value="score">Sort: Score</option>
        </select>
      </div>

      {/* Table */}
      {loading ? (
        <div className="text-center py-16 text-slate-500">Loading…</div>
      ) : items.length === 0 ? (
        <div className="text-center py-16 text-slate-500">No scans found.</div>
      ) : (
        <div className="space-y-2">
          {items.map(s => (
            <div
              key={s.id}
              onClick={() => navigate(`/scan/${s.id}`)}
              className="flex items-center justify-between bg-slate-900 border border-slate-800
                         hover:border-slate-600 rounded-xl px-5 py-3 cursor-pointer transition group"
            >
              <div className="flex-1 min-w-0 mr-4">
                <p className="text-sm text-slate-300 group-hover:text-white truncate">{s.url}</p>
                <p className="text-xs text-slate-500 mt-0.5">{fmt(s.timestamp)}</p>
              </div>
              <div className="flex items-center gap-4 shrink-0">
                <span className="text-sm font-mono text-slate-300">{s.score.toFixed(1)}</span>
                <RiskBadge level={s.risk_level} />
                <button
                  onClick={e => handleDelete(s.id, e)}
                  disabled={deleting === s.id}
                  className="text-slate-600 hover:text-red-400 transition text-xs px-2 py-1"
                >
                  {deleting === s.id ? '…' : 'Delete'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {pages > 1 && (
        <div className="flex justify-center gap-2">
          <button
            disabled={page === 1}
            onClick={() => setPage(p => p - 1)}
            className="px-3 py-1 bg-slate-800 rounded text-sm disabled:opacity-40 hover:bg-slate-700"
          >← Prev</button>
          <span className="px-3 py-1 text-sm text-slate-400">
            {page} / {pages}
          </span>
          <button
            disabled={page === pages}
            onClick={() => setPage(p => p + 1)}
            className="px-3 py-1 bg-slate-800 rounded text-sm disabled:opacity-40 hover:bg-slate-700"
          >Next →</button>
        </div>
      )}
    </div>
  )
}
