import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../../components/layout/Layout";
import Table, { ColumnDef } from "../../components/table/Table";
import Modal from "../../components/modal/Modal";
import Button from "../../components/button/Button";
import BulkUploadModal from "../../components/bulkupload/BulkUploadModal";
import Badge from "../../components/badge/Badge";
import { useAlert } from "../../context/AlertContext";
import { useConfirm } from "../../context/ConfirmContext";
import { apiFetch } from "../../utils/api";
import "./Production.css";

interface UnitBasic {
  id: number;
  name: string;
  abbreviation: string;
}

interface RecipeBasic {
  id: number;
  name: string;
  product_id?: number | null;
  yield_quantity: number;
  yield_unit: UnitBasic;
}

interface ProductionOrder {
  id: number;
  token: string;
  recipe_id: number;
  recipe: RecipeBasic;
  quantity_multiplier: number;
  total_yield: number;
  status: "pending" | "in_progress" | "completed" | "cancelled";
  scheduled_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  cancelled_at: string | null;
  notes: string | null;
  created_at: string;
}

interface Recipe {
  id: number;
  name: string;
  yield_quantity: number;
  yield_unit_id: number;
  yield_unit: UnitBasic;
  status: "active" | "inactive";
}

interface OrderForm {
  recipe_id: string;
  quantity_multiplier: string;
  scheduled_at: string;
  notes: string;
}

type FormErrors = Partial<Record<keyof OrderForm, string>>;

type StatusVariant = "warning" | "access" | "active" | "inactive";

const STATUS_CONFIG: Record<
  ProductionOrder["status"],
  { label: string; variant: StatusVariant }
> = {
  pending: { label: "Pendiente", variant: "warning" },
  in_progress: { label: "En progreso", variant: "access" },
  completed: { label: "Completada", variant: "active" },
  cancelled: { label: "Cancelada", variant: "inactive" },
};

const emptyForm = (): OrderForm => ({
  recipe_id: "",
  quantity_multiplier: "1",
  scheduled_at: "",
  notes: "",
});

const formatDate = (value: string | null): string => {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString("es-CO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// FastAPI envía detail como string (HTTPException) o como lista de errores
// de validación (422); se normaliza a un mensaje legible para el toast.
const formatErrorDetail = (detail: unknown): string => {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) =>
        item && typeof item === "object" && "msg" in item
          ? String((item as { msg: unknown }).msg)
          : JSON.stringify(item)
      )
      .join("; ");
  }
  if (detail && typeof detail === "object") return JSON.stringify(detail);
  return "";
};

const columns: ColumnDef<ProductionOrder>[] = [
  {
    key: "recipe",
    header: "Receta",
    width: "30%",
    render: (row) => row.recipe?.name ?? `Receta #${row.recipe_id}`,
  },
  {
    key: "quantity_multiplier",
    header: "Multiplicador",
    width: "12%",
    render: (row) => (
      <span className="prd__badge-count">×{row.quantity_multiplier}</span>
    ),
  },
  {
    key: "total_yield",
    header: "Rendimiento total",
    width: "16%",
    render: (row) =>
      `${row.total_yield} ${row.recipe?.yield_unit?.abbreviation ?? ""}`,
  },
  {
    key: "status",
    header: "Estado",
    width: "12%",
    render: (row) => {
      const cfg = STATUS_CONFIG[row.status];
      return <Badge label={cfg.label} variant={cfg.variant} />;
    },
  },
  {
    key: "scheduled_at",
    header: "Programada",
    width: "14%",
    render: (row) => formatDate(row.scheduled_at),
  },
];

