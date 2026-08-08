import { useNavigate } from 'react-router-dom'
import ScoreGauge from './ScoreGauge'
import RiskBadge  from './RiskBadge'
import client     from '../api/client'

const FLAG_LABELS = {
  dns_resolves:       { label: 'DNS Resolves',        good: true  },
  ssl_valid:          { label: 'SSL Valid',            good: true  },
  is_https:           { label: 'HTTPS',                good: true  },
  brand_impersonation:{ label: 'Brand Impersonation',  good: false },
  suspicious_tld:     { label: 'Suspicious TLD',       good: false },
  domain_is_new:      { label: 'New Domain',           good: false },
  path_is_suspicious: { label: 'Suspicious Path',      good: false },
  ip_in_subdomain:    { label: 'IP in Subdomain',      good: false },
  suspicious_keywords:{ label: 'Phishing Keywords',    good: false },
  has_punycode:       { label: 'Punycode / IDN',       good: false },
}

export default function ResultCard({ result, scanId }) {
  const navigate = useNavigate()
  const hf = result.heuristic_flags || {}

  const handleDownload = async () => {
    try {
      const resp = await client.get(`/api/scans/${scanId}/report`, {
        responseType: 'blob',
      })
      const url  = window.URL.createObjectURL(new Blob([resp.data]))
      const link = document.createElement('a')
      link.href  = url
      link.setAttribute('download', `phishguard_${scanId?.slice(0,8) || 'report'}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (e) {
      alert('Could not download report')
    }
  }

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <ScoreGauge score={result.score} level={result.risk_level} />
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-3">
            <RiskBadge level={result.risk_level} size="lg" />
            <span className="text-slate-300 font-medium">{result.verdict}</span>
          </div>
          <p className="text-slate-400 text-sm break-all">{result.url}</p>
          <div className="flex flex-wrap gap-4 text-xs text-slate-500">
            <span>ML: {(result.ml_probability * 100).toFixed(1)}% phishing</span>
            <span>Trust factor: {result.trust_factor?.toFixed(2)}</span>
            <span>Time: {result.elapsed_time?.toFixed(1)}s</span>
          </div>
        </div>
      </div>

      {/* Heuristic signals */}
      <div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Heuristic Signals
        </h3>
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
      </div>

      {/* SHAP attribution */}
      {result.shap_values && (
        <div>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            SHAP Attribution
          </h3>
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-red-400 mb-2">Top phishing signals</p>
              {result.shap_values.top_risk?.map((f, i) => (
                <div key={i} className="flex justify-between text-xs py-1 border-b border-slate-800">
                  <span className="text-slate-300">{f.feature}</span>
                  <span className="text-red-400">{f.value.toFixed(3)}</span>
                </div>
              ))}
            </div>
            <div>
              <p className="text-xs text-emerald-400 mb-2">Top legitimate signals</p>
              {result.shap_values.top_safe?.map((f, i) => (
                <div key={i} className="flex justify-between text-xs py-1 border-b border-slate-800">
                  <span className="text-slate-300">{f.feature}</span>
                  <span className="text-emerald-400">+{f.value.toFixed(3)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-3 pt-2">
        {scanId && (
          <>
            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition"
            >
              Download PDF Report
            </button>
            <button
              onClick={() => navigate(`/scan/${scanId}`)}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition"
            >
              View Full Detail
            </button>
          </>
        )}
      </div>
    </div>
  )
}
