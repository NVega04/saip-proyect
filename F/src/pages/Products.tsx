import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import Badge from "../components/Badge";
import { apiFetch } from "../utils/api";
import "./products.css";

interface Unit {
  id: number;
  name: string;
  abbreviation: string;
}

interface Product {
  id: number;
  token: string;
  name: string;
  description?: string;
  unit_id: number;
  unit: Unit;
  available_quantity: number;
  min_stock: number;
  max_stock: number;
  is_locked: boolean;
  status: "active" | "inactive";
}

interface ProductForm {
  name: string;
  description?: string;
  unit_id: number;
  available_quantity: number;
  min_stock: number;
  max_stock: number;
  is_locked: boolean;
}

type FormErrors = Partial<Record<keyof ProductForm, string>>;

const emptyForm = (): ProductForm => ({
  name: "",
  description: "",
  unit_id: 0,
  available_quantity: 0,
  min_stock: 0,
  max_stock: 0,
  is_locked: false,
});

interface StockIndicatorProps {
  available: number;
  min: number;
  max: number;
}

function StockIndicator({ available, min, max }: StockIndicatorProps) {
  const percentage = max > 0 ? (available / max) * 100 : 0;
  const isLow = available <= min;
  const isHigh = available >= max;

  let color = "#4caf50";
  if (isLow) color = "#f44336";
  else if (isHigh) color = "#ff9800";

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
      <div style={{
        width: "60px",
        height: "6px",
        background: "#e0e0e0",
        borderRadius: "3px",
        overflow: "hidden",
      }}>
        <div style={{
          width: `${Math.min(percentage, 100)}%`,
          height: "100%",
          background: color,
          transition: "width 0.3s, background 0.3s",
        }} />
      </div>
      <span style={{ fontSize: "0.75rem", color: "#666" }}>
        {available}
      </span>
    </div>
  );
}

const columns: ColumnDef<Product>[] = [
  { key: "id", header: "ID", width: "5%" },
  { key: "name", header: "Producto", width: "25%" },
  { key: "unit", header: "Unidad", width: "10%", 
    render: (row) => row.unit?.abbreviation || "-" },
  { key: "stock", header: "Stock actual", width: "20%",
    render: (row) => (
      <StockIndicator 
        available={row.available_quantity} 
        min={row.min_stock} 
        max={row.max_stock} 
      />
    )
  },
  { key: "min_stock", header: "Stock mínimo", width: "25%" },
  { key: "max_stock", header: "Stock máximo", width: "25%" },
  { key: "is_locked", header: "Bloqueado", width: "10%",
    render: (row) => (
      <Badge 
        label={row.is_locked ? "Si" : "No"} 
        variant={row.is_locked ? "warning" : "active"} 
      />
    )
  },
];

