import { useAuth } from '../auth'
import './Admin.css'

export default function Admin() {
  const { user } = useAuth()

  return (
    <div className="admin-page">
      <h1>Admin</h1>
      <p className="admin-welcome">
        You are logged in as <strong>{user?.email}</strong> (role: <strong>{user?.role}</strong>).
      </p>
      <section className="admin-section">
        <h2>Admin panel</h2>
        <p>Here you can manage users and content. Only users with role <code>admin</code> can access this page.</p>
        <p>As admin you can edit and delete any article (not only your own).</p>
      </section>
    </div>
  )
}
