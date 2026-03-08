import { JSX, useState } from "react";
import Layout from "./Layout";
import "./user.css";

interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  position: string;
  phone?: string;
  role_id: number;
  is_admin: boolean;
  status: string;
}

export default function User(): JSX.Element {

  const [users] = useState<User[]>([
    {
      id: 1,
      first_name: "Yohan",
      last_name: "Martinez",
      email: "yohan@email.com",
      position: "Panadero",
      phone: "300000000",
      role_id: 1,
      is_admin: false,
      status: "Activo",
    },
    {
      id: 2,
      first_name: "Marta",
      last_name: "Lopez",
      email: "marta@email.com",
      position: "Administrador",
      phone: "300000001",
      role_id: 2,
      is_admin: true,
      status: "Activo",
    },
  ]);
  const [page, setPage] = useState<number | null>(null);
  
  return (
    <Layout>

      <h1 className="user-title">Gestión de usuarios</h1>

      <div className="user-card">

        {/* HEADER */}
        <div className="user-header">

          <div className="user-actions">
            <button className="btn-create">Crear Usuario</button>
            <button className="btn-delete">Eliminar Usuario</button>
          </div>

          <div className="user-filters">
            <input
              className="input-search"
              placeholder="Buscar"
            />
<button className="btn-filter">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polygon points="22 3 2 3 10 12 10 19 14 21 14 12 22 3"></polygon>
  </svg>
</button>
          </div>

        </div>

        {/* TABLA */}

        <table className="user-table">

          <thead>
            <tr>
              <th>Nombre</th>
              <th>Apellidos</th>
              <th>Cargo</th>
              <th>Accesos</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>

            {users.map((u) => (

              <tr key={u.id}>

                <td>{u.first_name}</td>
                <td>{u.last_name}</td>
                <td>{u.position}</td>

                <td>
                  <div className="access-tags">
                    <span className="tag">Inventario</span>
                    <span className="tag">Producción</span>
                    <span className="tag">Ventas</span>
                  </div>
                </td>

                <td>
                  <span className="status-active">{u.status}</span>
                </td>

                <td>

                  <div className="actions">

                    {/* editar */}
                    <button className="icon-btn">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6">
                        <path d="M12 20h9"/>
                        <path d="M16.5 3.5a2.1 2.1 0 013 3L7 19l-4 1 1-4 12.5-12.5z"/>
                      </svg>
                    </button>

                    {/* eliminar */}
                    <button className="icon-btn">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6l-1 14H6L5 6"/>
                        <path d="M10 11v6"/>
                        <path d="M14 11v6"/>
                        <path d="M9 6V4h6v2"/>
                      </svg>
                    </button>

                  </div>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

        {/* PAGINACIÓN */}

      <div className="pagination">

    <button
      className="page-btn"
     onClick={()=>setPage((page ?? 1) - 1)}
     >
     Anterior
    </button>

      <div className="pages">
          {[1,2,3].map((p)=>(
          <span
          key={p}
          className={`page-number ${page === p ? "active" : ""}`}
          onClick={()=>setPage(p)}
          >
          {p}
         </span>
       ))}
      </div>

      <button
        className="page-btn"
        onClick={()=>setPage((page ?? 0) + 1)}
        >
        Siguiente
      </button>

        </div>

      </div>

    </Layout>
  );
}