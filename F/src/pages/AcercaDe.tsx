import { JSX } from "react";
import { FaGithub } from "react-icons/fa";
import Layout from "../components/Layout";
import "./AcercaDe.css";

export default function AcercaDe(): JSX.Element {
  return (
    <Layout
      breadcrumbs={[
        { label: "Dashboard", to: "/dashboard" },
        { label: "Acerca de" },
      ]}
    >
      <div className="acerca">
        <header className="acerca__header">
          <div className="acerca__brand">
            <img
              src="/Images/Logo-saip.png"
              alt="SAIP Logo"
              className="acerca__logo"
            />
          </div>
          <h1 className="acerca__title">Acerca de SAIP</h1>
          <p className="acerca__subtitle">
            Sistema de Administración Integral de Productos
          </p>
        </header>

        <section className="acerca__section">
          <h2 className="acerca__section-title">Nuestra historia</h2>
          <div className="acerca__content">
            <p className="acerca__p">
              SAIP comenzó como un proyecto académico con una pregunta simple:
              ¿por qué tantos negocios locales siguen gestionando sus productos en
              cuadernos o en hojas de cálculo desconectadas?
            </p>
            <p className="acerca__p">
              A medida que avanzábamos, entendimos que el problema no era solo la
              falta de herramientas, sino la falta de soluciones diseñadas realmente
              para el día a día de un negocio. Por eso, decidimos construir SAIP
              con un enfoque práctico, pensando en la operación real.
            </p>
            <p className="acerca__p">
              El sistema fue desarrollado utilizando{" "}
              <strong>Python y FastAPI</strong> para el backend, permitiendo una
              arquitectura robusta, escalable y segura. Implementamos autenticación,
              manejo de sesiones, control de usuarios y una estructura modular
              orientada a servicios.
            </p>
            <p className="acerca__p">
              En el frontend utilizamos{" "}
              <strong>React con TypeScript</strong>, construyendo una interfaz
              moderna, intuitiva y dinámica. Diseñamos componentes reutilizables,
              navegación fluida y una experiencia centrada en la usabilidad para
              facilitar la gestión diaria.
            </p>
            <p className="acerca__p">
              Durante el desarrollo integramos funcionalidades clave como control
              de inventario, registro de ventas, gestión de roles, recetas,
              categorías de insumos y manejo de proveedores, conectando todo
              mediante APIs eficientes y bien estructuradas.
            </p>
            <p className="acerca__p">
              Hoy SAIP no es solo un proyecto académico, sino una solución real
              en evolución, construida con tecnologías modernas y con la visión
              de escalar hacia un sistema completo para la administración de
              negocios.
            </p>
          </div>
        </section>

        <section className="acerca__section">
          <h2 className="acerca__section-title">Tecnologías</h2>
          <div className="acerca__pills">
            {[
              "Proyecto académico",
              "Código abierto",
              "React + TypeScript",
              "Python + FastAPI",
              "Docker",
              "MySQL 8.0",
              "SQLModel",
              "Vite + pnpm",
              "Para negocios",
            ].map((p) => (
              <span key={p} className="acerca__pill">
                {p}
              </span>
            ))}
            <a
              href="https://github.com/NVega04/saip-proyect.git"
              target="_blank"
              rel="noopener noreferrer"
              className="acerca__pill acerca__pill--github"
            >
              <FaGithub />
              GitHub
            </a>
          </div>
        </section>

        <section className="acerca__section">
          <h2 className="acerca__section-title">Evolución del proyecto</h2>
          <div className="acerca__timeline">
            <div className="acerca__timeline-item">
              <div className="acerca__timeline-dot" />
              <div className="acerca__timeline-content">
                <strong>Inicio académico</strong>
                <p>
                  Idea inicial planteada en el entorno formativo con enfoque en
                  problemas reales.
                </p>
              </div>
            </div>
            <div className="acerca__timeline-item">
              <div className="acerca__timeline-dot" />
              <div className="acerca__timeline-content">
                <strong>Diseño del sistema</strong>
                <p>
                  Definición de arquitectura, modelos de datos y flujo de
                  usuarios.
                </p>
              </div>
            </div>
            <div className="acerca__timeline-item">
              <div className="acerca__timeline-dot" />
              <div className="acerca__timeline-content">
                <strong>Backend</strong>
                <p>
                  Desarrollo con Python y FastAPI, implementación de
                  autenticación, sesiones y API REST.
                </p>
              </div>
            </div>
            <div className="acerca__timeline-item">
              <div className="acerca__timeline-dot" />
              <div className="acerca__timeline-content">
                <strong>Frontend</strong>
                <p>
                  Construcción con React y TypeScript, enfoque en UX y
                  componentes reutilizables.
                </p>
              </div>
            </div>
            <div className="acerca__timeline-item">
              <div className="acerca__timeline-dot" />
              <div className="acerca__timeline-content">
                <strong>Versión actual</strong>
                <p>
                  Sistema funcional con módulos de gestión de usuarios, gestión de
                  roles, recetas, inventario, categorías, insumos y más.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="acerca__section">
          <h2 className="acerca__section-title">Módulos del sistema</h2>
          <div className="acerca__modules">
            {modules.map((m) => (
              <div key={m.title} className="acerca__module-card">
                <div className="acerca__module-icon">{m.icon}</div>
                <h3 className="acerca__module-title">{m.title}</h3>
                <p className="acerca__module-desc">{m.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </Layout>
  );
}

const modules = [
  {
    title: "Inventario",
    desc: "Controla el stock de materias primas y productos terminados.",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
      </svg>
    ),
  },
  {
    title: "Recetas y producción",
    desc: "Gestiona recetas, calcula costos y controla la producción.",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <path d="M4 19.5A2.5 2.5 0 016.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" />
      </svg>
    ),
  },
  {
    title: "Gestión de usuarios",
    desc: "Asigna roles y permisos a cada miembro del equipo.",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 00-3-3.87" />
        <path d="M16 3.13a4 4 0 010 7.75" />
      </svg>
    ),
  },
  {
    title: "Proveedores",
    desc: "Mantén un registro de tus proveedores y condiciones.",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <rect x="1" y="3" width="15" height="13" rx="1" />
        <path d="M16 8h4l3 3v5h-7V8z" />
        <circle cx="5.5" cy="18.5" r="2.5" />
        <circle cx="18.5" cy="18.5" r="2.5" />
      </svg>
    ),
  },
  {
    title: "Categorías e insumos",
    desc: "Organiza tus insumos por categorías y lleva control de stock.",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <path d="M3 6h18M3 12h18M3 18h18" />
      </svg>
    ),
  },
  {
    title: "Reportes",
    desc: "Consulta reportes y estadísticas del negocio.",
    icon: (
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
      </svg>
    ),
  },
];
