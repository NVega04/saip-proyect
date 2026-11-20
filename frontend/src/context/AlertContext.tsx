import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import Alerta from "../components/alert/Alert";
import { SESSION_NOTICE_KEY } from "../utils/api";

type AlertType = "success" | "error" | "warning" | "info";

interface AlertState {
  show: boolean;
  type: AlertType;
  message: string;
  duration?: number;
}

interface AlertContextType {
  showAlert: (type: AlertType, message: string, duration?: number) => void;
  hideAlert: () => void;
}

const AlertContext = createContext<AlertContextType | undefined>(undefined);

export function AlertProvider({ children }: { children: ReactNode }) {
  const [alert, setAlert] = useState<AlertState>({
    show: false,
    type: "info",
    message: "",
    duration: 3000,
  });

  const showAlert = (type: AlertType, message: string, duration = 3000) => {
    setAlert({ show: true, type, message, duration });
  };

  // Aviso dejado por api.ts tras un 401: como la recarga de página borra
  // el estado en memoria, se recupera y se muestra una sola vez. Se difiere
  // a un microtask para no hacer setState síncrono dentro del effect.
  useEffect(() => {
    const notice = localStorage.getItem(SESSION_NOTICE_KEY);
    if (notice) {
      localStorage.removeItem(SESSION_NOTICE_KEY);
      queueMicrotask(() => showAlert("warning", notice, 5000));
    }
  }, []);
  const hideAlert = () => {
    setAlert((prev) => ({ ...prev, show: false }));
  };

  return (
    <AlertContext.Provider value={{ showAlert, hideAlert }}>
      {children}
      <Alerta
        show={alert.show}
        type={alert.type}
        message={alert.message}
        duration={alert.duration}
        onClose={hideAlert}
      />
    </AlertContext.Provider>
  );
}

export function useAlert() {
  const context = useContext(AlertContext);
  if (!context) {
    throw new Error("useAlert debe usarse dentro de AlertProvider");
  }
  return context;
}