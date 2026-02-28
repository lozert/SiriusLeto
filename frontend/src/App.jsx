import { useState } from 'react'
import { SearchForm } from './components/SearchForm'
import { ResultsList } from './components/ResultsList'
import { useRecommendations } from './hooks/useRecommendations'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const { data, loading, error, fetchRecommendations } = useRecommendations()

  const handleSearch = (q) => {
    setQuery(q)
    fetchRecommendations(q)
  }

  return (
    <div className="app">
      <header className="header">
        <h1 className="logo">SciTinder</h1>
        <p className="tagline">Рекомендации университетов по научным темам</p>
      </header>

      <main className="main">
        <SearchForm onSearch={handleSearch} loading={loading} />

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        {data && <ResultsList items={data} query={query} />}
      </main>
    </div>
  )
}

export default App
