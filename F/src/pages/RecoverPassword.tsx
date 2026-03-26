import { useState, useEffect, ChangeEvent } from "react";
import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "./login.css";
import "./RecoverPassword.css";
import { useAlert } from "../context/AlertContext";

export default function RecoverPassword() {
  const [token, setToken] = useState<string | null>(null);
  const images = [
  "/Images/Pan 1.jpg",
  "/Images/Pan 2.jpg",
  "/Images/Pan 3.jpg",
  "/Images/Pan 4.jpg",
  "/Images/Pan 5.jpeg",
];

const [currentIndex, setCurrentIndex] = useState(0);

useEffect(() => {
  const interval = setInterval(() => {
    setCurrentIndex((prev) => (prev + 1) % images.length);
  }, 3000);

  return () => clearInterval(interval);
}, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setToken(params.get("token"));
  }, []);

  return (
    <div className="login-root">
      <div className="login-body">
        <div className="card-outer">
          <div className="card-inner">
            <div className="panel-image">
              <img
                key={currentIndex}
                src={images[currentIndex]}
                className="carousel-image"
              />

              <div className="carousel-overlay" />

              <div className="carousel-logo-card">
                <img src="/Images/Logo-saip.png" alt="SAIP" />
              </div>
            </div>
            <div className="panel-form">
              {token ? <ResetForm token={token} /> : <ForgotForm />}
            </div>
          </div>
        </div>
      </div>

      <footer className="login-footer">
        <div className="footer-links">
          <a href="#" className="footer-link">Contacto</a>
          <a href="#" className="footer-link">SAIP</a>
          <Link to="/" className="footer-link">Conócenos</Link>
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
    </div>
  );
}

// ── Paso 1: Ingresar email ─────────────────────────────────────────────────
function ForgotForm() {
  const [email, setEmail]         = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sent, setSent]           = useState(false);
  const [error, setError]         = useState<string | null>(null);

  const { showAlert } = useAlert();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!email) {
      setError("Ingresa tu correo electrónico.");
      showAlert("warning", "Ingresa tu correo electrónico.");
      return;
    }
    setError(null);
    setIsLoading(true);
    try {
      showAlert("success", "Si el correo está registrado, recibirás las instrucciones para restablecer tu contraseña.");
      const res = await fetch("http://localhost:8000/session/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) throw new Error();
      setSent(true);
    } catch {
        setError("Error de conexión con el servidor.");
        showAlert("error", "Error de conexión con el servidor.");
    } finally {
      setIsLoading(false);
    }
  };

  if (sent) return (
    <>
      <div className="rp-icon-wrap">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
          stroke="var(--medium)" strokeWidth="1.6" strokeLinecap="round">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
          <polyline points="22,6 12,13 2,6"/>
        </svg>
      </div>
      <h1 className="form-title">Revisa tu correo</h1>
      <p className="form-desc">
        Si <strong>{email}</strong> está registrado, recibirás un enlace
        para restablecer tu contraseña en los próximos minutos.
      </p>
      <p className="rp-hint">¿No lo ves? Revisa tu carpeta de spam.</p>
      <BackLink />
    </>
  );

  return (
    <>
      <div className="rp-icon-wrap">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
          stroke="var(--medium)" strokeWidth="1.6" strokeLinecap="round">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
          <path d="M7 11V7a5 5 0 0110 0v4"/>
        </svg>
      </div>
      <h1 className="form-title">Recuperar contraseña</h1>
      <p className="form-desc">
        Ingresa tu correo y te enviaremos las instrucciones para restablecer tu contraseña.
      </p>

      {error && <div className="rp-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="field-group">
          <label className="field-label" htmlFor="email">Correo electrónico</label>
          <input
            id="email"
            type="email"
            className="field-input"
            placeholder="tucorreo@ejemplo.com"
            value={email}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
            autoComplete="email"
          />
        </div>
        <button type="submit" className="btn-submit" disabled={isLoading}>
          {isLoading && <span className="btn-spinner" />}
          {isLoading ? "Enviando..." : "Enviar instrucciones"}
        </button>
      </form>
      <BackLink />
    </>
  );
}

