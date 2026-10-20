import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../../components/layout/Layout";
import Table, { ColumnDef } from "../../components/table/Table";
import Modal from "../../components/modal/Modal";
import Button from "../../components/button/Button";
import { useAlert } from "../../context/AlertContext";
import { useConfirm } from "../../context/ConfirmContext";
import { apiFetch } from "../../utils/api";
import "./ProductCategories.css";
import { useReportDownload } from "../../hooks/useReportDownload.ts";
import { LONGITUDES_MAX } from "../../constants/validations.constants";
import { validarCampoRequerido, validarLongitudMaxima } from "../../utils/validations";

interface CommercialProductBasic {
  id: number;
  token: string;
  name: string;
  status: string;
}

interface ProductCategory {
  id: number;
  token: string;
  name: string;
  description: string | null;
  status: string;
  created_at: string;
  created_by: number | null;
  updated_at: string | null;
  updated_by: number | null;
  deleted_at: string | null;
  deleted_by: number | null;
  commercial_products: CommercialProductBasic[];
}

interface ProductCategoryForm {
  name: string;
  description: string;
}

type FormErrors = Partial<Record<keyof ProductCategoryForm, string>>;

const crearFormularioVacio = (): ProductCategoryForm => ({
  name: "",
  description: "",
});

const columns: ColumnDef<ProductCategory>[] = [
  { key: "name", header: "Nombre", width: "30%" },
  { key: "description", header: "Descripcion", width: "25%" },
  {
    key: "commercial_products",
    header: "Productos",
    width: "40%",
    render: (row) => (
      <div className="pcat-products-list">
        {row.commercial_products.length === 0 ? (
          <span className="pcat-products-empty">Sin productos</span>
        ) : (
          row.commercial_products.map((p) => (
            <span key={p.id} className="pcat-product-tag">
              {p.name}
            </span>
          ))
        )}
      </div>
    ),
  },
];

/**
 * Valida los campos del formulario de categorías de productos.
 * Devuelve el objeto de errores (vacío si el formulario es válido).
 */
const validarFormulario = (datosFormulario: ProductCategoryForm): FormErrors => {
  const errores: FormErrors = {};

  const nombreRequerido = validarCampoRequerido(datosFormulario.name);
  const nombreDemasiadoLargo = validarLongitudMaxima(datosFormulario.name, LONGITUDES_MAX.name);
  if (nombreRequerido) errores.name = nombreRequerido;
  if (nombreDemasiadoLargo) errores.name = nombreDemasiadoLargo;

  const descripcionDemasiadoLarga = validarLongitudMaxima(
    datosFormulario.description,
    LONGITUDES_MAX.description
  );
  if (descripcionDemasiadoLarga) errores.description = descripcionDemasiadoLarga;

  return errores;
};

/**
 * Construye el cuerpo de la petición enviada al backend
 * a partir de los datos actuales del formulario.
 */
const construirCuerpoPeticion = (datosFormulario: ProductCategoryForm) => ({
  name: datosFormulario.name,
  description: datosFormulario.description || null,
});

