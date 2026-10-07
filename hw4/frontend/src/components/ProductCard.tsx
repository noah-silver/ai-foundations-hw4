import { Link } from 'react-router-dom'
import { formatPrice, type Product } from '../api'

export default function ProductCard({ product }: { product: Product }) {
  const soldOut = product.total_stock === 0
  return (
    <Link to={`/products/${product.product_id}`} className="product-card">
      <div className="product-card-img">
        <img src={product.image_url} alt={product.name} loading="lazy" />
        {soldOut && <span className="badge">Sold out</span>}
      </div>
      <div className="product-card-body">
        <p className="eyebrow">{product.garment_type}</p>
        <h3>{product.name}</h3>
        <div className="product-card-meta">
          <span className="price">{formatPrice(product.price)}</span>
          <span className="swatches" aria-label={product.colors.join(', ')}>
            {product.colors.length} {product.colors.length === 1 ? 'color' : 'colors'}
          </span>
        </div>
      </div>
    </Link>
  )
}
