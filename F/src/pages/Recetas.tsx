import { JSX, useState } from "react";
import React from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import Badge from "../components/Badge";
import Detallemodal from "../components/Detallemodal";
import "./Recetas.css";

// ─── Mock data ────────────────────────────────────────────────────────────────
const INSUMOS_MOCK = [
  { id: 1,  nombre: "Harina de trigo",  unidad: "kg" },
  { id: 2,  nombre: "Azúcar",           unidad: "kg" },
  { id: 3,  nombre: "Huevos",           unidad: "unidad" },
  { id: 4,  nombre: "Mantequilla",      unidad: "kg" },
  { id: 5,  nombre: "Leche",            unidad: "L" },
  { id: 6,  nombre: "Levadura",         unidad: "g" },
  { id: 7,  nombre: "Sal",              unidad: "g" },
  { id: 8,  nombre: "Cacao en polvo",   unidad: "g" },
  { id: 9,  nombre: "Vainilla",         unidad: "ml" },
  { id: 10, nombre: "Polvo de hornear", unidad: "g" },
];

// ─── Interfaces ───────────────────────────────────────────────────────────────
interface Ingrediente {
  insumo_id: number;
  nombre: string;
  cantidad: number;
  unidad: string;
}

interface Receta {
  id: number;
  nombre: string;
  descripcion?: string | null;
  ingredientes: Ingrediente[];
  estado: "activa" | "inactiva";
  created_at: string;
}

interface Insumo {
  id: number;
  nombre: string;
  unidad: string;
}

interface IngredienteForm {
  insumo_id: string;
  cantidad: string;
  unidad: string;
}

interface RecetaForm {
  nombre: string;
  descripcion: string;
  estado: "activa" | "inactiva";
  ingredientes: IngredienteForm[];
}

type FormErrors = Partial<Record<keyof RecetaForm | "ingredientes_list", string>>;

const RECETAS_INICIALES: Receta[] = [
  {
    id: 1,
    nombre: "Pan de chocolate",
    descripcion: "Pan esponjoso con sabor intenso a cacao, ideal para el desayuno.",
    estado: "activa",
    created_at: "2024-01-15",
    ingredientes: [
      { insumo_id: 1, nombre: "Harina de trigo", cantidad: 0.5,  unidad: "kg" },
      { insumo_id: 2, nombre: "Azúcar",          cantidad: 0.2,  unidad: "kg" },
      { insumo_id: 8, nombre: "Cacao en polvo",  cantidad: 50,   unidad: "g" },
      { insumo_id: 3, nombre: "Huevos",          cantidad: 2,    unidad: "unidad" },
      { insumo_id: 5, nombre: "Leche",           cantidad: 0.25, unidad: "L" },
    ],
  },
  {
    id: 2,
    nombre: "Croissant clásico",
    descripcion: "Croissant hojaldrado y mantequilloso de preparación artesanal.",
    estado: "activa",
    created_at: "2024-02-10",
    ingredientes: [
      { insumo_id: 1, nombre: "Harina de trigo", cantidad: 1,   unidad: "kg" },
      { insumo_id: 4, nombre: "Mantequilla",     cantidad: 0.3, unidad: "kg" },
      { insumo_id: 6, nombre: "Levadura",        cantidad: 20,  unidad: "g" },
      { insumo_id: 7, nombre: "Sal",             cantidad: 15,  unidad: "g" },
      { insumo_id: 5, nombre: "Leche",           cantidad: 0.3, unidad: "L" },
    ],
  },
  {
    id: 3,
    nombre: "Torta de vainilla",
    descripcion: "Torta suave y esponjosa con aroma a vainilla.",
    estado: "inactiva",
    created_at: "2024-03-05",
    ingredientes: [
      { insumo_id: 1,  nombre: "Harina de trigo",  cantidad: 0.4,  unidad: "kg" },
      { insumo_id: 2,  nombre: "Azúcar",            cantidad: 0.25, unidad: "kg" },
      { insumo_id: 3,  nombre: "Huevos",            cantidad: 3,    unidad: "unidad" },
      { insumo_id: 9,  nombre: "Vainilla",          cantidad: 10,   unidad: "ml" },
      { insumo_id: 10, nombre: "Polvo de hornear",  cantidad: 8,    unidad: "g" },
    ],
  },
];

const emptyIngrediente = (): IngredienteForm => ({
  insumo_id: "",
  cantidad: "",
  unidad: "",
});

const emptyForm = (): RecetaForm => ({
  nombre: "",
  descripcion: "",
  estado: "activa",
  ingredientes: [emptyIngrediente()],
});

// ─── Columnas ─────────────────────────────────────────────────────────────────
const columns: ColumnDef<Receta>[] = [
  { key: "id",          header: "ID",            width: "5%" },
  { key: "nombre",      header: "Nombre",        width: "22%" },
  { key: "descripcion", header: "Descripción",   width: "32%" },
  {
    key: "ingredientes",
    header: "# Ingredientes",
    width: "15%",
    render: (row) => (
      <span className="rcf__badge-count">{row.ingredientes.length}</span>
    ),
  },
  {
    key: "estado",
    header: "Estado",
    width: "12%",
    render: (row) => (
      <Badge
        label={row.estado === "activa" ? "Activa" : "Inactiva"}
        variant={row.estado === "activa" ? "active" : "inactive"}
      />
    ),
  },
];