export default function ProductCategories(): JSX.Element {
  const [categorias, setCategorias] = useState<ProductCategory[]>([]);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [categoriaEnEdicion, setCategoriaEnEdicion] = useState<ProductCategory | null>(null);
  const [datosFormulario, setDatosFormulario] = useState<ProductCategoryForm>(
    crearFormularioVacio()
  );
  const [errores, setErrores] = useState<FormErrors>({});
  const [cargando, setCargando] = useState(true);

  const { showAlert } = useAlert();
  const { showConfirm } = useConfirm();
  const { download: downloadReport, loading: reportLoading } = useReportDownload("product-categories");

  useEffect(() => {
    const cargarCategorias = async () => {
      try {
        const response = await apiFetch("/product-categories/");
        if (!response.ok) throw new Error("Error al cargar categorias");
        const data: ProductCategory[] = await response.json();
        setCategorias(data.filter((c) => c.status === "active"));
      } catch (err) {
        console.error(err);
      } finally {
        setCargando(false);
      }
    };
    cargarCategorias();
  }, []);

  const manejarCreacion = () => {
    setCategoriaEnEdicion(null);
    setDatosFormulario(crearFormularioVacio());
    setErrores({});
    setModalAbierto(true);
  };

  const manejarEdicion = (categoria: ProductCategory) => {
    setCategoriaEnEdicion(categoria);
    setDatosFormulario({
      name: categoria.name,
      description: categoria.description ?? "",
    });
    setErrores({});
    setModalAbierto(true);
  };

  const manejarCierre = () => {
    setModalAbierto(false);
    setCategoriaEnEdicion(null);
    setDatosFormulario(crearFormularioVacio());
  };

  const actualizarCampo = (campo: keyof ProductCategoryForm, valor: string) => {
    setDatosFormulario((prev) => ({ ...prev, [campo]: valor }));
    setErrores((prev) => ({ ...prev, [campo]: undefined }));
  };

  const validarYConfirmarFormulario = (): boolean => {
    const erroresDetectados = validarFormulario(datosFormulario);
    setErrores(erroresDetectados);
    return Object.keys(erroresDetectados).length === 0;
  };

  const guardarCategoria = async () => {
    const esActualizacion = categoriaEnEdicion !== null;
    const url = esActualizacion
      ? `/product-categories/${categoriaEnEdicion.id}`
      : "/product-categories/";
    const metodo = esActualizacion ? "PUT" : "POST";

    const response = await apiFetch(url, {
      method: metodo,
      body: JSON.stringify(construirCuerpoPeticion(datosFormulario)),
    });

    if (!response.ok) {
      const err = await response.json();
      showAlert(
        "error",
        err.detail ||
          (esActualizacion ? "Error al actualizar categoria" : "Error al crear categoria")
      );
      return;
    }

    const categoriaGuardada: ProductCategory = await response.json();
    if (esActualizacion) {
      setCategorias((prev) =>
        prev.map((c) => (c.id === categoriaEnEdicion.id ? categoriaGuardada : c))
      );
      showAlert("success", "Categoria actualizada correctamente.");
    } else {
      setCategorias((prev) => [...prev, categoriaGuardada]);
      showAlert("success", "Categoria creada correctamente.");
    }
  };

  const manejarEnvio = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validarYConfirmarFormulario()) {
      showAlert("warning", "Completa los campos obligatorios.");
      return;
    }

    try {
      await guardarCategoria();
      manejarCierre();
    } catch {
      showAlert("error", "Error de conexion con el servidor.");
    }
  };

  const manejarEliminacion = (id: number) => {
    showConfirm({
      title: "Eliminar categoria",
      message: "¿Esta seguro que desea eliminar este registro?",
      confirmText: "Eliminar",
      cancelText: "Cancelar",
      onConfirm: async () => {
        try {
          const response = await apiFetch(`/product-categories/${id}`, {
            method: "DELETE",
          });

          if (!response.ok) {
            const err = await response.json();
            showAlert("error", err.detail || "Error al eliminar categoria");
            return;
          }

          setCategorias((prev) => prev.filter((c) => c.id !== id));
          showAlert("success", "Categoria eliminada correctamente.");
        } catch {
          showAlert("error", "Error de conexion con el servidor.");
        }
      },
    });
  };

  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Panaderia" },
        { label: "Categorias de productos" },
      ]}
    >
      {cargando ? (
        <div className="saip-loading">Cargando categorias...</div>
      ) : (
        <Table
          title="Categorias de productos"
          columns={columns}
          data={categorias}
          searchPlaceholder="Buscar categoria"
          sortKey="name"
          headerActions={
            <>
            <Button variant="primary" onClick={manejarCreacion}>
              Crear categoria
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
                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                >
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
              </button>
              <button
                type="button"
                className="saip-table__action-btn saip-table__action-btn--danger"
                title="Eliminar"
                onClick={() => manejarEliminacion(row.id)}
              >
                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                >
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" />
                  <path d="M10 11v6M14 11v6" />
                  <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" />
                </svg>
              </button>
            </div>
          )}
        />
      )}

      <Modal
        isOpen={modalAbierto}
        onClose={manejarCierre}
        title={categoriaEnEdicion ? "Editar categoria" : "Crear categoria"}
        width="480px"
      >
        <form className="pcatf" onSubmit={manejarEnvio}>
          <div className="pcatf__group">
            <label className="pcatf__label">
              Nombre<span className="pcatf__required">*</span>
            </label>
            <input
              className={`pcatf__input ${errores.name ? "pcatf__input--error" : ""}`}
              placeholder="Ej: Lacteos, Gaseosas, Embutidos..."
              maxLength={LONGITUDES_MAX.name}
              value={datosFormulario.name}
              onChange={(e) => actualizarCampo("name", e.target.value)}
            />
            {errores.name && <span className="pcatf__error">{errores.name}</span>}
          </div>

          <div className="pcatf__group">
            <label className="pcatf__label">Descripcion</label>
            <textarea
              className="pcatf__textarea"
              placeholder="Describe esta categoria..."
              rows={3}
              maxLength={LONGITUDES_MAX.description}
              value={datosFormulario.description}
              onChange={(e) => actualizarCampo("description", e.target.value)}
            />
            {errores.description && (
              <span className="pcatf__error">{errores.description}</span>
            )}
          </div>

          <div className="pcatf__actions">
            <Button variant="secondary" type="button" onClick={manejarCierre}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {categoriaEnEdicion ? "Guardar cambios" : "Crear categoria"}
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