export default function Produccion(): JSX.Element {
  const [orders, setOrders] = useState<ProductionOrder[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<OrderForm>(emptyForm());
  const [errors, setErrors] = useState<FormErrors>({});
  // Id de la orden con acción en vuelo: bloquea reintentos (doble clic) y
  // deshabilita los botones de esa fila hasta que la petición termine.
  const [actionInProgressId, setActionInProgressId] = useState<number | null>(
    null
  );
  const [creating, setCreating] = useState(false);
  const [bulkOpen, setBulkOpen] = useState(false);
  const [exporting, setExporting] = useState(false);

  const { showAlert } = useAlert();
  const { showConfirm } = useConfirm();

  const handleExportExcel = async () => {
    setExporting(true);
    try {
      const response = await apiFetch("/production/orders/export");
      if (!response.ok) {
        const err = await response.json();
        showAlert("error", err.detail || "Error al generar el reporte.");
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ordenes_produccion_${new Date()
        .toISOString()
        .slice(0, 10)}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
      showAlert("success", "Reporte de órdenes de producción descargado.");
    } catch {
      showAlert("error", "No se pudo conectar con el servidor.");
    } finally {
      setExporting(false);
    }
  };

  const refetchOrders = async (): Promise<boolean> => {
    try {
      const res = await apiFetch("/production/orders/");
      if (res.ok) {
        setOrders(await res.json());
        return true;
      }
    } catch (err) {
      console.error(err);
    }
    return false;
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ordRes, recRes] = await Promise.all([
          apiFetch("/production/orders/"),
          apiFetch("/recipes/"),
        ]);
        if (ordRes.ok) setOrders(await ordRes.json());
        if (recRes.ok) setRecipes(await recRes.json());
      } catch (err) {
        console.error(err);
        showAlert("error", "Error al cargar las órdenes de producción.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activeRecipes = recipes.filter((r) => r.status === "active");

  const selectedRecipe = recipes.find(
    (r) => String(r.id) === form.recipe_id
  );

  const expectedYield =
    selectedRecipe && Number(form.quantity_multiplier) > 0
      ? selectedRecipe.yield_quantity * Number(form.quantity_multiplier)
      : null;

  const handleCrear = () => {
    setForm(emptyForm());
    setErrors({});
    setModalOpen(true);
  };

  const handleCerrar = () => {
    setModalOpen(false);
    setForm(emptyForm());
    setErrors({});
  };

  const setField = (field: keyof OrderForm, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (!form.recipe_id) e.recipe_id = "Selecciona una receta";
    const multiplier = Number(form.quantity_multiplier);
    if (!form.quantity_multiplier || Number.isNaN(multiplier) || multiplier <= 0)
      e.quantity_multiplier = "El multiplicador debe ser mayor a 0";
    if (form.notes.length > 500)
      e.notes = "Las notas no pueden superar 500 caracteres";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      showAlert("warning", "Completa los campos obligatorios.");
      return;
    }
    if (creating) return;
    setCreating(true);

    try {
      const response = await apiFetch("/production/orders/", {
        method: "POST",
        body: JSON.stringify({
          recipe_id: parseInt(form.recipe_id),
          quantity_multiplier: parseFloat(form.quantity_multiplier),
          scheduled_at: form.scheduled_at || null,
          notes: form.notes || null,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        showAlert(
          "error",
          formatErrorDetail(err.detail) ||
            "Error al registrar la orden de producción"
        );
        return;
      }

      await refetchOrders();
      showAlert("success", "Orden de producción registrada correctamente.");
      handleCerrar();
    } catch {
      showAlert("error", "Error de conexión con el servidor.");
    } finally {
      setCreating(false);
    }
  };

  const handleIniciar = (order: ProductionOrder) => {
    showConfirm({
      title: "Iniciar producción",
      message: `¿Deseas iniciar la producción de "${order.recipe?.name}" (#${order.id})?`,
      confirmText: "Iniciar",
      cancelText: "Cancelar",
      onConfirm: async () => {
        setActionInProgressId(order.id);
        try {
          const response = await apiFetch(`/production/orders/${order.id}/start`, {
            method: "PATCH",
          });

          if (!response.ok) {
            const err = await response.json();
            showAlert(
              "error",
              formatErrorDetail(err.detail) || "Error al iniciar la orden"
            );
            return;
          }

          const result = await response.json();
          await refetchOrders();
          showAlert("success", result.message || "Producción iniciada correctamente.");
        } catch {
          showAlert("error", "Error de conexión con el servidor.");
        } finally {
          setActionInProgressId(null);
        }
      },
    });
  };

  const handleConfirmar = (order: ProductionOrder) => {
    showConfirm({
      title: "Confirmar producción",
      message: [
        `Receta: "${order.recipe?.name}" (#${order.id})`,
        `Multiplicador: ×${order.quantity_multiplier}`,
        `Rendimiento esperado: ${order.total_yield} ${order.recipe?.yield_unit?.abbreviation ?? ""}`,
        ...(order.recipe?.product_id
          ? []
          : [
              "",
              "⚠ Esta receta no tiene producto terminado asociado: no se incrementará el stock de Productos terminados.",
            ]),
        "",
        "Se descontarán del inventario las materias primas de la receta. Esta acción no se puede deshacer.",
      ].join("\n"),
      confirmText: "Confirmar",
      cancelText: "Volver",
      onConfirm: async () => {
        setActionInProgressId(order.id);
        try {
          const response = await apiFetch(
            `/production/orders/${order.id}/complete`,
            { method: "POST" }
          );

          if (!response.ok) {
            const err = await response.json();
            showAlert(
              "error",
              formatErrorDetail(err.detail) || "Error al completar la producción"
            );
            return;
          }

          const result = await response.json();
          await refetchOrders();
          showAlert("success", result.message || "Producción completada correctamente.");
        } catch {
          showAlert("error", "Error de conexión con el servidor.");
        } finally {
          setActionInProgressId(null);
        }
      },
    });
  };

  const handleCancelar = (order: ProductionOrder) => {
    showConfirm({
      title: "Cancelar orden",
      message: `¿Estás seguro que deseas cancelar la orden #${order.id} de "${order.recipe?.name}"?`,
      confirmText: "Cancelar orden",
      cancelText: "Volver",
      onConfirm: async () => {
        setActionInProgressId(order.id);
        try {
          const response = await apiFetch(`/production/orders/${order.id}/cancel`, {
            method: "PATCH",
            body: JSON.stringify({ reason: null }),
          });

          if (!response.ok) {
            const err = await response.json();
            showAlert(
              "error",
              formatErrorDetail(err.detail) || "Error al cancelar la orden"
            );
            return;
          }

          const result = await response.json();
          await refetchOrders();
          showAlert("success", result.message || "Orden cancelada correctamente.");
        } catch {
          showAlert("error", "Error de conexión con el servidor.");
        } finally {
          setActionInProgressId(null);
        }
      },
    });
  };

  if (loading) {
    return (
      <Layout
        breadcrumbs={[
          { label: "Dashboard", to: "/dashboard" },
          { label: "Producción" },
        ]}
      >
        <div className="saip-loading">Cargando órdenes de producción...</div>
      </Layout>
    );
  }

  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Producción" },
      ]}
    >
      <Table
        title="Gestión de órdenes de producción"
        columns={columns}
        data={orders}
        searchPlaceholder="Buscar orden"
        emptyMessage="No hay órdenes de producción registradas."
        headerActions={
          <>
            <Button variant="primary" onClick={handleCrear}>
              Nueva orden
            </Button>
            <Button variant="secondary" onClick={() => setBulkOpen(true)}>
              Cargar masivo
            </Button>
            <Button variant="secondary" onClick={handleExportExcel} disabled={exporting}>
              {exporting ? "Generando..." : "Exportar excel"}
            </Button>
          </>
        }
        renderActions={(row) => {
          const busy = actionInProgressId === row.id;
          return (
            <div className="saip-table__actions">
            {row.status === "pending" && (
              <>
                <button
                  className="saip-table__action-btn"
                  title="Iniciar producción"
                  disabled={busy}
                  onClick={() => handleIniciar(row)}
                >
                  <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  >
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                </button>
                <button
                  className="saip-table__action-btn saip-table__action-btn--danger"
                  title="Cancelar orden"
                  disabled={busy}
                  onClick={() => handleCancelar(row)}
                >
                  <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <line x1="15" y1="9" x2="9" y2="15" />
                    <line x1="9" y1="9" x2="15" y2="15" />
                  </svg>
                </button>
              </>
            )}
            {row.status === "in_progress" && (
              <>
                <button
                  className="saip-table__action-btn"
                  title="Confirmar producción"
                  disabled={busy}
                  onClick={() => handleConfirmar(row)}
                >
                  <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  >
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </button>
                <button
                  className="saip-table__action-btn saip-table__action-btn--danger"
                  title="Cancelar orden"
                  disabled={busy}
                  onClick={() => handleCancelar(row)}
                >
                  <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <line x1="15" y1="9" x2="9" y2="15" />
                    <line x1="9" y1="9" x2="15" y2="15" />
                  </svg>
                </button>
              </>
            )}
            </div>
          );
        }}
      />

      <Modal
        isOpen={modalOpen}
        onClose={handleCerrar}
        title="Nueva orden de producción"
        width="520px"
      >
        <form className="prd" onSubmit={handleSubmit}>
          <div className="prd__group">
            <label className="prd__label">
              Receta <span className="prd__required">*</span>
            </label>
            <select
              className={`prd__select ${errors.recipe_id ? "prd__input--error" : ""}`}
              value={form.recipe_id}
              onChange={(e) => setField("recipe_id", e.target.value)}
            >
              <option value="">Selecciona una receta</option>
              {activeRecipes.map((r) => (
                <option key={r.id} value={String(r.id)}>
                  {r.name}
                </option>
              ))}
            </select>
            {errors.recipe_id && <span className="prd__error">{errors.recipe_id}</span>}
          </div>

          <div className="prd__row">
            <div className="prd__group prd__group--half">
              <label className="prd__label">
                Multiplicador de cantidad <span className="prd__required">*</span>
              </label>
              <input
                type="number"
                className={`prd__input ${
                  errors.quantity_multiplier ? "prd__input--error" : ""
                }`}
                min={0.01}
                step={0.01}
                placeholder="Ej: 2"
                value={form.quantity_multiplier}
                onChange={(e) =>
                  setField("quantity_multiplier", e.target.value)
                }
              />
              {errors.quantity_multiplier && (
                <span className="prd__error">{errors.quantity_multiplier}</span>
              )}
            </div>

            <div className="prd__group prd__group--half">
              <label className="prd__label">Fecha programada</label>
              <input
                type="datetime-local"
                className="prd__input"
                value={form.scheduled_at}
                onChange={(e) => setField("scheduled_at", e.target.value)}
              />
            </div>
          </div>

          {expectedYield !== null && selectedRecipe && (
            <div className="prd__preview">
              Rendimiento esperado:
              <strong>
                {expectedYield} {selectedRecipe.yield_unit.abbreviation}
              </strong>
              ({selectedRecipe.yield_quantity} × {form.quantity_multiplier})
            </div>
          )}

          <div className="prd__group">
            <label className="prd__label">Notas</label>
            <textarea
              className="prd__textarea"
              placeholder="Observaciones de la orden..."
              rows={2}
              maxLength={500}
              value={form.notes}
              onChange={(e) => setField("notes", e.target.value)}
            />
            {errors.notes && <span className="prd__error">{errors.notes}</span>}
          </div>

          <div className="prd__actions">
            <Button variant="secondary" type="button" onClick={handleCerrar} disabled={creating}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit" disabled={creating}>
              {creating ? "Registrando..." : "Registrar orden"}
            </Button>
          </div>
        </form>
      </Modal>

      <BulkUploadModal
        isOpen={bulkOpen}
        onClose={() => setBulkOpen(false)}
        title="Carga masiva de órdenes de producción"
        templateUrl="/production/orders/bulk/template"
        importUrl="/production/orders/bulk/import"
        onImported={() => refetchOrders()}
      />
    </Layout>
  );
}
