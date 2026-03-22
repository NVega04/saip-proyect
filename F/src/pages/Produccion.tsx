import { useState } from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Button from "../components/Button";
import Badge from "../components/Badge";

interface OrdenProduccion {
  id: number;
  codigo: string;
  producto: string;
  cantidad: number;
  unidad: string;
  fechaInicio: string;
  estado: "En proceso" | "Completada" | "Pendiente";
}

const mockOrdenes: OrdenProduccion[] = [
  { id: 1, codigo: "OP-001", producto: "Pan tajado",   cantidad: 200, unidad: "und", fechaInicio: "2024-03-01", estado: "Completada" },
  { id: 2, codigo: "OP-002", producto: "Croissant",    cantidad: 150, unidad: "und", fechaInicio: "2024-03-03", estado: "En proceso" },
  { id: 3, codigo: "OP-003", producto: "Torta básica", cantidad: 20,  unidad: "und", fechaInicio: "2024-03-05", estado: "Pendiente" },
  { id: 4, codigo: "OP-004", producto: "Galletas",     cantidad: 500, unidad: "und", fechaInicio: "2024-03-06", estado: "En proceso" },
];

const estadoVariant = (estado: OrdenProduccion["estado"]) => {
  if (estado === "Completada")  return "active";
  if (estado === "En proceso")  return "warning";
  return "access";
};

const columns: ColumnDef<OrdenProduccion>[] = [
  { key: "codigo",      header: "Código",      width: "12%" },
  { key: "producto",    header: "Producto",    width: "25%" },
  { key: "cantidad",    header: "Cantidad",    width: "12%" },
  { key: "unidad",      header: "Unidad",      width: "10%" },
  { key: "fechaInicio", header: "Fecha inicio", width: "16%" },
  { key: "estado",      header: "Estado",      width: "14%",
    render: (row) => <Badge label={row.estado} variant={estadoVariant(row.estado)} /> },
];

export default function Produccion() {
  const [ordenes, setOrdenes] = useState<OrdenProduccion[]>(mockOrdenes);

  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Producción" },
      ]}
    >
      <Table
        title="Producción"
        columns={columns}
        data={ordenes}
        searchPlaceholder="Buscar orden"
        sortKey="producto"
        headerActions={
          <>
            <Button variant="primary" onClick={() => console.log("nueva orden")}>
              Nueva orden
            </Button>
          </>
        }
        renderActions={(row) => (
          <div className="saip-table__actions">
            <button className="saip-table__action-btn" title="Editar"
              onClick={() => console.log("editar", row.id)}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="1.8">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
            </button>
            <button className="saip-table__action-btn saip-table__action-btn--danger" title="Eliminar"
              onClick={() => setOrdenes((o) => o.filter((x) => x.id !== row.id))}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="1.8">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
                <path d="M10 11v6M14 11v6"/>
                <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
              </svg>
            </button>
          </div>
        )}
      />
    </Layout>
  );
}
