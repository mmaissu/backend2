import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import './Layout.css'

export default function Layout() {
  const { token, user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="layout">
      <header className="layout-header">
        <Link to={token ? '/articles' : '/'} className="layout-brand">Scientific Data Harvester</Link>
        <nav>
          {token && <Link to="/articles">Articles</Link>}
          {token && <Link to="/profile">Профиль</Link>}
          {token && user?.role === 'admin' && <Link to="/admin">Admin</Link>}
          {token ? (
            <button type="button" onClick={handleLogout}>Logout</button>
          ) : (
            <>
              <Link to="/login">Войти</Link>
              <Link to="/register" className="nav-register">Регистрация</Link>
            </>
          )}
        </nav>
      </header>
      <main className="layout-main">
        <Outlet />
      </main>
    </div>
  )
}
