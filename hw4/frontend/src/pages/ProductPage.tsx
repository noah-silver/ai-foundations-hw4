import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice, type ProductDetail } from '../api'

const LOW_STOCK = 5

export default function ProductPage() {
  const { productId = '' } = useParams()
  const [product, setProduct] = useState<ProductDetail | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    setProduct(null)
    setError('')
    fetchProduct(productId)
      .then(setProduct)
      .catch(() => setError('We could not find that item in the stockroom.'))
  }, [productId])

  if (error) {
    return (
      <section className="container section">
        <p className="error">{error}</p>
        <Link to="/products" className="text-link">
          ← Back to all products
        </Link>
      </section>
    )
  }

  if (!product) return <section className="container section muted">Loading…</section>

  const inStock = product.total_stock > 0

  return (
    <section className="container section">
      <nav className="crumbs">
        <Link to="/products">Products</Link> <span>/</span> {product.name}
      </nav>
      <div className="detail">
        <div className="detail-img">
          <img src={product.image_url} alt={product.name} />
        </div>
        <div className="detail-info">
          <p className="eyebrow">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="detail-price">{formatPrice(product.price)}</p>
          <p className={`stock ${inStock ? 'in' : 'out'}`}>{inStock ? 'In stock' : 'Sold out in all sizes'}</p>

          <p className="detail-desc">{product.description}</p>

          <h4>Colors</h4>
          <ul className="tag-list">
            {product.colors.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>

          <h4>Sizes</h4>
          <ul className="sizes">
            {product.inventory.map((s) => (
              <li key={s.size} className={s.quantity === 0 ? 'out' : ''}>
                <strong>{s.size}</strong>
                <span>
                  {s.quantity === 0 ? 'Sold out' : s.quantity <= LOW_STOCK ? `Only ${s.quantity} left` : 'Available'}
                </span>
              </li>
            ))}
          </ul>

          <h4>Good for</h4>
          <ul className="tag-list subtle">
            {product.search_tags.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>

          <Link to="/products" className="text-link back">
            ← Back to all products
          </Link>
        </div>
      </div>
    </section>
  )
}
