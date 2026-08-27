import React, { JSX, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  ComposedChart,
  Legend,
} from "recharts";
import Layout from "../../components/layout/Layout";
import KpiCard from "../../components/kpicard/KpiCard";
import ChartCard from "../../components/chartcard/ChartCard";
import { apiFetch } from "../../utils/api";
import { useAlert } from "../../context/AlertContext";
import "./dashboard.css";

interface DashboardKpis {
  insumos_activos: number;
  stock_bajo_count: number;
  vencidos_count: number;
  por_vencer_count: number;
  consumo_periodo: number;
  consumo_por_unidad: Record<string, number>;
}

interface ConsumptionPoint {
  fecha: string;
  cantidad: number;
}

interface StockLevelPoint {
  name: string;
  disponible: number;
  minimo: number;
}

interface LowStockItem {
  id: number;
  name: string;
  category: string | null;
  unit: string | null;
  available_quantity: number;
  min_stock: number;
}

interface ExpiringItem {
  id: number;
  name: string;
  expiration_date: string;
  days_remaining: number;
  available_quantity: number;
}

interface SalesKpis {
  ventas_hoy: number;
  unidades_hoy: number;
  unidades_periodo: number;
  anuladas_periodo: number;
}

interface DailySalesPoint {
  fecha: string;
  num_ventas: number;
  cantidad: number;
}

interface TopSaleItem {
  name: string;
  cantidad: number;
}

interface ProductionByStatusPoint {
  estado: string;
  total: number;
}

interface DailyProductionPoint {
  fecha: string;
  unidades: number;
}

interface TopRecipePoint {
  nombre: string;
  veces: number;
  unidades: number;
}

interface SalesSection {
  kpis: SalesKpis;
  tendencia: DailySalesPoint[];
  top_items: TopSaleItem[];
}

interface ProductionSection {
  por_estado: ProductionByStatusPoint[];
  rendimiento_diario: DailyProductionPoint[];
  top_recetas: TopRecipePoint[];
}

interface ProductsKpis {
  productos_activos: number;
  productos_stock_bajo: number;
  comerciales_activos: number;
  comerciales_stock_bajo: number;
}

interface ProductStockPoint {
  name: string;
  disponible: number;
  minimo: number;
  maximo: number;
}

interface LowStockProduct {
  id: number;
  name: string;
  unit: string | null;
  available_quantity: number;
  min_stock: number;
  max_stock: number;
}

interface ProductProductionPoint {
  nombre: string;
  total: number;
  unidades: number;
}

interface CommercialStockPoint {
  name: string;
  disponible: number;
  minimo: number;
}

interface CategoryCountPoint {
  name: string;
  total: number;
}

interface StockHealthPoint {
  estado: string;
  total: number;
}

interface ProductsSection {
  kpis: ProductsKpis;
  productos_stock: ProductStockPoint[];
  productos_stock_bajo: LowStockProduct[];
  produccion_por_producto: ProductProductionPoint[];
  comerciales_stock: CommercialStockPoint[];
  comerciales_stock_bajo: LowStockProduct[];
  por_categoria: CategoryCountPoint[];
  stock_saludable: StockHealthPoint[];
}

interface DashboardStats {
  kpis: DashboardKpis;
  consumo_tendencia: ConsumptionPoint[];
  niveles_stock: StockLevelPoint[];
  stock_bajo: LowStockItem[];
  vencidos: ExpiringItem[];
  por_vencer: ExpiringItem[];
  ventas: SalesSection;
  produccion: ProductionSection;
  productos: ProductsSection;
}

const RANGES: readonly number[] = [7, 30, 90];
const LIST_LIMIT = 8;
const COLORS: readonly string[] = ["#3a7ca5", "#27ae60", "#d99a2b", "#9b59b6", "#e67e22", "#c0392b", "#1abc9c", "#34495e"];
type TabId = "insumos" | "ventas" | "produccion" | "productos";

const TABS: { id: TabId; label: string }[] = [
  { id: "insumos", label: "Insumos" },
  { id: "ventas", label: "Ventas" },
  { id: "produccion", label: "Producción" },
  { id: "productos", label: "Productos" },
];

function getInitialCols(): number {
  const w = window.innerWidth;
  if (w < 480) return 1;
  if (w < 900) return 2;
  return 3;
}

