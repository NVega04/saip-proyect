import { useNavigate } from "react-router-dom";
import "./Landing.css";
import { useEffect } from "react";

export default function Landing() {
  const navigate = useNavigate();
  useEffect(() => {
  const logo = document.getElementById("heroLogo");

  const handleScroll = () => {
    if (!logo) return;

    const scrollY = window.scrollY;

    const opacity = Math.max(0, 1 - scrollY / 300);
    const scale = Math.max(0.7, 1 - scrollY / 600);

    logo.style.opacity = opacity.toString();
    logo.style.transform = `scale(${scale})`;
  };

  window.addEventListener("scroll", handleScroll);
  return () => window.removeEventListener("scroll", handleScroll);
}, []);

  return (
    <div className="landing">

      {/* ── NAVBAR ─────────────────────────────────────────────── */}
      <nav className="landing-nav">
        <div className="landing-nav__brand">
          <div className="landing-nav__logo">
            <img src="/Images/Logo-saip.png" alt="SAIP" />
          </div>
          <span className="landing-nav__name">SAIP</span>
          <span className="landing-nav__sub">Sistema de administración integral de productos</span>
        </div>
        <button className="landing-nav__btn" onClick={() => navigate("/login")}>
          Iniciar sesión
        </button>
      </nav>
      
      <div className="landing-intro">
        <div className="landing-hero-logo" id="heroLogo">
          <img src="/Images/Logo-saip.png" alt="SAIP Logo" />
        </div>

      {/* ── HERO ───────────────────────────────────────────────── */}
        <section className="landing-hero">
          {/* Olas animadas de fondo */}
          <div className="landing-hero__waves">
            <svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
              <path className="wave wave--1" d="M0,160 C360,240 1080,80 1440,160 L1440,320 L0,320 Z"/>
              <path className="wave wave--2" d="M0,192 C480,100 960,260 1440,192 L1440,320 L0,320 Z"/>
              <path className="wave wave--3" d="M0,224 C400,160 1040,280 1440,224 L1440,320 L0,320 Z"/>
            </svg>
          </div>

          <div className="landing-hero__content">
            <span className="landing-hero__tag">🥖 Gestión para negocios</span>
            <h1 className="landing-hero__title">
              Administra tu negocio<br />
              <span className="landing-hero__title--accent">de forma inteligente</span>
            </h1>
            <p className="landing-hero__desc">
              SAIP centraliza el inventario, las ventas, las recetas y los roles de tu negocio
              en un solo lugar. Menos papeles, más control.
            </p>
            <div className="landing-hero__actions">
              <button className="landing-btn-primary" onClick={() => navigate("/login")}>
                Comenzar ahora
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </button>
              <a href="#features" className="landing-btn-ghost">Ver características</a>
            </div>
          </div>

          {/* Ilustración SVG animada */}
          <div className="landing-hero__visual">
            <svg className="landing-hero__svg" viewBox="0 0 320 280" xmlns="http://www.w3.org/2000/svg">

              {/* Fondo tarjeta */}
              <rect x="20" y="20" width="280" height="240" rx="18" fill="#ffffff" stroke="#e8ddd4" strokeWidth="1.5"/>

              {/* Header tarjeta */}
              <rect x="20" y="20" width="280" height="48" rx="18" fill="#f5f0ea"/>
              <rect x="20" y="50" width="280" height="18" fill="#f5f0ea"/>
              <circle cx="48" cy="44" r="10" fill="#cfc0b0"/>
              <rect x="64" y="38" width="80" height="8" rx="4" fill="#cfc0b0"/>
              <rect x="64" y="50" width="50" height="6" rx="3" fill="#e8ddd4"/>

              {/* Barras de gráfica animadas */}
              <rect x="50" y="180" width="28" height="50" rx="6" fill="#c9a87c">
                <animate attributeName="height" values="50;70;50" dur="2.5s" repeatCount="indefinite"/>
                <animate attributeName="y" values="180;160;180" dur="2.5s" repeatCount="indefinite"/>
              </rect>
              <rect x="90" y="160" width="28" height="70" rx="6" fill="#9e7e62">
                <animate attributeName="height" values="70;50;70" dur="2s" repeatCount="indefinite"/>
                <animate attributeName="y" values="160;180;160" dur="2s" repeatCount="indefinite"/>
              </rect>
              <rect x="130" y="150" width="28" height="80" rx="6" fill="#7d5a3c">
                <animate attributeName="height" values="80;95;80" dur="3s" repeatCount="indefinite"/>
                <animate attributeName="y" values="150;135;150" dur="3s" repeatCount="indefinite"/>
              </rect>
              <rect x="170" y="165" width="28" height="65" rx="6" fill="#9e7e62">
                <animate attributeName="height" values="65;80;65" dur="2.2s" repeatCount="indefinite"/>
                <animate attributeName="y" values="165;150;165" dur="2.2s" repeatCount="indefinite"/>
              </rect>
              <rect x="210" y="145" width="28" height="85" rx="6" fill="#5c3d1e">
                <animate attributeName="height" values="85;65;85" dur="2.8s" repeatCount="indefinite"/>
                <animate attributeName="y" values="145;165;145" dur="2.8s" repeatCount="indefinite"/>
              </rect>

              {/* Línea base */}
              <line x1="40" y1="232" x2="280" y2="232" stroke="#e8ddd4" strokeWidth="1.5"/>

              {/* Etiquetas eje X */}
              <text x="64"  y="248" fontSize="8" fill="#b8a08a" textAnchor="middle">Lun</text>
              <text x="104" y="248" fontSize="8" fill="#b8a08a" textAnchor="middle">Mar</text>
              <text x="144" y="248" fontSize="8" fill="#b8a08a" textAnchor="middle">Mié</text>
              <text x="184" y="248" fontSize="8" fill="#b8a08a" textAnchor="middle">Jue</text>
              <text x="224" y="248" fontSize="8" fill="#b8a08a" textAnchor="middle">Vie</text>

              {/* Badge flotante animado */}
              <g>
                <animateTransform attributeName="transform" type="translate"
                  values="0,0; 0,-6; 0,0" dur="3s" repeatCount="indefinite"/>
                <rect x="195" y="88" width="90" height="36" rx="10" fill="#5c3d1e"/>
                <text x="240" y="103" fontSize="9" fill="#f5f0ea" textAnchor="middle">Ventas hoy</text>
                <text x="240" y="116" fontSize="11" fontWeight="bold" fill="#ffffff" textAnchor="middle">+12.4%</text>
              </g>

              {/* Punto de datos animado */}
              <circle cx="224" cy="145" r="5" fill="#5c3d1e">
                <animate attributeName="r" values="5;7;5" dur="2.8s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="1;0.6;1" dur="2.8s" repeatCount="indefinite"/>
              </circle>
            </svg>
          </div>
        </section>
      </div>

      {/* ── FEATURES ───────────────────────────────────────────── */}
      <section className="landing-features" id="features">
        <div className="landing-section-header">
          <h2 className="landing-section-title">Todo lo que necesitas</h2>
          <p className="landing-section-desc">
            Módulos diseñados para el día a día de un negocio
          </p>
        </div>
        <div className="landing-features__grid">
          {features.map((f) => (
            <div key={f.title} className="landing-feature-card">
              <div className="landing-feature-card__icon">{f.icon}</div>
              <h3 className="landing-feature-card__title">{f.title}</h3>
              <p className="landing-feature-card__desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── HISTORIA ───────────────────────────────────────────── */}
      <section className="landing-about" id="about">
        <div className="landing-about__inner">
          <div className="landing-about__text">
            <span className="landing-hero__tag">📖 Nuestra historia</span>
            <h2 className="landing-section-title" style={{ marginTop: "0.75rem" }}>
              Nació en las aulas,<br />pensado para la vida real
            </h2>
            <p className="landing-about__p">
              SAIP comenzó como un proyecto académico con una pregunta simple:
              ¿por qué tantos negocios locales siguen gestionando sus productos en cuadernos
              o en hojas de cálculo desconectadas?
            </p>
            <p className="landing-about__p">
              Lo que empezó como una tarea académica se convirtió en una herramienta real.
              Diseñamos SAIP pensando en el panadero que abre a las 4am, en el administrador
              que necesita saber qué hay en bodega sin revisar físicamente, y en el cajero
              que registra ventas sin complicaciones.
            </p>
            <p className="landing-about__p">
              Hoy SAIP es un sistema integral que centraliza inventario, ventas, recetas
              y gestión de usuarios — construido con tecnología moderna y con el propósito
              de que cualquier negocio, grande o pequeño, pueda tener el control que merece.
            </p>
          </div>
          <div className="landing-about__pills">
            {["Proyecto académico", "Código abierto", "Hecho con 🤎", "React + FastAPI", "Para negocios"].map((p) => (
              <span key={p} className="landing-about__pill">{p}</span>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA FINAL ──────────────────────────────────────────── */}
      <section className="landing-cta">
        <h2 className="landing-cta__title">¿Listo para tomar el control?</h2>
        <p className="landing-cta__desc">Ingresa a SAIP y empieza a gestionar tu negocio hoy.</p>
        <button className="landing-btn-primary" onClick={() => navigate("/login")}>
          Iniciar sesión
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
      </section>

      {/* ── FOOTER ─────────────────────────────────────────────── */}
      <footer className="landing-footer">
        <span>© {new Date().getFullYear()} SAIP — Todos los derechos reservados</span>
        <div className="landing-footer__links">
          <a href="#features">Características</a>
          <a href="#about">Acerca de</a>
          <span className="landing-footer__sep">·</span>
          <span onClick={() => navigate("/login")}>Iniciar sesión</span>
        </div>
      </footer>

    </div>
  );
}

const features = [
  {
    title: "Inventario",
    desc: "Controla el stock de materias primas y productos terminados en tiempo real. Nunca te quedes sin ingredientes.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6">
        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
      </svg>
    ),
  },
  {
    title: "Registro de ventas",
    desc: "Registra cada venta del día de forma rápida y consulta el historial cuando lo necesites.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6">
        <line x1="12" y1="1" x2="12" y2="23"/>
        <path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
      </svg>
    ),
  },
  {
    title: "Recetas y producción",
    desc: "Gestiona tus recetas, calcula costos y lleva el control de lo que produces cada día.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6">
        <rect x="2" y="7" width="20" height="14" rx="1"/>
        <path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/>
        <line x1="12" y1="12" x2="12" y2="16"/>
        <line x1="10" y1="14" x2="14" y2="14"/>
      </svg>
    ),
  },
  {
    title: "Gestión de usuarios",
    desc: "Asigna roles y permisos a tu equipo. Cada persona accede solo a lo que necesita.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6">
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 00-3-3.87"/>
        <path d="M16 3.13a4 4 0 010 7.75"/>
      </svg>
    ),
  },
  {
    title: "Proveedores",
    desc: "Mantén un registro de tus proveedores y sus condiciones para tomar mejores decisiones de compra.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6">
        <rect x="1" y="3" width="15" height="13" rx="1"/>
        <path d="M16 8h4l3 3v5h-7V8z"/>
        <circle cx="5.5" cy="18.5" r="2.5"/>
        <circle cx="18.5" cy="18.5" r="2.5"/>
      </svg>
    ),
  },
  {
    title: "Roles y permisos",
    desc: "Define qué puede hacer cada usuario dentro del sistema con un control granular de accesos.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.6">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
        <path d="M7 11V7a5 5 0 0110 0v4"/>
      </svg>
    ),
  },
];