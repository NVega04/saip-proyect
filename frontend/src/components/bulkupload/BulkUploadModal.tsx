import { useState, useEffect } from "react";
import React from "react";
import Modal from "../modal/Modal";
import Button from "../button/Button";
import { useAlert } from "../../context/AlertContext";
import { apiFetch } from "../../utils/api";
import "./BulkUploadModal.css";

interface BulkErrorRow {
  fila: number;
  mensaje: string;
}

interface BulkResult {
  total: number;
  creados: number;
  actualizados: number;
  errores: BulkErrorRow[];
}

interface BulkUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  templateUrl: string;
  importUrl: string;
  importQuery?: string;
  onImported?: () => void;
}

export default function BulkUploadModal({
  isOpen,
  onClose,
  title,
  templateUrl,
  importUrl,
  importQuery,
  onImported,
}: BulkUploadModalProps): JSX.Element {
  const { showAlert } = useAlert();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [result, setResult] = useState<BulkResult | null>(null);

  useEffect(() => {
    if (isOpen) {
      setFile(null);
      setResult(null);
    }
  }, [isOpen]);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await apiFetch(templateUrl);
      if (!res.ok) {
        showAlert("error", "No fue posible descargar la plantilla.");
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = templateUrl.split("/").filter(Boolean).pop() ?? "plantilla.xlsx";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      showAlert("error", "No se pudo conectar con el servidor.");
    } finally {
      setDownloading(false);
    }
  };

  const handleImport = async () => {
    if (!file) {
      showAlert("warning", "Seleccione un archivo Excel o CSV.");
      return;
    }
    if (!/\.(xlsx|csv)$/i.test(file.name)) {
      showAlert("error", "Formato no válido. Use .xlsx o .csv.");
      return;
    }

    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    const url = importQuery ? `${importUrl}?${importQuery}` : importUrl;

    try {
      const res = await apiFetch(url, { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) {
        showAlert("error", data?.detail ?? "Error al importar el archivo.");
        return;
      }
      setResult(data as BulkResult);
      if (data.creados > 0 || data.actualizados > 0) {
        showAlert(
          data.errores.length > 0 ? "warning" : "success",
          `Importación completada: ${data.creados} creado(s), ${data.actualizados} actualizado(s), ${data.errores.length} error(es).`
        );
        onImported?.();
      } else {
        showAlert("error", "Ninguna fila se pudo importar. Revise los errores.");
      }
    } catch {
      showAlert("error", "No se pudo conectar con el servidor.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} width="560px">
      <div className="saip-bulk">
        <p className="saip-bulk__hint">
          Cargue un archivo <strong>.xlsx</strong> o <strong>.csv</strong>. Las filas con
          errores se omiten y se muestran al final del proceso.
        </p>

        <div className="saip-bulk__row">
          <label className="saip-bulk__file">
            <input
              type="file"
              accept=".xlsx,.csv"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            <span className="saip-bulk__file-name">
              {file ? file.name : "Seleccionar archivo..."}
            </span>
          </label>

          <Button variant="secondary" onClick={handleDownload} disabled={downloading}>
            {downloading ? "Descargando..." : "Descargar plantilla"}
          </Button>
        </div>

        <div className="saip-bulk__actions">
          <Button variant="secondary" onClick={onClose} disabled={uploading}>
            Cancelar
          </Button>
          <Button variant="primary" onClick={handleImport} disabled={!file || uploading}>
            {uploading ? "Importando..." : "Importar archivo"}
          </Button>
        </div>

        {result && (
          <div className="saip-bulk__result">
            <div className="saip-bulk__summary">
              <span className="saip-bulk__summary-item">
                Total: <strong>{result.total}</strong>
              </span>
              <span className="saip-bulk__summary-item saip-bulk__summary-item--ok">
                Creados: <strong>{result.creados}</strong>
              </span>
              <span className="saip-bulk__summary-item saip-bulk__summary-item--upd">
                Actualizados: <strong>{result.actualizados}</strong>
              </span>
              <span className="saip-bulk__summary-item saip-bulk__summary-item--err">
                Errores: <strong>{result.errores.length}</strong>
              </span>
            </div>

            {result.errores.length > 0 && (
              <div className="saip-bulk__errors">
                {result.errores.map((e) => (
                  <div key={`${e.fila}-${e.mensaje}`} className="saip-bulk__error">
                    <strong>Fila {e.fila}:</strong> {e.mensaje}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Modal>
  );
}