import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { apiFetch } from '../auth'
import './Articles.css'

type Article = {
  id: string
  title: string
  source: string | null
  published_at: string | null
  created_at: string
}

type ListResponse = { items: Article[]; total: number; skip: number; limit: number }

export default function Articles() {
  const [searchParams] = useSearchParams()
  const mine = searchParams.get('mine') === '1'
  const [items, setItems] = useState<Article[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const limit = 20

  useEffect(() => {
    let cancelled = false
    const params = new URLSearchParams({
      skip: String(page * limit),
      limit: String(limit),
      ...(search ? { search } : {}),
      ...(mine ? { mine: 'true' } : {}),
    })
    apiFetch(`/articles?${params}`)
      .then(r => r.ok ? r.json() : Promise.reject(new Error('Failed to load')))
      .then((data: ListResponse) => {
        if (!cancelled) {
          setItems(data.items)
          setTotal(data.total)
        }
      })
      .catch(() => { if (!cancelled) setItems([]); setTotal(0) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [page, search, mine])

  const totalPages = Math.ceil(total / limit) || 1

  return (
    <div className="articles-page">
      <h1>{mine ? 'Мои публикации' : 'Метаданные статей'}</h1>
      <div className="articles-toolbar">
        <input
          type="search"
          placeholder="Search by title or abstract..."
          value={search}
          onChange={e => { setSearch(e.target.value); setPage(0) }}
        />
        <Link to="/articles/new" className="btn-primary">Add article</Link>
      </div>
      {loading ? <p className="loading-placeholder">Loading…</p> : items.length === 0 ? (
        <div className="articles-empty">
          <div className="articles-empty-icon">📚</div>
          <h2>Пока нет статей</h2>
          <p>Добавьте первую статью, чтобы начать собирать метаданные публикаций.</p>
          <Link to="/articles/new" className="btn-primary">Добавить статью</Link>
        </div>
      ) : (
        <>
          <ul className="articles-list">
            {items.map(a => (
              <li key={a.id}>
                <Link to={`/articles/${a.id}`}>{a.title}</Link>
                {a.source && <span className="meta">{a.source}</span>}
                {a.published_at && <span className="meta">{new Date(a.published_at).toLocaleDateString()}</span>}
              </li>
            ))}
          </ul>
          {totalPages > 1 && (
            <div className="pagination">
              <button disabled={page === 0} onClick={() => setPage(p => p - 1)}>Prev</button>
              <span>Page {page + 1} of {totalPages}</span>
              <button disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}>Next</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
