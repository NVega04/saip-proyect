import React, { useState } from "react";
import SearchBar, { SortOrder, SortCriteria } from "./SearchBar"; 
import Pagination from "./Pagination";
import "./Table.css";

// ─── Tipos ────────────────────────────────────────────────────────────────────

export interface ColumnDef<T> {
  /** Clave del campo en el objeto, o string arbitrario si usas render */
  key: string;
  header: string;
  width?: string;
  /** Renderer personalizado para la celda */
  render?: (row: T) => React.ReactNode;
}

interface SAIPTableProps<T extends { id: string | number }> {
  /** Título de la sección, ej: "Gestión de usuarios" */
  title: string;
  columns: ColumnDef<T>[];
  data: T[];
  /** Acciones al final de cada fila */
  renderActions?: (row: T) => React.ReactNode;
  /** Botones sobre la tabla (Crear, Eliminar…) */
  headerActions?: React.ReactNode;
  /** Texto vacío */
  emptyMessage?: string;
  /** Registros por página */
  pageSize?: number;
  /** Desactiva la búsqueda */
  searchable?: boolean;
  /** Placeholder del buscador */
  searchPlaceholder?: string;
  /** Callback externo de búsqueda (si quieres manejarla fuera) */
  onSearch?: (value: string) => void;
  /** Clave para orden alfabético */
  sortKey?: string;    
  /** Clave numérica para ordenar por ID (default "id") */  
  idKey?: string;     
}

// ─── Componente ───────────────────────────────────────────────────────────────

export default function Table<T extends { id: string | number }>({
  title,
  columns,
  data,
  renderActions,
  headerActions,
  emptyMessage = "No hay registros para mostrar.",
  pageSize = 10,
  searchable = true,
  searchPlaceholder = "Buscar",
  onSearch,
  sortKey,
  idKey,
}: SAIPTableProps<T>) {
  const [search, setSearch] = useState("");
  const [sortOrder, setSortOrder] = useState<SortOrder>(null);   
  const [sortCriteria, setSortCriteria] = useState<SortCriteria>("id"); 
  const [currentPage, setCurrentPage] = useState(1);
  const filtered = onSearch
    ? data
    : data.filter((row) =>
        Object.values(row as Record<string, unknown>).some((val) =>
          String(val ?? "").toLowerCase().includes(search.toLowerCase())
        )
      );

    const sorted = (() => {
  if (!sortOrder) return filtered;

  return [...filtered].sort((a, b) => {
    const rec = a as Record<string, unknown>;
    const recB = b as Record<string, unknown>;

    if (sortCriteria === "id") {
      const aId = Number(rec[idKey ?? "id"] ?? 0);
      const bId = Number(recB[idKey ?? "id"] ?? 0);
      return sortOrder === "asc" ? aId - bId : bId - aId;
    }

    // orden alfabético
    const aVal = String(rec[sortKey ?? "name"] ?? "").toLowerCase();
    const bVal = String(recB[sortKey ?? "name"] ?? "").toLowerCase();

    if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
    if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
    return 0;
  });
})();

  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize));
  const paginated = sorted.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const handleSearch = (val: string) => {
    setSearch(val);
    setCurrentPage(1);
    onSearch?.(val);
  };

  return (
    <section className="saip-table-section">
      {/* Título */}
      <h1 className="saip-table-section__title">{title}</h1>

      {/* Card */}
      <div className="saip-table-card">
        {/* Toolbar */}
        <div className="saip-table-card__toolbar">
          <div className="saip-table-card__toolbar-left">
            {headerActions}
          </div>
          {searchable && (

         <SearchBar
     value={search}
     onChange={handleSearch}
     placeholder={searchPlaceholder}
     sortOrder={sortOrder}
     sortCriteria={sortCriteria}
     onSort={(order, criteria) => {
     setSortOrder(order);
     setSortCriteria(criteria);
     setCurrentPage(1);
  }}
/>
          )}
        </div>

        {/* Tabla */}
        <div className="saip-table-wrapper">
          <table className="saip-table">
            <thead>
              <tr>
                {columns.map((col) => (
                  <th
                    key={col.key}
                    className="saip-table__th"
                    style={col.width ? { width: col.width } : undefined}
                  >
                    {col.header}
                  </th>
                ))}
                {renderActions && (
                  <th className="saip-table__th saip-table__th--actions">Acciones</th>
                )}
              </tr>
            </thead>
            <tbody>
              {paginated.length === 0 ? (
                <tr>
                  <td
                    colSpan={columns.length + (renderActions ? 1 : 0)}
                    className="saip-table__empty"
                  >
                    {emptyMessage}
                  </td>
                </tr>
              ) : (
                paginated.map((row) => (
                  <tr key={row.id} className="saip-table__row">
                    {columns.map((col) => (
                      <td key={col.key} className="saip-table__td">
                        {col.render
                          ? col.render(row)
                          : String((row as Record<string, unknown>)[col.key] ?? "")}
                      </td>
                    ))}
                    {renderActions && (
                      <td className="saip-table__td saip-table__td--actions">
                        {renderActions(row)}
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Paginación */}
        {totalPages > 1 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        )}
      </div>
    </section>
  );
}


