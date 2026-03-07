import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../auth'
import './Profile.css'

type ProfileData = {
  user: { id: string; email: string; full_name: string | null; role: string; is_active: boolean }
  articles_count: number
  recent_articles: Array<{
    id: string
    title: string
    source: string | null
    published_at: string | null
    created_at: string
  }>
}

export default function Profile() {
  const [data, setData] = useState<ProfileData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiFetch('/profile')
      .then(r => {
        if (!r.ok) throw new Error('Failed to load')
        return r.json()
      })
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="loading-placeholder">Загрузка профиля…</p>
  if (!data) return <p className="loading-placeholder">Не удалось загрузить профиль.</p>

  const { user, articles_count, recent_articles } = data
  const initials = user.full_name
    ? user.full_name.split(/\s+/).map(n => n[0]).slice(0, 2).join('').toUpperCase()
    : user.email.slice(0, 2).toUpperCase()

  return (
    <div className="profile-page">
      <div className="profile-hero">
        <div className="profile-hero-glow" />
        <div className="profile-avatar">
          <span className="avatar-initials">{initials}</span>
        </div>
        <h1 className="profile-name">{user.full_name || user.email}</h1>
        <p className="profile-email">{user.email}</p>
        <span className={`profile-role profile-role-${user.role}`}>{user.role === 'admin' ? 'Администратор' : 'Исследователь'}</span>
      </div>

      <div className="profile-stats">
        <div className="stat-card">
          <span className="stat-icon">📚</span>
          <span className="stat-value">{articles_count}</span>
          <span className="stat-label">Публикаций</span>
        </div>
        <div className="stat-card">
          <span className="stat-icon">📄</span>
          <span className="stat-value">{recent_articles.length}</span>
          <span className="stat-label">Недавних</span>
        </div>
      </div>

      <section className="profile-section">
        <div className="profile-section-header">
          <h2>Мои публикации</h2>
          <Link to="/articles/new" className="btn-primary">Добавить статью</Link>
        </div>
        <p className="profile-section-desc">
          Система для сбора и анализа метаданных научных публикаций. Здесь отображаются статьи, которые вы добавили.
        </p>
        {recent_articles.length === 0 ? (
          <div className="profile-empty">
            <div className="profile-empty-icon">📑</div>
            <p>Пока нет публикаций</p>
            <Link to="/articles/new" className="btn-primary">Добавить первую статью</Link>
          </div>
        ) : (
          <ul className="profile-articles">
            {recent_articles.map(a => (
              <li key={a.id}>
                <Link to={`/articles/${a.id}`} className="profile-article-link">
                  <span className="profile-article-title">{a.title}</span>
                  <span className="profile-article-meta">
                    {a.source && <span>{a.source}</span>}
                    {a.published_at && <span>{new Date(a.published_at).toLocaleDateString()}</span>}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
        {articles_count > recent_articles.length && (
          <Link to="/articles?mine=1" className="profile-view-all">Все публикации ({articles_count}) →</Link>
        )}
      </section>

      <section className="profile-about">
        <h2>О системе</h2>
        <p>
          <strong>Scientific Data Harvester</strong> — платформа для исследователей, позволяющая собирать, хранить и анализировать
          метаданные научных статей: название, аннотацию, авторов, DOI, источник, ключевые слова. Поиск, фильтрация и экспорт данных.
        </p>
      </section>
    </div>
  )
}
