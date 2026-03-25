import React, { useState, useEffect } from "react";
import Modal from "./Modal";
import { apiFetch, getMe, UserProfile } from "../utils/api";
import "./Profilemodal.css";

// ── Tipos ──────────────────────────────────────────────────────────────────
interface FormState {
  first_name: string;
  last_name: string;
  phone: string;
  email: string;
}

interface PasswordForm {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("es-CO", {
    year: "numeric", month: "long", day: "numeric",
  });
}

function getInitials(first: string, last: string) {
  return `${first[0] ?? ""}${last[0] ?? ""}`.toUpperCase();
}

// ── Modal de perfil ────────────────────────────────────────────────────────
export default function PerfilModal({ isOpen, onClose }: Props) {
  const [user, setUser]             = useState<UserProfile | null>(null);
  const [form, setForm]             = useState<FormState>({ first_name: "", last_name: "", phone: "", email: "" });
  const [editing, setEditing]       = useState(false);
  const [loading, setLoading]       = useState(true);
  const [saving, setSaving]         = useState(false);
  const [showPwModal, setShowPwModal] = useState(false);
  const [toast, setToast]           = useState<{ msg: string; type: "success" | "error" } | null>(null);
  const [loggingOutAll, setLoggingOutAll] = useState(false);

  const handleLogoutAll = async () => {
    setLoggingOutAll(true);
    try {
      const res = await apiFetch("/session/logout-all", { method: "POST" });
      if (!res.ok) throw new Error();
      localStorage.removeItem("session_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    } catch {
      setToast({ msg: "Error al cerrar sesiones", type: "error" });
    } finally {
      setLoggingOutAll(false);
    }
  };
  // Carga usuario al abrir
  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);
    getMe().then((data) => {
      if (data) {
        setUser(data);
        setForm({
          first_name: data.first_name,
          last_name:  data.last_name,
          phone:      data.phone ?? "",
          email:      data.email,
        });
      }
      setLoading(false);
    });
  }, [isOpen]);

  // Auto-ocultar toast
  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(null), 3500);
      return () => clearTimeout(t);
    }
  }, [toast]);

  // Reset al cerrar
  const handleClose = () => {
    setEditing(false);
    setToast(null);
    onClose();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    if (!user) return;
    setSaving(true);
    try {
      const res = await apiFetch(`/users/${user.id}`, {
        method: "PUT",
        body: JSON.stringify({
          first_name: form.first_name,
          last_name:  form.last_name,
          phone:      form.phone || null,
          email:      form.email,
        }),
      });
      if (!res.ok) throw new Error();
      const updated = await res.json();
      setUser((prev) => prev ? { ...prev, ...updated } : prev);
      setEditing(false);
      setToast({ msg: "Perfil actualizado con éxito", type: "success" });
    } catch {
      setToast({ msg: "Error al actualizar el perfil", type: "error" });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    if (!user) return;
    setForm({ first_name: user.first_name, last_name: user.last_name, phone: user.phone ?? "", email: user.email });
    setEditing(false);
  };

  return (
    <>
      <Modal isOpen={isOpen} onClose={handleClose} title="Mi perfil" width="600px">

        {/* Toast */}
        {toast && (
          <div className={`pm-toast pm-toast--${toast.type}`}>
            <span>{toast.type === "success" ? "✓" : "✕"}</span>
            {toast.msg}
          </div>
        )}

        {/* Header con avatar */}
        {loading ? (
          <div className="pm-header-skeleton" />
        ) : user ? (
          <div className="pm-profile-header">
            <div className="pm-avatar">{getInitials(user.first_name, user.last_name)}</div>
            <div className="pm-header-info">
              <p className="pm-fullname">{user.first_name} {user.last_name}</p>
              <div className="pm-badges">
                <span className="pm-badge">{user.role.name}</span>
                {user.is_admin && <span className="pm-badge pm-badge--admin">Administrador</span>}
              </div>
            </div>
            {!editing && (
              <button className="pm-edit-btn" onClick={() => setEditing(true)}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Editar
              </button>
            )}
          </div>
        ) : null}

        <div className="pm-divider" />

        {/* Información personal */}
        {loading ? (
          <div className="pm-body-skeleton" />
        ) : user ? (
          <>
            <div className="pm-section">
              <p className="pm-section-title">Información personal</p>
              <div className="pm-grid">

                <div className="pm-field">
                  <label className="pm-label">Nombre</label>
                  {editing
                    ? <input className="pm-input" name="first_name" value={form.first_name} onChange={handleChange} />
                    : <p className="pm-value">{user.first_name}</p>}
                </div>

                <div className="pm-field">
                  <label className="pm-label">Apellido</label>
                  {editing
                    ? <input className="pm-input" name="last_name" value={form.last_name} onChange={handleChange} />
                    : <p className="pm-value">{user.last_name}</p>}
                </div>

                <div className="pm-field">
                  <label className="pm-label">Teléfono</label>
                  {editing
                    ? <input className="pm-input" name="phone" value={form.phone} onChange={handleChange} placeholder="+57 300 000 0000" />
                    : <p className="pm-value">{user.phone ?? "—"}</p>}
                </div>

                <div className="pm-field">
                  <label className="pm-label">Correo electrónico</label>
                  {editing
                    ? <input className="pm-input" name="email" type="email" value={form.email} onChange={handleChange} />
                    : <p className="pm-value">{user.email}</p>}
                </div>

              </div>
            </div>

            <div className="pm-divider" />

            {/* Información de cuenta — solo lectura */}
            <div className="pm-section">
              <p className="pm-section-title">
                Información de cuenta
                <span className="pm-readonly-tag">Solo lectura</span>
              </p>
              <div className="pm-grid">
                <div className="pm-readonly-field">
                  <span className="pm-readonly-icon">ROL</span>
                  <div>
                    <p className="pm-label">Rol asignado</p>
                    <p className="pm-value">{user.role.name}</p>
                  </div>
                </div>
                <div className="pm-readonly-field">
                  <span className="pm-readonly-icon">REG</span>
                  <div>
                    <p className="pm-label">Miembro desde</p>
                    <p className="pm-value">{formatDate(user.created_at)}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="pm-footer">
              <button className="pm-pw-btn" onClick={() => setShowPwModal(true)}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0110 0v4"/>
                </svg>
                Cambiar contraseña
              </button>
              <button className="pm-pw-btn pm-pw-btn--danger" onClick={handleLogoutAll} disabled={loggingOutAll}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
                  <polyline points="16 17 21 12 16 7"/>
                  <line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
                {loggingOutAll ? "Cerrando..." : "Cerrar sesión en todos los dispositivos"}
              </button>

              {editing && (
                <div className="pm-actions">
                  <button className="pm-btn-cancel" onClick={handleCancel} disabled={saving}>
                    Cancelar
                  </button>
                  <button className="pm-btn-save" onClick={handleSave} disabled={saving}>
                    {saving ? <><span className="pm-spinner" /> Guardando...</> : "Guardar cambios"}
                  </button>
                </div>
              )}
            </div>
          </>
        ) : (
          <p className="pm-error">No se pudo cargar el perfil.</p>
        )}

      </Modal>

      {/* Modal cambiar contraseña — encima */}
      <ChangePasswordModal
        isOpen={showPwModal}
        onClose={() => setShowPwModal(false)}
        onSuccess={() => {
          setShowPwModal(false);
          setToast({ msg: "Contraseña actualizada correctamente", type: "success" });
        }}
      />
    </>
  );
}

