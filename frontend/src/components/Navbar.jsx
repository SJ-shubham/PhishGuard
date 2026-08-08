import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { pathname }     = useLocation()

  const link = (to, label) => (
    <Link
      to={to}
      className={`text-sm px-3 py-1 rounded transition
        ${pathname === to
          ? 'bg-blue-600 text-white'
          : 'text-slate-400 hover:text-white'}`}
    >
      {label}
    </Link>
  )

  return (
    <nav className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-blue-400 font-bold text-lg">PhishGuard</span>
        </Link>

        <div className="flex items-center gap-1">
          {link('/',        'Dashboard')}
          {link('/history', 'History')}
          {link('/bulk',    'Bulk Scan')}
        </div>

        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-400 hidden sm:block">
            {user?.name}
          </span>
          {link('/profile', 'Profile')}
          <button
            onClick={logout}
            className="text-sm text-slate-400 hover:text-red-400 transition px-2 py-1"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  )
}
