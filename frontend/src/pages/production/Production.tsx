import { JSX } from "react";
import Layout from "../../components/layout/Layout";
import "../inventory/Inventory.css";

export default function Produccion(): JSX.Element {
  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Producción" },
      ]}
    >
      <div className="construccion">
        <div className="construccion__icon">
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#3a7ca5"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="2,20 2,12 6,8 6,12 10,8 10,12 14,8 14,20" />
            <line x1="2" y1="20" x2="22" y2="20" />
            <line x1="14" y1="20" x2="14" y2="10" />
            <line x1="14" y1="10" x2="22" y2="10" />
            <line x1="22" y1="10" x2="22" y2="20" />
            <rect x="17" y="4" width="3" height="6" rx="0" />
            <circle cx="18.5" cy="2.5" r="0.7" />
            <circle cx="20" cy="1.5" r="0.5" />
          </svg>
        </div>
        <h1 className="construccion__title">Módulo en construcción</h1>
        <p className="construccion__desc">
          Estamos trabajando en este módulo. Muy pronto estará disponible.
        </p>
      </div>
    </Layout>
  );
}
