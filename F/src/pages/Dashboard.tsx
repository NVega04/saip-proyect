import {JSX} from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";

interface Module {
  id: string;
  label: string;
  desc: string;
  icon: JSX.Element;
}

const modules: Module[] = [
  {
    id: "usuarios",
    label: "Gestión de usuarios",
    desc: "Gestión detallada de los usuarios.",
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
    id: "roles",
    label: "Gestión de roles",
    desc: "Administración, creación y distribución de roles.",
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.3">
        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
      </svg>
    ),
  },
  {
    id: "recetario",
    label: "Recetas",
    desc: "Gestión detallada de las recetas.",
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.3">
        <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/>
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
        <line x1="9" y1="7" x2="15" y2="7"/>
        <line x1="9" y1="11" x2="15" y2="11"/>
        <line x1="9" y1="15" x2="12" y2="15"/>
      </svg>
    ),
  },
  {
    id: "proveedores",
    label: "Proveedores",
    desc: "Administración de contactos y contratos de proveedores.",
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round">
        <rect x="1" y="3" width="15" height="13" rx="1"/>
        <path d="M16 8h4l3 5v4h-7V8z"/>
        <circle cx="5.5" cy="18.5" r="2.5"/>
        <circle cx="18.5" cy="18.5" r="2.5"/>
      </svg>
    ),
  },
    {
    id: "ventas",
    label: "Ventas",
    desc: "Detalle y administración de las ventas.",
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round">
        <line x1="12" y1="1" x2="12" y2="23"/>
        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
      </svg>
    ),
  }, 
     {
    id: "produccion",
    label: "Producción",
    desc: "Detalle y control de la producción",
    icon: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round">
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
  
];

export default function Dashboard(): JSX.Element {
  const navigate = useNavigate();

  return (
    <Layout>
      <h1 style={styles.title}>Módulos principales</h1>
      <div style={styles.grid}>
        {modules.map((mod) => (
          <div key={mod.id} 
          style={styles.card}
          onClick={() => navigate(`/${mod.id}`)}
          >
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
    color: "#5c3d1e",
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