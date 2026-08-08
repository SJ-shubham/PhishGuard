import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchMe = useCallback(async () => {
    try {
      const { data } = await client.get('/auth/me')
      setUser(data)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (sessionStorage.getItem('access_token')) fetchMe()
    else setLoading(false)
  }, [fetchMe])

  const login = async (email, password) => {
    const { data } = await client.post('/auth/login', { email, password })
    sessionStorage.setItem('access_token',  data.access_token)
    sessionStorage.setItem('refresh_token', data.refresh_token)
    await fetchMe()
  }

  const register = async (name, email, password) => {
    const { data } = await client.post('/auth/register', { name, email, password })
    sessionStorage.setItem('access_token',  data.access_token)
    sessionStorage.setItem('refresh_token', data.refresh_token)
    await fetchMe()
  }

  const logout = async () => {
    try { await client.post('/auth/logout') } catch {}
    sessionStorage.clear()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, fetchMe }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
