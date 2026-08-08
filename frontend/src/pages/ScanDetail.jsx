import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ScoreGauge from '../components/ScoreGauge'
import RiskBadge  from '../components/RiskBadge'
import client     from '../api/client'

const FLAG_LABELS = {
  dns_resolves:        { label: 'DNS Resolves',        good: true  },
  ssl_valid:           { label: 'SSL Valid',            good: true  },
  is_https:            { label: 'HTTPS',                good: true  },
  brand_impersonation: { label: 'Brand Impersonation',  good: false },
  suspicious_tld:      { label: 'Suspicious TLD',       good: false },
  domain_is_new:       { label: 'New Domain',           good: false },
  path_is_suspicious:  { label: 'Suspicious Path',      good: false },
  ip_in_subdomain:     { label: 'IP in Subdomain',      good: false },
  suspicious_keywords: { label: 'Phishing Keywords',    good: false },
  has_punycode:        { label: 'Punycode / IDN',       good: false },
}

function Section({ title, children }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">{title}</h2>
      {children}
    </div>
  )
}

function KV({ label, value, mono = false, color }) {
  return (
    <div className="flex justify-between py-1.5 border-b border-slate-800 last:border-0">
      <span className="text-sm text-slate-400">{label}</span>
      <span className={`text-sm ${color || 'text-slate-200'} ${mono ? 'font-mono' : ''}`}>{value ?? '—'}</span>
    </div>
  )
}

