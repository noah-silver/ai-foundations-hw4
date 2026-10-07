import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container footer-grid">
        <div>
          <p className="footer-brand">Campus Customs</p>
          <p className="muted-light">
            Outfitters to the Bulldog faithful. Stitched for Saturdays in the Bowl and every reunion after.
          </p>
        </div>
        <div>
          <p className="footer-head">Shop</p>
          <Link to="/products">All products</Link>
          <Link to="/about">Our story</Link>
        </div>
        <div>
          <p className="footer-head">Account</p>
          <Link to="/login">Log in</Link>
          <Link to="/create-account">Create account</Link>
        </div>
        <div>
          <p className="footer-head">Visit</p>
          <p className="muted-light">Chapel Street, New Haven, CT</p>
          <p className="muted-light">Open late on game days</p>
        </div>
      </div>
      <div className="container footer-base">© {new Date().getFullYear()} Campus Customs. Class project, not affiliated with Yale University.</div>
    </footer>
  )
}
