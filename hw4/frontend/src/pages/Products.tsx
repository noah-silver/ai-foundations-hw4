import { useEffect, useMemo, useState } from 'react'
import { CATEGORIES, category, fetchProducts, type Product } from '../api'
import ProductCard from '../components/ProductCard'

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [active, setActive] = useState('All')
  const [query, setQuery] = useState('')

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch(() => setError('We could not reach the stockroom. Is the backend running?'))
      .finally(() => setLoading(false))
  }, [])

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase()
    return products.filter((p) => {
      if (active !== 'All' && category(p.garment_type) !== active) return false
      if (!q) return true
      return [p.name, p.garment_type, p.description, ...p.colors, ...p.search_tags].join(' ').toLowerCase().includes(q)
    })
  }, [products, active, query])

  return (
    <>
      <section className="page-head">
        <div className="container">
          <p className="eyebrow light">The Full Roster</p>
          <h1>Products</h1>
          <p>Every crest, every college, every cut we carry, from the Bowl to the reunion tent.</p>
        </div>
      </section>

      <section className="container section">
        <div className="toolbar">
          <div className="chips">
            {['All', ...CATEGORIES].map((c) => (
              <button key={c} className={`chip ${active === c ? 'active' : ''}`} onClick={() => setActive(c)}>
                {c}
              </button>
            ))}
          </div>
          <input
            className="search"
            type="search"
            placeholder="Search by college, sport, or color"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        {loading && <p className="muted">Pulling the lineup from the locker room…</p>}
        {error && <p className="error">{error}</p>}
        {!loading && !error && (
          <>
            <p className="muted count">
              {visible.length} {visible.length === 1 ? 'item' : 'items'}
            </p>
            <div className="product-grid">
              {visible.map((p) => (
                <ProductCard key={p.product_id} product={p} />
              ))}
            </div>
            {visible.length === 0 && <p className="muted">Nothing matches that search. Try another college or sport.</p>}
          </>
        )}
      </section>
    </>
  )
}
