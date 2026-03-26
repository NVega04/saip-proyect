import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import { useAlert } from "../context/AlertContext";
import { useConfirm } from "../context/ConfirmContext";
import { apiFetch } from "../utils/api";
import "./supply-categories.css";

interface Supply {
  id: number;
  token: string;
  name: string;
  status: string;
}

interface SupplyCategory {
  id: number;
  token: string;
  name: string;
  description: string | null;
  status: string;
  created_at: string;
  created_by: number | null;
  updated_at: string | null;
  updated_by: number | null;
  deleted_at: string | null;
  deleted_by: number | null;
  supplies: Supply[];
}

interface SupplyCategoryForm {
  name: string;
  description: string;
}

type FormErrors = Partial<Record<keyof SupplyCategoryForm, string>>;

const emptyForm = (): SupplyCategoryForm => ({
  name: "",
  description: "",
});

const columns: ColumnDef<SupplyCategory>[] = [
  { key: "id", header: "ID", width: "5%" },
  { key: "name", header: "Nombre", width: "30%" },
  { key: "description", header: "Descripcion", width: "25%" },
  {
    key: "supplies",
    header: "Insumos",
    width: "40%",
    render: (row) => (
      <div className="sc-supplies-list">
        {row.supplies.length === 0 ? (
          <span className="sc-supplies-empty">Sin insumos</span>
        ) : (
          row.supplies.map((supply) => (
            <span key={supply.id} className="sc-supply-tag">
              {supply.name}
            </span>
          ))
        )}
      </div>
    ),
  },
];

export default function SupplyCategories(): JSX.Element {
  const [categories, setCategories] = useState<SupplyCategory[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<SupplyCategory | null>(null);
  const [form, setForm] = useState<SupplyCategoryForm>(emptyForm());
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(true);

  const { showAlert } = useAlert();
  const { showConfirm } = useConfirm();

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await apiFetch("/supply-categories/");
        if (!response.ok) throw new Error("Error al cargar categorias");
        const data: SupplyCategory[] = await response.json();
        setCategories(data.filter((c) => c.status === "active"));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchCategories();
  }, []);

  const handleCrear = () => {
    setEditTarget(null);
    setForm(emptyForm());
    setErrors({});
    setModalOpen(true);
  };

  const handleEditar = (category: SupplyCategory) => {
    setEditTarget(category);
    setForm({
      name: category.name,
      description: category.description ?? "",
    });
    setErrors({});
    setModalOpen(true);
  };

  const handleCerrar = () => {
    setModalOpen(false);
    setEditTarget(null);
    setForm(emptyForm());
  };

  const setField = (field: keyof SupplyCategoryForm, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (!form.name.trim()) e.name = "El nombre es requerido";
    if (form.name.length > 100) e.name = "Maximo 100 caracteres";
    if (form.description && form.description.length > 255)
      e.description = "Maximo 255 caracteres";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      showAlert("warning", "Completa los campos obligatorios.");
      return;
    }

    try {
      if (editTarget) {
        const response = await apiFetch(`/supply-categories/${editTarget.id}`, {
          method: "PUT",
          body: JSON.stringify({
            name: form.name,
            description: form.description || null,
          }),
        });

        if (!response.ok) {
          const err = await response.json();
          showAlert("error", err.detail || "Error al actualizar categoria");
          return;
        }

        const updated: SupplyCategory = await response.json();
        setCategories((prev) =>
          prev.map((c) => (c.id === editTarget.id ? updated : c))
        );
        showAlert("success", "Categoria actualizada correctamente.");
      } else {
        const response = await apiFetch("/supply-categories/", {
          method: "POST",
          body: JSON.stringify({
            name: form.name,
            description: form.description || null,
          }),
        });

        if (!response.ok) {
          const err = await response.json();
          showAlert("error", err.detail || "Error al crear categoria");
          return;
        }

        const created: SupplyCategory = await response.json();
        setCategories((prev) => [...prev, created]);
        showAlert("success", "Categoria creada correctamente.");
      }

      handleCerrar();
    } catch {
      showAlert("error", "Error de conexion con el servidor.");
    }
  };

  const handleEliminar = (id: number) => {
    showConfirm({
      title: "Eliminar categoria",
      message: "¿Esta seguro que desea eliminar este registro?",
      confirmText: "Eliminar",
      cancelText: "Cancelar",
      onConfirm: async () => {
        try {
          const response = await apiFetch(`/supply-categories/${id}`, {
            method: "DELETE",
          });

          if (!response.ok) {
            const err = await response.json();
            showAlert("error", err.detail || "Error al eliminar categoria");
            return;
          }

          setCategories((prev) => prev.filter((c) => c.id !== id));
          showAlert("success", "Categoria eliminada correctamente.");
        } catch {
          showAlert("error", "Error de conexion con el servidor.");
        }
      },
    });
  };

  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Panaderia" },
        { label: "Categorias de insumos" },
      ]}
    >
      {loading ? (
        <div className="saip-loading">Cargando categorias...</div>
      ) : (
        <Table
          title="Categorias de insumos"
          columns={columns}
          data={categories}
          searchPlaceholder="Buscar categoria"
          sortKey="name"
          headerActions={
            <Button variant="primary" onClick={handleCrear}>
              Crear categoria
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
                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                >
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
              </button>
              <button
                type="button"
                className="saip-table__action-btn saip-table__action-btn--danger"
                title="Eliminar"
                onClick={() => handleEliminar(row.id)}
              >
                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                >
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" />
                  <path d="M10 11v6M14 11v6" />
                  <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" />
                </svg>
              </button>
            </div>
          )}
        />
      )}

      <Modal
        isOpen={modalOpen}
        onClose={handleCerrar}
        title={editTarget ? "Editar categoria" : "Crear categoria"}
        width="480px"
      >
        <form className="scf" onSubmit={handleSubmit}>
          <div className="scf__group">
            <label className="scf__label">
              Nombre<span className="scf__required">*</span>
            </label>
            <input
              className={`scf__input ${errors.name ? "scf__input--error" : ""}`}
              placeholder="Ej: Harinas, Azucares, Frutas..."
              maxLength={100}
              value={form.name}
              onChange={(e) => setField("name", e.target.value)}
            />
            {errors.name && <span className="scf__error">{errors.name}</span>}
          </div>

          <div className="scf__group">
            <label className="scf__label">Descripcion</label>
            <textarea
              className="scf__textarea"
              placeholder="Describe esta categoria de insumo..."
              rows={3}
              maxLength={255}
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
            />
            {errors.description && (
              <span className="scf__error">{errors.description}</span>
            )}
          </div>


          <div className="scf__actions">
            <Button variant="secondary" type="button" onClick={handleCerrar}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {editTarget ? "Guardar cambios" : "Crear categoria"}
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
