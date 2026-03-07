import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiFetch } from '../auth'
import './CreateArticle.css'

export default function CreateArticle() {
  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')
  const [source, setSource] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const res = await apiFetch('/articles', {
        method: 'POST',
        body: JSON.stringify({
          title: title.trim(),
          abstract: abstract.trim() || null,
          source: source.trim() || null,
        }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail ?? 'Failed to create')
      }
      const data = await res.json()
      navigate(`/articles/${data.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed')
    }
  }

  return (
    <div className="create-article">
      <h1>Add article metadata</h1>
      <form onSubmit={handleSubmit}>
        {error && <div className="form-error">{error}</div>}
        <label>Title *</label>
        <input value={title} onChange={e => setTitle(e.target.value)} required maxLength={1024} />
        <label>Abstract</label>
        <textarea value={abstract} onChange={e => setAbstract(e.target.value)} rows={4} />
        <label>Source (journal/conference)</label>
        <input value={source} onChange={e => setSource(e.target.value)} maxLength={255} />
        <div className="form-actions">
          <button type="submit">Create</button>
          <button type="button" onClick={() => navigate('/articles')}>Cancel</button>
        </div>
      </form>
    </div>
  )
}
