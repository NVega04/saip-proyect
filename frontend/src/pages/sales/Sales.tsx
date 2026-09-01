import { JSX, useState, useEffect, useCallback } from "react";
import Layout from "../../components/layout/Layout";
import Button from "../../components/button/Button";
import Badge from "../../components/badge/Badge";
import Modal from "../../components/modal/Modal";
import Pagination from "../../components/pagination/Pagination";
import { useAlert } from "../../context/AlertContext";
import { useConfirm } from "../../context/ConfirmContext";
import { apiFetch } from "../../utils/api";
import "./Sales.css";

type ItemType = "product" | "commercial";

interface Product {
  id: number;
  name: string;
  unit?: { abbreviation: string };
  available_quantity: number;
  min_stock: number;
  status: string;
}

interface CartItem {
  item_type: ItemType;
  item_id: number;
  item_name: string;
  quantity: number;
}

interface StockWarning {
  item_name: string;
  available_quantity: number;
  min_stock: number;
}

interface UserBasic {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
}

interface SaleListItem {
  id: number;
  token: string;
  user_id: number;
  user: UserBasic;
  sale_date: string;
  status: string;
  notes?: string | null;
  item_count: number;
  total_quantity: number;
}

interface SaleItem {
  id: number;
  item_type: string;
  item_id: number;
  item_name: string;
  quantity: number;
}

interface SaleDetail {
  id: number;
  sale_date: string;
  status: string;
  notes?: string | null;
  user: UserBasic;
  items: SaleItem[];
}

interface SaleListPage {
  items: SaleListItem[];
  total: number;
  page: number;
  limit: number;
}

const PAGE_SIZE = 10;

