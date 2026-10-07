import { Link } from 'react-router-dom'
import { useChatResults } from '../chatResults'
import ProductCard from '../components/ProductCard'

/**
 * The storefront view driven by the chat. The Outfitter's latest search results land here as
 * product cards. Each card is the same component the Products page uses, so clicking one opens
 * the single-item page from Problem 3.
 */
export default function Shop() {
  const { products, query } = useChatResults()

  return (
    <>
      <section className="page-head">
        <div className="container">
          <p className="eyebrow light">From your conversation</p>
          <h1>Your Outfitter picks</h1>
          <p>
            {products.length > 0
              ? `Showing ${products.length} ${products.length === 1 ? 'item' : 'items'} the Outfitter found${
                  query ? ` for “${query}”` : ''
                }.`
              : 'Ask the Outfitter about a hoodie, a crewneck, a sport, or a residential college, and matches appear here.'}
          </p>
        </div>
      </section>

      <section className="container section">
        {products.length > 0 ? (
          <div className="product-grid">
            {products.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        ) : (
          <p className="muted">
            Open <strong>Ask the Outfitter</strong> at the bottom right and tell it what you're after. You can also
            browse <Link to="/products">all products</Link>.
          </p>
        )}
      </section>
    </>
  )
}
