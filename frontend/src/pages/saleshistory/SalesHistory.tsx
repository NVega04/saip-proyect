import { JSX, useState, useEffect, useCallback } from "react";
import Layout from "../../components/layout/Layout";
import Button from "../../components/button/Button";
import Badge from "../../components/badge/Badge";
import Modal from "../../components/modal/Modal";
import Pagination from "../../components/pagination/Pagination";
import { useAlert } from "../../context/AlertContext";
import { useConfirm } from "../../context/ConfirmContext";
import { apiFetch } from "../../utils/api";
import "./SalesHistory.css";

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

export default function SalesHistory(): JSX.Element {
  const [sales, setSales] = useState<SaleListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState<SaleDetail | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  const { showAlert } = useAlert();
  const { showConfirm } = useConfirm();

  const fetchSales = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: String(page), limit: String(PAGE_SIZE) });
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
      setLoading(false);
    }
  }, [page, dateFrom, dateTo, statusFilter, showAlert]);

  useEffect(() => {
    fetchSales();
  }, [fetchSales]);

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
        { label: "Historial de ventas" },
      ]}
    >
      <div className="sales-hist">
        {/* Filtros */}
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
        </div>

        {/* Tabla */}
        <div className="sales-hist__table-card">
          <h2 className="sales-hist__title">Historial de ventas</h2>

          {loading ? (
            <div className="saip-loading">Cargando ventas...</div>
          ) : (
            <table className="sales-hist__table">
              <thead>
                <tr>
                  <th>ID</th>
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
                    <td colSpan={7} className="sales-hist__empty">
                      No hay ventas para mostrar.
                    </td>
                  </tr>
                ) : (
                  sales.map((sale) => (
                    <tr key={sale.id}>
                      <td>{sale.id}</td>
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