function formatDate(value: string): string {
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString("es-CO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function Ventas(): JSX.Element {
  const [products, setProducts] = useState<Product[]>([]);
  const [commercial, setCommercial] = useState<Product[]>([]);
  const [tab, setTab] = useState<ItemType>("product");
  const [selectedId, setSelectedId] = useState<number>(0);
  const [quantity, setQuantity] = useState<string>("1");
  const [cart, setCart] = useState<CartItem[]>([]);
  const [notes, setNotes] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [sales, setSales] = useState<SaleListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [historyLoading, setHistoryLoading] = useState(true);
  const [detail, setDetail] = useState<SaleDetail | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  const { showAlert } = useAlert();
  const { showConfirm } = useConfirm();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [prodRes, comRes] = await Promise.all([
          apiFetch("/products/"),
          apiFetch("/commercial-products/"),
        ]);
        if (prodRes.ok) {
          const data: Product[] = await prodRes.json();
          setProducts(data.filter((p) => p.status === "active"));
        }
        if (comRes.ok) {
          const data: Product[] = await comRes.json();
          setCommercial(data.filter((p) => p.status === "active"));
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const fetchSales = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        limit: String(PAGE_SIZE),
      });
      if (dateFrom) params.set("date_from", dateFrom);
      if (dateTo) params.set("date_to", dateTo);
      if (statusFilter) params.set("status", statusFilter);

      const response = await apiFetch(`/sales/?${params.toString()}`);
      if (!response.ok) {
        const err = await response.json();
        showAlert("error", err.detail || "Error al cargar las ventas.");
        return;
      }

      const data: SaleListPage = await response.json();
      setSales(data.items);
      setTotal(data.total);
    } catch {
      showAlert("error", "Error de conexión con el servidor.");
    } finally {
      setHistoryLoading(false);
    }
  }, [page, dateFrom, dateTo, statusFilter, showAlert]);

  useEffect(() => {
    fetchSales();
  }, [fetchSales]);

  const [exporting, setExporting] = useState(false);

  const handleExportExcel = async () => {
    setExporting(true);
    try {
      const params = new URLSearchParams();
      if (dateFrom) params.set("date_from", dateFrom);
      if (dateTo) params.set("date_to", dateTo);
      if (statusFilter) params.set("status", statusFilter);

      const response = await apiFetch(`/sales/export?${params.toString()}`);
      if (!response.ok) {
        const err = await response.json();
        showAlert("error", err.detail || "Error al generar el reporte.");
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ventas_${new Date().toISOString().slice(0, 10)}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
      showAlert("success", "Reporte de ventas descargado.");
    } catch {
      showAlert("error", "No se pudo conectar con el servidor.");
    } finally {
      setExporting(false);
    }
  };

  const source = tab === "product" ? products : commercial;
  const selected = source.find((p) => p.id === selectedId);

  const handleTabChange = (next: ItemType) => {
    setTab(next);
    setSelectedId(0);
    setQuantity("1");
  };

  const handleAdd = () => {
    if (!selected) {
      showAlert("warning", "Selecciona un producto.");
      return;
    }

    const qty = parseFloat(quantity);
    if (!qty || qty <= 0) {
      showAlert("warning", "La cantidad debe ser mayor a cero.");
      return;
    }

    const existing = cart.find(
      (c) => c.item_type === tab && c.item_id === selected.id
    );
    const total = qty + (existing?.quantity ?? 0);

    if (total > selected.available_quantity) {
      showAlert(
        "error",
        `Stock insuficiente para '${selected.name}': disponible ${selected.available_quantity}.`
      );
      return;
    }

    if (existing) {
      setCart((prev) =>
        prev.map((c) =>
          c.item_type === tab && c.item_id === selected.id
            ? { ...c, quantity: total }
            : c
        )
      );
    } else {
      setCart((prev) => [
        ...prev,
        {
          item_type: tab,
          item_id: selected.id,
          item_name: selected.name,
          quantity: qty,
        },
      ]);
    }

    setQuantity("1");
    showAlert("success", `'${selected.name}' agregado al carrito.`);
  };

  const handleRemove = (index: number) => {
    setCart((prev) => prev.filter((_, i) => i !== index));
  };

  const handleRegister = async () => {
    if (cart.length === 0) {
      showAlert("warning", "El carrito está vacío.");
      return;
    }

    setSubmitting(true);
    try {
      const response = await apiFetch("/sales/", {
        method: "POST",
        body: JSON.stringify({
          items: cart.map((c) => ({
            item_type: c.item_type,
            item_id: c.item_id,
            quantity: c.quantity,
          })),
          notes: notes || null,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        showAlert("error", err.detail || "Error al registrar la venta.");
        return;
      }

      const data: { warnings: StockWarning[] } = await response.json();
      setCart([]);
      setNotes("");
      fetchSales();

      if (data.warnings.length > 0) {
        const msgs = data.warnings
          .map(
            (w) =>
              `'${w.item_name}' quedó con ${w.available_quantity} (mínimo ${w.min_stock})`
          )
          .join("; ");
        showAlert("warning", `Venta registrada. Stock bajo en: ${msgs}`);
      } else {
        showAlert("success", "Venta registrada correctamente.");
      }
    } catch {
      showAlert("error", "Error de conexión con el servidor.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    fetchSales();
  };

  const handleReset = () => {
    setDateFrom("");
    setDateTo("");
    setStatusFilter("");
    setPage(1);
  };

  const handleViewDetail = async (id: number) => {
    setDetailLoading(true);
    setDetailOpen(true);
    try {
      const response = await apiFetch(`/sales/${id}`);
      if (!response.ok) {
        const err = await response.json();
        showAlert("error", err.detail || "Error al cargar el detalle.");
        setDetailOpen(false);
        return;
      }
      setDetail(await response.json());
    } catch {
      showAlert("error", "Error de conexión con el servidor.");
      setDetailOpen(false);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleAnnul = (sale: SaleListItem) => {
    showConfirm({
      title: "Anular venta",
      message: `¿Desea anular la venta #${sale.id}? El stock de los productos será restaurado.`,
      confirmText: "Anular",
      cancelText: "Cancelar",
      onConfirm: async () => {
        try {
          const response = await apiFetch(`/sales/${sale.id}/annul`, {
            method: "PATCH",
          });
          if (!response.ok) {
            const err = await response.json();
            showAlert("error", err.detail || "Error al anular la venta.");
            return;
          }
          showAlert("success", "Venta anulada y stock restaurado.");
          fetchSales();
        } catch {
          showAlert("error", "Error de conexión con el servidor.");
        }
      },
    });
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Ventas" },
        { label: "Registrar venta" },
      ]}
    >
      {loading ? (
        <div className="saip-loading">Cargando productos...</div>
      ) : (
        <div className="sales">
          <div className="sales__grid">
            {/* Selector de producto */}
            <div className="sales__card">
              <h2 className="sales__card-title">Seleccionar producto</h2>

              <div className="sales__tabs">
                <button
                  type="button"
                  className={`sales__tab ${
                    tab === "product" ? "sales__tab--active" : ""
                  }`}
                  onClick={() => handleTabChange("product")}
                >
                  Terminados
                </button>
                <button
                  type="button"
                  className={`sales__tab ${
                    tab === "commercial" ? "sales__tab--active" : ""
                  }`}
                  onClick={() => handleTabChange("commercial")}
                >
                  Comerciales
                </button>
              </div>

              <div className="sales__group">
                <label className="sales__label">
                  Producto<span style={{ color: "#c0392b" }}>*</span>
                </label>
                <select
                  className="sales__select"
                  value={selectedId}
                  onChange={(e) => setSelectedId(parseInt(e.target.value))}
                >
                  <option value={0}>Selecciona un producto</option>
                  {source.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>

              {selected && (
                <div
                  className={`sales__stock-info ${
                    selected.available_quantity <= selected.min_stock
                      ? "sales__stock-info--low"
                      : ""
                  }`}
                >
                  Stock disponible: {selected.available_quantity}{" "}
                  {selected.unit?.abbreviation ?? ""} · Mínimo:{" "}
                  {selected.min_stock}
                </div>
              )}

              <div className="sales__row">
                <div className="sales__group">
                  <label className="sales__label">
                    Cantidad<span style={{ color: "#c0392b" }}>*</span>
                  </label>
                  <input
                    type="number"
                    className="sales__input"
                    min={0}
                    step={1}
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                  />
                </div>
                <Button variant="primary" onClick={handleAdd}>
                  Agregar
                </Button>
              </div>
            </div>

            {/* Carrito */}
            <div className="sales__card">
              <h2 className="sales__card-title">Carrito de venta</h2>

              {cart.length === 0 ? (
                <p className="sales__cart-empty">
                  No hay productos agregados.
                </p>
              ) : (
                <table className="sales__cart">
                  <thead>
                    <tr>
                      <th>Producto</th>
                      <th>Tipo</th>
                      <th>Cantidad</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {cart.map((item, index) => (
                      <tr key={`${item.item_type}-${item.item_id}`}>
                        <td>{item.item_name}</td>
                        <td>
                          <Badge
                            label={
                              item.item_type === "product"
                                ? "Terminado"
                                : "Comercial"
                            }
                            variant={
                              item.item_type === "product"
                                ? "access"
                                : "warning"
                            }
                          />
                        </td>
                        <td>{item.quantity}</td>
                        <td>
                          <button
                            type="button"
                            className="sales__remove"
                            title="Quitar"
                            onClick={() => handleRemove(index)}
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
                            </svg>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              <div className="sales__group">
                <label className="sales__label">Notas (opcional)</label>
                <textarea
                  className="sales__textarea"
                  placeholder="Observaciones sobre la venta..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </div>

              <div className="sales__summary">
                <span className="sales__summary-count">
                  {cart.length} item{cart.length !== 1 ? "s" : ""} ·{" "}
                  {cart.reduce((acc, c) => acc + c.quantity, 0)} unidades
                </span>
                <Button
                  variant="primary"
                  onClick={handleRegister}
                  disabled={submitting || cart.length === 0}
                >
                  {submitting ? "Registrando..." : "Registrar venta"}
                </Button>
              </div>
            </div>
          </div>

          {/* Historial de ventas */}
          <div className="sales-hist__filters">
            <div className="sales-hist__group">
              <label className="sales-hist__label">Desde</label>
              <input
                type="date"
                className="sales-hist__input"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
              />
            </div>
            <div className="sales-hist__group">
              <label className="sales-hist__label">Hasta</label>
              <input
                type="date"
                className="sales-hist__input"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
              />
            </div>
            <div className="sales-hist__group">
              <label className="sales-hist__label">Estado</label>
              <select
                className="sales-hist__select"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="">Todos</option>
                <option value="completada">Completada</option>
                <option value="anulada">Anulada</option>
              </select>
            </div>
            <Button variant="primary" onClick={handleSearch}>
              Buscar
            </Button>
            <Button variant="secondary" onClick={handleReset}>
              Limpiar
            </Button>
            <Button variant="secondary" onClick={handleExportExcel} disabled={exporting}>
              {exporting ? "Generando..." : "Exportar excel"}
            </Button>
          </div>

          <div className="sales-hist__table-card">
            <h2 className="sales-hist__title">Historial de ventas</h2>

            {historyLoading ? (
              <div className="saip-loading">Cargando ventas...</div>
            ) : (
              <table className="sales-hist__table">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Vendedor</th>
                    <th>Items</th>
                    <th>Unidades</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {sales.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="sales-hist__empty">
                        No hay ventas para mostrar.
                      </td>
                    </tr>
                  ) : (
                    sales.map((sale) => (
                      <tr key={sale.id}>
                        <td>{formatDate(sale.sale_date)}</td>
                        <td>
                          {sale.user.first_name} {sale.user.last_name}
                        </td>
                        <td>{sale.item_count}</td>
                        <td>{sale.total_quantity}</td>
                        <td>
                          <Badge
                            label={
                              sale.status === "completada"
                                ? "Completada"
                                : "Anulada"
                            }
                            variant={
                              sale.status === "completada"
                                ? "active"
                                : "inactive"
                            }
                          />
                        </td>
                        <td>
                          <div style={{ display: "flex", gap: "0.25rem" }}>
                            <button
                              type="button"
                              className="sales-hist__action-btn"
                              title="Ver detalle"
                              onClick={() => handleViewDetail(sale.id)}
                            >
                              <svg
                                width="15"
                                height="15"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.8"
                              >
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                                <circle cx="12" cy="12" r="3" />
                              </svg>
                            </button>
                            {sale.status === "completada" && (
                              <button
                                type="button"
                                className="sales-hist__action-btn sales-hist__action-btn--danger"
                                title="Anular venta"
                                onClick={() => handleAnnul(sale)}
                              >
                                <svg
                                  width="15"
                                  height="15"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  strokeWidth="1.8"
                                >
                                  <path d="M18 6L6 18" />
                                  <path d="M6 6l12 12" />
                                </svg>
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            )}

            {totalPages > 1 && (
              <div className="sales-hist__pagination">
                <Pagination
                  currentPage={page}
                  totalPages={totalPages}
                  onPageChange={setPage}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Detalle */}
      <Modal
        isOpen={detailOpen}
        onClose={() => setDetailOpen(false)}
        title={`Detalle de venta #${detail?.id ?? ""}`}
        width="520px"
      >
        {detailLoading ? (
          <div className="saip-loading">Cargando detalle...</div>
        ) : detail ? (
          <div className="sales-hist__detail-list">
            <div className="sales-hist__detail-row">
              <strong>Fecha</strong>
              <span>{formatDate(detail.sale_date)}</span>
            </div>
            <div className="sales-hist__detail-row">
              <strong>Vendedor</strong>
              <span>
                {detail.user.first_name} {detail.user.last_name}
              </span>
            </div>
            <div className="sales-hist__detail-row">
              <strong>Estado</strong>
              <span>
                <Badge
                  label={detail.status === "completada" ? "Completada" : "Anulada"}
                  variant={detail.status === "completada" ? "active" : "inactive"}
                />
              </span>
            </div>

            <h3 className="sales-hist__items-title">Productos</h3>
            {detail.items.map((item) => (
              <div className="sales-hist__detail-row" key={item.id}>
                <span>
                  {item.item_name}{" "}
                  <Badge
                    label={item.item_type === "product" ? "Terminado" : "Comercial"}
                    variant={item.item_type === "product" ? "access" : "warning"}
                  />
                </span>
                <strong>x {item.quantity}</strong>
              </div>
            ))}

            {detail.notes && (
              <p className="sales-hist__notes">Notas: {detail.notes}</p>
            )}
          </div>
        ) : null}
      </Modal>
    </Layout>
  );
}