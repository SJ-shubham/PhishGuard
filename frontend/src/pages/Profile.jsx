import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import client from '../api/client'

function Section({ title, children }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
      <h2 className="text-base font-semibold text-white">{title}</h2>
      {children}
    </div>
  )
}

function Field({ label, name, type = 'text', value, onChange, placeholder, disabled }) {
  return (
    <div>
      <label className="text-sm text-slate-300 block mb-1">{label}</label>
      <input
        name={name} type={type}
        value={value} onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2
                   text-white text-sm focus:outline-none focus:border-blue-500 transition
                   disabled:opacity-60"
      />
    </div>
  )
}

export default function Profile() {
  const { user, logout, fetchMe } = useAuth()
  const navigate                  = useNavigate()

  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '', confirm: '' })
  const [pwError, setPwError] = useState('')
  const [pwSuccess, setPwSuccess] = useState('')
  const [pwBusy, setPwBusy] = useState(false)

  const [delConfirm, setDelConfirm] = useState('')
  const [delError,   setDelError]   = useState('')
  const [delBusy,    setDelBusy]    = useState(false)

  const onPwChange = e => setPwForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const handleChangePassword = async e => {
    e.preventDefault()
    setPwError(''); setPwSuccess('')
    if (pwForm.new_password !== pwForm.confirm) {
      setPwError('New passwords do not match'); return
    }
    if (pwForm.new_password.length < 8) {
      setPwError('New password must be at least 8 characters'); return
    }
    setPwBusy(true)
    try {
      await client.put('/auth/change-password', {
        old_password: pwForm.old_password,
        new_password: pwForm.new_password,
      })
      setPwSuccess('Password updated successfully.')
      setPwForm({ old_password: '', new_password: '', confirm: '' })
    } catch (err) {
      setPwError(err.response?.data?.detail || 'Failed to change password.')
    } finally {
      setPwBusy(false)
    }
  }

  const handleDeleteAccount = async e => {
    e.preventDefault()
    setDelError('')
    if (delConfirm !== 'DELETE') {
      setDelError('Type DELETE to confirm.'); return
    }
    setDelBusy(true)
    try {
      await client.delete('/auth/delete-account')
      await logout()
      navigate('/login', { replace: true })
    } catch (err) {
      setDelError(err.response?.data?.detail || 'Failed to delete account.')
      setDelBusy(false)
    }
  }

  return (
    <div className="space-y-6 max-w-xl">
      <h1 className="text-xl font-bold text-white">Profile</h1>

      {/* Account info */}
      <Section title="Account Information">
        <div className="space-y-1">
          <div className="flex justify-between py-2 border-b border-slate-800">
            <span className="text-sm text-slate-400">Name</span>
            <span className="text-sm text-white">{user?.name}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-800">
            <span className="text-sm text-slate-400">Email</span>
            <span className="text-sm text-white">{user?.email}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-800">
            <span className="text-sm text-slate-400">Total Scans</span>
            <span className="text-sm text-white">{user?.scan_count ?? 0}</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-sm text-slate-400">Member Since</span>
            <span className="text-sm text-white">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}
            </span>
          </div>
        </div>
      </Section>

      {/* Change password */}
      <Section title="Change Password">
        <form onSubmit={handleChangePassword} className="space-y-3">
          <Field
            label="Current Password" name="old_password" type="password"
            value={pwForm.old_password} onChange={onPwChange}
            placeholder="••••••••" disabled={pwBusy}
          />
          <Field
            label="New Password" name="new_password" type="password"
            value={pwForm.new_password} onChange={onPwChange}
            placeholder="••••••••" disabled={pwBusy}
          />
          <Field
            label="Confirm New Password" name="confirm" type="password"
            value={pwForm.confirm} onChange={onPwChange}
            placeholder="••••••••" disabled={pwBusy}
          />

          {pwError && (
            <div className="bg-red-900/20 border border-red-800 text-red-400 text-sm px-4 py-2 rounded-lg">
              {pwError}
            </div>
          )}
          {pwSuccess && (
            <div className="bg-emerald-900/20 border border-emerald-800 text-emerald-400 text-sm px-4 py-2 rounded-lg">
              {pwSuccess}
            </div>
          )}

          <button
            type="submit" disabled={pwBusy}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50
                       text-white rounded-lg text-sm font-medium transition"
          >
            {pwBusy ? 'Updating…' : 'Update Password'}
          </button>
        </form>
      </Section>

      {/* Danger zone */}
      <Section title="Danger Zone">
        <p className="text-sm text-slate-400">
          Permanently delete your account and all associated scan history. This action cannot be undone.
        </p>
        <form onSubmit={handleDeleteAccount} className="space-y-3 mt-2">
          <div>
            <label className="text-sm text-slate-400 block mb-1">
              Type <span className="text-red-400 font-mono font-bold">DELETE</span> to confirm
            </label>
            <input
              value={delConfirm} onChange={e => setDelConfirm(e.target.value)}
              placeholder="DELETE"
              disabled={delBusy}
              className="w-full bg-slate-800 border border-red-900 rounded-lg px-3 py-2
                         text-white text-sm focus:outline-none focus:border-red-500 transition
                         disabled:opacity-60"
            />
          </div>
          {delError && (
            <div className="bg-red-900/20 border border-red-800 text-red-400 text-sm px-4 py-2 rounded-lg">
              {delError}
            </div>
          )}
          <button
            type="submit" disabled={delBusy || delConfirm !== 'DELETE'}
            className="px-5 py-2 bg-red-700 hover:bg-red-600 disabled:opacity-40
                       text-white rounded-lg text-sm font-medium transition"
          >
            {delBusy ? 'Deleting…' : 'Delete My Account'}
          </button>
        </form>
      </Section>
    </div>
  )
}
