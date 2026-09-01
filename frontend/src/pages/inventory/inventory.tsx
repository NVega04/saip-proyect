import { JSX, useState, useEffect, useCallback } from "react";
import Layout from "../../components/layout/Layout";
import Button from "../../components/button/Button";
import Badge from "../../components/badge/Badge";
import Pagination from "../../components/pagination/Pagination";
import { useAlert } from "../../context/AlertContext";
import { apiFetch } from "../../utils/api";
import "./Inventory.css";

type ItemTypeValue = "supply" | "product" | "commercial";
type StockStatusValue = "bajo" | "normal" | "sobre";

interface InventoryItemData {
  id: number;
  item_type: ItemTypeValue;
  name: string;
  description?: string | null;
  category_name?: string | null;
  unit_abbreviation?: string | null;
  available_quantity: number;
  min_stock: number;
  max_stock: number;
  stock_status: StockStatusValue;
  status: string;
}

interface InventorySummaryData {
  total_items: number;
  bajo_stock: number;
  sobre_stock: number;
}

interface InventoryPageData {
  items: InventoryItemData[];
  total: number;
  page: number;
  limit: number;
  summary: InventorySummaryData;
}

const PAGE_SIZE = 10;

const ITEM_TYPE_LABEL: Record<ItemTypeValue, string> = {
  supply: "Insumo",
  product: "Terminado",
  commercial: "Comercial",
};

const STOCK_LABEL: Record<StockStatusValue, string> = {
  bajo: "Bajo stock",
  normal: "Normal",
  sobre: "Sobre stock",
};

