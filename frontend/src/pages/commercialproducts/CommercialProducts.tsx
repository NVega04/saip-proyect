import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../../components/layout/Layout";
import Table, { ColumnDef } from "../../components/table/Table";
import Modal from "../../components/modal/Modal";
import Button from "../../components/button/Button";
import Badge from "../../components/badge/Badge";
import { useAlert } from "../../context/AlertContext";
import { useConfirm } from "../../context/ConfirmContext";
import { apiFetch } from "../../utils/api";
import "./CommercialProducts.css";
import { useReportDownload } from "../../hooks/useReportDownload.ts";

interface Unit {
  id: number;
  name: string;
  abbreviation: string;
}

interface ProductCategory {
  id: number;
  token: string;
  name: string;
}

interface Provider {
  id: number;
  token: string;
  company: string;
}

interface CommercialProduct {
  id: number;
  token: string;
  name: string;
  description?: string;
  category_id: number;
  category: ProductCategory;
  unit_id: number;
  unit: Unit;
  provider_id?: number | null;
  provider?: Provider | null;
  purchase_price: number;
  sale_price: number;
  available_quantity: number;
  min_stock: number;
  max_stock: number;
  status: string;
}

interface CommercialProductForm {
  name: string;
  description?: string;
  category_id: number;
  unit_id: number;
  provider_id?: number | null;
  purchase_price: number;
  sale_price: number;
  available_quantity: number;
  min_stock: number;
  max_stock: number;
}

type FormErrors = Partial<Record<keyof CommercialProductForm, string>>;

