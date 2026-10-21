
import React, { useState } from "react";
import "./Login.css";

export default function Login() {
  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: form.email.trim(),
            password: form.password,
          }),
        }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok || data.success === false) {
        throw new Error(
          data.message || data.error || "Login failed. Check your credentials."
        );
      }

      if (!data.user) {
        throw new Error("Login response did not contain user details.");
      }

      // Store basic login state for the frontend.
      // Protect sensitive API operations on the backend as well.
      localStorage.setItem("user", JSON.stringify(data.user));
      setSuccess("Login successful! Opening your dashboard...");

      setTimeout(() => {
        window.location.href = "/";
      }, 700);
    } catch (err) {
      setError(
        err.message || "Cannot connect to the server. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <div className="login-card">
        <section className="login-brand">
          <div className="login-brand-top">
            <div className="login-logo">AE</div>
            <div>
              <strong>Adaptive Encryption</strong>
              <span>AI-Powered Security System</span>
            </div>
          </div>

          <p className="login-eyebrow">ENTERPRISE DATA PROTECTION</p>

          <h1>
            Your security.
            <br />
            <span>Your control.</span>
          </h1>

          <p className="login-description">
            Sign in to securely analyze, encrypt and manage your
            organization's files with intelligent adaptive protection.
          </p>

          <div className="login-feature">
            <span className="login-feature-icon">✦</span>
            <div>
              <strong>AI-Powered Analysis</strong>
              <span>Intelligent file sensitivity detection</span>
            </div>
          </div>

          <div className="login-feature">
            <span className="login-feature-icon">♙</span>
            <div>
              <strong>Adaptive Encryption</strong>
              <span>Protection tailored to your files</span>
            </div>
          </div>

          <div className="login-brand-footer">
            A SAFER TOMORROW · INTELLIGENT SECURITY
          </div>
        </section>

        <section className="login-form-panel">
          <div className="login-heading">
            <span className="login-tag">WELCOME BACK</span>
            <h2>Sign in to your account</h2>
            <p>Enter your work email and password to continue.</p>
          </div>

          {error && (
            <div className="login-message login-error" role="alert">
              {error}
            </div>
          )}

          {success && (
            <div className="login-message login-success" role="status">
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="login-field">
              <label htmlFor="login-email">Work email</label>
              <input
                id="login-email"
                type="email"
                name="email"
                placeholder="you@organization.com"
                value={form.email}
                onChange={handleChange}
                autoComplete="email"
                required
              />
            </div>

            <div className="login-field">
              <label htmlFor="login-password">Password</label>
              <div className="login-password-wrap">
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  name="password"
                  placeholder="Enter your password"
                  value={form.password}
                  onChange={handleChange}
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  className="login-toggle"
                  onClick={() => setShowPassword((prev) => !prev)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="login-submit"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign In"}
              {!loading && <span aria-hidden="true">→</span>}
            </button>
          </form>

          <div className="login-divider">
            <span />
            <span>SECURE ACCESS</span>
            <span />
          </div>

          <p className="login-signup">
            New to Adaptive Encryption? <a href="/signup">Create account</a>
          </p>

          <p className="login-form-footer">
            Protected access · AI-Based Adaptive Encryption System
          </p>
        </section>
      </div>
    </main>
  );
}
