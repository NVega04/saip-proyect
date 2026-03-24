import { createContext, useContext, useState, ReactNode } from "react";
import Alerta from "../components/Alert";

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