import { Routes, Route } from "react-router-dom";
import User from "./pages/user";
import Dashboard from "./pages/Dashboard";
import Roles from "./pages/Roles";
import Login from "./pages/login";
import Proveedores from "./pages/Proveedores";
import Produccion from "./pages/Produccion";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/proveedores" element={<ProtectedRoute><Proveedores /></ProtectedRoute>} />
      <Route path="/produccion" element={<ProtectedRoute><Produccion /></ProtectedRoute>} />
      <Route path="/usuarios" element={<ProtectedRoute><User /></ProtectedRoute>} />
      <Route path="/roles" element={<ProtectedRoute><Roles /></ProtectedRoute>} />
    </Routes>
  );
}

export default App;