export default function Products(): JSX.Element {
  const [products, setProducts] = useState<Product[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Product | null>(null);
  const [form, setForm] = useState<ProductForm>(emptyForm());
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [productsRes, unitsRes] = await Promise.all([
          apiFetch("/products/"),
          apiFetch("/units/"),
        ]);
        if (productsRes.ok && unitsRes.ok) {
          const productsData: Product[] = await productsRes.json();
          const unitsData: Unit[] = await unitsRes.json();
          setProducts(productsData);
          setUnits(unitsData);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleCrear = () => {
    setEditTarget(null);
    setForm(emptyForm());
    setErrors({});
    setModalOpen(true);
  };

  const handleEditar = (product: Product) => {
    setEditTarget(product);
    setForm({
      name: product.name,
      description: product.description ?? "",
      unit_id: product.unit_id,
      available_quantity: product.available_quantity,
      min_stock: product.min_stock,
      max_stock: product.max_stock,
      is_locked: product.is_locked,
    });
    setErrors({});
    setModalOpen(true);
  };

  const handleCerrar = () => {
    setModalOpen(false);
    setEditTarget(null);
    setForm(emptyForm());
  };

  const setField = (field: keyof ProductForm, value: string | number | boolean) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (!form.name.trim()) e.name = "El nombre es requerido";
    if (!form.unit_id) e.unit_id = "Selecciona una unidad";
    if (form.min_stock < 0) e.min_stock = "No puede ser negativo";
    if (form.max_stock < 0) e.max_stock = "No puede ser negativo";
    if (form.available_quantity < 0) e.available_quantity = "No puede ser negativo";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      if (editTarget) {
        const response = await apiFetch(`/products/${editTarget.id}`, {
          method: "PATCH",
          body: JSON.stringify({
            name: form.name,
            description: form.description || null,
            unit_id: form.unit_id,
            available_quantity: form.available_quantity,
            min_stock: form.min_stock,
            max_stock: form.max_stock,
            is_locked: form.is_locked,
          }),
        });
        if (response.status === 403) {
          alert("El producto esta bloqueado y no puede ser modificado");
          return;
        }
        if (!response.ok) {
          const err = await response.json();
          alert(err.detail || "Error al actualizar producto");
          return;
        }
        const updated: Product = await response.json();
        setProducts((prev) => prev.map((p) => p.id === editTarget.id ? updated : p));
      } else {
        const response = await apiFetch("/products/", {
          method: "POST",
          body: JSON.stringify({
            name: form.name,
            description: form.description || null,
            unit_id: form.unit_id,
            available_quantity: form.available_quantity,
            min_stock: form.min_stock,
            max_stock: form.max_stock,
            is_locked: form.is_locked,
          }),
        });
        if (!response.ok) {
          const err = await response.json();
          alert(err.detail || "Error al crear producto");
          return;
        }
        const created: Product = await response.json();
        setProducts((prev) => [...prev, created]);
      }
      handleCerrar();
    } catch {
      alert("Error de conexion con el servidor.");
    }
  };

  const handleEliminar = async (id: number) => {
    const product = products.find(p => p.id === id);
    if (product?.is_locked) {
      alert("El producto esta bloqueado y no puede ser eliminado");
      return;
    }
    if (!confirm("¿Esta seguro de eliminar este producto?")) return;
    try {
      const response = await apiFetch(`/products/${id}`, { method: "DELETE" });
      if (response.status === 403) {
        alert("El producto esta bloqueado y no puede ser eliminado");
        return;
      }
      if (!response.ok) {
        const err = await response.json();
        alert(err.detail || "Error al eliminar producto");
        return;
      }
      setProducts((prev) => prev.filter((p) => p.id !== id));
    } catch {
      alert("Error de conexion con el servidor.");
    }
  };

  const handleToggleLock = async (id: number) => {
    try {
      const response = await apiFetch(`/products/${id}/lock`, { method: "PATCH" });
      if (!response.ok) {
        const err = await response.json();
        alert(err.detail || "Error al cambiar estado de bloqueo");
        return;
      }
      const updated: Product = await response.json();
      setProducts((prev) => prev.map((p) => p.id === id ? updated : p));
    } catch {
      alert("Error de conexion con el servidor.");
    }
  };

  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Recetas" },
        { label: "Productos" },
      ]}
    >
      {loading ? (
        <div className="saip-loading">Cargando productos...</div>
      ) : (
        <Table
          title="Productos terminados"
          columns={columns}
          data={products}
          searchPlaceholder="Buscar producto"
          sortKey="name"
          headerActions={
            <Button variant="primary" onClick={handleCrear}>
              Crear producto
            </Button>
          }
          renderActions={(row) => (
            <div className="saip-table__actions">
              <button
                type="button"
                className="saip-table__action-btn"
                title={row.is_locked ? "Desbloquear" : "Bloquear"}
                onClick={() => handleToggleLock(row.id)}
                style={{ opacity: 0.7 }}
              >
                {row.is_locked ? (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="1.8">
                    <rect x="3" y="11" width="18" height="11" rx="2"/>
                    <path d="M7 11V7a5 5 0 0110 0v4"/>
                  </svg>
                ) : (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="1.8">
                    <rect x="3" y="11" width="18" height="11" rx="2"/>
                    <path d="M7 11V7a5 5 0 019.9-1"/>
                  </svg>
                )}
              </button>
              <button
                type="button"
                className="saip-table__action-btn"
                title="Editar"
                onClick={() => handleEditar(row)}
                disabled={row.is_locked}
                style={{ opacity: row.is_locked ? 0.3 : 1 }}
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
                disabled={row.is_locked}
                style={{ opacity: row.is_locked ? 0.3 : 1 }}
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

      <Modal
        isOpen={modalOpen}
        onClose={handleCerrar}
        title={editTarget ? "Editar producto" : "Crear producto"}
        width="480px"
      >
        <form className="pf" onSubmit={handleSubmit}>
          <div className="pf__group">
            <label className="pf__label">
              Nombre<span className="pf__required">*</span>
            </label>
            <input
              className={`pf__input ${errors.name ? "pf__input--error" : ""}`}
              placeholder="Ej: Harina de trigo, Azucar..."
              value={form.name}
              onChange={(e) => setField("name", e.target.value)}
              disabled={editTarget?.is_locked}
            />
            {errors.name && <span className="pf__error">{errors.name}</span>}
          </div>

          <div className="pf__group">
            <label className="pf__label">Descripcion</label>
            <textarea
              className="pf__textarea"
              placeholder="Describe este producto..."
              rows={2}
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
              disabled={editTarget?.is_locked}
            />
          </div>

          <div className="pf__group">
            <label className="pf__label">
              Unidad de medida<span className="pf__required">*</span>
            </label>
            <select
              className={`pf__select ${errors.unit_id ? "pf__input--error" : ""}`}
              value={form.unit_id}
              onChange={(e) => setField("unit_id", parseInt(e.target.value))}
              disabled={editTarget?.is_locked}
            >
              <option value={0}>Selecciona una unidad</option>
              {units.map((unit) => (
                <option key={unit.id} value={unit.id}>
                  {unit.name} ({unit.abbreviation})
                </option>
              ))}
            </select>
            {errors.unit_id && <span className="pf__error">{errors.unit_id}</span>}
          </div>

          <div className="pf__group">
            <label className="pf__label">Stock actual</label>
            <input
              type="number"
              className={`pf__input ${errors.available_quantity ? "pf__input--error" : ""}`}
              min={0}
              step={1}
              value={form.available_quantity}
              onChange={(e) => setField("available_quantity", parseFloat(e.target.value) || 0)}
              disabled={editTarget?.is_locked}
            />
            {errors.available_quantity && <span className="pf__error">{errors.available_quantity}</span>}
          </div>

          <div className="pf__group">
            <label className="pf__label">Stock minimo</label>
            <input
              type="number"
              className={`pf__input ${errors.min_stock ? "pf__input--error" : ""}`}
              min={0}
              step={1}
              value={form.min_stock}
              onChange={(e) => setField("min_stock", parseFloat(e.target.value) || 0)}
              disabled={editTarget?.is_locked}
            />
            {errors.min_stock && <span className="pf__error">{errors.min_stock}</span>}
          </div>

          <div className="pf__group">
            <label className="pf__label">Stock maximo</label>
            <input
              type="number"
              className={`pf__input ${errors.max_stock ? "pf__input--error" : ""}`}
              min={0}
              step={1}
              value={form.max_stock}
              onChange={(e) => setField("max_stock", parseFloat(e.target.value) || 0)}
              disabled={editTarget?.is_locked}
            />
            {errors.max_stock && <span className="pf__error">{errors.max_stock}</span>}
          </div>

          <div className="pf__actions">
            <Button variant="secondary" type="button" onClick={handleCerrar}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit" disabled={editTarget?.is_locked}>
              {editTarget ? "Guardar cambios" : "Crear producto"}
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
