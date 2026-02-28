import './ResultsList.css'

export function ResultsList({ items, query }) {
  if (items.length === 0) {
    return (
      <div className="results-empty">
        По запросу «{query}» ничего не найдено.
      </div>
    )
  }

  return (
    <section className="results">
      <h2 className="results-title">
        Университеты по запросу «{query}»
      </h2>
      <ul className="results-list">
        {items.map((item, i) => (
          <li key={`${item.organization_id}-${i}`} className="result-card">
            <span className="result-rank">{i + 1}</span>
            <div className="result-body">
              <h3 className="result-name">{item.organization_name}</h3>
              <p className="result-meta">
                Средний коэффициент: <strong>{item.average_coefficient.toFixed(2)}</strong>
              </p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
