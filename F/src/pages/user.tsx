import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import Badge from "../components/Badge";
import { apiFetch } from "../utils/api";
import "./user.css";
import { useAuth } from "../context/AuthContext";

// ─── Interfaces ───────────────────────────────────────────────────────────────

interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;
  role_id: number;
  role: Role;
  is_admin: boolean;
  status: "active" | "inactive";
  created_at: string;
}

interface UserForm {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  role_id: string;
  is_admin: boolean;
  accesos: string[];
}

interface Role {
  id: number;
  name: string;
}

type FormErrors = Partial<Record<keyof UserForm, string>>;

const emptyForm = (): UserForm => ({
  first_name: "",
  last_name:  "",
  email:      "",
  phone:      "",
  role_id:    "",
  is_admin:   false,
  accesos:    [],
});

// ─── Columnas ─────────────────────────────────────────────────────────────────

const columns: ColumnDef<User>[] = [
  { key: "id",         header: "ID",        width: "5%"  },
  { key: "first_name", header: "Nombre",    width: "12%" },
  { key: "last_name",  header: "Apellidos", width: "12%" },
  { key: "email",      header: "Correo",    width: "15%" },
  { key: "phone",      header: "Número",    width: "10%" },
  {
    key: "col_is_admin",
    header: "Usuario",
    width: "10%",
    render: (row) => (
      <Badge label={row.is_admin ? "Admin" : "Usuario"} variant="access" />
    ),
  },
  {
    key: "col_role",
    header: "Rol",
    width: "14%",
    render: (row) => (
      <Badge label={row.role.name} variant="access" />
    ),
  },
  {
    key: "status",
    header: "Estado",
    width: "12%",
    render: (row) => (
      <Badge
        label={row.status === "active" ? "ACTIVO" : "INACTIVO"}
        variant={row.status === "active" ? "active" : "inactive"}
      />
    ),
  },
];

// ─── Página ───────────────────────────────────────────────────────────────────

