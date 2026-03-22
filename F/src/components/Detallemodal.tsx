import { JSX, ReactNode } from "react";
import Modal from "./Modal";
import Button from "./Button";
import Badge from "./Badge";
import "./Detallemodal.css";

// ─── Interfaces ───────────────────────────────────────────────────────────────

/** Un campo a mostrar en la sección de detalles */
export interface DetalleField {
  label: string;
  value: ReactNode; // string, number, Badge, etc.
}

/** Un ítem de la lista (ej: ingrediente, producto, permiso...) */
export interface DetalleItem {
  nombre: string;
  detalle: ReactNode; // cantidad + unidad, precio, rol, etc.
}

export interface DetallemodalProps {
  /** Controla visibilidad */
  isOpen: boolean;
  onClose: () => void;

  /** Título principal (nombre del registro) */
  titulo: string;

  /** Badge de estado — opcional */
  estado?: {
    label: string;
    variant: "active" | "inactive" | "access" | "warning";
  };

  /** Texto descriptivo debajo del título — opcional */
  descripcion?: string | null;

  /**
   * Campos tipo ficha: Correo, Teléfono, Fecha, etc.
   * Se renderizan como pares label → valor antes de la lista.
   * Opcional.
   */
  campos?: DetalleField[];

  /**
   * Lista de ítems secundarios: ingredientes, productos, permisos...
   * Opcional — si no se pasa, no se muestra la sección.
   */
  items?: DetalleItem[];

  /** Título de la sección de ítems. Default: "Ítems" */
  itemsLabel?: string;

  /** Texto del botón de acción principal — opcional */
  accionLabel?: string;

  /** Callback del botón de acción principal — opcional */
  onAccion?: () => void;
}

// ─── Componente ───────────────────────────────────────────────────────────────
export default function Detallemodal({
  isOpen,
  onClose,
  titulo,
  estado,
  descripcion,
  campos,
  items,
  itemsLabel = "Ítems",
  accionLabel,
  onAccion,
}: DetallemodalProps): JSX.Element {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Detalle" width="480px">
      <div className="dm">
        {/* ── Encabezado ─────────────────────────────────────────────────── */}
        <div className="dm__header">
          <h2 className="dm__titulo">{titulo}</h2>
          {estado && (
            <Badge label={estado.label} variant={estado.variant} />
          )}
        </div>

        {/* ── Descripción ────────────────────────────────────────────────── */}
        {descripcion && (
          <p className="dm__descripcion">{descripcion}</p>
        )}

        {/* ── Campos tipo ficha ──────────────────────────────────────────── */}
        {campos && campos.length > 0 && (
          <div className="dm__campos">
            {campos.map((campo, idx) => (
              <div key={idx} className="dm__campo">
                <span className="dm__campo-label">{campo.label}</span>
                <span className="dm__campo-value">{campo.value}</span>
              </div>
            ))}
          </div>
        )}

        {/* ── Lista de ítems ─────────────────────────────────────────────── */}
        {items && items.length > 0 && (
          <div className="dm__section">
            <h3 className="dm__section-title">
              {itemsLabel} ({items.length})
            </h3>
            <div className="dm__items">
              {items.map((item, idx) => (
                <div key={idx} className="dm__item">
                  <span className="dm__item-nombre">{item.nombre}</span>
                  <span className="dm__item-detalle">{item.detalle}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Footer ─────────────────────────────────────────────────────── */}
        <div className="dm__footer">
          <Button variant="secondary" onClick={onClose}>
            Cerrar
          </Button>
          {accionLabel && onAccion && (
            <Button variant="primary" onClick={onAccion}>
              {accionLabel}
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
}