import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { apiFetch } from '../auth'
import './ArticleDetail.css'

type Article = {
  id: string
  title: string
  abstract: string | null
  authors: string[] | null
  doi: string | null
  source: string | null
  published_at: string | null
  keywords: string[] | null
  created_at: string
  updated_at: string
}

export default function ArticleDetail() {
  const { id } = useParams<{ id: string }>()
  const [article, setArticle] = useState<Article | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    apiFetch(`/articles/${id}`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(setArticle)
      .catch(() => setArticle(null))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <p className="loading-placeholder">Loading…</p>
  if (!article) return <p className="loading-placeholder">Article not found. <Link to="/articles">Back to list</Link></p>

  const authors = Array.isArray(article.authors) ? article.authors : (article.authors ? [String(article.authors)] : [])

  return (
    <div className="article-detail">
      <Link to="/articles" className="back">← Back to list</Link>
      <h1>{article.title}</h1>
      {article.source && <p className="source">{article.source}</p>}
      {article.published_at && <p className="date">{new Date(article.published_at).toLocaleDateString()}</p>}
      {article.doi && <p className="doi">DOI: {article.doi}</p>}
      {authors.length > 0 && <p className="authors">Authors: {authors.join(', ')}</p>}
      {article.abstract && <section><h2>Abstract</h2><p>{article.abstract}</p></section>}
      {article.keywords?.length && <p className="keywords">Keywords: {article.keywords.join(', ')}</p>}
      <p className="meta">Created: {new Date(article.created_at).toLocaleString()}</p>
    </div>
  )
}
