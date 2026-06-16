import React, { JSX, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAllowedModules, canAccessModule } from "../../utils/permissions";

interface MenuItem {
  id: string;
  label: string;
  icon: JSX.Element;
  path: string;
  group?: string;
  subitems?: MenuItem[];
}

interface SidebarProps {
  activeMenu: string;
  onMenuChange: (id: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

const Icon = {
  dashboard: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/>
      <rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>
    </svg>
  ),
  inventory: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
      <polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
    </svg>
  ),
  suppliers: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
    </svg>
  ),
  sales: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>
    </svg>
  ),
  production: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 20h20"/><path d="M5 20V10l4-6 4 6 4-4 4 4v10"/><rect x="9" y="14" width="6" height="6"/>
    </svg>
  ),
  recipes: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
      <line x1="9" y1="7" x2="15" y2="7"/><line x1="9" y1="11" x2="15" y2="11"/><line x1="9" y1="15" x2="12" y2="15"/>
    </svg>
  ),
  users: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
      <path d="M19 8l2 2-6 6"/><path d="M21 10l-2 2"/>
    </svg>
  ),
  roles: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
    </svg>
  ),
  about: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
      <circle cx="12" cy="16" r="0.5" fill="currentColor"/>
    </svg>
  ),
  contact: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
    </svg>
  ),
  units: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 6h18M3 12h18M3 18h18"/>
    </svg>
  ),
  products: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
      <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
      <line x1="12" y1="22.08" x2="12" y2="12"/>
    </svg>
  ),
  reports: (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round">
    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
    <polyline points="10 9 9 9 8 9"/>
  </svg>
  ),
  providers:(
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round">
       <rect x="1" y="3" width="15" height="13" rx="1" />
       <path d="M16 8h4l3 5v4h-7V8z" />
       <circle cx="5.5" cy="18.5" r="2.5" />
       <circle cx="18.5" cy="18.5" r="2.5" />
    </svg>
  ),
};

const menuItems: MenuItem[] = [
  { id: "dashboard",        label: "Dashboard",          path: "/dashboard",  icon: Icon.dashboard,  group: "principal" },
  { id: "produccion",       label: "Producción",         path: "#",           icon: Icon.production, group: "operaciones", subitems: [
    { id: "production",      label: "Órdenes de producción",  path: "/produccion", icon: Icon.production, group: "produccion" },
    { id: "recipes",         label: "Recetas",                path: "/recetas",    icon: Icon.recipes,   group: "produccion" },
    { id: "supplies",        label: "Insumos / Materia Prima", path: "/supplies",  icon: Icon.products,  group: "produccion" },
    { id: "supply-categories", label: "Categorías de insumos", path: "/supply-categories", icon: Icon.products, group: "produccion" },
    { id: "units",           label: "Unidades de medida",      path: "/units",    icon: Icon.units,     group: "produccion" },
  ]},
  { id: "ventas-comercial", label: "Ventas y Comercial", path: "#",           icon: Icon.sales,      group: "operaciones", subitems: [
    { id: "sales",           label: "Registrar Venta",         path: "/ventas",   icon: Icon.sales,     group: "ventas" },
    { id: "sales-history",   label: "Historial de Ventas",    path: "/ventas/historial", icon: Icon.sales, group: "ventas" },
    { id: "products",        label: "Productos Terminados",    path: "/products", icon: Icon.products,  group: "ventas" },
    { id: "commercial-products", label: "Productos Comerciales", path: "/commercial-products", icon: Icon.products, group: "ventas" },
    { id: "product-categories",  label: "Categorías de productos", path: "/product-categories", icon: Icon.products, group: "ventas" },
  ]},
  { id: "logistica-compras", label: "Logística y Compras", path: "#",           icon: Icon.inventory,  group: "operaciones", subitems: [
    { id: "inventary",       label: "Inventario General",     path: "/inventario", icon: Icon.inventory, group: "logistica" },
    { id: "providers",       label: "Proveedores",            path: "/proveedores", icon: Icon.providers, group: "logistica" },
  ]},
  { id: "users",         label: "Gestión de usuarios",path: "/usuarios",   icon: Icon.users,      group: "administracion" },
  { id: "roles",            label: "Gestión de roles",   path: "/roles",      icon: Icon.users,      group: "administracion" },
  { id: "reports",         label: "Reportes",           path: "/reportes",   icon: Icon.roles,      group: "administracion" },
  { id: "acerca",           label: "Acerca de SAIP",     path: "/acerca",     icon: Icon.about,      group: "soporte" },
];