// ─── Página ───────────────────────────────────────────────────────────────────
export default function Recetas(): JSX.Element {
  const [recetas, setRecetas]       = useState<Receta[]>(RECETAS_INICIALES);
  const insumos: Insumo[]           = INSUMOS_MOCK;
  const [modalOpen, setModalOpen]   = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Receta | null>(null);
  const [viewTarget, setViewTarget] = useState<Receta | null>(null);
  const [form, setForm]             = useState<RecetaForm>(emptyForm());
  const [errors, setErrors]         = useState<FormErrors>({});

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleCrear = () => {
    setEditTarget(null);
    setForm(emptyForm());
    setErrors({});
    setModalOpen(true);
  };

  const handleEditar = (receta: Receta) => {
    setDetailOpen(false);
    setEditTarget(receta);
    setForm({
      nombre:      receta.nombre,
      descripcion: receta.descripcion ?? "",
      estado:      receta.estado,
      ingredientes: receta.ingredientes.length
        ? receta.ingredientes.map((ing) => ({
            insumo_id: String(ing.insumo_id),
            cantidad:  String(ing.cantidad),
            unidad:    ing.unidad,
          }))
        : [emptyIngrediente()],
    });
    setErrors({});
    setModalOpen(true);
  };

  const handleVerDetalle = (receta: Receta) => {
    setViewTarget(receta);
    setDetailOpen(true);
  };

  const handleCerrar = () => {
    setModalOpen(false);
    setDetailOpen(false);
    setEditTarget(null);
    setViewTarget(null);
    setForm(emptyForm());
  };

  // ── Ingredientes dinámicos ────────────────────────────────────────────────
  const setIngredienteField = (
    index: number,
    field: keyof IngredienteForm,
    value: string
  ) => {
    setForm((prev) => {
      const updated = [...prev.ingredientes];
      updated[index] = { ...updated[index], [field]: value };
      if (field === "insumo_id") {
        const insumo = insumos.find((i) => String(i.id) === value);
        if (insumo) updated[index].unidad = insumo.unidad;
      }
      return { ...prev, ingredientes: updated };
    });
    setErrors((prev) => ({ ...prev, ingredientes_list: undefined }));
  };

  const addIngrediente = () =>
    setForm((prev) => ({
      ...prev,
      ingredientes: [...prev.ingredientes, emptyIngrediente()],
    }));

  const removeIngrediente = (index: number) =>
    setForm((prev) => ({
      ...prev,
      ingredientes: prev.ingredientes.filter((_, i) => i !== index),
    }));

  // ── Formulario ────────────────────────────────────────────────────────────
  const setField = (field: keyof RecetaForm, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (!form.nombre.trim()) e.nombre = "El nombre es requerido";
    const ingValidos = form.ingredientes.every(
      (ing) => ing.insumo_id && ing.cantidad && Number(ing.cantidad) > 0
    );
    if (form.ingredientes.length === 0 || !ingValidos)
      e.ingredientes_list = "Agrega al menos un ingrediente con cantidad válida";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const buildIngredientes = (): Ingrediente[] =>
    form.ingredientes.map((ing) => {
      const insumo = insumos.find((i) => String(i.id) === ing.insumo_id);
      return {
        insumo_id: Number(ing.insumo_id),
        nombre:    insumo?.nombre ?? "",
        cantidad:  Number(ing.cantidad),
        unidad:    ing.unidad,
      };
    });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    if (editTarget) {
      setRecetas((prev) =>
        prev.map((r) =>
          r.id === editTarget.id
            ? {
                ...editTarget,
                nombre:       form.nombre,
                descripcion:  form.descripcion || null,
                estado:       form.estado,
                ingredientes: buildIngredientes(),
              }
            : r
        )
      );
    } else {
      const newId =
        recetas.length > 0 ? Math.max(...recetas.map((r) => r.id)) + 1 : 1;
      setRecetas((prev) => [
        ...prev,
        {
          id:           newId,
          nombre:       form.nombre,
          descripcion:  form.descripcion || null,
          estado:       form.estado,
          ingredientes: buildIngredientes(),
          created_at:   new Date().toISOString().split("T")[0],
        },
      ]);
    }
    handleCerrar();
  };

  const handleEliminar = (id: number) => {
    if (!window.confirm("¿Estás seguro de que deseas eliminar esta receta?")) return;
    setRecetas((prev) => prev.filter((r) => r.id !== id));
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Gestión de recetas" },
      ]}
    >
      <Table
        sortKey="nombre"
        title="Gestión de recetas"
        columns={columns}
        data={recetas}
        searchPlaceholder="Buscar receta"
        headerActions={
          <Button variant="primary" onClick={handleCrear}>
            Crear receta
          </Button>
        }
        renderActions={(row) => (
          <div className="saip-table__actions">
            <button
              className="saip-table__action-btn"
              title="Ver detalle"
              onClick={() => handleVerDetalle(row)}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="1.8">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            </button>
            <button
              className="saip-table__action-btn"
              title="Editar"
              onClick={() => handleEditar(row)}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="1.8">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
              </svg>
            </button>
            <button
              className="saip-table__action-btn saip-table__action-btn--danger"
              title="Eliminar"
              onClick={() => handleEliminar(row.id)}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="1.8">
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" />
                <path d="M10 11v6M14 11v6" />
                <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" />
              </svg>
            </button>
          </div>
        )}
      />

      {/* ── MODAL CREAR / EDITAR ──────────────────────────────────────────── */}
      <Modal
        isOpen={modalOpen}
        onClose={handleCerrar}
        title={editTarget ? "Editar receta" : "Crear receta"}
        width="580px"
      >
        <form className="rcf" onSubmit={handleSubmit}>
          <div className="rcf__group">
            <label className="rcf__label">
              Nombre <span className="rcf__required">*</span>
            </label>
            <input
              className={`rcf__input ${errors.nombre ? "rcf__input--error" : ""}`}
              placeholder="Ej: Pan de chocolate"
              value={form.nombre}
              onChange={(e) => setField("nombre", e.target.value)}
            />
            {errors.nombre && <span className="rcf__error">{errors.nombre}</span>}
          </div>

          <div className="rcf__group">
            <label className="rcf__label">Descripción</label>
            <textarea
              className="rcf__textarea"
              placeholder="Describe brevemente la receta..."
              rows={2}
              value={form.descripcion}
              onChange={(e) => setField("descripcion", e.target.value)}
            />
          </div>

          <div className="rcf__group">
            <label className="rcf__label">Estado</label>
            <select
              className="rcf__select"
              value={form.estado}
              onChange={(e) =>
                setField("estado", e.target.value as "activa" | "inactiva")
              }
            >
              <option value="activa">Activa</option>
              <option value="inactiva">Inactiva</option>
            </select>
          </div>

          <div className="rcf__group">
            <div className="rcf__ing-header">
              <label className="rcf__label">
                Ingredientes <span className="rcf__required">*</span>
              </label>
              <button
                type="button"
                className="rcf__add-ing-btn"
                onClick={addIngrediente}
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="2.5">
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Agregar
              </button>
            </div>

            <div className="rcf__ing-list">
              <div className="rcf__ing-cols-header">
                <span>Insumo</span>
                <span>Cantidad</span>
                <span>Unidad</span>
                <span></span>
              </div>

              {form.ingredientes.map((ing, idx) => (
                <div key={idx} className="rcf__ing-row">
                  <select
                    className="rcf__select rcf__select--sm"
                    value={ing.insumo_id}
                    onChange={(e) =>
                      setIngredienteField(idx, "insumo_id", e.target.value)
                    }
                  >
                    <option value="">Seleccionar…</option>
                    {insumos.map((ins) => (
                      <option key={ins.id} value={String(ins.id)}>
                        {ins.nombre}
                      </option>
                    ))}
                  </select>

                  <input
                    className="rcf__input rcf__input--sm"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="0"
                    value={ing.cantidad}
                    onChange={(e) =>
                      setIngredienteField(idx, "cantidad", e.target.value)
                    }
                  />

                  <input
                    className="rcf__input rcf__input--sm rcf__input--unit"
                    placeholder="kg, g, L…"
                    value={ing.unidad}
                    readOnly={!!ing.insumo_id}
                    onChange={(e) =>
                      setIngredienteField(idx, "unidad", e.target.value)
                    }
                  />

                  <button
                    type="button"
                    className="rcf__remove-ing-btn"
                    onClick={() => removeIngrediente(idx)}
                    disabled={form.ingredientes.length === 1}
                    title="Eliminar ingrediente"
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" strokeWidth="2.5">
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>

            {errors.ingredientes_list && (
              <span className="rcf__error">{errors.ingredientes_list}</span>
            )}
          </div>

          <div className="rcf__actions">
            <Button variant="secondary" type="button" onClick={handleCerrar}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {editTarget ? "Guardar cambios" : "Crear receta"}
            </Button>
          </div>
        </form>
      </Modal>

      {/* ── DETALLE — componente genérico ─────────────────────────────────── */}
      <Detallemodal
        isOpen={detailOpen}
        onClose={handleCerrar}
        titulo={viewTarget?.nombre ?? ""}
        estado={
          viewTarget
            ? {
                label:   viewTarget.estado === "activa" ? "Activa" : "Inactiva",
                variant: viewTarget.estado === "activa" ? "active" : "inactive",
              }
            : undefined
        }
        descripcion={viewTarget?.descripcion}
        itemsLabel="Ingredientes"
        items={viewTarget?.ingredientes.map((ing) => ({
          nombre:  ing.nombre,
          detalle: `${ing.cantidad} ${ing.unidad}`,
        }))}
        accionLabel="Editar receta"
        onAccion={() => viewTarget && handleEditar(viewTarget)}
      />
    </Layout>
  );
}