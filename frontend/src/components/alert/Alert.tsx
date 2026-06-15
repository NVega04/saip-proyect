import { useEffect } from "react";
import "./Alert.css";

interface AlertaProps {
  show: boolean;
  type?: "success" | "error" | "warning" | "info";
  message: string;
  duration?: number;
  onClose: () => void;
}

export default function Alerta({
  show,
  type = "info",
  message,
  duration = 3000,
  onClose,
}: AlertaProps) {
  useEffect(() => {
    if (!show) return;

    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [show, duration, onClose]);

  if (!show) return null;

  return (
    <div className={`saip-alerta saip-alerta--${type}`} role="alert">
      <div className="saip-alerta__content">
        <span className="saip-alerta__icon">
          {type === "success" && "✓"}
          {type === "error" && "✕"}
          {type === "warning" && "!"}
          {type === "info" && "i"}
        </span>

        <span className="saip-alerta__message">{message}</span>
      </div>

      <button
        type="button"
        className="saip-alerta__close"
        onClick={onClose}
        aria-label="Cerrar alerta"
      >
        ×
      </button>
    </div>
  );
}