import { useState } from 'react'
import './SearchForm.css'

export function SearchForm({ onSearch, loading }) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!query.trim()) return
    onSearch(query.trim())
  }

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <div className="search-row">
        <textarea
          className="search-input"
          placeholder="Напишите, чем планируете заниматься?"
          rows={1}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="search-btn" disabled={loading}>
          {loading ? 'Поиск...' : 'Найти'}
        </button>
      </div>
    </form>
  )
}
