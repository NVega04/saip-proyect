import React, { JSX, useEffect, useState } from "react";
import { Link } from "react-router-dom";

interface MenuItem {
  id: string;
  label: string;
  icon: JSX.Element;
  path: string;
  group?: string;
}

interface SidebarProps {
  activeMenu: string;
  onMenuChange: (id: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
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
};

const menuItems: MenuItem[] = [
  { id: "dashboard",        label: "Dashboard",          path: "/dashboard",  icon: Icon.dashboard,  group: "principal" },
  { id: "inventario",       label: "Inventario",         path: "/inventario", icon: Icon.inventory,  group: "operaciones" },
  { id: "proveedores",      label: "Proveedores",        path: "/proveedores",icon: Icon.suppliers,  group: "operaciones" },
  { id: "ventas",           label: "Ventas",             path: "/ventas",     icon: Icon.sales,      group: "operaciones" },
  { id: "produccion",       label: "Producción",         path: "/produccion", icon: Icon.production, group: "operaciones" },
  { id: "recetario",        label: "Recetas",            path: "/recetas",    icon: Icon.recipes,    group: "operaciones" },
  { id: "gestion-usuarios", label: "Gestión de usuarios",path: "/usuarios",   icon: Icon.users,      group: "administracion" },
  { id: "roles",            label: "Gestión de roles",   path: "/roles",      icon: Icon.roles,      group: "administracion" },
  { id: "acerca",           label: "Acerca de SAIP",     path: "/acerca",     icon: Icon.about,      group: "soporte" },
  { id: "contacto",         label: "Contáctanos",        path: "/contacto",   icon: Icon.contact,    group: "soporte" },
];

const groupLabels: Record<string, string> = {
  principal:      "Principal",
  operaciones:    "Operaciones",
  administracion: "Administración",
  soporte:        "Soporte",
};

const groupOrder = ["principal", "operaciones", "administracion", "soporte"];

const grouped = menuItems.reduce<Record<string, MenuItem[]>>((acc, item) => {
  const g = item.group ?? "otros";
  if (!acc[g]) acc[g] = [];
  acc[g].push(item);
  return acc;
}, {});

// ── NavItem: combinación C (dot) + D (recuadro sutil) ────────────────────────
function NavItem({ item, isActive, onClick }: { item: MenuItem; isActive: boolean; onClick: () => void }) {
  const [hovered, setHovered] = useState(false);

  return (
    <Link to={item.path} style={{ textDecoration: "none" }} onClick={onClick}>
      <div
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          display: "flex", alignItems: "center", gap: "0.6rem",
          padding: "0.5rem 0.75rem",
          borderRadius: "7px",
          fontSize: "0.81rem",
          fontWeight: isActive ? 600 : 400,
          color: isActive ? "var(--dark, #3b1f08)" : hovered ? "var(--dark, #3b1f08)" : "var(--mid, #8c5530)",
          background: isActive ? "var(--bg, #faf4ec)" : hovered ? "#faf4ec" : "transparent",
          boxShadow: isActive ? "inset 0 0 0 1px rgba(107,58,24,0.22)" : "none",
          cursor: "pointer",
          fontFamily: "'Outfit', system-ui, sans-serif",
          transition: "background 0.15s, color 0.15s, box-shadow 0.15s",
        }}
      >
        <span style={{
          flexShrink: 0, display: "flex",
          color: isActive ? "var(--medium, #6b3a18)" : "currentColor",
          transition: "color 0.15s",
        }}>
          {item.icon}
        </span>
        <span style={{ flex: 1 }}>{item.label}</span>
        {isActive && (
          <span style={{
            width: "5px", height: "5px", borderRadius: "50%",
            background: "var(--medium, #6b3a18)", flexShrink: 0,
          }} />
        )}
      </div>
    </Link>
  );
}

function NavContent({ activeMenu, onItemClick }: { activeMenu: string; onItemClick: (id: string) => void }) {
  return (
    <nav style={{ display: "flex", flexDirection: "column", padding: "0.4rem 0" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');`}</style>
      {groupOrder.map((group, gi) => {
        const items = grouped[group];
        if (!items) return null;
        return (
          <div key={group} style={{ marginBottom: gi < groupOrder.length - 1 ? "0.3rem" : 0 }}>
            <div style={{
              fontSize: "0.6rem", fontWeight: 700, letterSpacing: "0.13em",
              textTransform: "uppercase" as const,
              color: "var(--pale, #c99870)",
              padding: "0.75rem 0.9rem 0.28rem",
              fontFamily: "'Outfit', system-ui, sans-serif",
            }}>
              {groupLabels[group]}
            </div>
            <div style={{ padding: "0 0.65rem", display: "flex", flexDirection: "column", gap: "2px" }}>
              {items.map((item) => (
                <NavItem
                  key={item.id}
                  item={item}
                  isActive={activeMenu === item.id}
                  onClick={() => onItemClick(item.id)}
                />
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
      borderBottom: "1px solid var(--border, rgba(107,58,24,0.18))",
    }}>
      <div style={{
        width: "30px", height: "30px",
        background: "var(--bg, #faf4ec)",
        border: "1px solid var(--border-s, rgba(107,58,24,0.30))",
        borderRadius: "7px",
        display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
      }}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
          stroke="var(--medium, #6b3a18)" strokeWidth="1.8" strokeLinecap="round">
          <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/>
          <path d="M9 21V12h6v9"/>
        </svg>
      </div>
      <span style={{
        fontFamily: "'Outfit', system-ui, sans-serif",
        fontSize: "0.95rem", fontWeight: 700,
        color: "var(--dark, #3b1f08)", flex: 1, letterSpacing: "0.07em",
      }}>
        SAIP
      </span>
      {withClose && onClose && (
        <button onClick={onClose} aria-label="Cerrar menú" style={{
          width: "28px", height: "28px",
          border: "1px solid var(--border-s, rgba(107,58,24,0.30))",
          borderRadius: "7px", background: "none", cursor: "pointer",
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "var(--mid, #8c5530)", flexShrink: 0,
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
  borderTop: "1px solid var(--border, rgba(107,58,24,0.18))",
  fontSize: "0.62rem",
  color: "var(--pale, #c99870)",
  fontFamily: "'Outfit', system-ui, sans-serif",
  fontWeight: 500,
  letterSpacing: "0.04em",
};

export default function Sidebar({ activeMenu, onMenuChange, isOpen = true, onClose }: SidebarProps): JSX.Element {
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
            background: "rgba(59,31,8,0.22)",
            backdropFilter: "blur(3px)",
            zIndex: 150, cursor: "pointer",
          }} />
        )}
        <aside aria-hidden={!isOpen} style={{
          position: "fixed", top: 0, left: 0,
          width: "255px", height: "100vh",
          background: "var(--white, #fff)",
          borderRight: "1px solid var(--border-s, rgba(107,58,24,0.30))",
          boxShadow: "6px 0 24px rgba(59,31,8,0.12)",
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
      width: "220px",
      minHeight: "calc(100vh - 58px)",
      background: "var(--white, #fff)",
      borderRight: "1px solid var(--border-s, rgba(107,58,24,0.30))",
      display: "flex", flexDirection: "column",
      position: "sticky", top: "58px",
      height: "calc(100vh - 58px)",
      fontFamily: "'Outfit', system-ui, sans-serif",
      overflowY: "auto",
    }}>
      <NavContent activeMenu={activeMenu} onItemClick={onMenuChange} />
      <div style={versionTag}>SAIP v1.0</div>
    </aside>
  );
}
