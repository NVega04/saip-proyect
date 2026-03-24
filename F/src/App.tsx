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
import RecoverPassword from "./pages/RecoverPassword";
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
        {/* <Route path="/inventario"  element={<ProtectedRoute module="inventario"> <Inventario />  </ProtectedRoute>} /> */}
        <Route path="/proveedores" element={<ProtectedRoute module="proveedores"><Proveedores /> </ProtectedRoute>} />
        {/* <Route path="/ventas"      element={<ProtectedRoute module="ventas">     <Ventas />      </ProtectedRoute>} /> */}
        <Route path="/produccion"  element={<ProtectedRoute module="produccion"> <Produccion />  </ProtectedRoute>} />
        <Route path="/recetas"     element={<ProtectedRoute module="recetas">    <Recetas />     </ProtectedRoute>} />
        <Route path="/usuarios"    element={<ProtectedRoute module="usuarios">   <User />        </ProtectedRoute>} />
        <Route path="/roles"       element={<ProtectedRoute module="roles">      <Roles />       </ProtectedRoute>} />
        <Route path="/perfil" element={<Perfil />} />
        <Route path="/reset-password" element={<RecoverPassword />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;