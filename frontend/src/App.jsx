import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar     from './components/Navbar'
import Login      from './pages/Login'
import Register   from './pages/Register'
import Dashboard  from './pages/Dashboard'
import History    from './pages/History'
import ScanDetail from './pages/ScanDetail'
import BulkScan   from './pages/BulkScan'
import Profile    from './pages/Profile'

function Spinner() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <Spinner />
  return user ? children : <Navigate to="/login" replace />
}

function Layout({ children }) {
  return <><Navbar /><main className="max-w-5xl mx-auto px-4 py-8">{children}</main></>
}

function AppRoutes() {
  const { user } = useAuth()
  return (
    <Routes>
      <Route path="/login"    element={user ? <Navigate to="/" /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/" /> : <Register />} />
      <Route path="/" element={
        <Protected><Layout><Dashboard /></Layout></Protected>
      } />
      <Route path="/history" element={
        <Protected><Layout><History /></Layout></Protected>
      } />
      <Route path="/scan/:id" element={
        <Protected><Layout><ScanDetail /></Layout></Protected>
      } />
      <Route path="/bulk" element={
        <Protected><Layout><BulkScan /></Layout></Protected>
      } />
      <Route path="/profile" element={
        <Protected><Layout><Profile /></Layout></Protected>
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}
