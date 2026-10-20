import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../../components/layout/Layout";
import Table, { ColumnDef } from "../../components/table/Table";
import Modal from "../../components/modal/Modal";
import Button from "../../components/button/Button";
import { useAlert } from "../../context/AlertContext";
import { useConfirm } from "../../context/ConfirmContext";
import { apiFetch } from "../../utils/api";
import "./units.css";
import { useReportDownload } from "../../hooks/useReportDownload.ts";
import { LONGITUDES_MAX, MENSAJES_VALIDACION } from "../../constants/validations.constants";
import { validarCampoRequerido, validarLongitudMaxima } from "../../utils/validations";

interface Unit {
  id: number;
  token: string;
  name: string;
  abbreviation: string;
  description: string | null;
  quantity: number;
}

interface UnitForm {
  name: string;
  abbreviation: string;
  description: string;
  quantity: number;
}

type FormErrors = Partial<Record<keyof UnitForm, string>>;

const crearFormularioVacio = (): UnitForm => ({
  name: "",
  abbreviation: "",
  description: "",
  quantity: 0,
});

const columns: ColumnDef<Unit>[] = [
  { key: "name", header: "Nombre", width: "25%" },
  { key: "abbreviation", header: "Abreviatura", width: "15%" },
  { key: "description", header: "Descripcion", width: "35%" },
  { key: "quantity", header: "Cantidad base", width: "10%" },
];

/**
 * Valida los campos del formulario de unidades.
 * Devuelve el objeto de errores (vacío si el formulario es válido).
 */
const validarFormulario = (datosFormulario: UnitForm): FormErrors => {
  const errores: FormErrors = {};

  const nombreRequerido = validarCampoRequerido(datosFormulario.name);
  const nombreDemasiadoLargo = validarLongitudMaxima(datosFormulario.name, LONGITUDES_MAX.name);
  if (nombreRequerido) errores.name = nombreRequerido;
  if (nombreDemasiadoLargo) errores.name = nombreDemasiadoLargo;

  const abreviaturaRequerida = validarCampoRequerido(
    datosFormulario.abbreviation,
    MENSAJES_VALIDACION.abreviaturaRequerida
  );
  const abreviaturaDemasiadoLarga = validarLongitudMaxima(
    datosFormulario.abbreviation,
    LONGITUDES_MAX.abbreviation
  );
  if (abreviaturaRequerida) errores.abbreviation = abreviaturaRequerida;
  if (abreviaturaDemasiadoLarga) errores.abbreviation = abreviaturaDemasiadoLarga;

  if (datosFormulario.quantity < 0) errores.quantity = MENSAJES_VALIDACION.cantidadNegativa;

  return errores;
};

/**
 * Construye el cuerpo de la petición enviada al backend
 * a partir de los datos actuales del formulario.
 */
const construirCuerpoPeticion = (datosFormulario: UnitForm) => ({
  name: datosFormulario.name,
  abbreviation: datosFormulario.abbreviation,
  description: datosFormulario.description || null,
  quantity: datosFormulario.quantity,
});

