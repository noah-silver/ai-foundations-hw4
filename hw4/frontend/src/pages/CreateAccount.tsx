import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export default function CreateAccount() {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const data = new FormData(e.currentTarget)
    if (data.get('password') !== data.get('confirm')) {
      setError('Passwords do not match.')
      return
    }
    setBusy(true)
    setError('')
    try {
      await signup({
        first_name: String(data.get('first_name')),
        last_name: String(data.get('last_name')),
        email: String(data.get('email')),
        password: String(data.get('password')),
      })
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create account.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="auth container">
      <div className="auth-card">
        <p className="eyebrow">Join the section</p>
        <h1>Create account</h1>
        <p className="muted">Save your sizes, keep your chat history, and hear first when rivalry-week gear drops.</p>
        <form onSubmit={handleSubmit}>
          <div className="row">
            <label>
              First name
              <input name="first_name" autoComplete="given-name" required />
            </label>
            <label>
              Last name
              <input name="last_name" autoComplete="family-name" required />
            </label>
          </div>
          <label>
            Email
            <input type="email" name="email" autoComplete="email" required />
          </label>
          <label>
            Password
            <input type="password" name="password" autoComplete="new-password" minLength={8} required />
          </label>
          <label>
            Confirm password
            <input type="password" name="confirm" autoComplete="new-password" minLength={8} required />
          </label>
          <button className="btn full" type="submit" disabled={busy}>
            {busy ? 'Creating account…' : 'Create account'}
          </button>
        </form>
        {error && <p className="error">{error}</p>}
        <p className="muted small">
          Already a member? <Link to="/login">Log in</Link>
        </p>
      </div>
    </section>
  )
}
