import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import Badge from "../components/Badge";
import { apiFetch } from "../utils/api";
import "../pages/roles.css";
import { useAuth } from "../context/AuthContext";

// ─── Interfaces ───────────────────────────────────────────────────────────────

interface Role {
  id: number;
  name: string;
  description: string;
  status: "active" | "inactive";
}

interface RoleForm {
  name: string;
  description: string;
  module_ids: number[];
}

interface Module {
  id: number;
  name: string;
  label: string;
}

interface RoleModule {
  id: number;
  module_id: number;
}

type FormErrors = Partial<Record<keyof RoleForm, string>>;

const emptyForm = (): RoleForm => ({ name: "", description: "", module_ids: [] });

// ─── Columnas ─────────────────────────────────────────────────────────────────

const columns: ColumnDef<Role>[] = [
  { key: "id",          header: "ID",          width: "5%"  },
  { key: "name",        header: "Nombre",      width: "25%" },
  { key: "description", header: "Descripción", width: "50%" },
  {
    key: "status",
    header: "Estado",
    width: "15%",
    render: (row) => (
      <Badge
        label={row.status === "active" ? "Activo" : "Inactivo"}
        variant={row.status === "active" ? "active" : "inactive"}
      />
    ),
  },
];

// ─── Página ───────────────────────────────────────────────────────────────────