export default function Units(): JSX.Element {
  const [unidades, setUnidades] = useState<Unit[]>([]);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [unidadEnEdicion, setUnidadEnEdicion] = useState<Unit | null>(null);
  const [datosFormulario, setDatosFormulario] = useState<UnitForm>(crearFormularioVacio());
  const [errores, setErrores] = useState<FormErrors>({});
  const [cargando, setCargando] = useState(true);

  const { showAlert } = useAlert();
  const { showConfirm } = useConfirm();
  const { download: downloadReport, loading: reportLoading } = useReportDownload("units");

  useEffect(() => {
    const cargarUnidades = async () => {
      try {
        const response = await apiFetch("/units/");
        if (!response.ok) throw new Error("Error al cargar unidades");
        const data: Unit[] = await response.json();
        setUnidades(data);
      } catch (err) {
        console.error(err);
      } finally {
        setCargando(false);
      }
    };
    cargarUnidades();
  }, []);

  const manejarCreacion = () => {
    setUnidadEnEdicion(null);
    setDatosFormulario(crearFormularioVacio());
    setErrores({});
    setModalAbierto(true);
  };

  const manejarEdicion = (unidad: Unit) => {
    setUnidadEnEdicion(unidad);
    setDatosFormulario({
      name: unidad.name,
      abbreviation: unidad.abbreviation,
      description: unidad.description ?? "",
      quantity: unidad.quantity,
    });
    setErrores({});
    setModalAbierto(true);
  };

  const manejarCierre = () => {
    setModalAbierto(false);
    setUnidadEnEdicion(null);
    setDatosFormulario(crearFormularioVacio());
  };

  const actualizarCampo = (campo: keyof UnitForm, valor: string | number) => {
    setDatosFormulario((prev) => ({ ...prev, [campo]: valor }));
    setErrores((prev) => ({ ...prev, [campo]: undefined }));
  };

  const validarYConfirmarFormulario = (): boolean => {
    const erroresDetectados = validarFormulario(datosFormulario);
    setErrores(erroresDetectados);
    return Object.keys(erroresDetectados).length === 0;
  };

  const guardarUnidad = async () => {
    const esActualizacion = unidadEnEdicion !== null;
    const url = esActualizacion ? `/units/${unidadEnEdicion.id}` : "/units/";
    const metodo = esActualizacion ? "PATCH" : "POST";

    const response = await apiFetch(url, {
      method: metodo,
      body: JSON.stringify(construirCuerpoPeticion(datosFormulario)),
    });

    if (!response.ok) {
      const err = await response.json();
      showAlert(
        "error",
        err.detail || (esActualizacion ? "Error al actualizar unidad" : "Error al crear unidad")
      );
      return;
    }

    const unidadGuardada: Unit = await response.json();
    if (esActualizacion) {
      setUnidades((prev) => prev.map((u) => (u.id === unidadEnEdicion.id ? unidadGuardada : u)));
      showAlert("success", "Unidad actualizada correctamente.");
    } else {
      setUnidades((prev) => [...prev, unidadGuardada]);
      showAlert("success", "Unidad creada correctamente.");
    }
  };

  const manejarEnvio = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validarYConfirmarFormulario()) {
      showAlert("warning", "Completa los campos obligatorios.");
      return;
    }

    try {
      await guardarUnidad();
      manejarCierre();
    } catch {
      showAlert("error", "Error de conexión con el servidor.");
    }
  };

  const manejarEliminacion = (id: number) => {
    showConfirm({
      title: "Eliminar unidad",
      message: "¿Está seguro que desea eliminar este registro?",
      confirmText: "Eliminar",
      cancelText: "Cancelar",
      onConfirm: async () => {
        try {
          const response = await apiFetch(`/units/${id}`, { method: "DELETE" });

          if (!response.ok) {
            const err = await response.json();
            showAlert("error", err.detail || "Error al eliminar unidad");
            return;
          }

          setUnidades((prev) => prev.filter((u) => u.id !== id));
          showAlert("success", "Unidad eliminada correctamente.");
        } catch {
          showAlert("error", "Error de conexión con el servidor.");
        }
      },
    });
  };
  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Panadería" },
        { label: "Unidades" },
      ]}
    >
      {cargando ? (
        <div className="saip-loading">Cargando unidades...</div>
      ) : (
        <Table
          title="Unidades de medida"
          columns={columns}
          data={unidades}
          searchPlaceholder="Buscar unidad"
          sortKey="name"
          headerActions={
            <>
            <Button variant="primary" onClick={manejarCreacion}>
              Crear unidad
            </Button>
             <Button
                variant="secondary"
                onClick={downloadReport}
                disabled={reportLoading}
                icon={
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                  }
                >
                {reportLoading ? "Generando..." : "Exportar excel"}
            </Button>
            </>
          }
          renderActions={(row) => (
            <div className="saip-table__actions">
              <button
                type="button"
                className="saip-table__action-btn"
                title="Editar"
                onClick={() => manejarEdicion(row)}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="1.8">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button
                type="button"
                className="saip-table__action-btn saip-table__action-btn--danger"
                title="Eliminar"
                onClick={() => manejarEliminacion(row.id)}
              >
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
      )}

      <Modal
        isOpen={modalAbierto}
        onClose={manejarCierre}
        title={unidadEnEdicion ? "Editar unidad" : "Crear unidad"}
        width="480px"
      >
        <form className="unf" onSubmit={manejarEnvio}>
          <div className="unf__group">
            <label className="unf__label">
              Nombre<span className="unf__required">*</span>
            </label>
            <input
              className={`unf__input ${errores.name ? "unf__input--error" : ""}`}
              placeholder="Ej: Kilogramo, Litro..."
              value={datosFormulario.name}
              onChange={(e) => actualizarCampo("name", e.target.value)}
            />
            {errores.name && <span className="unf__error">{errores.name}</span>}
          </div>

          <div className="unf__group">
            <label className="unf__label">
              Abreviatura<span className="unf__required">*</span>
            </label>
            <input
              className={`unf__input ${errores.abbreviation ? "unf__input--error" : ""}`}
              placeholder="Ej: kg, L, g..."
              maxLength={LONGITUDES_MAX.abbreviation}
              value={datosFormulario.abbreviation}
              onChange={(e) => actualizarCampo("abbreviation", e.target.value)}
            />
            {errores.abbreviation && <span className="unf__error">{errores.abbreviation}</span>}
          </div>

          <div className="unf__group">
            <label className="unf__label">Descripcion</label>
            <textarea
              className="unf__textarea"
              placeholder="Describe esta unidad de medida..."
              rows={3}
              value={datosFormulario.description}
              onChange={(e) => actualizarCampo("description", e.target.value)}
            />
          </div>

          <div className="unf__group">
            <label className="unf__label">
              Cantidad base<span className="unf__required">*</span>
            </label>
            <input
              type="number"
              className={`unf__input ${errores.quantity ? "unf__input--error" : ""}`}
              placeholder="Cantidad base para conversion"
              min={0}
              step={1}
              value={datosFormulario.quantity}
              onChange={(e) => actualizarCampo("quantity", parseFloat(e.target.value) || 0)}
            />
            {errores.quantity && <span className="unf__error">{errores.quantity}</span>}
          </div>

          <div className="unf__actions">
            <Button variant="secondary" type="button" onClick={manejarCierre}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {unidadEnEdicion ? "Guardar cambios" : "Crear unidad"}
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