export default function User(): JSX.Element {
  const [users, setUsers]           = useState<User[]>([]);
  const [modalOpen, setModalOpen]   = useState(false);
  const [editTarget, setEditTarget] = useState<User | null>(null);
  const [form, setForm]             = useState<UserForm>(emptyForm());
  const [errors, setErrors]         = useState<FormErrors>({});
  const [loading, setLoading]       = useState(true);


  const { currentUser } = useAuth();
  const isCurrentUserAdmin = currentUser?.is_admin ?? false;

  // ── Cargar usuarios ────────────────────────────────────────────────────────
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await apiFetch("/users/");
        if (!response.ok) throw new Error("Error al cargar usuarios");
        const data: User[] = await response.json();
        setUsers(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  const [roles, setRoles] = useState<Role[]>([]);

  useEffect(() => {
    apiFetch("/roles/")
      .then((res) => res.json())
      .then((data: Role[]) => setRoles(data))
      .catch((err) => console.error("Error al cargar roles:", err));
  }, []);

  // ── Handlers modal ─────────────────────────────────────────────────────────

  const handleCrear = () => {
    setEditTarget(null);
    setForm(emptyForm());
    setErrors({});
    setModalOpen(true);
  };

  const handleEditar = (user: User) => {
    console.log("handleEditar llamado", user); 
    setEditTarget(user);
    setForm({
      first_name: user.first_name,
      last_name:  user.last_name,
      email:      user.email,
      phone:      user.phone ?? "",
      role_id:    String(user.role_id),
      is_admin:   user.is_admin,
      accesos:    [],
    });
    setErrors({});
    setModalOpen(true);
  };

  const handleCerrar = () => {
    setModalOpen(false);
    setEditTarget(null);
    setForm(emptyForm());
  };

  // ── Formulario ─────────────────────────────────────────────────────────────

  const setField = (field: keyof UserForm, value: string | boolean | string[]) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

 /*  const toggleAcceso = (acceso: string) => {
    setForm((prev) => ({
      ...prev,
      accesos: prev.accesos.includes(acceso)
        ? prev.accesos.filter((a) => a !== acceso)
        : [...prev.accesos, acceso],
    }));
    setErrors((prev) => ({ ...prev, accesos: undefined }));
  }; */

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (!form.first_name.trim()) e.first_name = "El nombre es requerido";
    if (!form.last_name.trim())  e.last_name  = "El apellido es requerido";
    if (!form.email.trim())      e.email      = "El correo es requerido";
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = "Correo inválido";

    // Validaciones exclusivas de creación
    if (!editTarget) {
      if (!form.role_id)             e.role_id = "Selecciona un rol";
      if (form.accesos.length === 0) e.accesos = "Selecciona al menos un módulo";
    }

    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      if (editTarget) {
        // ── Edición ──
        const body: Record<string, unknown> = {
          first_name: form.first_name,
          last_name:  form.last_name,
          email:      form.email,
          phone:      form.phone || null,
        };

        if (isCurrentUserAdmin) {
          body.role_id  = Number(form.role_id);
          body.is_admin = form.is_admin;
        }

        const response = await apiFetch(`/users/${editTarget.id}`, {
          method: "PUT",
          body: JSON.stringify(body),
        });
        if (!response.ok) {
          const err = await response.json();
          alert(err.detail || "Error al actualizar usuario");
          return;
        }
        const updated: User = await response.json();

        const updatedWithRole: User = {
          ...updated,
          role: roles.find((r) => r.id === updated.role_id) ?? editTarget.role,
        };

        setUsers((prev) => prev.map((u) => u.id === editTarget.id ? updatedWithRole : u));
        
      } else {
        const response = await apiFetch("/users/", {
          method: "POST",
          body: JSON.stringify({
            first_name: form.first_name,
            last_name:  form.last_name,
            email:      form.email,
            phone:      form.phone || null,
            role_id:    Number(form.role_id),
            is_admin:   form.is_admin,
          }),
        });
        if (!response.ok) {
          const err = await response.json();
          alert(err.detail || "Error al crear usuario");
          return;
        }
        const created: User = await response.json();
        setUsers((prev) => [...prev, created]);
      }
      handleCerrar();
    } catch {
      alert("Error de conexión con el servidor.");
    }
  };

  const handleEliminar = async (id: number) => {
    try {
      const response = await apiFetch(`/users/${id}`, { method: "DELETE" });
      if (!response.ok) {
        const err = await response.json();
        alert(err.detail || "Error al eliminar usuario");
        return;
      }
      setUsers((prev) => prev.filter((u) => u.id !== id));
    } catch {
      alert("Error de conexión con el servidor.");
    }
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <Layout>
      {loading ? (
        <div className="saip-loading">Cargando usuarios...</div>
      ) : (
        <Table
          sortKey="first_name"
          title="Gestión de usuarios"
          columns={columns}
          data={users}
          searchPlaceholder="Buscar usuario"
          headerActions={
            <Button variant="primary" onClick={handleCrear}>
              Crear usuario
            </Button>
          }
          renderActions={(row) => (
            <div className="saip-table__actions">
              <button
                type="button"
                className="saip-table__action-btn"
                title="Editar"
                onClick={() => handleEditar(row)}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="1.8">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button
                type="button"
                className="saip-table__action-btn saip-table__action-btn--danger"
                title="Eliminar"
                onClick={() => handleEliminar(row.id)}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="1.8">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
                  <path d="M10 11v6M14 11v6"/>
                  <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
                </svg>
              </button>
            </div>
          )}
        />
      )}

      {/* ── MODAL ────────────────────────────────────────────────────────── */}
      <Modal
        isOpen={modalOpen}
        onClose={handleCerrar}
        title={editTarget ? "Editar usuario" : "Crear usuario"}
        width="520px"
      >
        <form className="cuf" onSubmit={handleSubmit}>

          {/* ── Nombre y Apellido (siempre visibles) ── */}
          <div className="cuf__row">
            <div className="cuf__group">
              <label className="cuf__label">Nombre</label>
              <input
                className={`cuf__input ${errors.first_name ? "cuf__input--error" : ""}`}
                placeholder="Ej: Yohan"
                value={form.first_name}
                onChange={(e) => setField("first_name", e.target.value)}
              />
              {errors.first_name && <span className="cuf__error">{errors.first_name}</span>}
            </div>
            <div className="cuf__group">
              <label className="cuf__label">Apellido</label>
              <input
                className={`cuf__input ${errors.last_name ? "cuf__input--error" : ""}`}
                placeholder="Ej: Martinez"
                value={form.last_name}
                onChange={(e) => setField("last_name", e.target.value)}
              />
              {errors.last_name && <span className="cuf__error">{errors.last_name}</span>}
            </div>
          </div>

          {/* ── Correo (siempre visible) ── */}
          <div className="cuf__group">
            <label className="cuf__label">Correo electrónico</label>
            <input
              className={`cuf__input ${errors.email ? "cuf__input--error" : ""}`}
              type="email"
              placeholder="usuario@saip.com"
              value={form.email}
              onChange={(e) => setField("email", e.target.value)}
            />
            {errors.email && <span className="cuf__error">{errors.email}</span>}
          </div>

          {/* ── Teléfono (siempre visible) ── */}
          <div className="cuf__group">
            <label className="cuf__label">Teléfono</label>
            <input
              className="cuf__input"
              placeholder="300 000 0000"
              value={form.phone}
              onChange={(e) => setField("phone", e.target.value)}
            />
          </div>

          {/* ── Rol e is_admin: siempre en creación, solo admin en edición ── */}
          {(!editTarget || isCurrentUserAdmin) && (
            <>
              <div className="cuf__group">
                <label className="cuf__label">Rol</label>
                <select
                  className={`cuf__select ${errors.role_id ? "cuf__input--error" : ""}`}
                  value={form.role_id}
                  onChange={(e) => setField("role_id", e.target.value)}
                >
                  <option value="">Seleccionar rol…</option>
                  {roles.map((r) => (
                    <option key={r.id} value={String(r.id)}>{r.name}</option>
                  ))}
                </select>
                {errors.role_id && <span className="cuf__error">{errors.role_id}</span>}
              </div>

              <div className="cuf__group">
                <label className="cuf__label cuf__label--checkbox">
                  <input
                    type="checkbox"
                    checked={form.is_admin}
                    onChange={(e) => setField("is_admin", e.target.checked)}
                  />
                  Es administrador
                </label>
              </div>
            </>
          )}

          {/* ── Módulos con acceso: solo en creación ── */}

          {/* {!editTarget && (
            <div className="cuf__group">
              <label className="cuf__label">Módulos con acceso</label>
              <div className="cuf__accesos">
                {ACCESOS_DISPONIBLES.map((acceso) => {
                  const checked = form.accesos.includes(acceso);
                  return (
                    <button
                      key={acceso}
                      type="button"
                      onClick={() => toggleAcceso(acceso)}
                      className={`cuf__acceso-btn ${checked ? "cuf__acceso-btn--active" : ""}`}
                    >
                      {checked && (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
                          stroke="currentColor" strokeWidth="2.5">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      )}
                      {acceso}
                    </button>
                  );
                })}
              </div>
              {errors.accesos && <span className="cuf__error">{errors.accesos}</span>}
            </div>
          )} */}

          <div className="cuf__actions">
            <Button variant="secondary" type="button" onClick={handleCerrar}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {editTarget ? "Guardar cambios" : "Crear usuario"}
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}