import { useEffect } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import User from "./pages/user";
import Dashboard from "./pages/Dashboard";
import Roles from "./pages/Roles";
import Login from "./pages/login";
import Proveedores from "./pages/Proveedores";
import Produccion from "./pages/Produccion";
import Recetas from "./pages/Recetas";
import ProtectedRoute from "./components/ProtectedRoute";
import Perfil from "./pages/Perfil";
import './variables.css'
import { AuthProvider } from "./context/AuthContext";
import RecuperarPassword from "./pages/RecuperarPassword";
import Landing from "./pages/Landing";

function App() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/proveedores" element={<ProtectedRoute><Proveedores /></ProtectedRoute>} />
        <Route path="/produccion" element={<ProtectedRoute><Produccion /></ProtectedRoute>} />
        <Route path="/recetas" element={<ProtectedRoute><Recetas /></ProtectedRoute>} />
        <Route path="/usuarios" element={<ProtectedRoute><User /></ProtectedRoute>} />
        <Route path="/roles" element={<ProtectedRoute><Roles /></ProtectedRoute>} />
        <Route path="/perfil" element={<Perfil />} />
        <Route path="/reset-password" element={<RecuperarPassword />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;