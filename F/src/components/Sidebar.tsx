import {JSX} from "react";

interface MenuItem {
  id: string;
  label: string;
  icon: JSX.Element;
}

interface SidebarProps {
  activeMenu: string;
  onMenuChange: (id: string) => void;
}

const menuItems: MenuItem[] = [
  {
    id: "inventario",
    label: "Inventario",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
      </svg>
    ),
  },
  {
    id: "proveedores",
    label: "Proveedores",
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
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <rect x="2" y="7" width="20" height="14" rx="1"/>
        <path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/>
        <line x1="12" y1="12" x2="12" y2="16"/>
        <line x1="10" y1="14" x2="14" y2="14"/>
      </svg>
    ),
  },
  {
    id: "acerca",
    label: "Acerca de SAIP",
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
          <button
            key={item.id}
            onClick={() => onMenuChange(item.id)}
            style={{
              ...styles.item,
              ...(activeMenu === item.id ? styles.itemActive : {}),
            }}
          >
            {item.icon}
            {item.label}
          </button>
        ))}
      </nav>

      <div style={styles.footer}>
        <div style={styles.userInfo}>
          <div style={styles.avatar}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.5">
              <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <div>
            <div style={styles.userName}>Usuario</div>
            <div style={styles.userRole}>Rol</div>
          </div>
        </div>
        <button style={styles.logoutBtn}>Cerrar sesión</button>
      </div>
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
  footer: {
    padding: "1rem 1rem 0",
    borderTop: "1px solid #cfc0b066",
  },
  userInfo: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    marginBottom: "0.85rem",
  },
  avatar: {
    width: "34px",
    height: "34px",
    borderRadius: "50%",
    background: "#cfc0b0",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  userName: {
    fontSize: "0.82rem",
    fontWeight: 500,
    color: "#5c3d1e",
  },
  userRole: {
    fontSize: "0.72rem",
    fontWeight: 300,
    color: "#9e7e62",
  },
  logoutBtn: {
    fontSize: "0.8rem",
    fontWeight: 400,
    color: "#9e7e62",
    background: "none",
    border: "none",
    cursor: "pointer",
    padding: 0,
    fontFamily: "'Roboto', sans-serif",
  },
};