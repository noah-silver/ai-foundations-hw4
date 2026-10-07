import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProducts, type Product } from '../api'
import ProductCard from '../components/ProductCard'

const FEATURED_IDS = [
  '2025-yale-vs-harvard-t-shirt',
  'champion-reverse-weave-hoodie-1',
  'benjamin-franklin-1-4-zip',
  'baseball-left-chest-crewneck',
]

const pillars = [
  {
    title: 'Game Day Heritage',
    body: 'From the first kickoff in the Bowl to the last verse of the fight song, our gear is cut for long Saturdays in the stands.',
  },
  {
    title: 'Residential College Pride',
    body: 'Crests for all fourteen colleges, stitched with the care a family coat of arms deserves.',
  },
  {
    title: 'Built for the Long Haul',
    body: 'Heavyweight fleece, reverse-weave cotton, and classic cuts that look better at your twenty-fifth reunion than they did at your first.',
  },
]

export default function Home() {
  const [featured, setFeatured] = useState<Product[]>([])

  useEffect(() => {
    fetchProducts()
      .then((all) => {
        const picks = FEATURED_IDS.map((id) => all.find((p) => p.product_id === id)).filter(
          (p): p is Product => Boolean(p),
        )
        setFeatured(picks.length ? picks : all.slice(0, 4))
      })
      .catch(() => setFeatured([]))
  }, [])

  return (
    <>
      <section className="hero">
        <div className="container hero-inner">
          <p className="eyebrow light">Fall Season · Kickoff Collection</p>
          <h1>Saturdays in Blue, since before the forward pass.</h1>
          <p className="hero-lede">
            Campus Customs dresses the Bulldog faithful for tailgates on the lawn, rivalry weekends against
            Cambridge, and the quiet walk back across the Green. Heritage cuts, honest fabrics, and a lot of navy.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="btn btn-light">
              Shop the collection
            </Link>
            <Link to="/about" className="btn btn-outline-light">
              Our story
            </Link>
          </div>
        </div>
      </section>

      <section className="container section">
        <div className="section-head">
          <div>
            <p className="eyebrow">Fresh off the field</p>
            <h2>The Kickoff Lineup</h2>
          </div>
          <Link to="/products" className="text-link">
            View all products →
          </Link>
        </div>
        <div className="product-grid">
          {featured.map((p) => (
            <ProductCard key={p.product_id} product={p} />
          ))}
        </div>
      </section>

      <section className="band">
        <div className="container pillars">
          {pillars.map((p) => (
            <div key={p.title} className="pillar">
              <span className="rule" />
              <h3>{p.title}</h3>
              <p>{p.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="container section rivalry">
        <div>
          <p className="eyebrow">The Game</p>
          <h2>Dress for Harvard week.</h2>
          <p>
            Some rivalries are older than the stadium. When the Crimson come to town, the whole city turns navy.
            Stock up before the tailgates start, because the good sizes go early.
          </p>
          <Link to="/products/2025-yale-vs-harvard-t-shirt" className="btn">
            Shop The Game tee
          </Link>
        </div>
        <blockquote>
          “Win or lose, you always look like you belong in the Bowl.”
          <cite>A season-ticket holder, Class of ’88</cite>
        </blockquote>
      </section>
    </>
  )
}
