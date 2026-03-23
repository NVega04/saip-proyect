import { useState, ChangeEvent } from "react";
import "./reset-password.css";
import { useSearchParams, useNavigate } from "react-router-dom";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") ?? "";

  const [newPassword, setNewPassword] = useState<string>("");
  const [confirm, setConfirm] = useState<string>("");
  const [showNew, setShowNew] = useState<boolean>(false);
  const [showConfirm, setShowConfirm] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setError("");

    if (!token) {
      setError("Token inválido o expirado.");
      return;
    }

    if (newPassword.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
      return;
    }

    if (newPassword !== confirm) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/session/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: newPassword }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail ?? "Error al restablecer la contraseña.");
        return;
      }

      setSuccess(true);
      setTimeout(() => navigate("/"), 3000);
    } catch {
      setError("No se pudo conectar con el servidor.");
    } finally {
      setIsLoading(false);
    }
  };

  const EyeIcon = ({ open }: { open: boolean }) =>
    open ? (
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94" />
        <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19" />
        <line x1="1" y1="1" x2="23" y2="23" />
      </svg>
    ) : (
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
        <circle cx="12" cy="12" r="3" />
      </svg>
    );

  return (
    <div className="login-root">
      <div className="login-body">
        <div className="card-outer">
          <div className="card-inner">

            {/* ── Panel izquierdo ── */}
            <div className="panel-image" />

            {/* ── Panel derecho ── */}
            <div className="panel-form">
              {success ? (
                <div className="success-state">
                  <div className="success-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 6L9 17l-5-5" />
                    </svg>
                  </div>
                  <h1 className="form-title">¡Contraseña actualizada!</h1>
                  <p className="form-desc">Tu contraseña fue restablecida correctamente. Serás redirigido al inicio de sesión en unos segundos.</p>
                </div>
              ) : (
                <>
                  <h1 className="form-title">Restablecer contraseña</h1>
                  <p className="form-desc">Ingrese y confirme su nueva contraseña para recuperar el acceso a su cuenta.</p>

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
                        <button
                          type="button"
                          className="toggle-pw"
                          onClick={() => setShowNew(!showNew)}
                          aria-label={showNew ? "Ocultar contraseña" : "Mostrar contraseña"}
                        >
                          <EyeIcon open={showNew} />
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
                          placeholder="Repita su nueva contraseña"
                          value={confirm}
                          onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirm(e.target.value)}
                          autoComplete="new-password"
                        />
                        <button
                          type="button"
                          className="toggle-pw"
                          onClick={() => setShowConfirm(!showConfirm)}
                          aria-label={showConfirm ? "Ocultar contraseña" : "Mostrar contraseña"}
                        >
                          <EyeIcon open={showConfirm} />
                        </button>
                      </div>
                    </div>

                    {error && <p className="error-msg">{error}</p>}

                    <button type="submit" className="btn-submit" disabled={isLoading}>
                      {isLoading && <span className="btn-spinner" />}
                      {isLoading ? "Procesando..." : "Restablecer contraseña"}
                    </button>

                    <div className="back-row">
                      <a href="/" className="forgot-link">Volver al inicio de sesión</a>
                    </div>
                  </form>
                </>
              )}
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
              <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
            </svg>
          </div>
          <div className="footer-icon">
            <svg viewBox="0 0 24 24">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
              <circle cx="12" cy="12" r="4" />
              <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" />
            </svg>
          </div>
        </div>
      </footer>
    </div>
  );
}