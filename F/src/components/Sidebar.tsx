import React, {JSX} from "react";
import { Link} from "react-router-dom";

interface MenuItem {
  id: string;
  label: string;
  icon: JSX.Element;
  path:string;
}

interface SidebarProps {
  activeMenu: string;
  onMenuChange: (id: string) => void;
}

const menuItems: MenuItem[] = [
  {
    id: "dashboard",
    label: "Dashboard",
    path: "/dashboard",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <rect x="3" y="3" width="7" height="7" rx="1"/>
        <rect x="14" y="3" width="7" height="7" rx="1"/>
        <rect x="3" y="14" width="7" height="7" rx="1"/>
        <rect x="14" y="14" width="7" height="7" rx="1"/>
      </svg>
    ),
  },

  {
    id: "inventario",
    label: "Inventario",
    path: "/inventario",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
      </svg>
    ),
  },
  {
    id: "proveedores",
    label: "Proveedores",
    path: "/proveedores",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 00-3-3.87"/>
        <path d="M16 3.13a4 4 0 010 7.75"/>
      </svg>
    ),
  },
  {
    id: "ventas",
    label: "Ventas",
    path: "/ventas",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <line x1="12" y1="1" x2="12" y2="23"/>
        <path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
      </svg>
    ),
  },
  {
    id: "produccion",
    label: "Producción",
    path: "/produccion",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="2,20 2,12 6,8 6,12 10,8 10,12 14,8 14,20"/>
        <line x1="2" y1="20" x2="22" y2="20"/>
        <line x1="14" y1="20" x2="14" y2="10"/>
        <line x1="14" y1="10" x2="22" y2="10"/>
        <line x1="22" y1="10" x2="22" y2="20"/>
        <rect x="17" y="4" width="3" height="6" rx="0"/>
        <circle cx="18.5" cy="2.5" r="0.7"/>
        <circle cx="20" cy="1.5" r="0.5"/>
      </svg>
    ),
  },
   {
    id: "recetario",
    label: "Recetas",
    path: "/recetas",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.3">
        <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/>
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
        <line x1="9" y1="7" x2="15" y2="7"/>
        <line x1="9" y1="11" x2="15" y2="11"/>
        <line x1="9" y1="15" x2="12" y2="15"/>
      </svg>
    ),
  },
  {
    id: "gestion-usuarios",
    label: "Gestión de usuarios",
    path: "/usuarios",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M19 8l2 2-6 6"/>
        <path d="M21 10l-2 2"/>
      </svg>
    ),
  },
    {
    id: "roles",
    label: "Gestión de roles",
    path: "/roles",
    icon: (
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
        <path d="M7 11V7a5 5 0 0110 0v4"/>
      </svg>
    ),
  },
  {
    id: "acerca",
    label: "Acerca de SAIP",
    path: "/acerca",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
    ),
  },
  {
    id: "contacto",
    label: "Contáctanos",
    path: "/contacto",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 10.8 19.79 19.79 0 01.1 2.18 2 2 0 012.08 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.91 7.91a16 16 0 006.18 6.18l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 14.92v2z"/>
      </svg>
    ),
  },
];

export default function Sidebar({ activeMenu, onMenuChange }: SidebarProps): JSX.Element {
  return (
    <aside style={styles.sidebar}>
      <nav style={styles.nav}>
        {menuItems.map((item) => (
         <Link
         key={item.id}
         to={item.path || "#"}
         style={{ textDecoration: "none" }}
         onClick={() => onMenuChange(item.id)}
  >
    <div
      style={{
        ...styles.item,
        ...(activeMenu === item.id ? styles.itemActive : {}),
      }}
    >
      {item.icon}
      {item.label}
    </div>
  </Link>
))}
      </nav>
    </aside>
  );
}

const styles: Record<string, React.CSSProperties> = {
  sidebar: {
    width: "220px",
    minHeight: "calc(100vh - 56px)",
    background: "#ffffff",
    borderRight: "1px solid #cfc0b066",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    padding: "1.2rem 0",
    position: "sticky",
    top: "56px",
    height: "calc(100vh - 56px)",
    fontFamily: "'Roboto', sans-serif",
  },
  nav: {
    display: "flex",
    flexDirection: "column",
    gap: "0.15rem",
    padding: "0 0.75rem",
  },
  item: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    padding: "0.6rem 0.85rem",
    borderRadius: "6px",
    fontSize: "0.85rem",
    fontWeight: 400,
    color: "#7d5a3c",
    cursor: "pointer",
    background: "none",
    border: "none",
    width: "100%",
    textAlign: "left",
    fontFamily: "'Roboto', sans-serif",
  },
  itemActive: {
    background: "#f5f0ea",
    color: "#5c3d1e",
    fontWeight: 500,
  },
};