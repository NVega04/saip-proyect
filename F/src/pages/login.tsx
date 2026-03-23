import { useState, ChangeEvent } from "react";
import React from "react";
import './login.css';
import ForgotPasswordModal from "../components/ForgotPasswordModal.tsx";

export default function Login() {
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [remember, setRemember] = useState<boolean>(false);
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showForgot, setShowForgot] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/session/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        alert(error.detail || "Credenciales inválidas.");
        return;
      }

      const data = await response.json();
      localStorage.setItem("session_token", data.session_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      window.location.href = "/dashboard";

    } catch {
      alert("Error de conexión con el servidor.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-root">
      <div className="login-body">
        <div className="card-outer">
          <div className="card-inner">

            {/* ── Panel izquierdo ── */}
            <div className="panel-image" />

            {/* ── Panel derecho ── */}
            <div className="panel-form">
              <h1 className="form-title">Iniciar sesión</h1>
              <p className="form-desc">Ingrese sus credenciales para acceder a su cuenta.</p>

              <form onSubmit={handleSubmit}>
                <div className="field-group">
                  <label className="field-label" htmlFor="email">Usuario</label>
                  <input
                    id="email"
                    type="text"
                    className="field-input"
                    placeholder="Su nombre de usuario o correo electrónico"
                    value={email}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                    autoComplete="username"
                  />
                </div>
                <div className="field-group">
                  <label className="field-label" htmlFor="password">Contraseña</label>
                  <div className="field-wrapper">
                    <input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      className="field-input has-icon"
                      placeholder="Ingrese su contraseña"
                      value={password}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                      autoComplete="current-password"
                    />
                    <button
                      type="button"
                      className="toggle-pw"
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                    >
                      {showPassword ? (
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                          <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/>
                          <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/>
                          <line x1="1" y1="1" x2="23" y2="23"/>
                        </svg>
                      ) : (
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                          <circle cx="12" cy="12" r="3"/>
                        </svg>
                      )}
                    </button>
                  </div>
                </div>

                <div className="options-row">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={remember}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setRemember(e.target.checked)}
                    />
                    Recordar contraseña
                  </label>
                  <a href="#" className="forgot-link" onClick={(e) => {e.preventDefault(); setShowForgot(true); }}>¿Olvidó su contraseña?</a>
                </div>

                <button type="submit" className="btn-submit" disabled={isLoading}>
                  {isLoading && <span className="btn-spinner" />}
                  {isLoading ? "Verificando..." : "Iniciar sesión"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* ── Footer ── */}
      <footer className="login-footer">
        <div className="footer-links">
          <a href="#" className="footer-link">Contacto</a>
          <a href="#" className="footer-link">SAIP</a>
        </div>
        <div className="footer-social">
          <div className="footer-icon">
            <svg viewBox="0 0 24 24">
              <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
            </svg>
          </div>
          <div className="footer-icon">
            <svg viewBox="0 0 24 24">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
              <circle cx="12" cy="12" r="4"/>
              <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>
            </svg>
          </div>
        </div>
      </footer>
      {showForgot && <ForgotPasswordModal onClose={() => setShowForgot(false)} />}
    </div>
  );
}