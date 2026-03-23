import { useState, ChangeEvent } from "react";
import "./forgot-password-modal.css";

interface Props {
  onClose: () => void;
}

export default function ForgotPasswordModal({ onClose }: Props) {
  const [email, setEmail] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [sent, setSent] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/session/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!res.ok) {
        const data = await res.json();
        setError(data.detail ?? "Error al procesar la solicitud.");
        return;
      }

      setSent(true);
    } catch {
      setError("No se pudo conectar con el servidor.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>

        <button className="modal-close" onClick={onClose} aria-label="Cerrar">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        {sent ? (
          <div className="modal-success">
            <div className="modal-success-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 6L9 17l-5-5" />
              </svg>
            </div>
            <h2 className="modal-title">Correo enviado</h2>
            <p className="modal-desc">
              Si el correo está registrado, recibirás un enlace para restablecer tu contraseña en los próximos minutos.
            </p>
            <button className="btn-submit" onClick={onClose}>
              Volver al inicio de sesión
            </button>
          </div>
        ) : (
          <>
            <div className="modal-header">
              <div className="modal-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0110 0v4" />
                </svg>
              </div>
              <h2 className="modal-title">¿Olvidó su contraseña?</h2>
              <p className="modal-desc">
                Ingrese su correo electrónico y le enviaremos un enlace para restablecer su contraseña.
              </p>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="field-group">
                <label className="field-label" htmlFor="forgot-email">Correo electrónico</label>
                <input
                  id="forgot-email"
                  type="email"
                  className="field-input"
                  placeholder="Su correo electrónico"
                  value={email}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                  autoComplete="email"
                  required
                />
              </div>

              {error && <p className="modal-error">{error}</p>}

              <button type="submit" className="btn-submit" disabled={isLoading}>
                {isLoading && <span className="btn-spinner" />}
                {isLoading ? "Enviando..." : "Enviar enlace"}
              </button>

              <div className="back-row">
                <button type="button" className="forgot-link btn-link" onClick={onClose}>
                  Volver al inicio de sesión
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
}