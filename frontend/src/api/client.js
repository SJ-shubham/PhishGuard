import axios from 'axios'

const client = axios.create({
  baseURL: '',   // Vite proxy handles routing
  headers: { 'Content-Type': 'application/json' },
})

// Attach access token to every request
client.interceptors.request.use(cfg => {
  const token = sessionStorage.getItem('access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// Auto-refresh on 401
client.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = sessionStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post('/auth/refresh', null, {
            headers: { Authorization: `Bearer ${refresh}` },
          })
          sessionStorage.setItem('access_token',  data.access_token)
          sessionStorage.setItem('refresh_token', data.refresh_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return client(original)
        } catch {
          sessionStorage.clear()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(err)
  }
)

export default client
