import { createContext, useContext, useState, ReactNode } from "react";
import ConfirmModal from "../components/ConfirmModal";

interface ConfirmOptions {
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
}

interface ConfirmState extends ConfirmOptions {
  isOpen: boolean;
}

interface ConfirmContextType {
  showConfirm: (options: ConfirmOptions) => void;
  hideConfirm: () => void;
}

const ConfirmContext = createContext<ConfirmContextType | undefined>(undefined);

export function ConfirmProvider({ children }: { children: ReactNode }) {
  const [confirmState, setConfirmState] = useState<ConfirmState>({
    isOpen: false,
    message: "",
    onConfirm: () => {},
  });

  const showConfirm = (options: ConfirmOptions) => {
    setConfirmState({
      isOpen: true,
      ...options,
    });
  };

  const hideConfirm = () => {
    setConfirmState((prev) => ({ ...prev, isOpen: false }));
  };

  const handleConfirm = () => {
    confirmState.onConfirm();
    hideConfirm();
  };

  return (
    <ConfirmContext.Provider value={{ showConfirm, hideConfirm }}>
      {children}
      <ConfirmModal
        isOpen={confirmState.isOpen}
        title={confirmState.title}
        message={confirmState.message}
        confirmText={confirmState.confirmText}
        cancelText={confirmState.cancelText}
        onConfirm={handleConfirm}
        onCancel={hideConfirm}
      />
    </ConfirmContext.Provider>
  );
}

export function useConfirm() {
  const context = useContext(ConfirmContext);
  if (!context) {
    throw new Error("useConfirm debe usarse dentro de ConfirmProvider");
  }
  return context;
}