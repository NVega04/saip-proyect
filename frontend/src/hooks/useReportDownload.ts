import { useState } from "react";
import { apiFetch, toApiError } from "../utils/api";
import { useAlert } from "../context/AlertContext";

/**
 * Descarga de reportes Excel con estado de carga.
 *
 * Los errores se muestran con el ``AlertContext`` (en lugar del
 * ``alert()`` nativo, que bloquea el hilo y no sigue la interfaz).
 */
export function useReportDownload(entity: string) {
  const [loading, setLoading] = useState(false);
  const { showAlert } = useAlert();

  const download = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`/reports/${entity}`);
      if (!res.ok) {
        const error = await toApiError(res);
        showAlert("error", error.message || "Error al generar el reporte.");
        return;
      }
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `reporte_${entity}_${new Date().toISOString().slice(0, 10)}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      showAlert("error", "No se pudo conectar con el servidor.");
    } finally {
      setLoading(false);
    }
  };

  return { download, loading };
}