export default function ScanDetail() {
  const { id }          = useParams()
  const navigate        = useNavigate()
  const [scan, setScan] = useState(null)
  const [err,  setErr]  = useState('')
  const [busy, setBusy] = useState({ download: false, rescan: false, del: false })

  useEffect(() => {
    client.get(`/api/scans/${id}`)
      .then(r => setScan(r.data))
      .catch(() => setErr('Scan not found or access denied.'))
  }, [id])

  const handleDownload = async () => {
    setBusy(b => ({ ...b, download: true }))
    try {
      const resp = await client.get(`/api/scans/${id}/report`, { responseType: 'blob' })
      const url  = window.URL.createObjectURL(new Blob([resp.data]))
      const a    = document.createElement('a')
      a.href     = url
      a.setAttribute('download', `phishguard_${id.slice(0, 8)}.pdf`)
      document.body.appendChild(a)
      a.click()
      a.remove()
    } catch {
      alert('Failed to download report.')
    } finally {
      setBusy(b => ({ ...b, download: false }))
    }
  }

  const handleRescan = async () => {
    setBusy(b => ({ ...b, rescan: true }))
    try {
      const { data } = await client.post(`/api/scans/${id}/rescan`)
      setScan(data)
    } catch {
      alert('Rescan failed.')
    } finally {
      setBusy(b => ({ ...b, rescan: false }))
    }
  }

  const handleDelete = async () => {
    if (!confirm('Permanently delete this scan?')) return
    setBusy(b => ({ ...b, del: true }))
    try {
      await client.delete(`/api/scans/${id}`)
      navigate('/history', { replace: true })
    } catch {
      alert('Delete failed.')
      setBusy(b => ({ ...b, del: false }))
    }
  }

  if (err) {
    return (
      <div className="text-center py-20">
        <p className="text-red-400">{err}</p>
        <button onClick={() => navigate(-1)} className="mt-4 text-blue-400 hover:underline text-sm">
          ← Go Back
        </button>
      </div>
    )
  }

  if (!scan) {
    return <div className="text-center py-20 text-slate-500">Loading…</div>
  }

  const hf  = scan.heuristic_flags || {}
  const sb  = scan.score_breakdown  || {}
  const sh  = scan.shap_values
  const fmt = ts => new Date(ts).toLocaleString()

  return (
    <div className="space-y-6">
      {/* Back */}
      <button onClick={() => navigate(-1)} className="text-sm text-slate-400 hover:text-white transition">
        ← Back
      </button>

      {/* Hero */}
      <div className="bg-slate-900 border border-slate-700 rounded-xl p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
          <ScoreGauge score={scan.score} level={scan.risk_level} />
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <RiskBadge level={scan.risk_level} size="lg" />
              <span className="text-white font-medium">{scan.verdict}</span>
            </div>
            <p className="text-slate-400 text-sm break-all">{scan.url}</p>
            <p className="text-xs text-slate-500">{fmt(scan.timestamp)}</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-3 mt-5 pt-5 border-t border-slate-800">
          <button
            onClick={handleDownload} disabled={busy.download}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50
                       text-white rounded-lg text-sm font-medium transition"
          >
            {busy.download ? 'Generating…' : 'Download PDF'}
          </button>
          <button
            onClick={handleRescan} disabled={busy.rescan}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50
                       text-white rounded-lg text-sm font-medium transition"
          >
            {busy.rescan ? 'Rescanning…' : 'Re-Scan'}
          </button>
          <button
            onClick={handleDelete} disabled={busy.del}
            className="px-4 py-2 bg-red-900/40 hover:bg-red-900/70 border border-red-800
                       text-red-400 rounded-lg text-sm font-medium transition disabled:opacity-50"
          >
            {busy.del ? 'Deleting…' : 'Delete'}
          </button>
        </div>
      </div>

      {/* Score Breakdown */}
      {Object.keys(sb).length > 0 && (
        <Section title="Score Breakdown">
          {Object.entries(sb).map(([k, v]) => (
            <KV key={k} label={k.replace(/_/g, ' ')} value={typeof v === 'number' ? v.toFixed(3) : String(v)} mono />
          ))}
        </Section>
      )}

      {/* ML details */}
      <Section title="Model Details">
        <KV label="ML Phishing Probability"   value={`${(scan.ml_probability * 100).toFixed(2)}%`}   color="text-white" />
        <KV label="ML Legitimate Probability" value={`${((1 - scan.ml_probability) * 100).toFixed(2)}%`} />
        <KV label="Trust Factor"              value={scan.trust_factor?.toFixed(4)} mono />
        <KV label="Elapsed Time"              value={scan.elapsed_time ? `${scan.elapsed_time.toFixed(2)}s` : '—'} />
      </Section>

      {/* Heuristic flags */}
      {Object.keys(hf).length > 0 && (
        <Section title="Heuristic Signals">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {Object.entries(FLAG_LABELS).map(([key, { label, good }]) => {
              const val = hf[key]
              if (val === undefined) return null
              const isGood = good ? val === true : val === false
              return (
                <div key={key}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs border
                    ${isGood
                      ? 'bg-emerald-900/20 border-emerald-800 text-emerald-400'
                      : 'bg-red-900/20 border-red-800 text-red-400'}`}>
                  <span>{isGood ? '✓' : '✗'}</span>
                  <span>{label}</span>
                </div>
              )
            })}
          </div>
        </Section>
      )}

      {/* SHAP values */}
      {sh && (
        <Section title="SHAP Feature Attribution">
          <div className="grid sm:grid-cols-2 gap-6">
            <div>
              <p className="text-xs text-red-400 font-medium mb-2">Top phishing signals</p>
              {sh.top_risk?.map((f, i) => (
                <div key={i} className="flex justify-between text-xs py-1.5 border-b border-slate-800">
                  <span className="text-slate-300">{f.feature}</span>
                  <span className="text-red-400 font-mono">{f.value.toFixed(4)}</span>
                </div>
              ))}
            </div>
            <div>
              <p className="text-xs text-emerald-400 font-medium mb-2">Top legitimate signals</p>
              {sh.top_safe?.map((f, i) => (
                <div key={i} className="flex justify-between text-xs py-1.5 border-b border-slate-800">
                  <span className="text-slate-300">{f.feature}</span>
                  <span className="text-emerald-400 font-mono">+{f.value.toFixed(4)}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800 flex gap-6 text-xs text-slate-500">
            <span>Base value: <span className="text-slate-300 font-mono">{sh.base_value?.toFixed(4)}</span></span>
            <span>Prediction value: <span className="text-slate-300 font-mono">{sh.prediction_value?.toFixed(4)}</span></span>
          </div>
        </Section>
      )}

      {/* Raw features */}
      {scan.features && Object.keys(scan.features).length > 0 && (
        <Section title="Raw ML Features">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-1 text-xs">
            {Object.entries(scan.features).map(([k, v]) => (
              <div key={k} className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-500 truncate mr-2">{k}</span>
                <span className="text-slate-300 font-mono shrink-0">
                  {typeof v === 'number' ? v.toFixed(3) : String(v)}
                </span>
              </div>
            ))}
          </div>
        </Section>
      )}
    </div>
  )
}
