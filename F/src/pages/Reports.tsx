import React, { useState } from "react";
import Layout from "../components/Layout";
import { apiFetch } from "../utils/api";

interface ReportEntity {
  id: string;
  label: string;
  desc: string;
  icon: React.ReactElement;
}

const entities: ReportEntity[] = [
  {
    id: "users",
    label: "Usuarios",
    desc: "Listado completo de usuarios registrados en el sistema.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6" strokeLinecap="round">
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 00-3-3.87"/>
        <path d="M16 3.13a4 4 0 010 7.75"/>
      </svg>
    ),
  },
  {
    id: "roles",
    label: "Roles",
    desc: "Roles definidos en el sistema con su estado actual.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6" strokeLinecap="round">
        <rect x="3" y="11" width="18" height="11" rx="2"/>
        <path d="M7 11V7a5 5 0 0110 0v4"/>
      </svg>
    ),
  },
    {
    id: "units",
    label: "Unidades",
    desc: "Listado de unidades de medida configuradas en el sistema.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6" strokeLinecap="round">
        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
        <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
        <line x1="12" y1="22.08" x2="12" y2="12"/>
      </svg>
    ),
  },
  {
    id: "supplies",
    label: "Insumos",
    desc: "Listado de insumos con stock y categorizacion.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6" strokeLinecap="round">
        <path d="M3 6h18M3 12h18M3 18h18"/>
      </svg>
    ),
  },
];

export default function Reportes() {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError]     = useState<string | null>(null);

  const handleDownload = async (entity: ReportEntity) => {
    setError(null);
    setLoading(entity.id);
    try {
      const res = await apiFetch(`/reports/${entity.id}`);
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail ?? "Error al generar el reporte.");
        return;
      }
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      const now  = new Date().toISOString().slice(0, 10);
      a.href     = url;
      a.download = `reporte_${entity.id}_${now}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("No se pudo conectar con el servidor.");
    } finally {
      setLoading(null);
    }
  };

  return (
    <Layout>
      <div style={{ marginBottom: "1.75rem" }}>
        <h1 style={styles.title}>Reportes</h1>
        <p style={styles.subtitle}>
          Descarga reportes en formato Excel (.xlsx) por entidad.
        </p>
      </div>

      {error && (
        <div style={styles.errorBox}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {error}
        </div>
      )}

      <div style={styles.grid}>
        {entities.map((entity) => (
          <div key={entity.id} style={styles.card}>
            <div style={styles.cardIcon}>{entity.icon}</div>
            <div style={styles.cardBody}>
              <p style={styles.cardLabel}>{entity.label}</p>
              <p style={styles.cardDesc}>{entity.desc}</p>
            </div>
            <button
              style={{
                ...styles.downloadBtn,
                opacity: loading === entity.id ? 0.7 : 1,
                cursor: loading === entity.id ? "not-allowed" : "pointer",
              }}
              onClick={() => handleDownload(entity)}
              disabled={loading !== null}
            >
              {loading === entity.id ? (
                <>
                  <span style={styles.spinner} />
                  Generando...
                </>
              ) : (
                <>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  Descargar Excel
                </>
              )}
            </button>
          </div>
        ))}
      </div>

      <div style={styles.infoBox}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9e7e62" strokeWidth="1.6">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        Los reportes incluyen todos los registros activos al momento de la descarga. Próximamente se agregarán filtros por fecha y estado.
      </div>
    </Layout>
  );
}

const styles: Record<string, React.CSSProperties> = {
  title: {
    fontSize: "1.5rem",
    fontWeight: 700,
    color: "#5c3d1e",
    marginBottom: "0.35rem",
    fontFamily: "'Outfit', system-ui, sans-serif",
  },
  subtitle: {
    fontSize: "0.88rem",
    color: "#9e7e62",
    fontFamily: "'Outfit', system-ui, sans-serif",
  },
  grid: {
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
  },
  card: {
    background: "#ffffff",
    border: "1px solid #cfc0b066",
    borderRadius: "10px",
    padding: "1.25rem 1.5rem",
    display: "flex",
    alignItems: "center",
    gap: "1.25rem",
    fontFamily: "'Outfit', system-ui, sans-serif",
    transition: "box-shadow 0.15s",
  },
  cardIcon: {
    width: "44px",
    height: "44px",
    background: "#f5f0ea",
    border: "1px solid #e8ddd4",
    borderRadius: "10px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  cardBody: {
    flex: 1,
  },
  cardLabel: {
    fontSize: "0.92rem",
    fontWeight: 600,
    color: "#5c3d1e",
    marginBottom: "0.2rem",
  },
  cardDesc: {
    fontSize: "0.8rem",
    color: "#9e7e62",
    lineHeight: 1.5,
  },
  downloadBtn: {
    display: "inline-flex",
    alignItems: "center",
    gap: "0.4rem",
    padding: "0.55rem 1.1rem",
    background: "#5c3d1e",
    color: "#ffffff",
    border: "none",
    borderRadius: "8px",
    fontSize: "0.8rem",
    fontWeight: 500,
    fontFamily: "'Outfit', system-ui, sans-serif",
    flexShrink: 0,
    transition: "background 0.15s",
  },
  spinner: {
    display: "inline-block",
    width: "11px",
    height: "11px",
    border: "2px solid rgba(255,255,255,0.3)",
    borderTopColor: "#ffffff",
    borderRadius: "50%",
    animation: "spin 0.7s linear infinite",
  },
  errorBox: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    fontSize: "0.85rem",
    color: "#c0392b",
    background: "#fdf0ef",
    border: "1px solid #f5c6c2",
    borderRadius: "8px",
    padding: "0.75rem 1rem",
    marginBottom: "1rem",
    fontFamily: "'Outfit', system-ui, sans-serif",
  },
  infoBox: {
    display: "flex",
    alignItems: "flex-start",
    gap: "0.5rem",
    fontSize: "0.78rem",
    color: "#9e7e62",
    background: "#f5f0ea",
    border: "1px solid #e8ddd4",
    borderRadius: "8px",
    padding: "0.75rem 1rem",
    marginTop: "1.5rem",
    lineHeight: 1.6,
    fontFamily: "'Outfit', system-ui, sans-serif",
  },
};