export default function Roles(): JSX.Element {
  const [roles, setRoles]           = useState<Role[]>([]);
  const [modules, setModules]       = useState<Module[]>([]);
  const [modalOpen, setModalOpen]   = useState(false);
  const [editTarget, setEditTarget] = useState<Role | null>(null);
  const [form, setForm]             = useState<RoleForm>(emptyForm());
  const [errors, setErrors]         = useState<FormErrors>({});
  const [loading, setLoading]       = useState(true);

  const { currentUser } = useAuth();
  const isCurrentUserAdmin = currentUser?.is_admin ?? false;

  // ── Cargar roles ───────────────────────────────────────────────────────────
  useEffect(() => {
    const fetchRoles = async () => {
      try {
        const response = await apiFetch("/roles/");
        if (!response.ok) throw new Error("Error al cargar roles");
        const data: Role[] = await response.json();
        setRoles(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRoles();
  }, []);

  // ── Cargar módulos disponibles ─────────────────────────────────────────────
  useEffect(() => {
    apiFetch("/role-modules/modules")
      .then((res) => res.json())
      .then((data: Module[]) => setModules(data))
      .catch((err) => console.error("Error al cargar módulos:", err));
  }, []);

  // ── Handlers modal ─────────────────────────────────────────────────────────

  const handleCrear = () => {
    setEditTarget(null);
    setForm(emptyForm());
    setErrors({});
    setModalOpen(true);
  };

  const handleEditar = async (role: Role) => {
    setEditTarget(role);
    setErrors({});

    // Cargar módulos actuales del rol
    try {
      const response = await apiFetch(`/role-modules/${role.id}`);
      const roleModules: RoleModule[] = await response.json();
      setForm({
        name:        role.name,
        description: role.description,
        module_ids:  roleModules.map((rm) => rm.module_id),
      });
    } catch {
      setForm({ name: role.name, description: role.description, module_ids: [] });
    }

    setModalOpen(true);
  };

  const handleCerrar = () => {
    setModalOpen(false);
    setEditTarget(null);
    setForm(emptyForm());
  };

  // ── Formulario ─────────────────────────────────────────────────────────────

  const setField = (field: keyof RoleForm, value: string | number[]) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const toggleModule = (moduleId: number) => {
    setForm((prev) => ({
      ...prev,
      module_ids: prev.module_ids.includes(moduleId)
        ? prev.module_ids.filter((id) => id !== moduleId)
        : [...prev.module_ids, moduleId],
    }));
    setErrors((prev) => ({ ...prev, module_ids: undefined }));
  };

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (isCurrentUserAdmin || !editTarget) {
      if (!form.name.trim()) e.name = "El nombre es requerido";
    }
    if (!form.description.trim()) e.description = "La descripción es requerida";
    if (form.module_ids.length === 0) e.module_ids = "Selecciona al menos un módulo";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      let roleId: number;

      if (editTarget) {
        // ── Editar rol ──
        const body: Record<string, string> = { description: form.description };
        if (isCurrentUserAdmin) body.name = form.name;

        const response = await apiFetch(`/roles/${editTarget.id}`, {
          method: "PATCH",
          body: JSON.stringify(body),
        });
        if (!response.ok) {
          const err = await response.json();
          alert(err.detail || "Error al actualizar rol");
          return;
        }
        const updated: Role = await response.json();
        setRoles((prev) => prev.map((r) => r.id === editTarget.id ? updated : r));
        roleId = editTarget.id;

      } else {
        // ── Crear rol ──
        const response = await apiFetch("/roles/", {
          method: "POST",
          body: JSON.stringify({
            name:        form.name,
            description: form.description,
          }),
        });
        if (!response.ok) {
          const err = await response.json();
          alert(err.detail || "Error al crear rol");
          return;
        }
        const created: Role = await response.json();
        setRoles((prev) => [...prev, { ...created, status: "active" }]);
        roleId = created.id;
      }

      // ── Asignar módulos al rol ──
      const modulesResponse = await apiFetch(`/role-modules/${roleId}`, {
        method: "POST",
        body: JSON.stringify({ module_ids: form.module_ids }),
      });
      if (!modulesResponse.ok) {
        alert("Rol guardado pero error al asignar módulos.");
      }

      handleCerrar();
    } catch {
      alert("Error de conexión con el servidor.");
    }
  };

  const handleEliminar = async (id: number) => {
    try {
      const response = await apiFetch(`/roles/${id}`, { method: "DELETE" });
      if (response.status === 410) { alert("El rol ya está desactivado."); return; }
      if (response.status === 403) { alert("No se puede desactivar un rol del sistema."); return; }
      if (!response.ok) {
        const err = await response.json();
        alert(err.detail || "Error al desactivar rol");
        return;
      }
      setRoles((prev) => prev.filter((r) => r.id !== id));
    } catch {
      alert("Error de conexión con el servidor.");
    }
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <Layout>
      {loading ? (
        <div className="saip-loading">Cargando roles...</div>
      ) : (
        <Table
          title="Gestión de roles"
          columns={columns}
          data={roles}
          searchPlaceholder="Buscar rol"
          sortKey="name"
          headerActions={
            <Button variant="primary" onClick={handleCrear}>
              Crear rol
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
                title="Desactivar"
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
        title={editTarget ? "Editar rol" : "Crear rol"}
        width="480px"
      >
        <form className="crf" onSubmit={handleSubmit}>

          {(!editTarget || isCurrentUserAdmin) && (
            <div className="crf__group">
              <label className="crf__label">
                Nombre del rol<span className="crf__required">*</span>
              </label>
              <input
                className={`crf__input ${errors.name ? "crf__input--error" : ""}`}
                placeholder="Ej: Administrador, Cajero…"
                value={form.name}
                onChange={(e) => setField("name", e.target.value)}
              />
              {errors.name && <span className="crf__error">{errors.name}</span>}
            </div>
          )}

          <div className="crf__group">
            <label className="crf__label">Descripción</label>
            <textarea
              className={`crf__textarea ${errors.description ? "crf__input--error" : ""}`}
              placeholder="Describe las responsabilidades de este rol…"
              rows={3}
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
            />
            {errors.description && <span className="crf__error">{errors.description}</span>}
          </div>

          {/* ── Módulos ── */}
          <div className="crf__group">
            <label className="crf__label">
              Módulos con acceso<span className="crf__required">*</span>
            </label>
            <div className="cuf__accesos">
              {modules.map((module) => {
                const checked = form.module_ids.includes(module.id);
                return (
                  <button
                    key={module.id}
                    type="button"
                    onClick={() => toggleModule(module.id)}
                    className={`cuf__acceso-btn ${checked ? "cuf__acceso-btn--active" : ""}`}
                  >
                    {checked && (
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="2.5">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    )}
                    {module.label}
                  </button>
                );
              })}
            </div>
            {errors.module_ids && <span className="crf__error">{errors.module_ids}</span>}
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