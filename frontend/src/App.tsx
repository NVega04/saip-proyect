import { useEffect } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import User from "./pages/user/user";
import Dashboard from "./pages/dashboard/Dashboard";
import Roles from "./pages/roles/Roles";
import Login from "./pages/login/login";
import Proveedores from "./pages/providers/Providers";
import Produccion from "./pages/production/Production";
import Recetas from "./pages/recipes/Recipes";
import Units from "./pages/units/Units";
import Products from "./pages/products/Products";
import SupplyCategories from "./pages/supplycategories/SupplyCategories";
import Supplies from "./pages/supplies/Supplies";
import AcercaDe from "./pages/acercade/AcercaDe";
import Ventas from "./pages/sales/Sales";
import SalesHistory from "./pages/saleshistory/SalesHistory";
import Inventory from "./pages/inventory/inventory";
import ProtectedRoute from "./components/protectedroute/ProtectedRoute";
import Perfil from "./pages/profile/Profile";
import './variables.css'
import { AuthProvider } from "./context/AuthContext";
import RecoverPassword from "./pages/recoverpassword/RecoverPassword";
import Landing from "./pages/landing/Landing";
import { AlertProvider } from "./context/AlertContext";
import { ConfirmProvider } from "./context/ConfirmContext";
import Reports from "./pages/reports/Reports";
import ProductCategories from "./pages/productcategories/ProductCategories";
import CommercialProducts from "./pages/commercialproducts/CommercialProducts";


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
            <Route path="/inventario" element={<ProtectedRoute module="inventory"><Inventory /></ProtectedRoute>} />
            <Route path="/proveedores" element={<ProtectedRoute module="providers"><Proveedores /> </ProtectedRoute>} />
            <Route path="/ventas" element={<ProtectedRoute module="sales"><Ventas /></ProtectedRoute>} />
            <Route path="/ventas/historial" element={<ProtectedRoute module="sales"><SalesHistory /></ProtectedRoute>} />
            <Route path="/produccion"  element={<ProtectedRoute module="production"> <Produccion />  </ProtectedRoute>} />
            <Route path="/recetas"     element={<ProtectedRoute module="recipes">    <Recetas />     </ProtectedRoute>} />
            <Route path="/units"       element={<ProtectedRoute module="supplies">   <Units />       </ProtectedRoute>} />
            <Route path="/products"    element={<ProtectedRoute module="supplies">   <Products />    </ProtectedRoute>} />
            <Route path="/supply-categories" element={<ProtectedRoute module="supplies"><SupplyCategories /></ProtectedRoute>} />
            <Route path="/supplies"    element={<ProtectedRoute module="supplies">   <Supplies />    </ProtectedRoute>} />
            <Route path="/product-categories" element={<ProtectedRoute module="supplies"><ProductCategories /></ProtectedRoute>} />
            <Route path="/commercial-products" element={<ProtectedRoute module="supplies"><CommercialProducts /></ProtectedRoute>} />
            <Route path="/usuarios"    element={<ProtectedRoute module="users">      <User />        </ProtectedRoute>} />
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