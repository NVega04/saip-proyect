import React from 'react';
import './App.css'; // Mantenemos el CSS base de Vite, o puedes crear uno nuevo

function App() {
  return (
    <div className="src-container">
      <header className="src-header">
        <h1>SAIP</h1>
        <h2>Sistema Administrativo Integral de Productos</h2>
        <p>¡Frontend funcionando y listo para conectar con el backend!</p>
        <button onClick={() => alert('¡Botón clickeado! El frontend es interactivo.')}>
          Haz clic aquí
        </button>
      </header>
    </div>
  );
}

export default App;