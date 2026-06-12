import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import Badge from "../components/Badge";
import Detallemodal from "../components/Detailmodal";
import { useAlert } from "../context/AlertContext";
import { useConfirm } from "../context/ConfirmContext";
import { apiFetch } from "../utils/api";
import "./Recipes.css";
import { useReportDownload } from "../hooks/useReportDownload.ts";

interface UnitBasic {
  id: number;
  name: string;
  abbreviation: string;
}

interface SupplyBasic {
  id: number;
  token: string;
  name: string;
  status: string;
}

interface RecipeIngredient {
  id: number;
  token: string;
  supply_id: number;
  supply: SupplyBasic;
  quantity: number;
  unit_id: number;
  unit: UnitBasic;
  notes: string | null;
}

interface Recipe {
  id: number;
  token: string;
  name: string;
  description: string | null;
  product_id: number | null;
  yield_quantity: number;
  yield_unit_id: number;
  yield_unit: UnitBasic;
  status: "active" | "inactive";
  ingredients: RecipeIngredient[];
  created_at: string;
}

interface Supply {
  id: number;
  token: string;
  name: string;
  unit_id: number;
  unit: UnitBasic;
  status: string;
}

interface Unit {
  id: number;
  name: string;
  abbreviation: string;
}

interface IngredienteForm {
  supply_id: string;
  quantity: string;
  unit_id: string;
}

interface RecipeForm {
  name: string;
  description: string;
  yield_quantity: string;
  yield_unit_id: string;
  status: "active" | "inactive";
  ingredients: IngredienteForm[];
}

type FormErrors = Partial<Record<keyof RecipeForm | "ingredientes_list", string>>;

const emptyIngrediente = (): IngredienteForm => ({
  supply_id: "",
  quantity: "",
  unit_id: "",
});

const emptyForm = (): RecipeForm => ({
  name: "",
  description: "",
  yield_quantity: "1",
  yield_unit_id: "",
  status: "active",
  ingredients: [emptyIngrediente()],
});

const columns: ColumnDef<Recipe>[] = [
  { key: "id", header: "ID", width: "5%" },
  { key: "name", header: "Nombre", width: "22%" },
  { key: "description", header: "Descripcion", width: "27%" },
  {
    key: "yield_unit",
    header: "Rendimiento",
    width: "12%",
    render: (row) => `${row.yield_quantity} ${row.yield_unit?.abbreviation || ""}`,
  },
  {
    key: "ingredients",
    header: "# Ingredientes",
    width: "12%",
    render: (row) => (
      <span className="rcf__badge-count">{row.ingredients.length}</span>
    ),
  },
  {
    key: "status",
    header: "Estado",
    width: "10%",
    render: (row) => (
      <Badge
        label={row.status === "active" ? "Activa" : "Inactiva"}
        variant={row.status === "active" ? "active" : "inactive"}
      />
    ),
  },
];

