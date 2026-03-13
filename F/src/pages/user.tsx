import { JSX, useState } from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import Badge from "../components/Badge";
import "./user.css";

// ─── Tipos ────────────────────────────────────────────────────────────────────

interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  position: string;
  phone?: string;
  role_id: number;
  is_admin: boolean;
  status: "Activo" | "Inactivo";
  accesos: string[];
}

interface UserForm {
  first_name: string;
  last_name: string;
  email: string;
  position: string;
  phone: string;
  role_id: string;
  is_admin: boolean;
  status: "Activo" | "Inactivo";
  accesos: string[];
}

type FormErrors = Partial<Record<keyof UserForm, string>>;

const ACCESOS_DISPONIBLES = ["Inventario", "Proveedores", "Ventas", "Producción"];
const ROLES_DISPONIBLES   = [
  { value: "1", label: "Administrador" },
  { value: "2", label: "Cajero" },
  { value: "3", label: "Panadero" },
];

const emptyForm = (): UserForm => ({
  first_name: "",
  last_name:  "",
  email:      "",
  position:   "",
  phone:      "",
  role_id:    "",
  is_admin:   false,
  status:     "Activo",
  accesos:    [],
});

// ─── Datos mock ───────────────────────────────────────────────────────────────

const mockUsers: User[] = [
  {
    id: 1, first_name: "Yohan", last_name: "Martinez",
    email: "yohan@email.com", position: "Panadero", phone: "300000000",
    role_id: 1, is_admin: false, status: "Activo",
    accesos: ["Inventario", "Producción", "Ventas"],
  },
  {
    id: 2, first_name: "Marta", last_name: "Lopez",
    email: "marta@email.com", position: "Administrador", phone: "300000001",
    role_id: 2, is_admin: true, status: "Activo",
    accesos: ["Inventario", "Producción", "Ventas"],
  },
];

// ─── Columnas ─────────────────────────────────────────────────────────────────

const columns: ColumnDef<User>[] = [
  { key: "first_name", header: "Nombre",    width: "14%" },
  { key: "last_name",  header: "Apellidos", width: "14%" },
  { key: "position",   header: "Cargo",     width: "16%" },
  {
    key: "accesos",
    header: "Accesos",
    render: (row) => (
      <div className="saip-table__badges">
        {row.accesos.map((a) => <Badge key={a} label={a} variant="access" />)}
      </div>
    ),
  },
  {
    key: "status",
    header: "Estado",
    width: "12%",
    render: (row) => (
      <Badge label={row.status} variant={row.status === "Activo" ? "active" : "inactive"} />
    ),
  },
];

// ─── Página ───────────────────────────────────────────────────────────────────

export default function User(): JSX.Element {
  const [users, setUsers]           = useState<User[]>(mockUsers);
  const [nextId, setNextId]         = useState(mockUsers.length + 1);
  const [modalOpen, setModalOpen]   = useState(false);
  const [editTarget, setEditTarget] = useState<User | null>(null);
  const [form, setForm]             = useState<UserForm>(emptyForm());
  const [errors, setErrors]         = useState<FormErrors>({});

  // ── Handlers modal ─────────────────────────────────────────────────────────

  const handleCrear = () => {
    setEditTarget(null);
    setForm(emptyForm());
    setErrors({});
    setModalOpen(true);
  };

  const handleEditar = (user: User) => {
    setEditTarget(user);
    setForm({
      first_name: user.first_name,
      last_name:  user.last_name,
      email:      user.email,
      position:   user.position,
      phone:      user.phone ?? "",
      role_id:    String(user.role_id),
      is_admin:   user.is_admin,
      status:     user.status,
      accesos:    user.accesos,
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

  const toggleAcceso = (acceso: string) => {
    setForm((prev) => ({
      ...prev,
      accesos: prev.accesos.includes(acceso)
        ? prev.accesos.filter((a) => a !== acceso)
        : [...prev.accesos, acceso],
    }));
    setErrors((prev) => ({ ...prev, accesos: undefined }));
  };

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (!form.first_name.trim()) e.first_name = "El nombre es requerido";
    if (!form.last_name.trim())  e.last_name  = "El apellido es requerido";
    if (!form.email.trim())      e.email      = "El correo es requerido";
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = "Correo inválido";
    if (!form.position.trim())   e.position   = "El cargo es requerido";
    if (!form.role_id)           e.role_id    = "Selecciona un rol";
    if (form.accesos.length === 0) e.accesos  = "Selecciona al menos un módulo";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    if (editTarget) {
      setUsers((prev) =>
        prev.map((u) =>
          u.id === editTarget.id
            ? { ...u, ...form, role_id: Number(form.role_id) }
            : u
        )
      );
    } else {
      setUsers((prev) => [
        ...prev,
        { id: nextId, ...form, role_id: Number(form.role_id) },
      ]);
      setNextId((n) => n + 1);
    }
    handleCerrar();
  };

  const handleEliminar = (id: number) => {
    setUsers((prev) => prev.filter((u) => u.id !== id));
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <Layout>
      <Table
        title="Gestión de usuarios"
        columns={columns}
        data={users}
        searchPlaceholder="Buscar usuario"
        onFilter={() => console.log("filtrar")}
        headerActions={
          <>
            <Button variant="primary" onClick={handleCrear}>
              Crear usuario
            </Button>
          </>
        }
        renderActions={(row) => (
          <div className="saip-table__actions">
            <button
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

      {/* ── MODAL ────────────────────────────────────────────────────────── */}
      <Modal
        isOpen={modalOpen}
        onClose={handleCerrar}
        title={editTarget ? "Editar usuario" : "Crear usuario"}
        width="520px"
      >
        <form className="cuf" onSubmit={handleSubmit}>

          {/* Nombre + Apellido */}
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

          {/* Email */}
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

          {/* Cargo + Teléfono */}
          <div className="cuf__row">
            <div className="cuf__group">
              <label className="cuf__label">Cargo</label>
              <input
                className={`cuf__input ${errors.position ? "cuf__input--error" : ""}`}
                placeholder="Ej: Cajero"
                value={form.position}
                onChange={(e) => setField("position", e.target.value)}
              />
              {errors.position && <span className="cuf__error">{errors.position}</span>}
            </div>
            <div className="cuf__group">
              <label className="cuf__label">Teléfono</label>
              <input
                className="cuf__input"
                placeholder="300 000 0000"
                value={form.phone}
                onChange={(e) => setField("phone", e.target.value)}
              />
            </div>
          </div>

          {/* Rol */}
          <div className="cuf__group">
            <label className="cuf__label">Rol</label>
            <select
              className={`cuf__select ${errors.role_id ? "cuf__input--error" : ""}`}
              value={form.role_id}
              onChange={(e) => setField("role_id", e.target.value)}
            >
              <option value="">Seleccionar rol…</option>
              {ROLES_DISPONIBLES.map((r) => (
                <option key={r.value} value={r.value}>{r.label}</option>
              ))}
            </select>
            {errors.role_id && <span className="cuf__error">{errors.role_id}</span>}
          </div>

          {/* Accesos */}
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


          {/* Acciones */}
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
