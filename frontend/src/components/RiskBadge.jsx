const LEVELS = {
  Low:      { bg: 'bg-emerald-900/40', text: 'text-emerald-400', border: 'border-emerald-700' },
  Medium:   { bg: 'bg-yellow-900/40',  text: 'text-yellow-400',  border: 'border-yellow-700'  },
  High:     { bg: 'bg-orange-900/40',  text: 'text-orange-400',  border: 'border-orange-700'  },
  Critical: { bg: 'bg-red-900/40',     text: 'text-red-400',     border: 'border-red-700'     },
}

export default function RiskBadge({ level, size = 'md' }) {
  const s   = LEVELS[level] || LEVELS.Low
  const pad = size === 'lg' ? 'px-4 py-2 text-base' : 'px-2 py-0.5 text-xs'
  return (
    <span className={`inline-flex items-center rounded border font-semibold ${s.bg} ${s.text} ${s.border} ${pad}`}>
      {level}
    </span>
  )
}