// ── Paso 2: Nueva contraseña ───────────────────────────────────────────────
function ResetForm({ token }: { token: string }) {
  const navigate                              = useNavigate();
  const { showAlert }                         = useAlert();
  const [newPassword, setNewPassword]         = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showNew, setShowNew]                 = useState(false);
  const [showConfirm, setShowConfirm]         = useState(false);
  const [isLoading, setIsLoading]             = useState(false);
  const [success, setSuccess]                 = useState(false);
  const [error, setError]                     = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
      if (!newPassword || !confirmPassword) {
        setError("Todos los campos son obligatorios.");
        showAlert("warning", "Todos los campos son obligatorios.");
        return;
      }
      if (newPassword !== confirmPassword) {
        setError("Las contraseñas no coinciden.");
        showAlert("warning", "Las contraseñas no coinciden.");
        return;
      }
      if (newPassword.length < 8) {
        setError("La contraseña debe tener al menos 8 caracteres.");
        showAlert("warning", "La contraseña debe tener al menos 8 caracteres.");
        return;
      }
        setError(null);
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/session/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: newPassword }),
      });
      if (!res.ok) {
        const data = await res.json();
        const message = data.detail ?? "El enlace es inválido o ha expirado.";
        setError(message);
        showAlert("error", message);
        return;
      }
      setSuccess(true);
      showAlert("success", "Tu contraseña fue actualizada correctamente.");
      setTimeout(() => navigate("/"), 3000);
    } catch {
        setError("Error de conexión con el servidor.");
        showAlert("error", "Error de conexión con el servidor.");
    } finally {
      setIsLoading(false);
    }
  };

  if (success) return (
    <>
      <div className="rp-icon-wrap rp-icon-wrap--success">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
          stroke="#2e7d32" strokeWidth="1.6" strokeLinecap="round">
          <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
      </div>
      <h1 className="form-title">¡Contraseña actualizada!</h1>
      <p className="form-desc">
        Tu contraseña fue cambiada correctamente. Serás redirigido al
        inicio de sesión en unos segundos.
      </p>
      <Link to="/" className="btn-submit" style={{ textDecoration: "none", marginTop: "0.5rem" }}>
        Ir al inicio de sesión
      </Link>
    </>
  );

  return (
    <>
      <div className="rp-icon-wrap">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
          stroke="var(--medium)" strokeWidth="1.6" strokeLinecap="round">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
          <path d="M7 11V7a5 5 0 0110 0v4"/>
        </svg>
      </div>
      <h1 className="form-title">Nueva contraseña</h1>
      <p className="form-desc">Ingresa y confirma tu nueva contraseña.</p>

      {error && <div className="rp-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="field-group">
          <label className="field-label" htmlFor="new-password">Nueva contraseña</label>
          <div className="field-wrapper">
            <input
              id="new-password"
              type={showNew ? "text" : "password"}
              className="field-input has-icon"
              placeholder="Mínimo 8 caracteres"
              value={newPassword}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setNewPassword(e.target.value)}
              autoComplete="new-password"
            />
            <button type="button" className="toggle-pw" onClick={() => setShowNew(!showNew)}>
              <EyeIcon visible={showNew} />
            </button>
          </div>
        </div>

        <div className="field-group">
          <label className="field-label" htmlFor="confirm-password">Confirmar contraseña</label>
          <div className="field-wrapper">
            <input
              id="confirm-password"
              type={showConfirm ? "text" : "password"}
              className="field-input has-icon"
              placeholder="Repite tu nueva contraseña"
              value={confirmPassword}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
            />
            <button type="button" className="toggle-pw" onClick={() => setShowConfirm(!showConfirm)}>
              <EyeIcon visible={showConfirm} />
            </button>
          </div>
        </div>

        <button type="submit" className="btn-submit" disabled={isLoading}>
          {isLoading && <span className="btn-spinner" />}
          {isLoading ? "Actualizando..." : "Actualizar contraseña"}
        </button>
      </form>
      <BackLink />
    </>
  );
}

// ── Componentes compartidos ────────────────────────────────────────────────
function BackLink() {
  return (
    <div className="rp-back-row">
      <Link to="/login" className="rp-back-link">
        Volver al inicio de sesión
      </Link>
    </div>
  );
}

function EyeIcon({ visible }: { visible: boolean }) {
  return visible ? (
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
  );
}
