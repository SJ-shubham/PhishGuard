const COLORS = {
  Low:      '#10b981',
  Medium:   '#f59e0b',
  High:     '#f97316',
  Critical: '#ef4444',
}

export default function ScoreGauge({ score, level }) {
  const color = COLORS[level] || '#10b981'
  const r     = 54
  const circ  = 2 * Math.PI * r
  const arc   = circ * 0.75               // 270° arc
  const dash  = arc * (score / 100)
  const gap   = arc - dash
  const rot   = -225                       // start at bottom-left

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width="140" height="140" viewBox="0 0 140 140">
        {/* Track */}
        <circle
          cx="70" cy="70" r={r}
          fill="none" stroke="#1e293b" strokeWidth="12"
          strokeDasharray={`${arc} ${circ - arc}`}
          strokeDashoffset={0}
          strokeLinecap="round"
          transform={`rotate(${rot} 70 70)`}
        />
        {/* Value */}
        <circle
          cx="70" cy="70" r={r}
          fill="none" stroke={color} strokeWidth="12"
          strokeDasharray={`${dash} ${circ - dash}`}
          strokeDashoffset={0}
          strokeLinecap="round"
          transform={`rotate(${rot} 70 70)`}
          style={{ transition: 'stroke-dasharray 0.6s ease' }}
        />
        <text x="70" y="68" textAnchor="middle" fill={color}
              fontSize="22" fontWeight="700">
          {score.toFixed(1)}
        </text>
        <text x="70" y="86" textAnchor="middle" fill="#64748b" fontSize="10">
          / 100
        </text>
      </svg>
    </div>
  )
}
