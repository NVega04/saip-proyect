import { useState } from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Button from "../components/Button";
import Badge from "../components/Badge";

interface Proveedor {
  id: number;
  nombre: string;
  contacto: string;
  telefono: string;
  categoria: string;
  estado: "Activo" | "Inactivo";
}

const mockProveedores: Proveedor[] = [
  { id: 1, nombre: "Harinera del Valle",  contacto: "Juan Pérez",    telefono: "310 000 0001", categoria: "Insumos",    estado: "Activo" },
  { id: 2, nombre: "Distribuidora Azúcar", contacto: "Ana Gómez",    telefono: "311 000 0002", categoria: "Insumos",    estado: "Activo" },
  { id: 3, nombre: "Empaques S.A.",        contacto: "Luis Torres",   telefono: "312 000 0003", categoria: "Empaques",   estado: "Inactivo" },
  { id: 4, nombre: "Lácteos del Norte",    contacto: "María Ruiz",    telefono: "313 000 0004", categoria: "Insumos",    estado: "Activo" },
];

const columns: ColumnDef<Proveedor>[] = [
  { key: "nombre",    header: "Nombre",    width: "25%" },
  { key: "contacto",  header: "Contacto",  width: "20%" },
  { key: "telefono",  header: "Teléfono",  width: "18%" },
  { key: "categoria", header: "Categoría", width: "15%" },
  { key: "estado",    header: "Estado",    width: "12%",
    render: (row) => (
      <Badge label={row.estado} variant={row.estado === "Activo" ? "active" : "inactive"} />
    ),
  },
];

export default function Proveedores() {
  const [proveedores, setProveedores] = useState<Proveedor[]>(mockProveedores);

  return (
    <Layout>
      <Table
        title="Proveedores"
        columns={columns}
        data={proveedores}
        searchPlaceholder="Buscar proveedor"
        sortKey="nombre"
        headerActions={
          <>
            <Button variant="primary" onClick={() => console.log("crear")}>
              Agregar Proveedores
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
              onClick={() => setProveedores((p) => p.filter((x) => x.id !== row.id))}>
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
