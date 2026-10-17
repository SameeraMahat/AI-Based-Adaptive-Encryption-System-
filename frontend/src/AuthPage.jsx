import { useState } from 'react'
import './AuthPage.css'

const API_URL = 'http://127.0.0.1:5000/api'

function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const isRegister = mode === 'register'

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setMessage('')

    if (isRegister && password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    if (password.length < 6) {
      setError('Password must contain at least 6 characters.')
      return
    }

    setLoading(true)

    try {
      const response = await fetch(
        `${API_URL}/auth/${isRegister ? 'register' : 'login'}`,
        {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(
            isRegister
              ? { username: username.trim(), email: email.trim(), password }
              : { email: email.trim(), password }
          ),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.message || data.error || 'Authentication failed.'
        )
      }

      if (isRegister) {
        setMode('login')
        setPassword('')
        setConfirmPassword('')
        setMessage('Account created successfully. Please sign in.')
      } else {
        onAuthenticated(data.user)
      }
    } catch (err) {
      setError(
        err.message || 'Could not connect to the authentication server.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="auth-screen">
      <section className="auth-panel">
        <div className="auth-brand">
          <div className="auth-logo">◆</div>
          <div>
            <h1>Adaptive Encryption</h1>
            <p>AI-Powered Security System</p>
          </div>
        </div>

        <div className="auth-heading">
          <span className="auth-eyebrow">
            YOUR FILES. YOUR SECURITY.
          </span>

          <h2>
            {isRegister ? 'Create your account' : 'Welcome back'}
          </h2>

          <p>
            {isRegister
              ? 'Register to protect and manage your files securely.'
              : 'Sign in to access your secure encryption workspace.'}
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {isRegister && (
            <label>
              Username
              <input
                id="username"
                name="username"
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Choose a username"
                autoComplete="username"
                required
                maxLength={50}
              />
            </label>
          )}

          <label>
            Email address
            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
              required
            />
          </label>

          <label>
            Password
            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="At least 6 characters"
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              minLength={6}
              required
            />
          </label>

          {isRegister && (
            <label>
              Confirm password
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                placeholder="Enter your password again"
                autoComplete="new-password"
                minLength={6}
                required
              />
            </label>
          )}

          {error && (
            <div className="auth-alert auth-error" role="alert">
              {error}
            </div>
          )}

          {message && (
            <div className="auth-alert auth-success" role="status">
              {message}
            </div>
          )}

          <button className="auth-submit" type="submit" disabled={loading}>
            {loading
              ? 'Please wait...'
              : isRegister
                ? 'Create account'
                : 'Sign in securely'}
          </button>
        </form>

        <div className="auth-switch">
          {isRegister
            ? 'Already have an account?'
            : "Don't have an account?"}

          <button
            type="button"
            onClick={() => {
              setMode(isRegister ? 'login' : 'register')
              setError('')
              setMessage('')
              setPassword('')
              setConfirmPassword('')
            }}
          >
            {isRegister ? 'Sign in' : 'Create account'}
          </button>
        </div>

        <p className="auth-footer">
          AI-Based Adaptive Encryption System
        </p>
      </section>

      <aside className="auth-aside">
        <div className="auth-orbit auth-orbit-one" />
        <div className="auth-orbit auth-orbit-two" />
        <div className="auth-orbit auth-orbit-three" />

        <div className="auth-aside-content">
          <div className="auth-shield">◆</div>
          <span>INTELLIGENT FILE PROTECTION</span>
          <h2>Your security, adapted to every file.</h2>
          <p>
            Analyze file sensitivity, select an adaptive encryption
            strategy, and manage your encrypted files in one workspace.
          </p>

          <div className="auth-benefits">
            <div><span>✓</span> Personal file history</div>
            <div><span>✓</span> Account-protected decryption</div>
            <div><span>✓</span> Adaptive encryption strategies</div>
          </div>
        </div>
      </aside>
    </main>
  )
}

export default AuthPage