export default function Dashboard(): JSX.Element {
  const navigate = useNavigate();
  const { showAlert } = useAlert();
  const [cols, setCols] = useState<number>(getInitialCols);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState<number>(30);
  const [reloadKey, setReloadKey] = useState<number>(0);
  const [tab, setTab] = useState<TabId>("insumos");
  const lastToastRef = useRef<string>("");

  useEffect(() => {
    const update = () => setCols(getInitialCols());
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  useEffect(() => {
    let cancelled = false;

    const load = async (): Promise<void> => {
      setIsLoading(true);
      try {
        const response = await apiFetch(`/stats/dashboard?days=${days}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = (await response.json()) as DashboardStats;
        if (cancelled) return;
        setStats(data);
        setError(null);

        const warnings: string[] = [];
        if (data.kpis.vencidos_count > 0) {
          warnings.push(`${data.kpis.vencidos_count} insumo(s) vencido(s)`);
        }
        if (data.kpis.stock_bajo_count > 0) {
          warnings.push(`${data.kpis.stock_bajo_count} en stock bajo`);
        }
        if (data.kpis.por_vencer_count > 0) {
          warnings.push(`${data.kpis.por_vencer_count} próximo(s) a vencer`);
        }
        const signature = `${days}:${warnings.join("|")}`;
        if (warnings.length > 0 && lastToastRef.current !== signature) {
          lastToastRef.current = signature;
          showAlert("warning", warnings.join(" · "), 5000);
        }
      } catch {
        if (cancelled) return;
        setStats(null);
        setError("No se pudieron cargar las estadísticas del dashboard.");
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, [days, reloadKey, showAlert]);

  const chartCols = Math.min(cols, 2);

  const statsGridStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: `repeat(${chartCols}, 1fr)`,
    gap: "1rem",
    marginBottom: "1rem",
  };

  const kpiGridStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))",
    gap: "1rem",
    marginBottom: "1rem",
  };

  const tooltipStyle: React.CSSProperties = {
    background: "#ffffff",
    border: "1px solid #bcc7d0",
    borderRadius: "8px",
    fontSize: "0.78rem",
    fontFamily: "'Roboto', sans-serif",
  };

  const formatQty = (value: number): string =>
    Number.isInteger(value) ? String(value) : value.toFixed(2);

  const pendingOrdersCount =
    stats?.produccion.por_estado.find((e) => e.estado === "pending")?.total ?? 0;

  const alerts = stats
    ? [
        { label: `${stats.kpis.stock_bajo_count} insumo(s) en stock bajo`, count: stats.kpis.stock_bajo_count, type: "danger" as const, route: "/supplies" },
        { label: `${stats.kpis.vencidos_count} insumo(s) vencido(s)`, count: stats.kpis.vencidos_count, type: "danger" as const, route: "/supplies" },
        { label: `${stats.kpis.por_vencer_count} próximo(s) a vencer`, count: stats.kpis.por_vencer_count, type: "warning" as const, route: "/supplies" },
        { label: `${pendingOrdersCount} orden(es) pendiente(s)`, count: pendingOrdersCount, type: "warning" as const, route: "/produccion" },
      ]
    : [];

  const hasActiveAlerts = alerts.some((a) => a.count > 0);

  return (
    <Layout>
      {stats !== null && (
        <div className="alert-bar">
          {alerts.map((a) => (
            <button
              key={a.route + a.label}
              type="button"
              className={`alert-bar-item alert-bar-item--${a.count > 0 ? a.type : "neutral"}${a.count > 0 ? " alert-bar-item--active" : ""}`}
              onClick={() => navigate(a.route)}
              style={{ border: "none" }}
            >
              <span className={`alert-bar-dot alert-bar-dot--${a.count > 0 ? a.type : "neutral"}`} />
              {a.label}
            </button>
          ))}
          {!hasActiveAlerts && (
            <span className="alert-bar-item alert-bar-item--neutral">
              <span className="alert-bar-dot alert-bar-dot--neutral" />
              Todo en orden
            </span>
          )}
        </div>
      )}

      <div style={styles.tabBar}>
        <div style={styles.tabGroup}>
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              style={{
                ...styles.tabBtn,
                ...(t.id === tab ? styles.tabBtnActive : {}),
              }}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div style={styles.rangeGroup}>
          {RANGES.map((range) => (
            <button
              key={range}
              type="button"
              style={{
                ...styles.rangeBtn,
                ...(range === days ? styles.rangeBtnActive : {}),
              }}
              onClick={() => setDays(range)}
            >
              {range} días
            </button>
          ))}
          <button
            type="button"
            style={styles.reloadBtn}
            onClick={() => setReloadKey((k) => k + 1)}
            aria-label="Recargar estadísticas"
          >
            ↻
          </button>
        </div>
      </div>

      {isLoading && (
        <div style={styles.centerBox}>
          <span style={styles.spinner} />
          <span style={styles.loadingText}>Cargando estadísticas...</span>
        </div>
      )}

      {!isLoading && error !== null && (
        <div style={styles.errorBox}>
          <span>{error}</span>
          <button
            type="button"
            style={styles.retryBtn}
            onClick={() => setReloadKey((k) => k + 1)}
          >
            Reintentar
          </button>
        </div>
      )}

      {!isLoading && error === null && stats !== null && (
        <>
          {tab === "insumos" && (
            <>
              <div style={kpiGridStyle}>
                <KpiCard
                  label="Insumos activos"
                  value={stats.kpis.insumos_activos}
                  hint="Materia prima registrada"
                  variant="info"
                />
                <KpiCard
                  label="En stock bajo"
                  value={stats.kpis.stock_bajo_count}
                  accent={stats.kpis.stock_bajo_count > 0 ? "danger" : "success"}
                  hint="Igual o debajo del mínimo"
                  variant={stats.kpis.stock_bajo_count > 0 ? "alert" : "info"}
                />
                <KpiCard
                  label="Vencidos"
                  value={stats.kpis.vencidos_count}
                  accent={stats.kpis.vencidos_count > 0 ? "danger" : "success"}
                  hint="Fecha de vencimiento pasada"
                  variant={stats.kpis.vencidos_count > 0 ? "alert" : "info"}
                />
                <KpiCard
                  label="Por vencer"
                  value={stats.kpis.por_vencer_count}
                  accent={stats.kpis.por_vencer_count > 0 ? "warning" : "default"}
                  hint="Dentro de los próximos 7 días"
                  variant={stats.kpis.por_vencer_count > 0 ? "alert" : "info"}
                />
              </div>

              <div style={statsGridStyle}>
                <ChartCard
                  title="Consumo diario de insumos"
                  subtitle="Cantidades descontadas por órdenes de producción completadas"
                >
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={stats.consumo_tendencia}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e0e5ea" />
                      <XAxis
                        dataKey="fecha"
                        tickFormatter={(value: string) => value.slice(5)}
                        tick={{ fontSize: 11, fill: "#647a8a" }}
                      />
                      <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#647a8a" }} label={{ value: "Cantidad (unidades)", angle: -90, position: "insideLeft", offset: -5, style: { fontSize: 10, fill: "#647a8a" } }} />
                      <Tooltip contentStyle={tooltipStyle} />
                      <Line
                        type="monotone"
                        dataKey="cantidad"
                        name="Consumido"
                        stroke="#3a7ca5"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>

                <ChartCard
                  title="Insumos más críticos vs mínimo"
                  subtitle="Los 10 insumos más críticos · rojo = bajo el mínimo"
                >
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={stats.niveles_stock} margin={{ bottom: 30 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e0e5ea" />
                      <XAxis
                        dataKey="name"
                        interval={0}
                        angle={-30}
                        textAnchor="end"
                        height={60}
                        tick={{ fontSize: 10, fill: "#647a8a" }}
                      />
                      <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#647a8a" }} label={{ value: "Cantidad", angle: -90, position: "insideLeft", offset: -5, style: { fontSize: 10, fill: "#647a8a" } }} />
                      <Tooltip contentStyle={tooltipStyle} />
                      <Bar dataKey="disponible" name="Disponible" radius={[4, 4, 0, 0]}>
                        {stats.niveles_stock.map((entry) => (
                          <Cell
                            key={entry.name}
                            fill={entry.disponible <= entry.minimo ? "#c0392b" : "#3a7ca5"}
                          />
                        ))}
                      </Bar>
                      <Bar dataKey="minimo" name="Mínimo" fill="#bcc7d0" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
              </div>

              <div style={statsGridStyle}>
                <ChartCard
                  title="Insumos en stock bajo"
                  subtitle={
                    stats.stock_bajo.length === 0
                      ? undefined
                      : "Requieren reposición prioritaria"
                  }
                >
                  {stats.stock_bajo.length === 0 ? (
                    <p style={styles.emptyText}>Sin alertas de stock bajo.</p>
                  ) : (
                    <ul style={styles.alertList}>
                      {stats.stock_bajo.slice(0, LIST_LIMIT).map((item) => (
                        <li key={`${item.id}-${item.name}`} style={styles.alertItem}>
                          <span style={styles.dangerDot} />
                          <div style={styles.alertInfo}>
                            <span style={styles.itemName}>{item.name}</span>
                            <span style={styles.itemMeta}>
                              {item.category ?? "Sin categoría"}
                            </span>
                          </div>
                          <span style={styles.dangerValue}>
                            {formatQty(item.available_quantity)} / mín{" "}
                            {formatQty(item.min_stock)} {item.unit ?? ""}
                          </span>
                        </li>
                      ))}
                      {stats.stock_bajo.length > LIST_LIMIT && (
                        <li style={styles.moreItem}>
                          +{stats.stock_bajo.length - LIST_LIMIT} insumo(s) más
                        </li>
                      )}
                    </ul>
                  )}
                </ChartCard>

                <ChartCard
                  title="Insumos vencidos"
                  subtitle={
                    stats.vencidos.length === 0
                      ? undefined
                      : "Requieren disposición o reposición inmediata"
                  }
                >
                  {stats.vencidos.length === 0 ? (
                    <p style={styles.emptyText}>Sin insumos vencidos.</p>
                  ) : (
                    <ul style={styles.alertList}>
                      {stats.vencidos.slice(0, LIST_LIMIT).map((item) => (
                        <li key={`${item.id}-${item.name}`} style={styles.alertItem}>
                          <span style={styles.dangerDot} />
                          <div style={styles.alertInfo}>
                            <span style={styles.itemName}>{item.name}</span>
                            <span style={styles.itemMeta}>
                              Venció el{" "}
                              {new Date(item.expiration_date).toLocaleDateString("es-CO")}
                              {" · "}
                              {formatQty(item.available_quantity)} en stock
                            </span>
                          </div>
                          <span style={{ ...styles.badge, ...styles.badgeExpired }}>
                            Vencido hace {Math.abs(item.days_remaining)} día(s)
                          </span>
                        </li>
                      ))}
                      {stats.vencidos.length > LIST_LIMIT && (
                        <li style={styles.moreItem}>
                          +{stats.vencidos.length - LIST_LIMIT} insumo(s) más
                        </li>
                      )}
                    </ul>
                  )}
                </ChartCard>

                <ChartCard
                  title="Próximos a vencer"
                  subtitle={
                    stats.por_vencer.length === 0
                      ? undefined
                      : "Vencimiento dentro de los próximos 7 días"
                  }
                >
                  {stats.por_vencer.length === 0 ? (
                    <p style={styles.emptyText}>Sin insumos próximos a vencer.</p>
                  ) : (
                    <ul style={styles.alertList}>
                      {stats.por_vencer.slice(0, LIST_LIMIT).map((item) => (
                        <li key={`${item.id}-${item.name}`} style={styles.alertItem}>
                          <span style={styles.warningDot} />
                          <div style={styles.alertInfo}>
                            <span style={styles.itemName}>{item.name}</span>
                            <span style={styles.itemMeta}>
                              {new Date(item.expiration_date).toLocaleDateString("es-CO")}
                              {" · "}
                              {formatQty(item.available_quantity)} en stock
                            </span>
                          </div>
                          <span
                            style={{
                              ...styles.badge,
                              ...(item.days_remaining < 0
                                ? styles.badgeExpired
                                : item.days_remaining <= 2
                                  ? styles.badgeSoon
                                  : {}),
                            }}
                          >
                            {item.days_remaining < 0
                              ? "Vencido"
                              : item.days_remaining === 0
                                ? "Vence hoy"
                                : `${item.days_remaining} día(s)`}
                          </span>
                        </li>
                      ))}
                      {stats.por_vencer.length > LIST_LIMIT && (
                        <li style={styles.moreItem}>
                          +{stats.por_vencer.length - LIST_LIMIT} insumo(s) más
                        </li>
                      )}
                    </ul>
                  )}
                </ChartCard>
              </div>
            </>
          )}

          {tab === "ventas" && (
            <>
              <div style={kpiGridStyle}>
                <KpiCard
                  label="Ventas hoy"
                  value={stats.ventas.kpis.ventas_hoy}
                  hint="Órdenes completadas"
                  variant="info"
                />
                <KpiCard
                  label="Unidades hoy"
                  value={formatQty(stats.ventas.kpis.unidades_hoy)}
                  hint="Unidades vendidas"
                  variant="info"
                />
                <KpiCard
                  label={`Unidades (${days} días)`}
                  value={formatQty(stats.ventas.kpis.unidades_periodo)}
                  hint="Total en el período"
                  variant="info"
                />
                <KpiCard
                  label="Anuladas"
                  value={stats.ventas.kpis.anuladas_periodo}
                  accent={stats.ventas.kpis.anuladas_periodo > 0 ? "warning" : "default"}
                  hint="Ventas anuladas"
                  variant={stats.ventas.kpis.anuladas_periodo > 0 ? "alert" : "info"}
                />
              </div>

              {stats.ventas.tendencia.length === 0 ? (
                <p style={{ ...styles.emptyText, marginBottom: "1rem" }}>
                  Sin ventas registradas en el período seleccionado.
                </p>
              ) : (
                <div style={statsGridStyle}>
                  <ChartCard
                    title="Tendencia diaria de ventas"
                    subtitle="Barras = número de ventas · Línea = unidades vendidas"
                  >
                    <ResponsiveContainer width="100%" height={260}>
                      <ComposedChart data={stats.ventas.tendencia}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e5ea" />
                        <XAxis
                          dataKey="fecha"
                          tickFormatter={(v: string) => v.slice(5)}
                          tick={{ fontSize: 11, fill: "#647a8a" }}
                        />
                        <YAxis yAxisId="left" allowDecimals={false} tick={{ fontSize: 11, fill: "#647a8a" }} label={{ value: "Nº Ventas", angle: -90, position: "insideLeft", offset: -5, style: { fontSize: 10, fill: "#647a8a" } }} />
                        <YAxis yAxisId="right" orientation="right" allowDecimals={false} tick={{ fontSize: 11, fill: "#647a8a" }} label={{ value: "Unidades", angle: 90, position: "insideRight", offset: -5, style: { fontSize: 10, fill: "#647a8a" } }} />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Legend />
                        <Bar yAxisId="left" dataKey="num_ventas" name="Nº Ventas" fill="#3a7ca5" radius={[4, 4, 0, 0]} />
                        <Line yAxisId="right" type="monotone" dataKey="cantidad" name="Unidades" stroke="#d99a2b" strokeWidth={2} dot={false} />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </ChartCard>

                  {stats.ventas.top_items.length === 1 ? (
                    <div className="insight-block">
                      <span className="insight-block__value">{formatQty(stats.ventas.top_items[0].cantidad)}</span>
                      <span className="insight-block__label">
                        {stats.ventas.top_items[0].name} — producto más vendido en el período
                      </span>
                    </div>
                  ) : (
                    <ChartCard
                      title="Top productos vendidos"
                      subtitle="Los más vendidos en el período seleccionado"
                    >
                      {stats.ventas.top_items.length === 0 ? (
                        <p style={styles.emptyText}>Sin datos de productos vendidos.</p>
                      ) : (
                        <ResponsiveContainer width="100%" height={260}>
                          <BarChart
                            data={stats.ventas.top_items}
                            layout="vertical"
                            margin={{ left: 10, right: 30 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" stroke="#e0e5ea" />
                            <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11, fill: "#647a8a" }} label={{ value: "Unidades", position: "insideBottom", offset: -5, style: { fontSize: 10, fill: "#647a8a" } }} />
                            <YAxis
                              dataKey="name"
                              type="category"
                              width={100}
                              tick={{ fontSize: 11, fill: "#647a8a" }}
                            />
                            <Tooltip contentStyle={tooltipStyle} />
                            <Bar dataKey="cantidad" name="Unidades" fill="#3a7ca5" radius={[0, 4, 4, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      )}
                    </ChartCard>
                  )}
                </div>
              )}
            </>
          )}

          {tab === "produccion" && (
            <>
              <div style={statsGridStyle}>
                <ChartCard
                  title="Órdenes por estado"
                  subtitle="Distribución actual de todas las órdenes de producción"
                >
                  {(() => {
                    const activeStatuses = stats.produccion.por_estado.filter((s) => s.total > 0);
                    if (activeStatuses.length === 0) {
                      return <p style={styles.emptyText}>Sin órdenes de producción registradas.</p>;
                    }
                    if (activeStatuses.length === 1) {
                      const statusNameMap: Record<string, string> = {
                        pending: "Pendiente",
                        in_progress: "En proceso",
                        completed: "Completada",
                        cancelled: "Cancelada",
                      };
                      const s = activeStatuses[0];
                      return (
                        <div className="insight-block">
                          <span className="insight-block__value">{s.total}</span>
                          <span className="insight-block__label">
                            {statusNameMap[s.estado] ?? s.estado} — todas las órdenes
                          </span>
                        </div>
                      );
                    }
                    return (
                      <ResponsiveContainer width="100%" height={260}>
                        <PieChart>
                          <Pie
                            data={activeStatuses}
                            dataKey="total"
                            nameKey="estado"
                            cx="50%"
                            cy="50%"
                            outerRadius={90}
                            label={({ estado, total }: { estado: string; total: number }) => {
                              const nameMap: Record<string, string> = {
                                pending: "Pendiente",
                                in_progress: "En proceso",
                                completed: "Completada",
                                cancelled: "Cancelada",
                              };
                              return `${nameMap[estado] ?? estado}: ${total}`;
                            }}
                          >
                            {stats.produccion.por_estado.map((entry) => (
                              <Cell
                                key={entry.estado}
                                fill={
                                  entry.estado === "pending"
                                    ? "#d99a2b"
                                    : entry.estado === "in_progress"
                                      ? "#3a7ca5"
                                      : entry.estado === "completed"
                                        ? "#27ae60"
                                        : "#95a5a6"
                                }
                              />
                            ))}
                          </Pie>
                          <Tooltip contentStyle={tooltipStyle} />
                        </PieChart>
                      </ResponsiveContainer>
                    );
                  })()}
                </ChartCard>

                <ChartCard
                  title="Unidades producidas diarias"
                  subtitle="Rendimiento total de órdenes completadas por día"
                >
                  {stats.produccion.rendimiento_diario.every((d) => d.unidades === 0) ? (
                    <p style={styles.emptyText}>Sin producción completada en el período.</p>
                  ) : (
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={stats.produccion.rendimiento_diario}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e5ea" />
                        <XAxis
                          dataKey="fecha"
                          tickFormatter={(v: string) => v.slice(5)}
                          tick={{ fontSize: 11, fill: "#647a8a" }}
                        />
                        <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#647a8a" }} label={{ value: "Unidades", angle: -90, position: "insideLeft", offset: -5, style: { fontSize: 10, fill: "#647a8a" } }} />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Bar dataKey="unidades" name="Unidades" fill="#27ae60" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </ChartCard>
              </div>

              {stats.produccion.top_recetas.length > 0 && (
                <div style={statsGridStyle}>
                  <ChartCard
                    title="Recetas más producidas"
                    subtitle="Top 5 por número de órdenes · barras muestran unidades y órdenes"
                  >
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart
                        data={stats.produccion.top_recetas}
                        layout="vertical"
                        margin={{ left: 10, right: 30 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e5ea" />
                        <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11, fill: "#647a8a" }} />
                        <YAxis
                          dataKey="nombre"
                          type="category"
                          width={100}
                          tick={{ fontSize: 11, fill: "#647a8a" }}
                        />
                        <Tooltip
                          contentStyle={tooltipStyle}
                          formatter={(value: number, name: string, props: { dataKey?: string | number }) =>
                            props.dataKey === "unidades"
                              ? [formatQty(value), "Unidades"]
                              : [value, "Órdenes"]
                          }
                        />
                        <Legend />
                        <Bar dataKey="veces" name="Órdenes" fill="#3a7ca5" radius={[0, 4, 4, 0]} />
                        <Bar dataKey="unidades" name="Unidades" fill="#27ae60" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </ChartCard>
                </div>
              )}
            </>
          )}

          {tab === "productos" && (
            <>
              <div style={kpiGridStyle}>
                <KpiCard
                  label="Productos activos"
                  value={stats.productos.kpis.productos_activos}
                  hint="Productos terminados"
                  variant="info"
                />
                <KpiCard
                  label="Stock bajo (terminados)"
                  value={stats.productos.kpis.productos_stock_bajo}
                  accent={stats.productos.kpis.productos_stock_bajo > 0 ? "danger" : "success"}
                  hint="Por debajo del mínimo"
                  variant={stats.productos.kpis.productos_stock_bajo > 0 ? "alert" : "info"}
                />
                <KpiCard
                  label="Comerciales activos"
                  value={stats.productos.kpis.comerciales_activos}
                  hint="Productos comerciales"
                  variant="info"
                />
                <KpiCard
                  label="Stock bajo (comerciales)"
                  value={stats.productos.kpis.comerciales_stock_bajo}
                  accent={stats.productos.kpis.comerciales_stock_bajo > 0 ? "danger" : "success"}
                  hint="Por debajo del mínimo"
                  variant={stats.productos.kpis.comerciales_stock_bajo > 0 ? "alert" : "info"}
                />
              </div>

              <h2 style={styles.sectionTitle}>Productos terminados</h2>
              <div style={statsGridStyle}>
                <ChartCard
                  title="Productos terminados vs mínimo"
                  subtitle="Top 10 más críticos · rojo = bajo el mínimo"
                >
                  {stats.productos.productos_stock.length === 0 ? (
                    <p style={styles.emptyText}>Sin productos terminados registrados.</p>
                  ) : (
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={stats.productos.productos_stock} margin={{ bottom: 30 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e5ea" />
                        <XAxis
                          dataKey="name"
                          interval={0}
                          angle={-30}
                          textAnchor="end"
                          height={60}
                          tick={{ fontSize: 10, fill: "#647a8a" }}
                        />
                        <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#647a8a" }} label={{ value: "Cantidad", angle: -90, position: "insideLeft", offset: -5, style: { fontSize: 10, fill: "#647a8a" } }} />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Bar dataKey="disponible" name="Disponible" radius={[4, 4, 0, 0]}>
                          {stats.productos.productos_stock.map((entry) => (
                            <Cell
                              key={entry.name}
                              fill={entry.disponible <= entry.minimo ? "#c0392b" : "#3a7ca5"}
                            />
                          ))}
                        </Bar>
                        <Bar dataKey="minimo" name="Mínimo" fill="#bcc7d0" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </ChartCard>

                <ChartCard
                  title="Producción por producto"
                  subtitle="Top 10 más producidos · barras muestran unidades y órdenes"
                >
                  {stats.productos.produccion_por_producto.length === 0 ? (
                    <p style={styles.emptyText}>Sin producción completada en el período.</p>
                  ) : (
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart
                        data={stats.productos.produccion_por_producto}
                        layout="vertical"
                        margin={{ left: 10, right: 30 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e5ea" />
                        <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11, fill: "#647a8a" }} label={{ value: "Unidades / Órdenes", position: "insideBottom", offset: -5, style: { fontSize: 10, fill: "#647a8a" } }} />
                        <YAxis
                          dataKey="nombre"
                          type="category"
                          width={100}
                          tick={{ fontSize: 11, fill: "#647a8a" }}
                        />
                        <Tooltip
                          contentStyle={tooltipStyle}
                          formatter={(value: number, name: string) =>
                            name === "unidades"
                              ? [formatQty(value), "Unidades"]
                              : [value, "Órdenes"]
                          }
                        />
                        <Legend />
                        <Bar dataKey="total" name="Órdenes" fill="#3a7ca5" radius={[0, 4, 4, 0]} />
                        <Bar dataKey="unidades" name="Unidades" fill="#27ae60" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </ChartCard>
              </div>

              {stats.productos.productos_stock_bajo.length > 0 && (
                <div style={{ marginBottom: "1rem" }}>
                  <ChartCard
                    title="Alertas de stock bajo"
                    subtitle="Productos terminados por debajo del mínimo"
                  >
                    <ul style={styles.alertList}>
                      {stats.productos.productos_stock_bajo.slice(0, LIST_LIMIT).map((item) => (
                        <li key={`prod-${item.id}-${item.name}`} style={styles.alertItem}>
                          <span style={styles.dangerDot} />
                          <div style={styles.alertInfo}>
                            <span style={styles.itemName}>{item.name}</span>
                            <span style={styles.itemMeta}>
                              {item.unit ?? "Sin unidad"}
                            </span>
                          </div>
                          <span style={styles.dangerValue}>
                            {formatQty(item.available_quantity)} / mín{" "}
                            {formatQty(item.min_stock)}
                          </span>
                        </li>
                      ))}
                      {stats.productos.productos_stock_bajo.length > LIST_LIMIT && (
                        <li style={styles.moreItem}>
                          +{stats.productos.productos_stock_bajo.length - LIST_LIMIT} producto(s) más
                        </li>
                      )}
                    </ul>
                  </ChartCard>
                </div>
              )}

              <h2 style={styles.sectionTitle}>Productos comerciales</h2>
              <div style={statsGridStyle}>
                <ChartCard
                  title="Stock de comerciales vs mínimo"
                  subtitle="Top 10 más críticos · rojo = bajo el mínimo"
                >
                  {stats.productos.comerciales_stock.length === 0 ? (
                    <p style={styles.emptyText}>Sin productos comerciales registrados.</p>
                  ) : (
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={stats.productos.comerciales_stock} margin={{ bottom: 30 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e5ea" />
                        <XAxis
                          dataKey="name"
                          interval={0}
                          angle={-30}
                          textAnchor="end"
                          height={60}
                          tick={{ fontSize: 10, fill: "#647a8a" }}
                        />
                        <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#647a8a" }} label={{ value: "Cantidad", angle: -90, position: "insideLeft", offset: -5, style: { fontSize: 10, fill: "#647a8a" } }} />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Bar dataKey="disponible" name="Disponible" radius={[4, 4, 0, 0]}>
                          {stats.productos.comerciales_stock.map((entry) => (
                            <Cell
                              key={entry.name}
                              fill={entry.disponible <= entry.minimo ? "#c0392b" : "#3a7ca5"}
                            />
                          ))}
                        </Bar>
                        <Bar dataKey="minimo" name="Mínimo" fill="#bcc7d0" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </ChartCard>

                {stats.productos.por_categoria.length === 1 ? (
                  <div className="insight-block">
                    <span className="insight-block__label" style={{ fontSize: "1rem" }}>
                      Todos los productos comerciales están en la categoría: {stats.productos.por_categoria[0].name}
                    </span>
                  </div>
                ) : (
                  <ChartCard
                    title="Distribución por categoría"
                    subtitle="Productos comerciales agrupados por categoría"
                  >
                    {stats.productos.por_categoria.length === 0 ? (
                      <p style={styles.emptyText}>Sin categorías registradas.</p>
                    ) : (
                      <ResponsiveContainer width="100%" height={260}>
                        <PieChart>
                          <Pie
                            data={stats.productos.por_categoria}
                            dataKey="total"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            outerRadius={90}
                            label={({ name, total }: { name: string; total: number }) => `${name}: ${total}`}
                          >
                            {stats.productos.por_categoria.map((entry) => (
                              <Cell key={entry.name} fill={COLORS[stats.productos.por_categoria.indexOf(entry) % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip contentStyle={tooltipStyle} />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    )}
                  </ChartCard>
                )}
              </div>

              <div style={statsGridStyle}>
                {stats.productos.comerciales_stock_bajo.length > 0 && (
                  <ChartCard
                    title="Comerciales con stock bajo"
                    subtitle="Requieren reposición"
                  >
                    <ul style={styles.alertList}>
                      {stats.productos.comerciales_stock_bajo.slice(0, LIST_LIMIT).map((item) => (
                        <li key={`com-${item.id}-${item.name}`} style={styles.alertItem}>
                          <span style={styles.dangerDot} />
                          <div style={styles.alertInfo}>
                            <span style={styles.itemName}>{item.name}</span>
                            <span style={styles.itemMeta}>
                              {item.unit ?? "Sin unidad"}
                            </span>
                          </div>
                          <span style={styles.dangerValue}>
                            {formatQty(item.available_quantity)} / mín{" "}
                            {formatQty(item.min_stock)}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </ChartCard>
                )}

                {(() => {
                  const activeStockHealth = stats.productos.stock_saludable.filter((s) => s.total > 0);
                  if (activeStockHealth.length === 0) {
                    return (
                      <ChartCard
                        title="Stock saludable"
                        subtitle="Distribución de productos comerciales por estado de stock"
                      >
                        <p style={styles.emptyText}>Sin datos de stock.</p>
                      </ChartCard>
                    );
                  }
                  if (activeStockHealth.length === 1) {
                    const estado = activeStockHealth[0].estado;
                    const label = estado === "OK" ? "Stock saludable" : estado;
                    const totalAll = stats.productos.stock_saludable.reduce((acc, s) => acc + s.total, 0);
                    const pct = totalAll > 0 ? Math.round((activeStockHealth[0].total / totalAll) * 100) : 0;
                    return (
                      <div className="insight-block">
                        <span className="insight-block__value">{pct}%</span>
                        <span className="insight-block__label">
                          de productos comerciales en {label.toLowerCase()}
                        </span>
                      </div>
                    );
                  }
                  const healthLabelMap: Record<string, string> = { OK: "Stock saludable" };
                  return (
                    <ChartCard
                      title="Stock saludable"
                      subtitle="Distribución de productos comerciales por estado de stock"
                    >
                      <ResponsiveContainer width="100%" height={260}>
                        <PieChart>
                          <Pie
                            data={activeStockHealth}
                            dataKey="total"
                            nameKey="estado"
                            cx="50%"
                            cy="50%"
                            outerRadius={90}
                            label={({ estado, total }: { estado: string; total: number }) => `${healthLabelMap[estado] ?? estado}: ${total}`}
                          >
                            {stats.productos.stock_saludable.map((entry) => (
                              <Cell
                                key={entry.estado}
                                fill={
                                  entry.estado === "OK"
                                    ? "#27ae60"
                                    : entry.estado === "Bajo mínimo"
                                      ? "#d99a2b"
                                      : "#c0392b"
                                }
                              />
                            ))}
                          </Pie>
                          <Tooltip contentStyle={tooltipStyle} />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </ChartCard>
                  );
                })()}
              </div>
            </>
          )}
        </>
      )}
    </Layout>
  );
}

const styles: Record<string, React.CSSProperties> = {
  tabBar: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "0.75rem",
    marginBottom: "1.25rem",
  },
  tabGroup: {
    display: "flex",
    gap: "0.3rem",
  },
  tabBtn: {
    padding: "0.5rem 1rem",
    borderRadius: "6px",
    border: "1px solid #bcc7d066",
    background: "#f2f2f2",
    color: "#647a8a",
    fontSize: "0.85rem",
    fontWeight: 600,
    cursor: "pointer",
    fontFamily: "'Roboto', sans-serif",
    transition: "background 0.15s, color 0.15s",
  },
  tabBtnActive: {
    background: "#16425b",
    color: "#ffffff",
    borderColor: "#16425b",
  },
  sectionTitle: {
    fontSize: "1.1rem",
    fontWeight: 700,
    color: "#16425b",
    marginTop: "0.5rem",
    marginBottom: "0.75rem",
    fontFamily: "'Roboto', sans-serif",
  },
  title: {
    fontSize: "1.5rem",
    fontWeight: 700,
    color: "#16425b",
    marginBottom: "0.5rem",
    fontFamily: "'Roboto', sans-serif",
  },
  rangeGroup: {
    display: "flex",
    gap: "0.4rem",
    alignItems: "center",
  },
  rangeBtn: {
    padding: "0.4rem 0.9rem",
    borderRadius: "6px",
    border: "1px solid #bcc7d066",
    background: "#f2f2f2",
    color: "#16425b",
    fontSize: "0.8rem",
    fontWeight: 700,
    cursor: "pointer",
    fontFamily: "'Roboto', sans-serif",
  },
  rangeBtnActive: {
    background: "#3a7ca5",
    color: "#ffffff",
    borderColor: "#3a7ca5",
  },
  reloadBtn: {
    padding: "0.35rem 0.7rem",
    borderRadius: "6px",
    border: "1px solid #bcc7d066",
    background: "#f2f2f2",
    color: "#16425b",
    fontSize: "0.95rem",
    cursor: "pointer",
  },
  centerBox: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "0.75rem",
    padding: "3rem 0",
  },
  spinner: {
    width: "22px",
    height: "22px",
    border: "3px solid #bcc7d066",
    borderTopColor: "#3a7ca5",
    borderRadius: "50%",
    display: "inline-block",
    animation: "dash-spin 0.8s linear infinite",
  },
  loadingText: {
    color: "#647a8a",
    fontFamily: "'Roboto', sans-serif",
    fontSize: "0.9rem",
  },
  errorBox: {
    background: "#fdf0ef",
    border: "1px solid #c0392b55",
    borderRadius: "8px",
    padding: "1rem 1.25rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "1rem",
    color: "#c0392b",
    fontFamily: "'Roboto', sans-serif",
    fontSize: "0.88rem",
    marginBottom: "1rem",
  },
  retryBtn: {
    padding: "0.4rem 1rem",
    borderRadius: "6px",
    border: "none",
    background: "#c0392b",
    color: "#ffffff",
    fontWeight: 700,
    cursor: "pointer",
    fontFamily: "'Roboto', sans-serif",
  },
  emptyText: {
    color: "#647a8a",
    fontSize: "0.85rem",
    margin: 0,
  },
  alertList: {
    listStyle: "none",
    margin: 0,
    padding: 0,
    display: "flex",
    flexDirection: "column",
    gap: "0.55rem",
  },
  alertItem: {
    display: "flex",
    alignItems: "center",
    gap: "0.65rem",
    background: "#ffffff",
    border: "1px solid #bcc7d055",
    borderRadius: "6px",
    padding: "0.55rem 0.75rem",
  },
  alertInfo: {
    display: "flex",
    flexDirection: "column",
    flex: 1,
    minWidth: 0,
  },
  itemName: {
    fontWeight: 700,
    color: "#16425b",
    fontSize: "0.85rem",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  itemMeta: {
    fontSize: "0.72rem",
    color: "#647a8a",
  },
  dangerDot: {
    width: "9px",
    height: "9px",
    borderRadius: "50%",
    background: "#c0392b",
    flexShrink: 0,
  },
  warningDot: {
    width: "9px",
    height: "9px",
    borderRadius: "50%",
    background: "#d99a2b",
    flexShrink: 0,
  },
  dangerValue: {
    fontSize: "0.75rem",
    fontWeight: 700,
    color: "#c0392b",
    whiteSpace: "nowrap",
  },
  badge: {
    fontSize: "0.7rem",
    fontWeight: 700,
    padding: "0.2rem 0.55rem",
    borderRadius: "999px",
    background: "#d99a2b22",
    color: "#b07d1e",
    whiteSpace: "nowrap",
  },
  badgeSoon: {
    background: "#d99a2b44",
    color: "#8a5f10",
  },
  badgeExpired: {
    background: "#c0392b22",
    color: "#c0392b",
  },
  moreItem: {
    fontSize: "0.78rem",
    color: "#647a8a",
    textAlign: "center",
    padding: "0.2rem 0",
  },
};