const emptyForm = (): CommercialProductForm => ({
  name: "",
  description: "",
  category_id: 0,
  unit_id: 0,
  provider_id: null,
  purchase_price: 0,
  sale_price: 0,
  available_quantity: 0,
  min_stock: 0,
  max_stock: 0,
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

const columns: ColumnDef<CommercialProduct>[] = [
  { key: "id", header: "ID", width: "5%" },
  { key: "name", header: "Producto", width: "18%" },
  { key: "category", header: "Categoria", width: "12%",
    render: (row) => row.category?.name || "-" },
  { key: "unit", header: "Unidad", width: "8%",
    render: (row) => row.unit?.abbreviation || "-" },
  { key: "provider", header: "Proveedor", width: "15%",
    render: (row) => row.provider?.company || "-" },
  { key: "purchase_price", header: "P. compra", width: "8%",
    render: (row) => `$${row.purchase_price.toFixed(2)}` },
  { key: "sale_price", header: "P. venta", width: "8%",
    render: (row) => `$${row.sale_price.toFixed(2)}` },
  { key: "stock", header: "Stock", width: "18%",
    render: (row) => (
      <StockIndicator
        available={row.available_quantity}
        min={row.min_stock}
        max={row.max_stock}
      />
    )
  },
  { key: "status", header: "Estado", width: "8%",
    render: (row) => (
      <Badge
        label={row.status === "active" ? "Activo" : "Inactivo"}
        variant={row.status === "active" ? "active" : "inactive"}
      />
    )
  },
];

export default function CommercialProducts(): JSX.Element {
  const [products, setProducts] = useState<CommercialProduct[]>([]);
  const [categories, setCategories] = useState<ProductCategory[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<CommercialProduct | null>(null);
  const [form, setForm] = useState<CommercialProductForm>(emptyForm());
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(true);

  const { showAlert } = useAlert();
  const { showConfirm } = useConfirm();
  const { download: downloadReport, loading: reportLoading } = useReportDownload("commercial-products");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [prodRes, catRes, unitRes, provRes] = await Promise.all([
          apiFetch("/commercial-products/"),
          apiFetch("/product-categories/"),
          apiFetch("/units/"),
          apiFetch("/providers/"),
        ]);

        if (prodRes.ok) {
          const data: CommercialProduct[] = await prodRes.json();
          setProducts(data);
        }
        if (catRes.ok) {
          const data: ProductCategory[] = await catRes.json();
          setCategories(data.filter((c) => c.status === "active"));
        }
        if (unitRes.ok) {
          const data: Unit[] = await unitRes.json();
          setUnits(data);
        }
        if (provRes.ok) {
          const data: Provider[] = await provRes.json();
          setProviders(data);
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

  const handleEditar = (product: CommercialProduct) => {
    setEditTarget(product);
    setForm({
      name: product.name,
      description: product.description ?? "",
      category_id: product.category_id,
      unit_id: product.unit_id,
      provider_id: product.provider_id ?? null,
      purchase_price: product.purchase_price,
      sale_price: product.sale_price,
      available_quantity: product.available_quantity,
      min_stock: product.min_stock,
      max_stock: product.max_stock,
    });
    setErrors({});
    setModalOpen(true);
  };

  const handleCerrar = () => {
    setModalOpen(false);
    setEditTarget(null);
    setForm(emptyForm());
  };

  const setField = (field: keyof CommercialProductForm, value: string | number | boolean | null) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (!form.name.trim()) e.name = "El nombre es requerido";
    if (!form.category_id) e.category_id = "Selecciona una categoria";
    if (!form.unit_id) e.unit_id = "Selecciona una unidad";
    if (form.purchase_price < 0) e.purchase_price = "No puede ser negativo";
    if (form.sale_price < 0) e.sale_price = "No puede ser negativo";
    if (form.min_stock < 0) e.min_stock = "No puede ser negativo";
    if (form.max_stock < 0) e.max_stock = "No puede ser negativo";
    if (form.available_quantity < 0) e.available_quantity = "No puede ser negativo";
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
        const response = await apiFetch(`/commercial-products/${editTarget.id}`, {
          method: "PATCH",
          body: JSON.stringify({
            name: form.name,
            description: form.description || null,
            category_id: form.category_id,
            unit_id: form.unit_id,
            provider_id: form.provider_id || null,
            purchase_price: form.purchase_price,
            sale_price: form.sale_price,
            available_quantity: form.available_quantity,
            min_stock: form.min_stock,
            max_stock: form.max_stock,
          }),
        });

        if (!response.ok) {
          const err = await response.json();
          showAlert("error", err.detail || "Error al actualizar producto");
          return;
        }

        const updated: CommercialProduct = await response.json();
        setProducts((prev) => prev.map((p) => (p.id === editTarget.id ? updated : p)));
        showAlert("success", "Producto actualizado correctamente.");
      } else {
        const response = await apiFetch("/commercial-products/", {
          method: "POST",
          body: JSON.stringify({
            name: form.name,
            description: form.description || null,
            category_id: form.category_id,
            unit_id: form.unit_id,
            provider_id: form.provider_id || null,
            purchase_price: form.purchase_price,
            sale_price: form.sale_price,
            available_quantity: form.available_quantity,
            min_stock: form.min_stock,
            max_stock: form.max_stock,
          }),
        });

        if (!response.ok) {
          const err = await response.json();
          showAlert("error", err.detail || "Error al crear producto");
          return;
        }

        const created: CommercialProduct = await response.json();
        setProducts((prev) => [...prev, created]);
        showAlert("success", "Producto creado correctamente.");
      }

      handleCerrar();
    } catch {
      showAlert("error", "Error de conexion con el servidor.");
    }
  };

  const handleEliminar = (id: number) => {
    showConfirm({
      title: "Eliminar producto",
      message: "¿Esta seguro que desea eliminar este registro?",
      confirmText: "Eliminar",
      cancelText: "Cancelar",
      onConfirm: async () => {
        try {
          const response = await apiFetch(`/commercial-products/${id}`, {
            method: "DELETE",
          });

          if (!response.ok) {
            const err = await response.json();
            showAlert("error", err.detail || "Error al eliminar producto");
            return;
          }

          setProducts((prev) => prev.filter((p) => p.id !== id));
          showAlert("success", "Producto eliminado correctamente.");
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
        { label: "Productos comerciales" },
      ]}
    >
      {loading ? (
        <div className="saip-loading">Cargando productos...</div>
      ) : (
        <Table
          title="Productos comerciales"
          columns={columns}
          data={products}
          searchPlaceholder="Buscar producto"
          sortKey="name"
          headerActions={
            <>
            <Button variant="primary" onClick={handleCrear}>
              Crear producto
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

      <Modal
        isOpen={modalOpen}
        onClose={handleCerrar}
        title={editTarget ? "Editar producto" : "Crear producto"}
        width="520px"
      >
        <form className="cpf" onSubmit={handleSubmit}>
          <div className="cpf__group">
            <label className="cpf__label">
              Nombre<span className="cpf__required">*</span>
            </label>
            <input
              className={`cpf__input ${errors.name ? "cpf__input--error" : ""}`}
              placeholder="Ej: Leche entera, Coca-Cola, Salchicha..."
              value={form.name}
              onChange={(e) => setField("name", e.target.value)}
            />
            {errors.name && <span className="cpf__error">{errors.name}</span>}
          </div>

          <div className="cpf__group">
            <label className="cpf__label">Descripcion</label>
            <textarea
              className="cpf__textarea"
              placeholder="Describe este producto..."
              rows={2}
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
            />
          </div>

          <div className="cpf__row">
            <div className="cpf__group cpf__group--half">
              <label className="cpf__label">
                Categoria<span className="cpf__required">*</span>
              </label>
              <select
                className={`cpf__select ${errors.category_id ? "cpf__input--error" : ""}`}
                value={form.category_id}
                onChange={(e) => setField("category_id", parseInt(e.target.value))}
              >
                <option value={0}>Selecciona</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
              {errors.category_id && <span className="cpf__error">{errors.category_id}</span>}
            </div>

            <div className="cpf__group cpf__group--half">
              <label className="cpf__label">
                Unidad<span className="cpf__required">*</span>
              </label>
              <select
                className={`cpf__select ${errors.unit_id ? "cpf__input--error" : ""}`}
                value={form.unit_id}
                onChange={(e) => setField("unit_id", parseInt(e.target.value))}
              >
                <option value={0}>Selecciona</option>
                {units.map((unit) => (
                  <option key={unit.id} value={unit.id}>
                    {unit.name} ({unit.abbreviation})
                  </option>
                ))}
              </select>
              {errors.unit_id && <span className="cpf__error">{errors.unit_id}</span>}
            </div>
          </div>

          <div className="cpf__group">
            <label className="cpf__label">Proveedor</label>
            <select
              className="cpf__select"
              value={form.provider_id ?? ""}
              onChange={(e) => setField("provider_id", e.target.value ? parseInt(e.target.value) : null)}
            >
              <option value="">Sin proveedor</option>
              {providers.map((prov) => (
                <option key={prov.id} value={prov.id}>
                  {prov.company}
                </option>
              ))}
            </select>
          </div>

          <div className="cpf__row">
            <div className="cpf__group cpf__group--half">
              <label className="cpf__label">Precio compra</label>
              <input
                type="number"
                className={`cpf__input ${errors.purchase_price ? "cpf__input--error" : ""}`}
                min={0}
                step={0.01}
                value={form.purchase_price}
                onChange={(e) => setField("purchase_price", parseFloat(e.target.value) || 0)}
              />
              {errors.purchase_price && <span className="cpf__error">{errors.purchase_price}</span>}
            </div>

            <div className="cpf__group cpf__group--half">
              <label className="cpf__label">Precio venta</label>
              <input
                type="number"
                className={`cpf__input ${errors.sale_price ? "cpf__input--error" : ""}`}
                min={0}
                step={0.01}
                value={form.sale_price}
                onChange={(e) => setField("sale_price", parseFloat(e.target.value) || 0)}
              />
              {errors.sale_price && <span className="cpf__error">{errors.sale_price}</span>}
            </div>
          </div>

          <div className="cpf__group">
            <label className="cpf__label">Stock actual</label>
            <input
              type="number"
              className={`cpf__input ${errors.available_quantity ? "cpf__input--error" : ""}`}
              min={0}
              step={1}
              value={form.available_quantity}
              onChange={(e) => setField("available_quantity", parseFloat(e.target.value) || 0)}
            />
            {errors.available_quantity && <span className="cpf__error">{errors.available_quantity}</span>}
          </div>

          <div className="cpf__row">
            <div className="cpf__group cpf__group--half">
              <label className="cpf__label">Stock minimo</label>
              <input
                type="number"
                className={`cpf__input ${errors.min_stock ? "cpf__input--error" : ""}`}
                min={0}
                step={1}
                value={form.min_stock}
                onChange={(e) => setField("min_stock", parseFloat(e.target.value) || 0)}
              />
              {errors.min_stock && <span className="cpf__error">{errors.min_stock}</span>}
            </div>

            <div className="cpf__group cpf__group--half">
              <label className="cpf__label">Stock maximo</label>
              <input
                type="number"
                className={`cpf__input ${errors.max_stock ? "cpf__input--error" : ""}`}
                min={0}
                step={1}
                value={form.max_stock}
                onChange={(e) => setField("max_stock", parseFloat(e.target.value) || 0)}
              />
              {errors.max_stock && <span className="cpf__error">{errors.max_stock}</span>}
            </div>
          </div>

          <div className="cpf__actions">
            <Button variant="secondary" type="button" onClick={handleCerrar}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {editTarget ? "Guardar cambios" : "Crear producto"}
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
