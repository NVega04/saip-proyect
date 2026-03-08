import { JSX, useState } from "react";
import Layout from "./Layout";
import "./roles.css";

interface Role{
  id:number
  name:string
  description:string
}

export default function Roles():JSX.Element{

  const [roles]=useState<Role[]>([
    {
      id:1,
      name:"Administrador",
      description:"Control total del sistema"
    },
    {
      id:2,
      name:"Cajero",
      description:"Gestiona ventas"
    },
    {
      id:3,
      name:"Panadero",
      description:"Gestiona producción"
    }
  ])

  return(

    <Layout>

      <h1 className="roles-title">Gestión de Roles</h1>

      <div className="roles-card">

        <table className="roles-table">

          <thead>
            <tr>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>

            {roles.map(r=>(
              <tr key={r.id}>

                <td>{r.name}</td>
                <td>{r.description}</td>

                <td>
                  <button className="icon-btn">
                    ✏️
                  </button>
                </td>

              </tr>
            ))}

          </tbody>

        </table>

      </div>

    </Layout>

  )

}