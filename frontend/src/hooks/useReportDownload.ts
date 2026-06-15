import { useState } from "react";
import { apiFetch } from "../utils/api";

export function useReportDownload(entity: string) {
  const [loading, setLoading] = useState(false);

  const download = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`/reports/${entity}`);
      if (!res.ok) { alert("Error al generar el reporte."); return; }
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `reporte_${entity}_${new Date().toISOString().slice(0, 10)}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("No se pudo conectar con el servidor.");
    } finally {
      setLoading(false);
    }
  };

  return { download, loading };
}