const groupLabels: Record<string, string> = {
  principal:      "Principal",
  operaciones:    "Operaciones",
  administracion: "Administración",
  soporte:        "Información",
};

const groupOrder = ["principal", "operaciones", "administracion", "soporte"];

const grouped = menuItems.reduce<Record<string, MenuItem[]>>((acc, item) => {
  const g = item.group ?? "otros";
  if (!acc[g]) acc[g] = [];
  acc[g].push(item);
  return acc;
}, {});

function NavItem({ 
  item, 
  isActive, 
  onClick, 
  isExpanded,
  hasSubitems,
  onToggle,
  isSubitem = false,
  collapsed = false,
}: { 
  item: MenuItem; 
  isActive: boolean; 
  onClick: () => void;
  isExpanded?: boolean;
  hasSubitems?: boolean;
  onToggle?: () => void;
  isSubitem?: boolean;
  collapsed?: boolean;
}) {
  const [hovered, setHovered] = useState(false);

  const handleClick = () => {
    if (hasSubitems) {
      onToggle?.();
    } else {
      onClick();
    }
  };

  if (collapsed && !isSubitem) {
    const iconContent = (
      <div
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        title={item.label}
        style={{
          display: "flex", alignItems: "center", justifyContent: "center",
          padding: "0.5rem", margin: "0 0.5rem",
          borderRadius: "7px",
          color: isActive ? "#ffffff" : hovered ? "#ffffff" : "rgba(255,255,255,0.85)",
          background: isActive ? "var(--bakery-sidebar-active)" : hovered ? "var(--bakery-sidebar-hover)" : "transparent",
          cursor: "pointer",
          transition: "background 0.15s, color 0.15s",
        }}
      >
        <span style={{ display: "flex", color: "inherit" }}>{item.icon}</span>
      </div>
    );
    if (hasSubitems || !item.path || item.path === "#") {
      return <div onClick={handleClick}>{iconContent}</div>;
    }
    return (
      <Link to={item.path} style={{ textDecoration: "none" }} onClick={onClick}>
        {iconContent}
      </Link>
    );
  }

  const baseStyle: React.CSSProperties = {
    display: "flex", alignItems: "center", gap: "0.6rem",
    padding: isSubitem ? "0.4rem 0.75rem 0.4rem 2rem" : "0.5rem 0.75rem",
    borderRadius: "7px",
    fontSize: isSubitem ? "0.78rem" : "0.81rem",
    fontWeight: isActive ? 600 : 400,
    color: isActive ? "#ffffff" : hovered ? "#ffffff" : "rgba(255,255,255,0.85)",
    background: isActive ? "var(--bakery-sidebar-active)" : hovered ? "var(--bakery-sidebar-hover)" : "transparent",
    boxShadow: "none",
    cursor: "pointer",
    fontFamily: "'Outfit', system-ui, sans-serif",
    transition: "background 0.15s, color 0.15s",
  };

  if (hasSubitems) {
    return (
      <div
        onClick={handleClick}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          ...baseStyle,
          background: hovered ? "var(--bakery-sidebar-hover)" : "transparent",
        }}
      >
        <span style={{ flexShrink: 0, display: "flex", color: "inherit" }}>
          {item.icon}
        </span>
        <span style={{ flex: 1 }}>{item.label}</span>
        <span style={{
          fontSize: "0.6rem",
          transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)",
          transition: "transform 0.2s ease",
          opacity: 0.7,
        }}>
          ▶
        </span>
      </div>
    );
  }

  return (
    <Link to={item.path} style={{ textDecoration: "none" }} onClick={onClick}>
      <div
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={baseStyle}
      >
        <span style={{ flexShrink: 0, display: "flex", color: "inherit" }}>
          {item.icon}
        </span>
        <span style={{ flex: 1 }}>{item.label}</span>
        {isActive && (
          <span style={{
            width: "5px", height: "5px", borderRadius: "50%",
            background: "rgba(255,255,255,0.8)", flexShrink: 0,
          }} />
        )}
      </div>
    </Link>
  );
}

const STORAGE_KEY = "saip_sidebar_expanded";

function loadExpanded(): Set<string> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return new Set(JSON.parse(raw));
  } catch { /* ignore */ }
  return new Set(
    menuItems.filter((item) => item.subitems?.length).map((item) => item.id)
  );
}

function saveExpanded(set: Set<string>) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...set]));
}