export default function Inventario(): JSX.Element {
  const [items, setItems] = useState<InventoryItemData[]>([]);
  const [total, setTotal] = useState(0);
  const [summary, setSummary] = useState<InventorySummaryData>({
    total_items: 0,
    bajo_stock: 0,
    sobre_stock: 0,
  });
  const [page, setPage] = useState(1);
  const [itemType, setItemType] = useState("");
  const [stockStatus, setStockStatus] = useState("");
  const [search, setSearch] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("active");
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  const { showAlert } = useAlert();

  const fetchSummary = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        limit: String(PAGE_SIZE),
      });
      if (itemType) params.set("item_type", itemType);
      if (stockStatus) params.set("stock_status", stockStatus);
      if (appliedSearch) params.set("search", appliedSearch);
      if (statusFilter) params.set("status", statusFilter);

      const response = await apiFetch(`/inventory/summary?${params.toString()}`);
      if (!response.ok) {
        const err = await response.json();
        showAlert("error", err.detail || "Error al cargar el inventario.");
        return;
      }

      const data: InventoryPageData = await response.json();
      setItems(data.items);
      setTotal(data.total);
      setSummary(data.summary);
    } catch {
      showAlert("error", "Error de conexión con el servidor.");
    } finally {
      setLoading(false);
    }
  }, [page, itemType, stockStatus, appliedSearch, statusFilter, showAlert]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  const handleSearch = () => {
    setPage(1);
    setAppliedSearch(search);
  };

  const handleReset = () => {
    setItemType("");
    setStockStatus("");
    setSearch("");
    setAppliedSearch("");
    setStatusFilter("active");
    setPage(1);
  };

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const params = new URLSearchParams();
      if (itemType) params.set("item_type", itemType);
      if (stockStatus) params.set("stock_status", stockStatus);
      if (appliedSearch) params.set("search", appliedSearch);
      if (statusFilter) params.set("status", statusFilter);

      const response = await apiFetch(`/inventory/report?${params.toString()}`);
      if (!response.ok) {
        const err = await response.json();
        showAlert("error", err.detail || "Error al generar el informe.");
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `reporte_inventario_${new Date().toISOString().slice(0, 10)}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
      showAlert("success", "Informe de inventario descargado.");
    } catch {
      showAlert("error", "No se pudo conectar con el servidor.");
    } finally {
      setDownloading(false);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Inventario" },
      ]}
    >
      <div className="inventory">
        {/* Resumen visual */}
        <div className="inventory__stats">
          <div className="inventory__stat">
            <span className="inventory__stat-value">{summary.total_items}</span>
            <span className="inventory__stat-label">Ítems en inventario</span>
          </div>
          <div className="inventory__stat inventory__stat--low">
            <span className="inventory__stat-value">{summary.bajo_stock}</span>
            <span className="inventory__stat-label">Bajo stock</span>
          </div>
          <div className="inventory__stat inventory__stat--over">
            <span className="inventory__stat-value">{summary.sobre_stock}</span>
            <span className="inventory__stat-label">Sobre stock</span>
          </div>
        </div>

        {/* Filtros */}
        <div className="inventory__filters">
          <div className="inventory__group">
            <label className="inventory__label">Tipo</label>
            <select
              className="inventory__select"
              value={itemType}
              onChange={(e) => setItemType(e.target.value)}
            >
              <option value="">Todos</option>
              <option value="supply">Insumos</option>
              <option value="product">Productos terminados</option>
              <option value="commercial">Comerciales</option>
            </select>
          </div>
          <div className="inventory__group">
            <label className="inventory__label">Estado de stock</label>
            <select
              className="inventory__select"
              value={stockStatus}
              onChange={(e) => setStockStatus(e.target.value)}
            >
              <option value="">Todos</option>
              <option value="bajo">Bajo stock</option>
              <option value="normal">Normal</option>
              <option value="sobre">Sobre stock</option>
            </select>
          </div>
          <div className="inventory__group">
            <label className="inventory__label">Estado</label>
            <select
              className="inventory__select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="active">Activos</option>
              <option value="inactive">Inactivos</option>
            </select>
          </div>
          <div className="inventory__group inventory__group--grow">
            <label className="inventory__label">Buscar</label>
            <input
              type="text"
              className="inventory__input"
              placeholder="Nombre del ítem..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSearch();
              }}
            />
          </div>
          <Button variant="primary" onClick={handleSearch}>
            Buscar
          </Button>
          <Button variant="secondary" onClick={handleReset}>
            Limpiar
          </Button>
          <Button variant="secondary" onClick={handleDownload} disabled={downloading}>
            {downloading ? "Generando..." : "Descargar informe"}
          </Button>
        </div>

        {/* Tabla */}
        <div className="inventory__table-card">
          <h2 className="inventory__title">Consolidado de inventario</h2>

          {loading ? (
            <div className="saip-loading">Cargando inventario...</div>
          ) : (
            <table className="inventory__table">
              <thead>
                <tr>
                  <th>Tipo</th>
                  <th>Nombre</th>
                  <th>Categoría</th>
                  <th>Unidad</th>
                  <th>Disponible</th>
                  <th>Mínimo</th>
                  <th>Máximo</th>
                  <th>Estado de stock</th>
                </tr>
              </thead>
              <tbody>
                {items.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="inventory__empty">
                      No hay ítems para mostrar.
                    </td>
                  </tr>
                ) : (
                  items.map((item) => (
                    <tr key={`${item.item_type}-${item.id}`}>
                      <td>
                        <Badge
                          label={ITEM_TYPE_LABEL[item.item_type]}
                          variant={
                            item.item_type === "product"
                              ? "access"
                              : item.item_type === "supply"
                                ? "active"
                                : "warning"
                          }
                        />
                      </td>
                      <td>{item.name}</td>
                      <td>{item.category_name ?? "—"}</td>
                      <td>{item.unit_abbreviation ?? "—"}</td>
                      <td>{item.available_quantity}</td>
                      <td>{item.min_stock}</td>
                      <td>{item.max_stock}</td>
                      <td>
                        <Badge
                          label={STOCK_LABEL[item.stock_status]}
                          variant={
                            item.stock_status === "bajo"
                              ? "inactive"
                              : item.stock_status === "sobre"
                                ? "warning"
                                : "active"
                          }
                        />
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}

          {totalPages > 1 && (
            <div className="inventory__pagination">
              <Pagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={setPage}
              />
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
