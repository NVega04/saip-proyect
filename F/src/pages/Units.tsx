import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import { useAlert } from "../context/AlertContext";
import { useConfirm } from "../context/ConfirmContext";
import { apiFetch } from "../utils/api";
import "./units.css";

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

const emptyForm = (): UnitForm => ({
  name: "",
  abbreviation: "",
  description: "",
  quantity: 0,
});

const columns: ColumnDef<Unit>[] = [
  { key: "id", header: "ID", width: "5%" },
  { key: "name", header: "Nombre", width: "25%" },
  { key: "abbreviation", header: "Abreviatura", width: "15%" },
  { key: "description", header: "Descripcion", width: "35%" },
  { key: "quantity", header: "Cantidad base", width: "10%" },
];

export default function Units(): JSX.Element {
  const [units, setUnits] = useState<Unit[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Unit | null>(null);
  const [form, setForm] = useState<UnitForm>(emptyForm());
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(true);

  const { showAlert } = useAlert();
  const { showConfirm } = useConfirm();

  useEffect(() => {
    const fetchUnits = async () => {
      try {
        const response = await apiFetch("/units/");
        if (!response.ok) throw new Error("Error al cargar unidades");
        const data: Unit[] = await response.json();
        setUnits(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchUnits();
  }, []);

  const handleCrear = () => {
    setEditTarget(null);
    setForm(emptyForm());
    setErrors({});
    setModalOpen(true);
  };

  const handleEditar = (unit: Unit) => {
    setEditTarget(unit);
    setForm({
      name: unit.name,
      abbreviation: unit.abbreviation,
      description: unit.description ?? "",
      quantity: unit.quantity,
    });
    setErrors({});
    setModalOpen(true);
  };

  const handleCerrar = () => {
    setModalOpen(false);
    setEditTarget(null);
    setForm(emptyForm());
  };

  const setField = (field: keyof UnitForm, value: string | number) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const e: FormErrors = {};
    if (!form.name.trim()) e.name = "El nombre es requerido";
    if (!form.abbreviation.trim()) e.abbreviation = "La abreviatura es requerida";
    if (form.abbreviation.length > 20) e.abbreviation = "Maximo 20 caracteres";
    if (form.quantity < 0) e.quantity = "La cantidad no puede ser negativa";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      showAlert("warning", "Completa los campos obligatorios.");
      return;
    }

    try {
      if (editTarget) {
        const response = await apiFetch(`/units/${editTarget.id}`, {
          method: "PATCH",
          body: JSON.stringify({
            name: form.name,
            abbreviation: form.abbreviation,
            description: form.description || null,
            quantity: form.quantity,
          }),
        });

        if (!response.ok) {
          const err = await response.json();
          showAlert("error", err.detail || "Error al actualizar unidad");
          return;
        }

        const updated: Unit = await response.json();
        setUnits((prev) => prev.map((u) => (u.id === editTarget.id ? updated : u)));
        showAlert("success", "Unidad actualizada correctamente.");
      } else {
        const response = await apiFetch("/units/", {
          method: "POST",
          body: JSON.stringify({
            name: form.name,
            abbreviation: form.abbreviation,
            description: form.description || null,
            quantity: form.quantity,
          }),
        });

        if (!response.ok) {
          const err = await response.json();
          showAlert("error", err.detail || "Error al crear unidad");
          return;
        }

        const created: Unit = await response.json();
        setUnits((prev) => [...prev, created]);
        showAlert("success", "Unidad creada correctamente.");
      }

      handleCerrar();
    } catch {
      showAlert("error", "Error de conexión con el servidor.");
    }
  };

  const handleEliminar = (id: number) => {
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

          setUnits((prev) => prev.filter((u) => u.id !== id));
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
        { label: "Recetas" },
        { label: "Unidades" },
      ]}
    >
      {loading ? (
        <div className="saip-loading">Cargando unidades...</div>
      ) : (
        <Table
          title="Unidades de medida"
          columns={columns}
          data={units}
          searchPlaceholder="Buscar unidad"
          sortKey="name"
          headerActions={
            <Button variant="primary" onClick={handleCrear}>
              Crear unidad
            </Button>
          }
          renderActions={(row) => (
            <div className="saip-table__actions">
              <button
                type="button"
                className="saip-table__action-btn"
                title="Editar"
                onClick={() => handleEditar(row)}
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
                onClick={() => handleEliminar(row.id)}
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
        isOpen={modalOpen}
        onClose={handleCerrar}
        title={editTarget ? "Editar unidad" : "Crear unidad"}
        width="480px"
      >
        <form className="unf" onSubmit={handleSubmit}>
          <div className="unf__group">
            <label className="unf__label">
              Nombre<span className="unf__required">*</span>
            </label>
            <input
              className={`unf__input ${errors.name ? "unf__input--error" : ""}`}
              placeholder="Ej: Kilogramo, Litro..."
              value={form.name}
              onChange={(e) => setField("name", e.target.value)}
            />
            {errors.name && <span className="unf__error">{errors.name}</span>}
          </div>

          <div className="unf__group">
            <label className="unf__label">
              Abreviatura<span className="unf__required">*</span>
            </label>
            <input
              className={`unf__input ${errors.abbreviation ? "unf__input--error" : ""}`}
              placeholder="Ej: kg, L, g..."
              maxLength={20}
              value={form.abbreviation}
              onChange={(e) => setField("abbreviation", e.target.value)}
            />
            {errors.abbreviation && <span className="unf__error">{errors.abbreviation}</span>}
          </div>

          <div className="unf__group">
            <label className="unf__label">Descripcion</label>
            <textarea
              className="unf__textarea"
              placeholder="Describe esta unidad de medida..."
              rows={3}
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
            />
          </div>

          <div className="unf__group">
            <label className="unf__label">
              Cantidad base<span className="unf__required">*</span>
            </label>
            <input
              type="number"
              className={`unf__input ${errors.quantity ? "unf__input--error" : ""}`}
              placeholder="Cantidad base para conversion"
              min={0}
              step={1}
              value={form.quantity}
              onChange={(e) => setField("quantity", parseFloat(e.target.value) || 0)}
            />
            {errors.quantity && <span className="unf__error">{errors.quantity}</span>}
          </div>

          <div className="unf__actions">
            <Button variant="secondary" type="button" onClick={handleCerrar}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {editTarget ? "Guardar cambios" : "Crear unidad"}
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
