import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import { useAlert } from "../context/AlertContext";
import { useConfirm } from "../context/ConfirmContext";
import { apiFetch } from "../utils/api";
import "./supplies.css";

interface SupplyCategoryBasic {
  id: number;
  token: string;
  name: string;
  status: string;
}

interface UnitBasic {
  id: number;
  token: string;
  name: string;
  abbreviation: string;
}

interface Supply {
  id: number;
  token: string;
  name: string;
  description: string | null;
  category_id: number;
  category: SupplyCategoryBasic;
  unit_id: number;
  unit: UnitBasic;
  available_quantity: number;
  min_stock: number;
  max_stock: number;
  supplier_id: number | null;
  expiration_date: string | null;
  status: string;
  created_at: string;
  created_by: number | null;
  updated_at: string | null;
  updated_by: number | null;
  deleted_at: string | null;
  deleted_by: number | null;
}

interface SupplyForm {
  name: string;
  description: string;
  category_id: number;
  unit_id: number;
  available_quantity: number;
  min_stock: number;
  max_stock: number;
  supplier_id: string;
  expiration_date: string;
}

type FormErrors = Partial<Record<keyof SupplyForm, string>>;

const emptyForm = (): SupplyForm => ({
  name: "",
  description: "",
  category_id: 0,
  unit_id: 0,
  available_quantity: 0,
  min_stock: 0,
  max_stock: 0,
  supplier_id: "",
  expiration_date: "",
});

