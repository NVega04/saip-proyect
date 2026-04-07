import { useEffect } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import User from "./pages/user";
import Dashboard from "./pages/Dashboard";
import Roles from "./pages/Roles";
import Login from "./pages/login";
import Proveedores from "./pages/Providers";
import Produccion from "./pages/Production";
import Recetas from "./pages/Recipes";
import Units from "./pages/Units";
import Products from "./pages/Products";
import SupplyCategories from "./pages/SupplyCategories";
import Supplies from "./pages/Supplies";
import AcercaDe from "./pages/AcercaDe";
import Ventas from "./pages/Sales";
import Inventory from "./pages/inventory";
import ProtectedRoute from "./components/ProtectedRoute";
import Perfil from "./pages/Profile";
import './variables.css'
import { AuthProvider } from "./context/AuthContext";
import RecoverPassword from "./pages/RecoverPassword";
import Landing from "./pages/Landing";
import { AlertProvider } from "./context/AlertContext";
import { ConfirmProvider } from "./context/ConfirmContext";
import Reports from "./pages/Reports";


function App() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return (
    <AuthProvider>
      <AlertProvider>
        <ConfirmProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Landing />} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/inventario" element={<ProtectedRoute module="inventario"><Inventory /></ProtectedRoute>} />
            <Route path="/proveedores" element={<ProtectedRoute module="proveedores"><Proveedores /> </ProtectedRoute>} />
            <Route path="/ventas" element={<ProtectedRoute module="ventas"><Ventas /></ProtectedRoute>} />
            <Route path="/produccion"  element={<ProtectedRoute module="produccion"> <Produccion />  </ProtectedRoute>} />
            <Route path="/recetas"     element={<ProtectedRoute module="recetas">    <Recetas />     </ProtectedRoute>} />
            <Route path="/units"       element={<ProtectedRoute module="recetas">    <Units />       </ProtectedRoute>} />
            <Route path="/products"    element={<ProtectedRoute module="recetas">    <Products />    </ProtectedRoute>} />
            <Route path="/supply-categories" element={<ProtectedRoute module="recetas"><SupplyCategories /></ProtectedRoute>} />
            <Route path="/supplies" element={<ProtectedRoute module="recetas"><Supplies /></ProtectedRoute>} />
            <Route path="/usuarios"    element={<ProtectedRoute module="usuarios">   <User />        </ProtectedRoute>} />
            <Route path="/roles"       element={<ProtectedRoute module="roles">      <Roles />       </ProtectedRoute>} />
            <Route path="/perfil" element={<Perfil />} />
            <Route path="/reset-password" element={<RecoverPassword />} />
            <Route path="/reportes" element={<ProtectedRoute><Reports /></ProtectedRoute>}/>
            <Route path="/acerca" element={<ProtectedRoute><AcercaDe /></ProtectedRoute>}/>
          </Routes>
        </ConfirmProvider>
      </AlertProvider>  
    </AuthProvider>
  );
}

export default App;