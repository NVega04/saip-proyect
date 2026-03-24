import { Navigate } from "react-router-dom";

interface Props {
  children: React.ReactNode;
  module?: string;
}

function canAccess(module: string): boolean {
  const raw = localStorage.getItem("modules");
  if (!raw) return false;
  const modules: string[] = JSON.parse(raw);
  if (modules.includes("all")) return true;
  if (["dashboard", "acerca", "contacto"].includes(module)) return true;
  return modules.includes(module);
}

export default function ProtectedRoute({ children, module }: Props) {
  const token = localStorage.getItem("session_token");
  if (!token) return <Navigate to="/" replace />;
  if (module && !canAccess(module)) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}