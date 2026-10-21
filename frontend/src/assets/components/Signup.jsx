import React, { useState } from "react";
import "./Signup.css";

export default function Signup() {

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [form, setForm] = useState({
    organizationName: "",
    organizationEmail: "",
    fullName: "",
    username: "",
    workEmail: "",
    password: "",
    confirmPassword: "",
    terms: false,
  });

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (form.password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (!form.terms) {
      setError("Please accept the Terms & Conditions.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/auth/signup",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
         body: JSON.stringify({
  organization_name: form.organizationName.trim(),
  organization_email: form.organizationEmail.trim(),
  full_name: form.fullName.trim(),
  username: form.username.trim(),
  email: form.workEmail.trim(),
  password: form.password,
  confirm_password: form.confirmPassword,
  role: "organization_admin",
}),
        }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok || data.success === false) {
        throw new Error(
          data.error || data.message || "Signup failed. Please try again."
        );
      }

      setSuccess("Organization Admin account created successfully!");

      setTimeout(() => {
         window.location.href = "/login";
      }, 1200);
    } catch (err) {
      setError(
        err.message ||
          "Cannot connect to the server. Please check your backend."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-card">
        <section className="signup-brand">
          <div className="signup-logo">
            <span>AE</span>
          </div>

          <p className="signup-eyebrow">SECURE ORGANIZATION ACCESS</p>

          <h1>
            Adaptive
            <br />
            Encryption
            <br />
            System
          </h1>

          <p className="signup-description">
            Intelligent security. Adaptive protection. Complete control
            over your organization's encryption environment.
          </p>

          <div className="signup-security">
            <span className="signup-security-dot" />
            Secure account registration
          </div>

          <div className="signup-brand-footer">
            AI-POWERED DATA PROTECTION
          </div>
        </section>

        <section className="signup-form-panel">
          <div className="signup-heading">
            <span className="signup-tag">ADMIN REGISTRATION</span>
            <h2>Create your account</h2>
            <p>
              Register your organization and set up your administrator
              account.
            </p>
          </div>

          {error && (
            <div className="signup-message signup-error" role="alert">
              {error}
            </div>
          )}

          {success && (
            <div className="signup-message signup-success" role="status">
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="signup-section-title">
              <span>01</span> Organization details
            </div>

            <div className="signup-field">
              <label htmlFor="organizationName">Organization name</label>
              <input
                id="organizationName"
                name="organizationName"
                type="text"
                placeholder="Enter organization name"
                value={form.organizationName}
                onChange={handleChange}
                autoComplete="organization"
                required
              />
            </div>

            <div className="signup-field">
              <label htmlFor="organizationEmail">Organization email</label>
              <input
                id="organizationEmail"
                name="organizationEmail"
                type="email"
                placeholder="admin@organization.com"
                value={form.organizationEmail}
                onChange={handleChange}
                autoComplete="email"
                required
              />
            </div>

            <div className="signup-section-title signup-account-title">
              <span>02</span> Administrator details
            </div>

            <div className="signup-two-columns">
              <div className="signup-field">
                <label htmlFor="fullName">Full name</label>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  placeholder="Your full name"
                  value={form.fullName}
                  onChange={handleChange}
                  autoComplete="name"
                  required
                />
              </div>

              <div className="signup-field">
                <label htmlFor="username">Username</label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  placeholder="Choose username"
                  value={form.username}
                  onChange={handleChange}
                  autoComplete="username"
                  required
                />
              </div>
            </div>

            <div className="signup-field">
              <label htmlFor="workEmail">Admin work email</label>
              <input
                id="workEmail"
                name="workEmail"
                type="email"
                placeholder="you@organization.com"
                value={form.workEmail}
                onChange={handleChange}
                autoComplete="email"
                required
              />
            </div>

            <div className="signup-two-columns">
              <div className="signup-field">
                <label htmlFor="password">Password</label>
                <div className="signup-password-wrap">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Minimum 8 characters"
                    value={form.password}
                    onChange={handleChange}
                    autoComplete="new-password"
                    minLength={8}
                    required
                  />
                  <button
                    type="button"
                    className="signup-toggle"
                    onClick={() => setShowPassword((prev) => !prev)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
              </div>

              <div className="signup-field">
                <label htmlFor="confirmPassword">Confirm password</label>
                <div className="signup-password-wrap">
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Re-enter password"
                    value={form.confirmPassword}
                    onChange={handleChange}
                    autoComplete="new-password"
                    required
                  />
                  <button
                    type="button"
                    className="signup-toggle"
                    onClick={() =>
                      setShowConfirmPassword((prev) => !prev)
                    }
                    aria-label={
                      showConfirmPassword
                        ? "Hide confirm password"
                        : "Show confirm password"
                    }
                  >
                    {showConfirmPassword ? "Hide" : "Show"}
                  </button>
                </div>
              </div>
            </div>

            <label className="signup-terms">
              <input
                type="checkbox"
                name="terms"
                checked={form.terms}
                onChange={handleChange}
              />
              <span>
                I agree to the <a href="/terms">Terms & Conditions</a> and
                privacy policy.
              </span>
            </label>

            <button
              type="submit"
              className="signup-submit"
              disabled={loading}
            >
              {loading ? "Creating account..." : "Create Admin Account"}
              {!loading && <span aria-hidden="true">→</span>}
            </button>
          </form>

          <p className="signup-login">
            Already registered? <a href="/login">Sign in</a>
          </p>

          <p className="signup-form-footer">
            Protected registration · AI-Based Adaptive Encryption System
          </p>
        </section>
      </div>
    </div>
  );
}