// ── Modal cambiar contraseña ───────────────────────────────────────────────
function ChangePasswordModal({
  isOpen,
  onClose,
  onSuccess,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [form, setForm] = useState<PasswordForm>({
    current_password: "", new_password: "", confirm_password: "",
  });
  const [show, setShow] = useState({ current: false, next: false, confirm: false });
  const [saving, setSaving] = useState(false);
  const [error, setError]   = useState<string | null>(null);

  // Reset al cerrar
  useEffect(() => {
    if (!isOpen) {
      setForm({ current_password: "", new_password: "", confirm_password: "" });
      setError(null);
      setSaving(false);
    }
  }, [isOpen]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError(null);
  };

  const handleSubmit = async () => {
    if (!form.current_password || !form.new_password || !form.confirm_password) {
      setError("Todos los campos son obligatorios."); return;
    }
    if (form.new_password !== form.confirm_password) {
      setError("Las contraseñas nuevas no coinciden."); return;
    }
    if (form.new_password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres."); return;
    }
    setSaving(true);
    try {
      const res = await apiFetch("/session/change-password", {
        method: "POST",
        body: JSON.stringify({
          current_password: form.current_password,
          new_password:     form.new_password,
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail ?? "Error al cambiar la contraseña.");
        return;
      }
      onSuccess();
    } catch {
      setError("Error de conexión. Intenta de nuevo.");
    } finally {
      setSaving(false);
    }
  };

  const fields: { name: keyof PasswordForm; label: string; showKey: keyof typeof show }[] = [
    { name: "current_password", label: "Contraseña actual",           showKey: "current" },
    { name: "new_password",     label: "Nueva contraseña",            showKey: "next"    },
    { name: "confirm_password", label: "Confirmar nueva contraseña",  showKey: "confirm" },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Cambiar contraseña" width="420px">
      <div className="pm-section" style={{ paddingTop: 0 }}>

        {error && <div className="pm-error-box">{error}</div>}

        {fields.map(({ name, label, showKey }) => (
          <div className="pm-field" key={name} style={{ marginBottom: "1rem" }}>
            <label className="pm-label">{label}</label>
            <div className="pm-input-wrapper">
              <input
                className="pm-input pm-input--icon"
                name={name}
                type={show[showKey] ? "text" : "password"}
                value={form[name]}
                onChange={handleChange}
                placeholder="••••••••"
              />
              <button
                type="button"
                className="pm-eye-btn"
                onClick={() => setShow((s) => ({ ...s, [showKey]: !s[showKey] }))}
              >
                {show[showKey] ? (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                    <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/>
                    <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                ) : (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                )}
              </button>
            </div>
          </div>
        ))}

        <div className="pm-actions" style={{ justifyContent: "flex-end", marginTop: "0.5rem" }}>
          <button className="pm-btn-cancel" onClick={onClose} disabled={saving}>
            Cancelar
          </button>
          <button className="pm-btn-save" onClick={handleSubmit} disabled={saving}>
            {saving ? <><span className="pm-spinner" /> Guardando...</> : "Actualizar contraseña"}
          </button>
        </div>

      </div>
    </Modal>
  );
}
