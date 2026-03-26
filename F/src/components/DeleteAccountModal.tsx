import { useState } from "react";
import Modal from "./Modal";
import Alerta from "./Alert";
import { apiFetch } from "../utils/api";
import "./DeleteAccountModal.css";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

// Pasos del flujo de confirmación doble
type Step = "confirm_intent" | "confirm_password";

export default function DeleteAccountModal({ isOpen, onClose }: Props) {
  const [step, setStep] = useState<Step>("confirm_intent");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState<{
    show: boolean;
    type: "success" | "error" | "warning";
    message: string;
  }>({ show: false, type: "error", message: "" });

  // Resetear estado al cerrar
  const handleClose = () => {
    setStep("confirm_intent");
    setPassword("");
    setShowPassword(false);
    setAlert({ show: false, type: "error", message: "" });
    onClose();
  };

  // Primer paso: el usuario confirma su intención
  const handleConfirmIntent = () => {
    setStep("confirm_password");
  };

  // Segundo paso: verificar contraseña y ejecutar eliminación
  const handleDeleteAccount = async () => {
    if (!password.trim()) {
      setAlert({
        show: true,
        type: "warning",
        message: "Debes ingresar tu contraseña para confirmar.",
      });
      return;
    }

    setLoading(true);
    try {
      // Verificar la contraseña usando change-password como validación previa
      // o llamar directamente al endpoint de eliminación
      const res = await apiFetch("/users/me", {
        method: "DELETE",
        headers: {
          "X-Confirm-Password": password,
        },
      });

      if (!res.ok) {
        const data = await res.json();
        setAlert({
          show: true,
          type: "error",
          message: data.detail ?? "Error al eliminar la cuenta.",
        });
        return;
      }

      // Limpiar sesión local y redirigir al login
      localStorage.removeItem("session_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    } catch {
      setAlert({
        show: true,
        type: "error",
        message: "Error de conexión. Intenta de nuevo.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Alerta
        show={alert.show}
        type={alert.type}
        message={alert.message}
        onClose={() => setAlert((a) => ({ ...a, show: false }))}
      />

      <Modal
        isOpen={isOpen}
        onClose={handleClose}
        title="Eliminar cuenta"
        width="420px"
      >
        {step === "confirm_intent" ? (
          // ── Paso 1: Advertencia inicial ──────────────────────────────
          <div className="da-container">
            <div className="da-warning-icon">
              <svg
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </div>

            <h3 className="da-title">¿Estás seguro de que deseas eliminar tu cuenta?</h3>

            <p className="da-description">
              Esta acción es <strong>irreversible</strong>. Al confirmar:
            </p>

            <ul className="da-consequences">
              <li>Tu cuenta quedará desactivada de forma permanente.</li>
              <li>Perderás acceso inmediato al sistema.</li>
              <li>Todas tus sesiones activas serán cerradas.</li>
              <li>Un administrador deberá gestionar tus datos.</li>
            </ul>

            <div className="da-actions">
              <button className="da-btn-cancel" onClick={handleClose}>
                Cancelar
              </button>
              <button className="da-btn-danger" onClick={handleConfirmIntent}>
                Sí, quiero eliminar mi cuenta
              </button>
            </div>
          </div>
        ) : (
          // ── Paso 2: Confirmar con contraseña ─────────────────────────
          <div className="da-container">
            <div className="da-lock-icon">
              <svg
                width="28"
                height="28"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0110 0v4" />
              </svg>
            </div>

            <h3 className="da-title">Confirma tu identidad</h3>
            <p className="da-description">
              Ingresa tu contraseña actual para confirmar la eliminación de tu cuenta.
            </p>

            <div className="da-field">
              <label className="da-label">Contraseña</label>
              <div className="da-input-wrapper">
                <input
                  className="da-input"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  onKeyDown={(e) => e.key === "Enter" && handleDeleteAccount()}
                  autoFocus
                />
                <button
                  type="button"
                  className="da-eye-btn"
                  onClick={() => setShowPassword((v) => !v)}
                >
                  {showPassword ? (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94" />
                      <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19" />
                      <line x1="1" y1="1" x2="23" y2="23" />
                    </svg>
                  ) : (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            <div className="da-actions">
              <button
                className="da-btn-cancel"
                onClick={() => setStep("confirm_intent")}
                disabled={loading}
              >
                Atrás
              </button>
              <button
                className="da-btn-danger"
                onClick={handleDeleteAccount}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="da-spinner" />
                    Eliminando...
                  </>
                ) : (
                  "Eliminar mi cuenta"
                )}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
}