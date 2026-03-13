import React, { useState } from "react";
import Table, { ColumnDef } from "../components/Table";
import Button from "../components/Button";
import Badge from "../components/Badge";

interface Venta {
  id: number;
  codigo: string;
  cliente: string;
  fecha: string;
  total: number;
  estado: "Completada" | "Pendiente" | "Cancelada";
}

const mockVentas: Venta[] = [
  { id: 1, codigo: "VTA-001", cliente: "Supermercado La 14",  fecha: "2024-03-01", total: 245000, estado: "Completada" },
  { id: 2, codigo: "VTA-002", cliente: "Restaurante El Buen Sabor", fecha: "2024-03-03", total: 87500,  estado: "Completada" },
  { id: 3, codigo: "VTA-003", cliente: "Cafetería Central",   fecha: "2024-03-05", total: 132000, estado: "Pendiente" },
  { id: 4, codigo: "VTA-004", cliente: "Tienda Don Pedro",    fecha: "2024-03-06", total: 56000,  estado: "Cancelada" },
  { id: 5, codigo: "VTA-005", cliente: "Panadería El Sol",    fecha: "2024-03-07", total: 198000, estado: "Pendiente" },
];

const estadoVariant = (estado: Venta["estado"]) => {
  if (estado === "Completada") return "active";
  if (estado === "Pendiente")  return "warning";
  return "inactive";
};

const columns: ColumnDef<Venta>[] = [
  { key: "codigo",  header: "Código",   width: "12%" },
  { key: "cliente", header: "Cliente",  width: "28%" },
  { key: "fecha",   header: "Fecha",    width: "14%" },
  { key: "total",   header: "Total",    width: "15%",
    render: (row) => `$${row.total.toLocaleString("es-CO")}` },
  { key: "estado",  header: "Estado",   width: "14%",
    render: (row) => <Badge label={row.estado} variant={estadoVariant(row.estado)} /> },
];

export default function Ventas() {
  const [ventas, setVentas] = useState<Venta[]>(mockVentas);

  return (
    <Table
      title="Ventas"
      columns={columns}
      data={ventas}
      searchPlaceholder="Buscar venta"
      onFilter={() => console.log("filtrar")}
      headerActions={
        <>
          <Button variant="primary" onClick={() => console.log("nueva venta")}>
            Nueva Venta
          </Button>
          <Button variant="danger" onClick={() => console.log("eliminar")}>
            Eliminar Venta
          </Button>
        </>
      }
      renderActions={(row) => (
        <div className="saip-table__actions">
          <button className="saip-table__action-btn" title="Ver detalle"
            onClick={() => console.log("detalle", row.id)}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="1.8">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </button>
          <button className="saip-table__action-btn saip-table__action-btn--danger" title="Eliminar"
            onClick={() => setVentas((v) => v.filter((x) => x.id !== row.id))}>
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
  );
}
