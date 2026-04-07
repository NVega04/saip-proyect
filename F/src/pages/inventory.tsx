import { JSX } from "react";
import Layout from "../components/Layout";
import "./Inventory.css";

export default function Inventario(): JSX.Element {
  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Inventario" },
      ]}
    >
      <div className="construccion">
        <div className="construccion__icon">
          <svg
            width="64"
            height="64"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#7d5a3c"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
            <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
            <line x1="12" y1="22.08" x2="12" y2="12" />
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
