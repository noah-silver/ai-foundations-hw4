import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

const links = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  return (
    <header className="site-header">
      <div className="ribbon">Kickoff Weekend: The Bowl opens Saturday · Free shipping over $100</div>
      <nav className="nav container">
        <Link to="/" className="brand">
          <span className="brand-mark">CC</span>
          <span className="brand-text">
            Campus Customs
            <small>New Haven, Connecticut</small>
          </span>
        </Link>
        <ul className="nav-links">
          {links.map((l) => (
            <li key={l.to}>
              <NavLink to={l.to} end={l.end}>
                {l.label}
              </NavLink>
            </li>
          ))}
        </ul>
        <div className="nav-account">
          {user ? (
            <>
              <span className="nav-greeting">Hi, {user.first_name || user.name}</span>
              <button className="btn btn-small" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login">Log in</NavLink>
              <NavLink to="/create-account" className="btn btn-small">
                Create account
              </NavLink>
            </>
          )}
        </div>
      </nav>
    </header>
  )
}
