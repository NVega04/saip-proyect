import {JSX} from "react";
import Layout from "./Layout";

interface Module {
  id: string;
  label: string;
  desc: string;
  icon: JSX.Element;
}

const modules: Module[] = [
  {
    id: "inventario",
    label: "Inventario",
    desc: "Gestión detallada de productos y existencias.",
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.3">
        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
      </svg>
    ),
  },
  {
    id: "proveedores",
    label: "Proveedores",
    desc: "Administración de contactos y contratos de proveedores.",
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.3">
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
    desc: "Seguimiento de pedidos, transacciones y clientes.",
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.3">
        <line x1="12" y1="1" x2="12" y2="23"/>
        <path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
      </svg>
    ),
  },
  {
    id: "produccion",
    label: "Producción",
    desc: "Control de procesos de fabricación y recursos.",
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.3">
        <rect x="2" y="7" width="20" height="14" rx="1"/>
        <path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/>
        <line x1="12" y1="12" x2="12" y2="16"/>
        <line x1="10" y1="14" x2="14" y2="14"/>
      </svg>
    ),
  },
];

export default function Dashboard(): JSX.Element {
  return (
    <Layout>
      <h1 style={styles.title}>Módulos principales</h1>
      <div style={styles.grid}>
        {modules.map((mod) => (
          <div key={mod.id} style={styles.card}>
            {mod.icon}
            <div style={styles.cardLabel}>{mod.label}</div>
            <div style={styles.cardDesc}>{mod.desc}</div>
          </div>
        ))}
      </div>
    </Layout>
  );
}

const styles: Record<string, React.CSSProperties> = {
  title: {
    fontSize: "1.5rem",
    fontWeight: 700,
    color: "#dc3434",
    marginBottom: "1.5rem",
    fontFamily: "'Roboto', sans-serif",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "1rem",
  },
  card: {
    background: "#ffffff",
    border: "1px solid #cfc0b066",
    borderRadius: "8px",
    padding: "2.5rem 2rem",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: "0.85rem",
    cursor: "pointer",
    textAlign: "center",
    fontFamily: "'Roboto', sans-serif",
  },
  cardLabel: {
    fontSize: "1rem",
    fontWeight: 700,
    color: "#5c3d1e",
  },
  cardDesc: {
    fontSize: "0.8rem",
    fontWeight: 300,
    color: "#9e7e62",
    lineHeight: 1.5,
  },
};