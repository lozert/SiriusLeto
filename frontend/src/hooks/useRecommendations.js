import { useState, useCallback } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || '/api'
/** Лимит результатов: не более 50 */
const RESULTS_LIMIT = 50

export function useRecommendations() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchRecommendations = useCallback(async (query) => {
    setLoading(true)
    setError(null)
    setData(null)

    try {
      const params = new URLSearchParams({
        query,
        limit: String(RESULTS_LIMIT),
        top_topics: '10',
      })
      const res = await fetch(
        `${API_BASE}/recommendations/universities-by-coefficients?${params}`
      )
      if (!res.ok) throw new Error(await res.text())
      const json = await res.json()
      setData(json)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки')
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, fetchRecommendations }
}
