import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <section className="container section">
      <h1>Wide right.</h1>
      <p className="muted">That page missed the uprights.</p>
      <Link to="/" className="btn">
        Back to Home
      </Link>
    </section>
  )
}
