import { useEffect } from "react";
import "./Modal.css";

interface SAIPModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  width?: string;
}

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  width = "480px",
}: SAIPModalProps) {
  // Cierra con Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [isOpen, onClose]);

  // Bloquea scroll del body
  useEffect(() => {
    document.body.style.overflow = isOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="saip-modal__overlay" onClick={onClose}>
      <div
        className="saip-modal__box"
        style={{ width }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="saip-modal__header">
          <h2 className="saip-modal__title">{title}</h2>
          <button className="saip-modal__close" onClick={onClose}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        <div className="saip-modal__body">
          {children}
        </div>
      </div>
    </div>
  );
}
