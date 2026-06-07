import { JSX, useState, useEffect } from "react";
import React from "react";
import Layout from "../components/Layout";
import Table, { ColumnDef } from "../components/Table";
import Modal from "../components/Modal";
import Button from "../components/Button";
import Badge from "../components/Badge";
import { apiFetch } from "../utils/api";
import "./Providers.css";
import { useReportDownload } from "../hooks/useReportDownload";

// ─── Interfaces ───────────────────────────────────────────────────────────────

type ProviderStatus = "active" | "inactive";

interface ProviderContact {
  id: number;
  token: string;
  provider_id: number;
  name: string;
  email: string | null;
  phone: string | null;
  notes: string | null;
  created_at: string;
  created_by: number | null;
  updated_at: string | null;
  updated_by: number | null;
  deleted_at: string | null;
  deleted_by: number | null;
}

interface Provider {
  id: number;
  token: string;
  company: string;
  nit: string;
  email: string;
  status: ProviderStatus;
  created_at: string;
  contacts: ProviderContact[];
}

interface ProviderForm {
  company: string;
  nit: string;
  email: string;
}

interface ContactForm {
  name: string;
  email: string;
  phone: string;
  notes: string;
}

type ProviderFormErrors = Partial<Record<keyof ProviderForm, string>>;
type ContactFormErrors  = Partial<Record<keyof ContactForm, string>>;

const emptyProviderForm = (): ProviderForm => ({ company: "", nit: "", email: "" });
const emptyContactForm  = (): ContactForm  => ({ name: "", email: "", phone: "", notes: "" });

// ─── Columnas ─────────────────────────────────────────────────────────────────

const columns: ColumnDef<Provider>[] = [
  { key: "id",      header: "ID",      width: "5%"  },
  { key: "company", header: "Empresa", width: "30%" },
  { key: "nit",     header: "NIT",     width: "20%" },
  { key: "email",   header: "Email",   width: "30%" },
  {
    key: "status",
    header: "Estado",
    width: "10%",
    render: (row) => (
      <Badge
        label={row.status === "active" ? "Activo" : "Inactivo"}
        variant={row.status === "active" ? "active" : "inactive"}
      />
    ),
  },
];

// ─── Página ───────────────────────────────────────────────────────────────────

