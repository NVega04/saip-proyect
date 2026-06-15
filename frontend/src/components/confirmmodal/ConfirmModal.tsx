import "./ConfirmModal.css";

interface ConfirmModalProps {
  isOpen: boolean;
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmModal({
  isOpen,
  title = "Confirmar acción",
  message,
  confirmText = "Eliminar",
  cancelText = "Cancelar",
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  if (!isOpen) return null;

  return (
    <div className="saip-confirm__overlay" onClick={onCancel}>
      <div className="saip-confirm__box" onClick={(e) => e.stopPropagation()}>
        <div className="saip-confirm__header">
          <h3>{title}</h3>
        </div>

        <div className="saip-confirm__body">
          <p>{message}</p>
        </div>

        <div className="saip-confirm__actions">
          <button className="saip-confirm__btn saip-confirm__btn--cancel" onClick={onCancel}>
            {cancelText}
          </button>
          <button className="saip-confirm__btn saip-confirm__btn--danger" onClick={onConfirm}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}