const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleDateString("es-CO", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

const columns: ColumnDef<Supply>[] = [
  { key: "id", header: "ID", width: "5%" },
  { key: "name", header: "Nombre", width: "18%" },
  { key: "category", header: "Categoria", width: "15%", render: (row) => row.category.name },
  { key: "unit", header: "Unidad", width: "10%", render: (row) => `${row.unit.name} (${row.unit.abbreviation})` },
  { key: "available_quantity", header: "Stock", width: "8%" },
  { key: "min_stock", header: "Stock min", width: "8%" },
  { key: "max_stock", header: "Stock max", width: "8%" },
  { key: "expiration_date", header: "Vencimiento", width: "13%", render: (row) => formatDate(row.expiration_date) },
];

export default function Supplies(): JSX.Element {
  const [supplies, setSupplies] = useState<Supply[]>([]);
  const [categories, setCategories] = useState<SupplyCategoryBasic[]>([]);
  const [units, setUnits] = useState<UnitBasic[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Supply | null>(null);
  const [form, setForm] = useState<SupplyForm>(emptyForm());
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(true);

  const { showAlert } = useAlert();
  const { showConfirm } = useConfirm();

  useEffect(() => {
    const fetchSupplies = async () => {
      try {
        const response = await apiFetch("/supplies/");
        if (!response.ok) throw new Error("Error al cargar insumos");
        const data: Supply[] = await response.json();
        setSupplies(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSupplies();
  }, []);

  const loadFormData = async () => {
    try {
      const [catsRes, unitsRes] = await Promise.all([
        apiFetch("/supply-categories/"),
        apiFetch("/units/"),
      ]);

      if (catsRes.ok) {
        const catsData: SupplyCategoryBasic[] = await catsRes.json();
        setCategories(catsData.filter((c) => c.status === "active"));
      }

      if (unitsRes.ok) {
        const unitsData: UnitBasic[] = await unitsRes.json();
        setUnits(unitsData);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCrear = () => {
    setEditTarget(null);
    setForm(emptyForm());
    setErrors({});
    loadFormData();
    setModalOpen(true);
  };

  const handleEditar = (supply: Supply) => {
    setEditTarget(supply);
    setForm({
      name: supply.name,
      description: supply.description ?? "",
      category_id: supply.category_id,
      unit_id: supply.unit_id,
      available_quantity: supply.available_quantity,
      min_stock: supply.min_stock,
      max_stock: supply.max_stock,
      supplier_id: supply.supplier_id?.toString() ?? "",
      expiration_date: supply.expiration_date
        ? supply.expiration_date.split("T")[0]
        : "",
    });
    setErrors({});
    loadFormData();
    setModalOpen(true);
  };

  const handleCerrar = () => {
    setModalOpen(false);
    setEditTarget(null);
    setForm(emptyForm());
  };

  const setField = (field: keyof SupplyForm, value: string | number) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (!form.name.trim()) e.name = "El nombre es requerido";
    if (form.name.length > 150) e.name = "Maximo 150 caracteres";
    if (form.description && form.description.length > 500)
      e.description = "Maximo 500 caracteres";
    if (form.category_id <= 0) e.category_id = "Selecciona una categoria";
    if (form.unit_id <= 0) e.unit_id = "Selecciona una unidad";
    if (form.available_quantity < 0) e.available_quantity = "No puede ser negativo";
    if (form.min_stock < 0) e.min_stock = "No puede ser negativo";
    if (form.max_stock < 0) e.max_stock = "No puede ser negativo";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      showAlert("warning", "Completa los campos obligatorios.");
      return;
    }

    const payload = {
      name: form.name,
      description: form.description || null,
      category_id: form.category_id,
      unit_id: form.unit_id,
      available_quantity: form.available_quantity,
      min_stock: form.min_stock,
      max_stock: form.max_stock,
      supplier_id: form.supplier_id ? parseInt(form.supplier_id) : null,
      expiration_date: form.expiration_date || null,
    };

    try {
      if (editTarget) {
        const response = await apiFetch(`/supplies/${editTarget.id}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const err = await response.json();
          showAlert("error", err.detail || "Error al actualizar insumo");
          return;
        }

        const updated: Supply = await response.json();
        setSupplies((prev) =>
          prev.map((s) => (s.id === editTarget.id ? updated : s))
        );
        showAlert("success", "Insumo actualizado correctamente.");
      } else {
        const response = await apiFetch("/supplies/", {
          method: "POST",
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const err = await response.json();
          showAlert("error", err.detail || "Error al crear insumo");
          return;
        }

        const created: Supply = await response.json();
        setSupplies((prev) => [...prev, created]);
        showAlert("success", "Insumo creado correctamente.");
      }

      handleCerrar();
    } catch {
      showAlert("error", "Error de conexion con el servidor.");
    }
  };

  const handleEliminar = (id: number) => {
    showConfirm({
      title: "Eliminar insumo",
      message: "¿Esta seguro que desea eliminar este registro?",
      confirmText: "Eliminar",
      cancelText: "Cancelar",
      onConfirm: async () => {
        try {
          const response = await apiFetch(`/supplies/${id}`, {
            method: "DELETE",
          });

          if (!response.ok) {
            const err = await response.json();
            showAlert("error", err.detail || "Error al eliminar insumo");
            return;
          }

          setSupplies((prev) => prev.filter((s) => s.id !== id));
          showAlert("success", "Insumo eliminado correctamente.");
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
        { label: "Insumos" },
      ]}
    >
      {loading ? (
        <div className="saip-loading">Cargando insumos...</div>
      ) : (
        <Table
          title="Insumos"
          columns={columns}
          data={supplies}
          searchPlaceholder="Buscar insumo"
          sortKey="name"
          headerActions={
            <Button variant="primary" onClick={handleCrear}>
              Crear insumo
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
        title={editTarget ? "Editar insumo" : "Crear insumo"}
        width="560px"
      >
        <form className="sf" onSubmit={handleSubmit}>
          <div className="sf__group">
            <label className="sf__label">
              Nombre<span className="sf__required">*</span>
            </label>
            <input
              className={`sf__input ${errors.name ? "sf__input--error" : ""}`}
              placeholder="Ej: Harina de trigo, Azucar refinada..."
              maxLength={150}
              value={form.name}
              onChange={(e) => setField("name", e.target.value)}
            />
            {errors.name && <span className="sf__error">{errors.name}</span>}
          </div>

          <div className="sf__group">
            <label className="sf__label">Descripcion</label>
            <textarea
              className="sf__textarea"
              placeholder="Describe este insumo..."
              rows={3}
              maxLength={500}
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
            />
            {errors.description && (
              <span className="sf__error">{errors.description}</span>
            )}
          </div>

          <div className="sf__group">
            <label className="sf__label">
              Categoria<span className="sf__required">*</span>
            </label>
            <select
              className={`sf__select ${errors.category_id ? "sf__input--error" : ""}`}
              value={form.category_id}
              onChange={(e) => setField("category_id", parseInt(e.target.value))}
            >
              <option value={0}>Seleccionar categoria</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
            {errors.category_id && (
              <span className="sf__error">{errors.category_id}</span>
            )}
          </div>

          <div className="sf__group">
            <label className="sf__label">
              Unidad<span className="sf__required">*</span>
            </label>
            <select
              className={`sf__select ${errors.unit_id ? "sf__input--error" : ""}`}
              value={form.unit_id}
              onChange={(e) => setField("unit_id", parseInt(e.target.value))}
            >
              <option value={0}>Seleccionar unidad</option>
              {units.map((unit) => (
                <option key={unit.id} value={unit.id}>
                  {unit.name} ({unit.abbreviation})
                </option>
              ))}
            </select>
            {errors.unit_id && (
              <span className="sf__error">{errors.unit_id}</span>
            )}
          </div>

          <div className="sf__group">
            <label className="sf__label">Stock disponible</label>
            <input
              type="number"
              className={`sf__input ${errors.available_quantity ? "sf__input--error" : ""}`}
              placeholder="0"
              min={0}
              step={1}
              value={form.available_quantity}
              onChange={(e) => setField("available_quantity", parseFloat(e.target.value) || 0)}
            />
            {errors.available_quantity && (
              <span className="sf__error">{errors.available_quantity}</span>
            )}
          </div>

          <div className="sf__group">
            <label className="sf__label">Stock minimo</label>
            <input
              type="number"
              className={`sf__input ${errors.min_stock ? "sf__input--error" : ""}`}
              placeholder="0"
              min={0}
              step={1}
              value={form.min_stock}
              onChange={(e) => setField("min_stock", parseFloat(e.target.value) || 0)}
            />
            {errors.min_stock && (
              <span className="sf__error">{errors.min_stock}</span>
            )}
          </div>

          <div className="sf__group">
            <label className="sf__label">Stock maximo</label>
            <input
              type="number"
              className={`sf__input ${errors.max_stock ? "sf__input--error" : ""}`}
              placeholder="0"
              min={0}
              step={1}
              value={form.max_stock}
              onChange={(e) => setField("max_stock", parseFloat(e.target.value) || 0)}
            />
            {errors.max_stock && (
              <span className="sf__error">{errors.max_stock}</span>
            )}
          </div>

          <div className="sf__group">
            <label className="sf__label">Fecha de vencimiento</label>
            <input
              type="date"
              className="sf__input"
              value={form.expiration_date}
              onChange={(e) => setField("expiration_date", e.target.value)}
            />
          </div>

          {/* <div className="sf__group">
            <label className="sf__label">ID Proveedor</label>
            <input
              type="number"
              className="sf__input"
              placeholder="Opcional"
              min={1}
              value={form.supplier_id}
              onChange={(e) => setField("supplier_id", e.target.value)}
            />
          </div> */}

          <div className="sf__actions">
            <Button variant="secondary" type="button" onClick={handleCerrar}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {editTarget ? "Guardar cambios" : "Crear insumo"}
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