export default function Providers(): JSX.Element {
  const [providers, setProviders]             = useState<Provider[]>([]);
  const [loading, setLoading]                 = useState(true);

  // Modal proveedor
  const [providerModalOpen, setProviderModalOpen] = useState(false);
  const [editTarget, setEditTarget]               = useState<Provider | null>(null);
  const [providerForm, setProviderForm]           = useState<ProviderForm>(emptyProviderForm());
  const [providerErrors, setProviderErrors]       = useState<ProviderFormErrors>({});

  // Modal detalle (con contactos)
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [detailProvider, setDetailProvider]   = useState<Provider | null>(null);

  // Modal contacto
  const [contactModalOpen, setContactModalOpen] = useState(false);
  const [editContact, setEditContact]           = useState<ProviderContact | null>(null);
  const [contactForm, setContactForm]           = useState<ContactForm>(emptyContactForm());
  const [contactErrors, setContactErrors]       = useState<ContactFormErrors>({});

  const { download: downloadReport, loading: reportLoading } = useReportDownload("providers");

  // ── Cargar proveedores ─────────────────────────────────────────────────────
  useEffect(() => {
    const fetchProviders = async () => {
      try {
        const response = await apiFetch("/providers/");
        if (!response.ok) throw new Error("Error al cargar proveedores");
        const data: Provider[] = await response.json();
        setProviders(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProviders();
  }, []);

  // ── Refrescar un proveedor individual ─────────────────────────────────────
  const refreshProvider = async (id: number): Promise<Provider | null> => {
    try {
      const res = await apiFetch(`/providers/${id}`);
      if (!res.ok) return null;
      const updated: Provider = await res.json();
      setProviders((prev) => prev.map((p) => (p.id === id ? updated : p)));
      return updated;
    } catch {
      return null;
    }
  };

  // ══════════════════════════════════════════════════════════════════════════
  // PROVEEDOR — handlers
  // ══════════════════════════════════════════════════════════════════════════

  const handleCrearProveedor = () => {
    setEditTarget(null);
    setProviderForm(emptyProviderForm());
    setProviderErrors({});
    setProviderModalOpen(true);
  };

  const handleEditarProveedor = (provider: Provider) => {
    setEditTarget(provider);
    setProviderForm({ company: provider.company, nit: provider.nit, email: provider.email });
    setProviderErrors({});
    setProviderModalOpen(true);
  };

  const handleCerrarProviderModal = () => {
    setProviderModalOpen(false);
    setEditTarget(null);
    setProviderForm(emptyProviderForm());
  };

  const setProviderField = (field: keyof ProviderForm, value: string) => {
    setProviderForm((prev) => ({ ...prev, [field]: value }));
    setProviderErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validateProvider = (): boolean => {
    const e: ProviderFormErrors = {};
    if (!providerForm.company.trim()) e.company = "El nombre de la empresa es requerido";
    if (!providerForm.nit.trim())     e.nit     = "El NIT es requerido";
    if (!providerForm.email.trim())   e.email   = "El email es requerido";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(providerForm.email))
      e.email = "El email no es válido";
    setProviderErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmitProvider = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateProvider()) return;

    try {
      if (editTarget) {
        const response = await apiFetch(`/providers/${editTarget.id}`, {
          method: "PATCH",
          body: JSON.stringify(providerForm),
        });
        if (!response.ok) {
          const err = await response.json();
          alert(err.detail || "Error al actualizar proveedor");
          return;
        }
        const updated: Provider = await response.json();
        setProviders((prev) => prev.map((p) => (p.id === editTarget.id ? updated : p)));
        // Actualizar detailProvider si está abierto
        if (detailProvider?.id === editTarget.id) setDetailProvider(updated);
      } else {
        const response = await apiFetch("/providers/", {
          method: "POST",
          body: JSON.stringify(providerForm),
        });
        if (!response.ok) {
          const err = await response.json();
          alert(err.detail || "Error al crear proveedor");
          return;
        }
        const created: Provider = await response.json();
        setProviders((prev) => [...prev, created]);
      }
      handleCerrarProviderModal();
    } catch {
      alert("Error de conexión con el servidor.");
    }
  };

  const handleEliminarProveedor = async (id: number) => {
    if (!window.confirm("¿Estás seguro de que deseas desactivar este proveedor?")) return;
    try {
      const response = await apiFetch(`/providers/${id}`, { method: "DELETE" });
      if (!response.ok) {
        const err = await response.json();
        alert(err.detail || "Error al desactivar proveedor");
        return;
      }
      setProviders((prev) =>
        prev.map((p) => (p.id === id ? { ...p, status: "inactive" as ProviderStatus } : p))
      );
    } catch {
      alert("Error de conexión con el servidor.");
    }
  };

  // ══════════════════════════════════════════════════════════════════════════
  // DETALLE — handlers
  // ══════════════════════════════════════════════════════════════════════════

  const handleVerDetalle = (provider: Provider) => {
    setDetailProvider(provider);
    setDetailModalOpen(true);
  };

  const handleCerrarDetalle = () => {
    setDetailModalOpen(false);
    setDetailProvider(null);
  };

  // ══════════════════════════════════════════════════════════════════════════
  // CONTACTO — handlers
  // ══════════════════════════════════════════════════════════════════════════

  const handleCrearContacto = () => {
    setEditContact(null);
    setContactForm(emptyContactForm());
    setContactErrors({});
    setContactModalOpen(true);
  };

  const handleEditarContacto = (contact: ProviderContact) => {
    setEditContact(contact);
    setContactForm({
      name:  contact.name,
      email: contact.email  ?? "",
      phone: contact.phone  ?? "",
      notes: contact.notes  ?? "",
    });
    setContactErrors({});
    setContactModalOpen(true);
  };

  const handleCerrarContactModal = () => {
    setContactModalOpen(false);
    setEditContact(null);
    setContactForm(emptyContactForm());
  };

  const setContactField = (field: keyof ContactForm, value: string) => {
    setContactForm((prev) => ({ ...prev, [field]: value }));
    setContactErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validateContact = (): boolean => {
    const e: ContactFormErrors = {};
    if (!contactForm.name.trim()) e.name = "El nombre del contacto es requerido";
    if (contactForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contactForm.email))
      e.email = "El email no es válido";
    setContactErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmitContact = async (ev: React.FormEvent) => {
    ev.preventDefault();
    if (!validateContact() || !detailProvider) return;

    const body = {
      name:  contactForm.name,
      email: contactForm.email  || null,
      phone: contactForm.phone  || null,
      notes: contactForm.notes  || null,
    };

    try {
      if (editContact) {
        const response = await apiFetch(
          `/providers/${detailProvider.id}/contacts/${editContact.id}`,
          { method: "PATCH", body: JSON.stringify(body) }
        );
        if (!response.ok) {
          const err = await response.json();
          alert(err.detail || "Error al actualizar contacto");
          return;
        }
      } else {
        const response = await apiFetch(
          `/providers/${detailProvider.id}/contacts/`,
          { method: "POST", body: JSON.stringify(body) }
        );
        if (!response.ok) {
          const err = await response.json();
          alert(err.detail || "Error al crear contacto");
          return;
        }
      }

      const updated = await refreshProvider(detailProvider.id);
      if (updated) setDetailProvider(updated);
      handleCerrarContactModal();
    } catch {
      alert("Error de conexión con el servidor.");
    }
  };

  const handleEliminarContacto = async (contact: ProviderContact) => {
    if (!detailProvider) return;
    if (!window.confirm(`¿Eliminar el contacto "${contact.name}"?`)) return;
    try {
      const response = await apiFetch(
        `/providers/${detailProvider.id}/contacts/${contact.id}`,
        { method: "DELETE" }
      );
      if (!response.ok) {
        const err = await response.json();
        alert(err.detail || "Error al eliminar contacto");
        return;
      }
      const updated = await refreshProvider(detailProvider.id);
      if (updated) setDetailProvider(updated);
    } catch {
      alert("Error de conexión con el servidor.");
    }
  };

  // ── Contactos activos ──────────────────────────────────────────────────────
  const activeContacts = detailProvider?.contacts.filter((c) => !c.deleted_at) ?? [];

  // ─── Render ────────────────────────────────────────────────────────────────
  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Proveedores" },
      ]}
    >
      {loading ? (
        <div className="saip-loading">Cargando proveedores...</div>
      ) : (
        <Table
          title="Gestión de proveedores"
          columns={columns}
          data={providers}
          searchPlaceholder="Buscar proveedor"
          sortKey="company"
          headerActions={
            <>
              <Button variant="primary" onClick={handleCrearProveedor}>
                Crear proveedor
              </Button>
              <Button
                variant="secondary"
                onClick={downloadReport}
                disabled={reportLoading}
                icon={
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round">
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
              {/* Ver detalle / contactos */}
              <button
                type="button"
                className="saip-table__action-btn"
                title="Ver detalle"
                onClick={() => handleVerDetalle(row)}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="1.8">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>

              {/* Editar */}
              <button
                type="button"
                className="saip-table__action-btn"
                title="Editar"
                onClick={() => handleEditarProveedor(row)}
                disabled={row.status === "inactive"}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="1.8">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>

              {/* Eliminar */}
              <button
                type="button"
                className="saip-table__action-btn saip-table__action-btn--danger"
                title="Desactivar"
                onClick={() => handleEliminarProveedor(row.id)}
                disabled={row.status === "inactive"}
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

      {/* ══════════════════════════════════════════════════════════════════
          MODAL — Crear / Editar Proveedor
      ══════════════════════════════════════════════════════════════════ */}
      <Modal
        isOpen={providerModalOpen}
        onClose={handleCerrarProviderModal}
        title={editTarget ? "Editar proveedor" : "Crear proveedor"}
        width="460px"
      >
        <form className="crf" onSubmit={handleSubmitProvider}>
          <div className="crf__group">
            <label className="crf__label">
              Empresa<span className="crf__required">*</span>
            </label>
            <input
              className={`crf__input ${providerErrors.company ? "crf__input--error" : ""}`}
              placeholder="Ej: Distribuidora Nacional S.A."
              value={providerForm.company}
              onChange={(e) => setProviderField("company", e.target.value)}
            />
            {providerErrors.company && (
              <span className="crf__error">{providerErrors.company}</span>
            )}
          </div>

          <div className="crf__group">
            <label className="crf__label">
              NIT<span className="crf__required">*</span>
            </label>
            <input
              className={`crf__input ${providerErrors.nit ? "crf__input--error" : ""}`}
              placeholder="Ej: 900123456-7"
              value={providerForm.nit}
              onChange={(e) => setProviderField("nit", e.target.value)}
            />
            {providerErrors.nit && (
              <span className="crf__error">{providerErrors.nit}</span>
            )}
          </div>

          <div className="crf__group">
            <label className="crf__label">
              Email<span className="crf__required">*</span>
            </label>
            <input
              type="email"
              className={`crf__input ${providerErrors.email ? "crf__input--error" : ""}`}
              placeholder="Ej: contacto@empresa.com"
              value={providerForm.email}
              onChange={(e) => setProviderField("email", e.target.value)}
            />
            {providerErrors.email && (
              <span className="crf__error">{providerErrors.email}</span>
            )}
          </div>

          <div className="crf__actions">
            <Button variant="secondary" type="button" onClick={handleCerrarProviderModal}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {editTarget ? "Guardar cambios" : "Crear proveedor"}
            </Button>
          </div>
        </form>
      </Modal>

      {/* ══════════════════════════════════════════════════════════════════
          MODAL — Detalle del proveedor + Contactos
      ══════════════════════════════════════════════════════════════════ */}
      <Modal
        isOpen={detailModalOpen}
        onClose={handleCerrarDetalle}
        title={detailProvider?.company ?? "Detalle del proveedor"}
        width="560px"
      >
        {detailProvider && (
          <div className="prd">
            {/* Info básica */}
            <div className="prd__info">
              <div className="prd__info-item">
                <span className="prd__info-label">NIT</span>
                <span className="prd__info-value">{detailProvider.nit}</span>
              </div>
              <div className="prd__info-item">
                <span className="prd__info-label">Email</span>
                <span className="prd__info-value">{detailProvider.email}</span>
              </div>
              <div className="prd__info-item">
                <span className="prd__info-label">Estado</span>
                <Badge
                  label={detailProvider.status === "active" ? "Activo" : "Inactivo"}
                  variant={detailProvider.status === "active" ? "active" : "inactive"}
                />
              </div>
            </div>

            {/* Sección contactos */}
            <div className="prd__contacts-header">
              <span className="prd__contacts-title">
                Contactos
                {activeContacts.length > 0 && (
                  <span className="prd__contacts-count">{activeContacts.length}</span>
                )}
              </span>
              {detailProvider.status === "active" && (
                <button
                  type="button"
                  className="prd__add-contact-btn"
                  onClick={handleCrearContacto}
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="2.5">
                    <line x1="12" y1="5" x2="12" y2="19"/>
                    <line x1="5" y1="12" x2="19" y2="12"/>
                  </svg>
                  Agregar contacto
                </button>
              )}
            </div>

            {activeContacts.length === 0 ? (
              <div className="prd__contacts-empty">
                No hay contactos registrados para este proveedor.
              </div>
            ) : (
              <div className="prd__contacts-list">
                {activeContacts.map((contact) => (
                  <div key={contact.id} className="prd__contact-card">
                    <div className="prd__contact-main">
                      <span className="prd__contact-name">{contact.name}</span>
                      <div className="prd__contact-actions">
                        <button
                          type="button"
                          className="saip-table__action-btn"
                          title="Editar contacto"
                          onClick={() => handleEditarContacto(contact)}
                        >
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" strokeWidth="1.8">
                            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                          </svg>
                        </button>
                        <button
                          type="button"
                          className="saip-table__action-btn saip-table__action-btn--danger"
                          title="Eliminar contacto"
                          onClick={() => handleEliminarContacto(contact)}
                        >
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" strokeWidth="1.8">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
                            <path d="M10 11v6M14 11v6"/>
                            <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                    <div className="prd__contact-meta">
                      {contact.email && (
                        <span className="prd__contact-meta-item">
                          <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" strokeWidth="2">
                            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                            <polyline points="22,6 12,13 2,6"/>
                          </svg>
                          {contact.email}
                        </span>
                      )}
                      {contact.phone && (
                        <span className="prd__contact-meta-item">
                          <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" strokeWidth="2">
                            <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.8 19.79 19.79 0 01.01 1.18 2 2 0 012 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 7.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 14.92z"/>
                          </svg>
                          {contact.phone}
                        </span>
                      )}
                      {contact.notes && (
                        <span className="prd__contact-notes">{contact.notes}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* ══════════════════════════════════════════════════════════════════
          MODAL — Crear / Editar Contacto
      ══════════════════════════════════════════════════════════════════ */}
      <Modal
        isOpen={contactModalOpen}
        onClose={handleCerrarContactModal}
        title={editContact ? "Editar contacto" : "Agregar contacto"}
        width="440px"
      >
        <form className="crf" onSubmit={handleSubmitContact}>
          <div className="crf__group">
            <label className="crf__label">
              Nombre<span className="crf__required">*</span>
            </label>
            <input
              className={`crf__input ${contactErrors.name ? "crf__input--error" : ""}`}
              placeholder="Ej: Juan Pérez"
              value={contactForm.name}
              onChange={(e) => setContactField("name", e.target.value)}
            />
            {contactErrors.name && (
              <span className="crf__error">{contactErrors.name}</span>
            )}
          </div>

          <div className="crf__group">
            <label className="crf__label">Email</label>
            <input
              type="email"
              className={`crf__input ${contactErrors.email ? "crf__input--error" : ""}`}
              placeholder="Ej: juan@empresa.com"
              value={contactForm.email}
              onChange={(e) => setContactField("email", e.target.value)}
            />
            {contactErrors.email && (
              <span className="crf__error">{contactErrors.email}</span>
            )}
          </div>

          <div className="crf__group">
            <label className="crf__label">Teléfono</label>
            <input
              className="crf__input"
              placeholder="Ej: +57 300 123 4567"
              value={contactForm.phone}
              onChange={(e) => setContactField("phone", e.target.value)}
            />
          </div>

          <div className="crf__group">
            <label className="crf__label">Notas</label>
            <textarea
              className="crf__textarea"
              placeholder="Información adicional sobre el contacto…"
              rows={3}
              value={contactForm.notes}
              onChange={(e) => setContactField("notes", e.target.value)}
            />
          </div>

          <div className="crf__actions">
            <Button variant="secondary" type="button" onClick={handleCerrarContactModal}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {editContact ? "Guardar cambios" : "Agregar contacto"}
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
