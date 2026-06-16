import { JSX } from "react";
import Layout from "../../components/layout/Layout";
import "../inventory/Inventory.css";

export default function SalesHistory(): JSX.Element {
  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Ventas" },
        { label: "Historial de ventas" },
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
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
            <polyline points="16 7 22 7 22 13" />
          </svg>
        </div>
        <h1 className="construccion__title">Módulo en construcción</h1>
        <p className="construccion__desc">
          Estamos trabajando en el historial de ventas. Muy pronto estará disponible.
        </p>
      </div>
    </Layout>
  );
}
