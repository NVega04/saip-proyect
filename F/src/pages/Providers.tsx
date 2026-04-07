import { JSX } from "react";
import Layout from "../components/Layout";
import "./Inventory.css";

export default function Proveedores(): JSX.Element {
  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Proveedores" },
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
            <rect x="1" y="3" width="15" height="13" rx="1" />
            <path d="M16 8h4l3 3v5h-7V8z" />
            <circle cx="5.5" cy="18.5" r="2.5" />
            <circle cx="18.5" cy="18.5" r="2.5" />
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
