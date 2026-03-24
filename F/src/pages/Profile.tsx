import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch, getMe, UserProfile } from "../utils/api";
import "./Profile.css";

interface FormState {
  first_name: string;
  last_name: string;
  phone: string;
  email: string;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("es-CO", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function getInitials(first: string, last: string) {
  return `${first[0] ?? ""}${last[0] ?? ""}`.toUpperCase();
}

export default function Perfil() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [form, setForm] = useState<FormState>({ first_name: "", last_name: "", phone: "", email: "" });
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: "success" | "error" } | null>(null);

  useEffect(() => {
    getMe().then((data) => {
      if (data) {
        setUser(data);
        setForm({
          first_name: data.first_name,
          last_name: data.last_name,
          phone: data.phone ?? "",
          email: data.email,
        });
      }
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(null), 3500);
      return () => clearTimeout(t);
    }
  }, [toast]);

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
          last_name: form.last_name,
          phone: form.phone || null,
          email: form.email,
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
    setForm({
      first_name: user.first_name,
      last_name: user.last_name,
      phone: user.phone ?? "",
      email: user.email,
    });
    setEditing(false);
  };

  if (loading) {
    return (
      <div className="perfil-page">
        <div className="perfil-skeleton" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="perfil-page">
        <p className="perfil-error">No se pudo cargar el perfil.</p>
      </div>
    );
  }

  return (
    <div className="perfil-page">

      {/* Toast */}
      {toast && (
        <div className={`perfil-toast perfil-toast--${toast.type}`}>
          <span className="toast-icon">{toast.type === "success" ? "✓" : "✕"}</span>
          {toast.msg}
        </div>
      )}

      {/* Botón volver */}
      <div className="perfil-topbar">
        <button className="perfil-back-btn" onClick={() => navigate(-1)}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5"/>
            <path d="M12 19l-7-7 7-7"/>
          </svg>
          Volver
        </button>
      </div>

      <div className="perfil-card">

        {/* Header */}
        <div className="perfil-header">
          <div className="perfil-avatar">
            {getInitials(user.first_name, user.last_name)}
          </div>
          <div className="perfil-header-info">
            <h1 className="perfil-fullname">{user.first_name} {user.last_name}</h1>
            <div className="perfil-badges">
              <span className="perfil-badge">{user.role.name}</span>
              {user.is_admin && (
                <span className="perfil-badge perfil-badge--admin">Administrador</span>
              )}
            </div>
          </div>
          {!editing && (
            <button className="perfil-edit-btn" onClick={() => setEditing(true)}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              Editar perfil
            </button>
          )}
        </div>

        <div className="perfil-divider" />

        {/* Sección editable */}
        <div className="perfil-section">
          <h2 className="perfil-section-title">Informacion personal</h2>
          <div className="perfil-grid">

            <div className="perfil-field">
              <label className="perfil-label">Nombre</label>
              {editing ? (
                <input className="perfil-input" name="first_name" value={form.first_name} onChange={handleChange} placeholder="Tu nombre" />
              ) : (
                <p className="perfil-value">{user.first_name}</p>
              )}
            </div>

            <div className="perfil-field">
              <label className="perfil-label">Apellido</label>
              {editing ? (
                <input className="perfil-input" name="last_name" value={form.last_name} onChange={handleChange} placeholder="Tu apellido" />
              ) : (
                <p className="perfil-value">{user.last_name}</p>
              )}
            </div>

            <div className="perfil-field">
              <label className="perfil-label">Telefono</label>
              {editing ? (
                <input className="perfil-input" name="phone" value={form.phone} onChange={handleChange} placeholder="Ej. +57 300 000 0000" />
              ) : (
                <p className="perfil-value">{user.phone ?? "—"}</p>
              )}
            </div>

            {/* Email ahora es editable */}
            <div className="perfil-field">
              <label className="perfil-label">Correo electronico</label>
              {editing ? (
                <input className="perfil-input" name="email" type="email" value={form.email} onChange={handleChange} placeholder="tucorreo@ejemplo.com" />
              ) : (
                <p className="perfil-value">{user.email}</p>
              )}
            </div>

          </div>
        </div>

        <div className="perfil-divider" />

        {/* Sección solo lectura */}
        <div className="perfil-section">
          <h2 className="perfil-section-title">
            Informacion de cuenta
            <span className="perfil-readonly-tag">Solo lectura</span>
          </h2>
          <div className="perfil-grid">

            <div className="perfil-readonly-field">
              <span className="perfil-readonly-icon">ROL</span>
              <div>
                <p className="perfil-label">Rol asignado</p>
                <p className="perfil-value">{user.role.name}</p>
              </div>
            </div>

            <div className="perfil-readonly-field">
              <span className="perfil-readonly-icon">REG</span>
              <div>
                <p className="perfil-label">Miembro desde</p>
                <p className="perfil-value">{formatDate(user.created_at)}</p>
              </div>
            </div>

          </div>
        </div>

        {/* Acciones */}
        {editing && (
          <div className="perfil-actions">
            <button className="perfil-btn-cancel" onClick={handleCancel} disabled={saving}>
              Cancelar
            </button>
            <button className="perfil-btn-save" onClick={handleSave} disabled={saving}>
              {saving ? (
                <>
                  <span className="btn-spinner" />
                  Guardando...
                </>
              ) : (
                "Guardar cambios"
              )}
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
