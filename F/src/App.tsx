import { Routes, Route } from "react-router-dom";
import User from "./pages/user";
import Dashboard from "./pages/Dashboard";
import Roles from "./pages/Roles";
import Login from "./pages/login";
import Proveedores from "./pages/Proveedores";
import Produccion from "./pages/Produccion";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard  />} />
      <Route path="/proveedores" element={<Proveedores />} />
      <Route path="/produccion" element={<Produccion />} />
      <Route path="/usuarios" element={<User />} />
      <Route path="/roles" element={<Roles />} />

    </Routes>
  );
}

export default App;