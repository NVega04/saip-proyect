import { JSX, useState } from "react";
import Layout from "./Layout";
import "./createUser.css";

export default function CreateUser(): JSX.Element {

  const [form, setForm] = useState({
    first_name:"",
    last_name:"",
    email:"",
    position:"",
    phone:"",
    role_id:"",
    is_admin:false
  });

  const handleChange = (e:any)=>{
    const {name,value,type,checked} = e.target;

    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value
    });
  };

  const handleSubmit = (e:any)=>{
    e.preventDefault();
    console.log(form);
  };

  return (

    <Layout>

      <h1 className="create-title">Crear Usuario</h1>

      <div className="create-card">

        <form className="create-form" onSubmit={handleSubmit}>

          <div className="form-grid">

            <div className="form-group">
              <label>Nombre</label>
              <input name="first_name" onChange={handleChange}/>
            </div>

            <div className="form-group">
              <label>Apellido</label>
              <input name="last_name" onChange={handleChange}/>
            </div>

            <div className="form-group">
              <label>Email</label>
              <input
              name="email"
              placeholder="example@gmail.com"
            />

            </div>

            <div className="form-group">
              <label>Cargo</label>
              <input
             name="position"
             placeholder="Ej: Cajero"
            />
            </div>

            <div className="form-group">
              <label>Teléfono</label>
              <input name="phone" onChange={handleChange}/>
            </div>

            <div className="form-group">
              <label>Rol</label>
              <select name="role_id" onChange={handleChange}>
                <option value="">Seleccionar</option>
                <option value="1">Administrador</option>
                <option value="2">Cajero</option>
                <option value="3">Panadero</option>
              </select>
            </div>

          </div>

          <div className="admin-check">
            <input
              type="checkbox"
              name="is_admin"
              onChange={handleChange}
            />
            <span>Administrador del sistema</span>
          </div>

          <div className="form-actions">
            <button className="btn-cancel">Cancelar</button>
            <button className="btn-save">Crear Usuario</button>
          </div>

        </form>

      </div>

    </Layout>

  );
}