// ── Módulos permitidos ─────────────────────────────────────────────────────
function NavContent({ activeMenu, onItemClick, collapsed, onToggleCollapse }: { activeMenu: string; onItemClick: (id: string) => void; collapsed?: boolean; onToggleCollapse?: () => void }) {
  const allowedModules = getAllowedModules();
  const [expandedItems, setExpandedItems] = useState<Set<string>>(loadExpanded);

  const toggleExpand = (id: string) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      saveExpanded(next);
      return next;
    });
  };

  const handleSubitemClick = (id: string) => {
    onItemClick(id);
  };

  const allCollapsed = expandedItems.size === 0;

  const toggleAll = () => {
    if (allCollapsed) {
      const all = new Set(
        menuItems.filter((item) => item.subitems?.length).map((item) => item.id)
      );
      setExpandedItems(all);
      saveExpanded(all);
    } else {
      setExpandedItems(new Set());
      saveExpanded(new Set());
    }
  };

  return (
    <nav style={{ display: "flex", flexDirection: "column", padding: "0.4rem 0" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');`}</style>
      {groupOrder.map((group, gi) => {
      const items = grouped[group].filter((item) => {
        if (item.subitems?.length) {
          return item.subitems.some(sub => canAccessModule(sub.id, allowedModules));
        }
        return canAccessModule(item.id, allowedModules);
      });
        if (!items.length) return null;
        const isPrincipal = group === "principal";
        return (
          <div key={group} style={{ marginBottom: gi < groupOrder.length - 1 ? "0.3rem" : 0 }}>
            {(!collapsed || isPrincipal) && (
              <div style={{
                display: "flex", alignItems: "center", justifyContent: isPrincipal ? (collapsed ? "center" : "space-between") : "flex-start",
                fontSize: "0.6rem", fontWeight: 700, letterSpacing: "0.13em",
                textTransform: "uppercase" as const,
                color: "rgb(186, 209, 224)",
                padding: isPrincipal ? (collapsed ? "0.5rem 0" : "0.75rem 0.9rem 0.28rem") : "0.75rem 0.9rem 0.28rem",
                fontFamily: "'Outfit', system-ui, sans-serif",
              }}>
                {(!collapsed || !isPrincipal) && (
                  <span>{groupLabels[group]}</span>
                )}
                {isPrincipal && (
                  <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
                    {!collapsed && (
                      <button
                        onClick={toggleAll}
                        aria-label={allCollapsed ? "Expandir todo" : "Colapsar todo"}
                        style={{
                          width: "22px", height: "22px",
                          border: "1px solid rgba(255,255,255,0.2)",
                          borderRadius: "5px", background: "none", cursor: "pointer",
                          display: "flex", alignItems: "center", justifyContent: "center",
                          color: "rgba(255,255,255,0.45)", flexShrink: 0,
                          transition: "background 0.15s",
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.background = "rgba(255,255,255,0.1)"}
                        onMouseLeave={(e) => e.currentTarget.style.background = "none"}
                      >
                        <svg width="8" height="8" viewBox="0 0 24 24" fill="none"
                          stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                          {allCollapsed ? (
                            <>
                              <polyline points="7 13 12 18 17 13" />
                              <polyline points="7 6 12 11 17 6" />
                            </>
                          ) : (
                            <>
                              <polyline points="7 11 12 6 17 11" />
                              <polyline points="7 18 12 13 17 18" />
                            </>
                          )}
                        </svg>
                      </button>
                    )}
                    {onToggleCollapse && (
                      <button
                        id="colapsar"
                        onClick={onToggleCollapse}
                        aria-label={collapsed ? "Expandir menú" : "Colapsar menú"}
                        style={{
                          width: "22px", height: "22px",
                          border: "1px solid rgba(255,255,255,0.2)",
                          borderRadius: "5px", background: "none", cursor: "pointer",
                          display: "flex", alignItems: "center", justifyContent: "center",
                          color: "rgba(255,255,255,0.7)", flexShrink: 0,
                          transition: "background 0.15s",
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.background = "rgba(255,255,255,0.1)"}
                        onMouseLeave={(e) => e.currentTarget.style.background = "none"}
                      >
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
                          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          {collapsed ? (
                            <polyline points="9 18 15 12 9 6" />
                          ) : (
                            <polyline points="15 18 9 12 15 6" />
                          )}
                        </svg>
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
            <div style={{
              padding: collapsed ? "0 0.2rem" : "0 0.65rem",
              display: "flex", flexDirection: "column", gap: collapsed ? "1px" : "2px",
            }}>
              {items.map((item) => (
                <div key={item.id}>
                  <NavItem
                    item={item}
                    isActive={activeMenu === item.id}
                    onClick={() => onItemClick(item.id)}
                    isExpanded={expandedItems.has(item.id)}
                    hasSubitems={!!item.subitems?.length}
                    onToggle={() => toggleExpand(item.id)}
                    collapsed={collapsed}
                  />
                  {item.subitems && expandedItems.has(item.id) && !collapsed && (
                    <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                      {item.subitems.filter(sub => canAccessModule(sub.id, allowedModules)).map(subitem => (
                        <NavItem
                          key={subitem.id}
                          item={subitem}
                          isActive={activeMenu === subitem.id}
                          onClick={() => handleSubitemClick(subitem.id)}
                          isSubitem
                          collapsed={collapsed}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </nav>
  );
}

function SidebarLogo({ withClose, onClose }: { withClose?: boolean; onClose?: () => void }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: "0.55rem",
      padding: "1rem 0.9rem 0.75rem",
      borderBottom: "1px solid rgba(255,255,255,0.12)",
    }}>
      <div style={{
        width: "30px", height: "30px",
        background: "var(--bakery-sidebar-active)",
        border: "1px solid rgba(255,255,255,0.15)",
        borderRadius: "7px",
        display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
      }}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
          stroke="rgba(255,255,255,0.9)" strokeWidth="1.8" strokeLinecap="round">
          <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/>
          <path d="M9 21V12h6v9"/>
        </svg>
      </div>
      <span style={{
        fontFamily: "'Outfit', system-ui, sans-serif",
        fontSize: "0.95rem", fontWeight: 700,
        color: "#ffffff", flex: 1, letterSpacing: "0.07em",
      }}>
        SAIP
      </span>
      {withClose && onClose && (
        <button onClick={onClose} aria-label="Cerrar menú" style={{
          width: "28px", height: "28px",
          border: "1px solid rgba(255,255,255,0.2)",
          borderRadius: "7px", background: "none", cursor: "pointer",
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "rgba(255,255,255,0.7)", flexShrink: 0,
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      )}
    </div>
  );
}

const versionTag: React.CSSProperties = {
  marginTop: "auto",
  padding: "0.75rem 1rem",
  borderTop: "1px solid rgba(255,255,255,0.12)",
  fontSize: "0.62rem",
  color: "rgba(255,255,255,0.35)",
  fontFamily: "'Outfit', system-ui, sans-serif",
  fontWeight: 500,
  letterSpacing: "0.04em",
};

export default function Sidebar({ activeMenu, onMenuChange, isOpen = true, onClose, collapsed = false, onToggleCollapse }: SidebarProps): JSX.Element {
  const [isMobile, setIsMobile] = React.useState(false);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);

  useEffect(() => {
    if (isMobile) document.body.style.overflow = isOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [isMobile, isOpen]);

  const handleItemClick = (id: string) => {
    onMenuChange(id);
    if (isMobile && onClose) onClose();
  };

  if (isMobile) {
    return (
      <>
        {isOpen && (
          <div onClick={onClose} aria-hidden="true" style={{
            position: "fixed", inset: 0,
            background: "rgba(22,66,91,0.22)",
            backdropFilter: "blur(3px)",
            zIndex: 150, cursor: "pointer",
          }} />
        )}
        <aside aria-hidden={!isOpen} style={{
          position: "fixed", top: 0, left: 0,
          width: "255px", height: "100vh",
          background: "var(--bakery-sidebar-bg)",
          borderRight: "1px solid rgba(255,255,255,0.08)",
          boxShadow: "6px 0 24px rgba(0,0,0,0.25)",
          zIndex: 200, display: "flex", flexDirection: "column",
          transform: isOpen ? "translateX(0)" : "translateX(-100%)",
          transition: "transform 0.28s cubic-bezier(0.4,0,0.2,1)",
          overflowY: "auto",
          fontFamily: "'Outfit', system-ui, sans-serif",
        }}>
          <SidebarLogo withClose onClose={onClose} />
          <NavContent activeMenu={activeMenu} onItemClick={handleItemClick} />
          <div style={versionTag}>SAIP v1.0 · Sistema Artesanal Integral</div>
        </aside>
      </>
    );
  }

  return (
    <aside style={{
      width: collapsed ? "60px" : "220px",
      minHeight: "calc(100vh - 58px)",
      background: "var(--bakery-sidebar-bg)",
      borderRight: "1px solid rgba(255,255,255,0.08)",
      display: "flex", flexDirection: "column",
      position: "sticky", top: "58px",
      height: "calc(100vh - 58px)",
      fontFamily: "'Outfit', system-ui, sans-serif",
      overflowY: "auto",
      transition: "width 0.3s ease",
    }}>
      <NavContent activeMenu={activeMenu} onItemClick={onMenuChange} collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      {!collapsed && <div style={versionTag}>SAIP v1.0</div>}
    </aside>
  );
}