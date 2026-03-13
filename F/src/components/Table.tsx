import React, { useState } from "react";
import SearchBar from "./SearchBar";
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
  /** Callback del botón filtro */
  onFilter?: () => void;
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
  onFilter,
}: SAIPTableProps<T>) {
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  // Filtrado interno (si no hay onSearch externo)
  const filtered = onSearch
    ? data
    : data.filter((row) =>
        Object.values(row as Record<string, unknown>).some((val) =>
          String(val ?? "").toLowerCase().includes(search.toLowerCase())
        )
      );

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const paginated = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);

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
              onFilter={onFilter}
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