export default function Recetas(): JSX.Element {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [supplies, setSupplies] = useState<Supply[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Recipe | null>(null);
  const [viewTarget, setViewTarget] = useState<Recipe | null>(null);
  const [form, setForm] = useState<RecipeForm>(emptyForm());
  const [errors, setErrors] = useState<FormErrors>({});

  const { showAlert } = useAlert();
  const { showConfirm } = useConfirm();
  const { download: downloadReport, loading: reportLoading } = useReportDownload("recipes");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [recRes, supRes, unitRes] = await Promise.all([
          apiFetch("/recipes/"),
          apiFetch("/supplies/"),
          apiFetch("/units/"),
        ]);
        if (recRes.ok) setRecipes(await recRes.json());
        if (supRes.ok) setSupplies(await supRes.json());
        if (unitRes.ok) setUnits(await unitRes.json());
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleCrear = () => {
    setEditTarget(null);
    setForm(emptyForm());
    setErrors({});
    setModalOpen(true);
  };

  const handleEditar = (recipe: Recipe) => {
    setDetailOpen(false);
    setEditTarget(recipe);
    setForm({
      name: recipe.name,
      description: recipe.description ?? "",
      yield_quantity: String(recipe.yield_quantity),
      yield_unit_id: String(recipe.yield_unit_id),
      status: recipe.status,
      ingredients: recipe.ingredients.length
        ? recipe.ingredients.map((ing) => ({
            supply_id: String(ing.supply_id),
            quantity: String(ing.quantity),
            unit_id: String(ing.unit_id),
          }))
        : [emptyIngrediente()],
    });
    setErrors({});
    setModalOpen(true);
  };

  const handleVerDetalle = (recipe: Recipe) => {
    setViewTarget(recipe);
    setDetailOpen(true);
  };

  const handleCerrar = () => {
    setModalOpen(false);
    setDetailOpen(false);
    setEditTarget(null);
    setViewTarget(null);
    setForm(emptyForm());
  };

  const supplyById = (id: string) => supplies.find((s) => String(s.id) === id);

  const setIngredienteField = (
    index: number,
    field: keyof IngredienteForm,
    value: string
  ) => {
    setForm((prev) => {
      const updated = [...prev.ingredients];
      updated[index] = { ...updated[index], [field]: value };
      if (field === "supply_id") {
        const supply = supplies.find((s) => String(s.id) === value);
        if (supply) updated[index].unit_id = String(supply.unit_id);
      }
      return { ...prev, ingredients: updated };
    });
    setErrors((prev) => ({ ...prev, ingredientes_list: undefined }));
  };

  const addIngrediente = () =>
    setForm((prev) => ({
      ...prev,
      ingredients: [...prev.ingredients, emptyIngrediente()],
    }));

  const removeIngrediente = (index: number) =>
    setForm((prev) => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index),
    }));

  const setField = (field: keyof RecipeForm, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (!form.name.trim()) e.name = "El nombre es requerido";
    if (!form.yield_unit_id) e.yield_unit_id = "Selecciona una unidad";
    const ingValidos = form.ingredients.every(
      (ing) => ing.supply_id && ing.quantity && Number(ing.quantity) > 0 && ing.unit_id
    );
    if (form.ingredients.length === 0 || !ingValidos)
      e.ingredientes_list = "Agrega al menos un ingrediente con cantidad valida";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const buildPayload = () => ({
    name: form.name,
    description: form.description || null,
    yield_quantity: parseFloat(form.yield_quantity) || 1,
    yield_unit_id: parseInt(form.yield_unit_id),
    status: form.status,
    ingredients: form.ingredients
      .filter((ing) => ing.supply_id && ing.quantity && Number(ing.quantity) > 0)
      .map((ing) => ({
        supply_id: parseInt(ing.supply_id),
        quantity: parseFloat(ing.quantity),
        unit_id: parseInt(ing.unit_id),
      })),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      showAlert("warning", "Completa los campos obligatorios.");
      return;
    }

    try {
      if (editTarget) {
        const response = await apiFetch(`/recipes/${editTarget.id}`, {
          method: "PATCH",
          body: JSON.stringify(buildPayload()),
        });

        if (!response.ok) {
          const err = await response.json();
          showAlert("error", err.detail || "Error al actualizar receta");
          return;
        }

        const updated: Recipe = await response.json();
        setRecipes((prev) => prev.map((r) => (r.id === editTarget.id ? updated : r)));
        showAlert("success", "Receta actualizada correctamente.");
      } else {
        const response = await apiFetch("/recipes/", {
          method: "POST",
          body: JSON.stringify(buildPayload()),
        });

        if (!response.ok) {
          const err = await response.json();
          showAlert("error", err.detail || "Error al crear receta");
          return;
        }

        const created: Recipe = await response.json();
        setRecipes((prev) => [...prev, created]);
        showAlert("success", "Receta creada correctamente.");
      }

      handleCerrar();
    } catch {
      showAlert("error", "Error de conexion con el servidor.");
    }
  };

  const handleEliminar = (id: number) => {
    showConfirm({
      title: "Eliminar receta",
      message: "¿Esta seguro que desea eliminar este registro?",
      confirmText: "Eliminar",
      cancelText: "Cancelar",
      onConfirm: async () => {
        try {
          const response = await apiFetch(`/recipes/${id}`, { method: "DELETE" });

          if (!response.ok) {
            const err = await response.json();
            showAlert("error", err.detail || "Error al eliminar receta");
            return;
          }

          setRecipes((prev) => prev.filter((r) => r.id !== id));
          showAlert("success", "Receta eliminada correctamente.");
        } catch {
          showAlert("error", "Error de conexion con el servidor.");
        }
      },
    });
  };

  if (loading) {
    return (
      <Layout
        breadcrumbs={[
          { label: "Dashboard", to: "/dashboard" },
          { label: "Produccion" },
          { label: "Recetas" },
        ]}
      >
        <div className="saip-loading">Cargando recetas...</div>
      </Layout>
    );
  }

  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Produccion" },
        { label: "Recetas" },
      ]}
    >
      <Table
        sortKey="name"
        title="Gestion de recetas"
        columns={columns}
        data={recipes}
        searchPlaceholder="Buscar receta"
        headerActions={
          <>
          <Button variant="primary" onClick={handleCrear}>
            Crear receta
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
              className={`rcf__input ${errors.name ? "rcf__input--error" : ""}`}
              placeholder="Ej: Pan de chocolate"
              value={form.name}
              onChange={(e) => setField("name", e.target.value)}
            />
            {errors.name && <span className="rcf__error">{errors.name}</span>}
          </div>

          <div className="rcf__group">
            <label className="rcf__label">Descripcion</label>
            <textarea
              className="rcf__textarea"
              placeholder="Describe brevemente la receta..."
              rows={2}
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
            />
          </div>

          <div className="rcf__row">
            <div className="rcf__group rcf__group--half">
              <label className="rcf__label">Rendimiento</label>
              <input
                type="number"
                className="rcf__input"
                min={0}
                step={0.01}
                placeholder="1"
                value={form.yield_quantity}
                onChange={(e) => setField("yield_quantity", e.target.value)}
              />
            </div>
            <div className="rcf__group rcf__group--half">
              <label className="rcf__label">
                Unidad de rendimiento <span className="rcf__required">*</span>
              </label>
              <select
                className={`rcf__select ${errors.yield_unit_id ? "rcf__input--error" : ""}`}
                value={form.yield_unit_id}
                onChange={(e) => setField("yield_unit_id", e.target.value)}
              >
                <option value="">Selecciona</option>
                {units.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name} ({u.abbreviation})
                  </option>
                ))}
              </select>
              {errors.yield_unit_id && <span className="rcf__error">{errors.yield_unit_id}</span>}
            </div>
          </div>

          <div className="rcf__group">
            <label className="rcf__label">Estado</label>
            <select
              className="rcf__select"
              value={form.status}
              onChange={(e) =>
                setField("status", e.target.value as "active" | "inactive")
              }
            >
              <option value="active">Activa</option>
              <option value="inactive">Inactiva</option>
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

              {form.ingredients.map((ing, idx) => {
                const selSupply = supplyById(ing.supply_id);
                return (
                  <div key={idx} className="rcf__ing-row">
                    <select
                      className="rcf__select rcf__select--sm"
                      value={ing.supply_id}
                      onChange={(e) =>
                        setIngredienteField(idx, "supply_id", e.target.value)
                      }
                    >
                      <option value="">Seleccionar...</option>
                      {supplies
                        .filter((s) => s.status === "active")
                        .map((s) => (
                          <option key={s.id} value={String(s.id)}>
                            {s.name}
                          </option>
                        ))}
                    </select>

                    <input
                      className="rcf__input rcf__input--sm"
                      type="number"
                      min="0"
                      step="0.01"
                      placeholder="0"
                      value={ing.quantity}
                      onChange={(e) =>
                        setIngredienteField(idx, "quantity", e.target.value)
                      }
                    />

                    <input
                      className="rcf__input rcf__input--sm rcf__input--unit"
                      placeholder="kg, g, L..."
                      value={selSupply?.unit?.abbreviation ?? ing.unit_id}
                      readOnly
                    />

                    <button
                      type="button"
                      className="rcf__remove-ing-btn"
                      onClick={() => removeIngrediente(idx)}
                      disabled={form.ingredients.length === 1}
                      title="Eliminar ingrediente"
                    >
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="2.5">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                      </svg>
                    </button>
                  </div>
                );
              })}
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

      <Detallemodal
        isOpen={detailOpen}
        onClose={handleCerrar}
        titulo={viewTarget?.name ?? ""}
        estado={
          viewTarget
            ? {
                label: viewTarget.status === "active" ? "Activa" : "Inactiva",
                variant: viewTarget.status === "active" ? "active" : "inactive",
              }
            : undefined
        }
        descripcion={viewTarget?.description}
        itemsLabel="Ingredientes"
        items={viewTarget?.ingredients.map((ing) => ({
          nombre: ing.supply?.name ?? `Insumo #${ing.supply_id}`,
          detalle: `${ing.quantity} ${ing.unit?.abbreviation || ""}`,
        }))}
        accionLabel="Editar receta"
        onAccion={() => viewTarget && handleEditar(viewTarget)}
      />
    </Layout>
  );
}
