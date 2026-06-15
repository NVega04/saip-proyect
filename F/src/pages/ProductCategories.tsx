import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import { useAlert } from "../context/AlertContext";
import { useConfirm } from "../context/ConfirmContext";
import { apiFetch } from "../utils/api";
import "./product-categories.css";
import { useReportDownload } from "../hooks/useReportDownload.ts";

interface CommercialProductBasic {
  id: number;
  token: string;
  name: string;
  status: string;
}

interface ProductCategory {
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
  commercial_products: CommercialProductBasic[];
}

interface ProductCategoryForm {
  name: string;
  description: string;
}

type FormErrors = Partial<Record<keyof ProductCategoryForm, string>>;

const emptyForm = (): ProductCategoryForm => ({
  name: "",
  description: "",
});

const columns: ColumnDef<ProductCategory>[] = [
  { key: "id", header: "ID", width: "5%" },
  { key: "name", header: "Nombre", width: "30%" },
  { key: "description", header: "Descripcion", width: "25%" },
  {
    key: "commercial_products",
    header: "Productos",
    width: "40%",
    render: (row) => (
      <div className="pcat-products-list">
        {row.commercial_products.length === 0 ? (
          <span className="pcat-products-empty">Sin productos</span>
        ) : (
          row.commercial_products.map((p) => (
            <span key={p.id} className="pcat-product-tag">
              {p.name}
            </span>
          ))
        )}
      </div>
    ),
  },
];

export default function ProductCategories(): JSX.Element {
  const [categories, setCategories] = useState<ProductCategory[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<ProductCategory | null>(null);
  const [form, setForm] = useState<ProductCategoryForm>(emptyForm());
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(true);

  const { showAlert } = useAlert();
  const { showConfirm } = useConfirm();
  const { download: downloadReport, loading: reportLoading } = useReportDownload("product-categories");

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await apiFetch("/product-categories/");
        if (!response.ok) throw new Error("Error al cargar categorias");
        const data: ProductCategory[] = await response.json();
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

  const handleEditar = (category: ProductCategory) => {
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

  const setField = (field: keyof ProductCategoryForm, value: string) => {
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
        const response = await apiFetch(`/product-categories/${editTarget.id}`, {
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

        const updated: ProductCategory = await response.json();
        setCategories((prev) =>
          prev.map((c) => (c.id === editTarget.id ? updated : c))
        );
        showAlert("success", "Categoria actualizada correctamente.");
      } else {
        const response = await apiFetch("/product-categories/", {
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

        const created: ProductCategory = await response.json();
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
          const response = await apiFetch(`/product-categories/${id}`, {
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
        { label: "Categorias de productos" },
      ]}
    >
      {loading ? (
        <div className="saip-loading">Cargando categorias...</div>
      ) : (
        <Table
          title="Categorias de productos"
          columns={columns}
          data={categories}
          searchPlaceholder="Buscar categoria"
          sortKey="name"
          headerActions={
            <>
            <Button variant="primary" onClick={handleCrear}>
              Crear categoria
            </Button>
             <Button
                variant="secondary"
                onClick={downloadReport}
                disabled={reportLoading}
                icon={
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                  }
                >
                {reportLoading ? "Generando..." : "Exportar excel"}
            </Button>
            </>
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
        <form className="pcatf" onSubmit={handleSubmit}>
          <div className="pcatf__group">
            <label className="pcatf__label">
              Nombre<span className="pcatf__required">*</span>
            </label>
            <input
              className={`pcatf__input ${errors.name ? "pcatf__input--error" : ""}`}
              placeholder="Ej: Lacteos, Gaseosas, Embutidos..."
              maxLength={100}
              value={form.name}
              onChange={(e) => setField("name", e.target.value)}
            />
            {errors.name && <span className="pcatf__error">{errors.name}</span>}
          </div>

          <div className="pcatf__group">
            <label className="pcatf__label">Descripcion</label>
            <textarea
              className="pcatf__textarea"
              placeholder="Describe esta categoria..."
              rows={3}
              maxLength={255}
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
            />
            {errors.description && (
              <span className="pcatf__error">{errors.description}</span>
            )}
          </div>

          <div className="pcatf__actions">
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
