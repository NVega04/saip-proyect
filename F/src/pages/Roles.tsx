import { JSX, useState } from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import Badge from "../components/Badge";
import "../pages/roles.css";

// ─── Tipos ────────────────────────────────────────────────────────────────────

interface Role {
  id: number;
  name: string;
  description: string;
  accesos: string[];
}

interface RoleForm {
  name: string;
  description: string;
  accesos: string[];
}

type FormErrors = Partial<Record<keyof RoleForm, string>>;

const ACCESOS_DISPONIBLES = ["Inventario", "Proveedores", "Ventas", "Producción"];

const emptyForm = (): RoleForm => ({ name: "", description: "", accesos: [] });

// ─── Datos mock ───────────────────────────────────────────────────────────────

const mockRoles: Role[] = [
  { id: 1, name: "Administrador", description: "Control total del sistema", accesos: ["Inventario", "Ventas", "Producción"] },
  { id: 2, name: "Cajero",        description: "Gestiona ventas",           accesos: ["Ventas"] },
  { id: 3, name: "Panadero",      description: "Gestiona producción",       accesos: ["Producción", "Inventario"] },
];

// ─── Columnas ─────────────────────────────────────────────────────────────────

const columns: ColumnDef<Role>[] = [
  { key: "name",        header: "Nombre",      width: "20%" },
  { key: "description", header: "Descripción", width: "35%" },
  {
    key: "accesos",
    header: "Accesos",
    render: (row) => (
      <div className="saip-table__badges">
        {row.accesos.map((a) => (
          <Badge key={a} label={a} variant="access" />
        ))}
      </div>
    ),
  },
];

// ─── Página ───────────────────────────────────────────────────────────────────

export default function Roles(): JSX.Element {
  const [roles, setRoles]           = useState<Role[]>(mockRoles);
  const [nextId, setNextId]         = useState(mockRoles.length + 1);
  const [modalOpen, setModalOpen]   = useState(false);
  const [editTarget, setEditTarget] = useState<Role | null>(null);
  const [form, setForm]             = useState<RoleForm>(emptyForm());
  const [errors, setErrors]         = useState<FormErrors>({});

  // ── Handlers modal ─────────────────────────────────────────────────────────

  const handleCrear = () => {
    setEditTarget(null);
    setForm(emptyForm());
    setErrors({});
    setModalOpen(true);
  };

  const handleEditar = (role: Role) => {
    setEditTarget(role);
    setForm({ name: role.name, description: role.description, accesos: role.accesos });
    setErrors({});
    setModalOpen(true);
  };

  const handleCerrar = () => {
    setModalOpen(false);
    setEditTarget(null);
    setForm(emptyForm());
  };

  // ── Formulario ─────────────────────────────────────────────────────────────

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
    if (!form.name.trim())         e.name        = "El nombre es requerido";
    if (!form.description.trim())  e.description = "La descripción es requerida";
    if (form.accesos.length === 0) e.accesos     = "Selecciona al menos un módulo";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    if (editTarget) {
      setRoles((prev) =>
        prev.map((r) => r.id === editTarget.id ? { ...r, ...form } : r)
      );
    } else {
      setRoles((prev) => [...prev, { id: nextId, ...form }]);
      setNextId((n) => n + 1);
    }
    handleCerrar();
  };

  const handleEliminar = (id: number) => {
    setRoles((prev) => prev.filter((r) => r.id !== id));
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <Layout>
      <Table
        title="Gestión de roles"
        columns={columns}
        data={roles}
        searchPlaceholder="Buscar rol"
        onFilter={() => console.log("filtrar")}
        headerActions={
          <>
            <Button variant="primary" onClick={handleCrear}>
              Crear rol
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
        title={editTarget ? "Editar rol" : "Crear rol"}
        width="480px"
      >
        <form className="crf" onSubmit={handleSubmit}>
          <div className="crf__group">
            <label className="crf__label">Nombre del rol</label>
            <input
              className={`crf__input ${errors.name ? "crf__input--error" : ""}`}
              placeholder="Ej: Administrador, Cajero…"
              value={form.name}
              onChange={(e) => {
                setForm({ ...form, name: e.target.value });
                setErrors((prev) => ({ ...prev, name: undefined }));
              }}
            />
            {errors.name && <span className="crf__error">{errors.name}</span>}
          </div>

          <div className="crf__group">
            <label className="crf__label">Descripción</label>
            <textarea
              className={`crf__textarea ${errors.description ? "crf__input--error" : ""}`}
              placeholder="Describe las responsabilidades de este rol…"
              rows={3}
              value={form.description}
              onChange={(e) => {
                setForm({ ...form, description: e.target.value });
                setErrors((prev) => ({ ...prev, description: undefined }));
              }}
            />
            {errors.description && <span className="crf__error">{errors.description}</span>}
          </div>

          <div className="crf__group">
            <label className="crf__label">Módulos con acceso</label>
            <div className="crf__accesos">
              {ACCESOS_DISPONIBLES.map((acceso) => {
                const checked = form.accesos.includes(acceso);
                return (
                  <button
                    key={acceso}
                    type="button"
                    onClick={() => toggleAcceso(acceso)}
                    className={`crf__acceso-btn ${checked ? "crf__acceso-btn--active" : ""}`}
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
            {errors.accesos && <span className="crf__error">{errors.accesos}</span>}
          </div>

          <div className="crf__actions">
            <Button variant="secondary" type="button" onClick={handleCerrar}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {editTarget ? "Guardar cambios" : "Crear rol"}
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
