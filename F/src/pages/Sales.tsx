import { JSX } from "react";
import Layout from "../components/Layout";
import "./Inventory.css";

export default function Ventas(): JSX.Element {
  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Ventas" },
      ]}
    >
      <div className="construccion">
        <div className="construccion__icon">
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#7d5a3c"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="12" y1="1" x2="12" y2="23" />
            <path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
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
