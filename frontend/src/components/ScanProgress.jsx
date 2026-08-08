const STEPS = ['dns', 'ssl', 'brand', 'whois', 'keywords', 'ml']
const LABELS = {
  dns:      'DNS Resolution',
  ssl:      'SSL Validation',
  brand:    'Brand Check',
  whois:    'Domain Age',
  keywords: 'Keyword Scan',
  ml:       'ML + SHAP',
}

export default function ScanProgress({ currentStep, done }) {
  const current = STEPS.indexOf(currentStep)

  return (
    <div className="w-full">
      <div className="flex justify-between mb-2">
        {STEPS.map((s, i) => {
          const completed = done || i < current
          const active    = !done && i === current
          return (
            <div key={s} className="flex flex-col items-center gap-1" style={{ width: `${100/6}%` }}>
              <div className={`w-3 h-3 rounded-full transition-colors
                ${completed ? 'bg-emerald-400' : active ? 'bg-blue-400 animate-pulse' : 'bg-slate-700'}`}
              />
              <span className={`text-xs text-center hidden sm:block
                ${completed ? 'text-emerald-400' : active ? 'text-blue-400' : 'text-slate-600'}`}>
                {LABELS[s]}
              </span>
            </div>
          )
        })}
      </div>
      <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 transition-all duration-500 rounded-full"
          style={{ width: done ? '100%' : `${((current + 1) / STEPS.length) * 100}%` }}
        />
      </div>
    </div>
  )
}
