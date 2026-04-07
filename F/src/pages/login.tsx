import { useState, useRef, ChangeEvent } from "react";
import React from "react";
import { Link } from "react-router-dom";
import './login.css';
import { apiFetch, getMe } from "../utils/api";
import { useAuth } from "../context/AuthContext";
import { useEffect} from "react";
import Modal from "../components/Modal";
import Alerta from "../components/Alert";

// ─── Interfaces ───────────────────────────────────────────────────────────────
interface LoginResponse {
  session_token: string;
  expires_at: string;
  user: UserData;
}

interface UserData {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  role_id: number;
  is_admin: boolean;
  status: string;
  created_at: string;
}

export default function Login() {
  const { setCurrentUser } = useAuth(); // ← para setear el usuario al contexto al instante

  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [remember, setRemember]         = useState<boolean>(() => !!localStorage.getItem("remembered_email"));
  const [email, setEmail]               = useState<string>(() => localStorage.getItem("remembered_email") ?? "");
  const [password, setPassword]         = useState<string>("");
  const [isLoading, setIsLoading]       = useState<boolean>(false);
  const termsAcceptedRef = useRef<boolean>(false);
  const [showTermsModal, setShowTermsModal] = useState<boolean>(false);
  const [showAlert, setShowAlert] = useState<boolean>(false);
  const [alertMessage, setAlertMessage] = useState<string>("");
  const [alertType, setAlertType] = useState<"success" | "error" | "warning" | "info">("error");
  const images = [
  "/Images/Pan 1.jpg",
  "/Images/Pan 2.jpg",
  "/Images/Pan 3.jpg",
  "/Images/Pan 4.jpg",
  "/Images/Pan 5.jpeg",
];

const [currentIndex, setCurrentIndex] = useState(0);

useEffect(() => {
  const interval = setInterval(() => {
    setCurrentIndex((prev) => (prev + 1) % images.length);
  }, 3000);

  return () => clearInterval(interval);
}, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/session/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, accepted_terms: termsAcceptedRef.current }),
      });

      if (response.status === 403) {
        const error = await response.json();
        if (error.detail?.includes("términos")) {
          setShowTermsModal(true);
          setIsLoading(false);
          return;
        }
        setAlertType("error");
        setAlertMessage(error.detail || "Acceso denegado.");
        setShowAlert(true);
        setIsLoading(false);
        return;
      }

      if (!response.ok) {
        const error = await response.json();
        setAlertType("error");
        setAlertMessage(error.detail || "Credenciales inválidas.");
        setShowAlert(true);
        setIsLoading(false);
        return;
      }

      const data: LoginResponse = await response.json();

      // Guarda el token y el usuario en localStorage
      localStorage.setItem("session_token", data.session_token);
      localStorage.setItem("user", JSON.stringify(data.user));

      if (remember) {
        localStorage.setItem("remembered_email", email);
      } else {
        localStorage.removeItem("remembered_email");
      }

      // Cargar módulos del rol
      if (!data.user.is_admin) {
        const modulesRes = await apiFetch(`/role-modules/${data.user.role_id}`);
        if (modulesRes.ok) {
          const roleModules: { module: { name: string } }[] = await modulesRes.json();
          const moduleNames = roleModules.map((rm) => rm.module.name);
          localStorage.setItem("modules", JSON.stringify(moduleNames));
        }
      } else {
        localStorage.setItem("modules", JSON.stringify(["all"]));
      }

      // Obtiene el perfil completo (con role.name) y lo setea en el contexto
      // para que el Navbar lo muestre inmediatamente sin esperar un nuevo fetch
      const me = await getMe();
      if (me) setCurrentUser(me);

      window.location.href = "/dashboard";
    } catch {
      setAlertType("error");
      setAlertMessage("Error de conexión con el servidor.");
      setShowAlert(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-root">
      <div className="login-body">
        <div className="card-outer">
          <div className="card-inner">
            {/* ── Panel izquierdo ── */}
            <div className="panel-image">
              <img
                key={currentIndex}
                src={images[currentIndex]}
                alt="login visual"
                className="carousel-image"
              />
               {/* 🔥 overlay oscuro */}
              <div className="carousel-overlay" />
              {/* 🔥 card del logo */}
              <div className="carousel-logo-card">
                <img src="/Images/Logo-saip.png" alt="SAIP" />
              </div>
            </div>
            {/* ── Panel derecho ── */}
            <div className="panel-form">
              <h1 className="form-title">Iniciar sesión</h1>
              <p className="form-desc">Ingrese sus credenciales para acceder a su cuenta.</p>
              <form onSubmit={handleSubmit} className="login-form">
                <div className="field-group">
                  <label className="field-label" htmlFor="email">Correo</label>
                  <input
                    id="email"
                    type="text"
                    className="field-input"
                    placeholder="Su nombre de usuario o correo electrónico"
                    value={email}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                    autoComplete="username"
                  />
                </div>
                <div className="field-group">
                  <label className="field-label" htmlFor="password">Contraseña</label>
                  <div className="field-wrapper">
                    <input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      className="field-input has-icon"
                      placeholder="Ingrese su contraseña"
                      value={password}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                      autoComplete="current-password"
                    />
                    <button
                      type="button"
                      className="toggle-pw"
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                    >
                      {showPassword ? (
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                          <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/>
                          <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/>
                          <line x1="1" y1="1" x2="23" y2="23"/>
                        </svg>
                      ) : (
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                          <circle cx="12" cy="12" r="3"/>
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
                <div className="options-row">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={remember}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setRemember(e.target.checked)}
                    />
                    Recordar correo
                  </label>
                  <Link to="/reset-password" className="forgot-link">¿Olvidó su contraseña?</Link>
                </div>
                <button type="submit" className="btn-submit" disabled={isLoading}>
                  {isLoading && <span className="btn-spinner" />}
                  {isLoading ? "Verificando..." : "Iniciar sesión"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
      {/* ── Footer ── */}
      <footer className="login-footer">
        <div className="footer-links">
          <Link to="/" className="footer-link">Conócenos</Link>
        </div>
        <div className="footer-social">
          <div className="footer-icon">
            <svg viewBox="0 0 24 24">
              <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
            </svg>
          </div>
          <div className="footer-icon">
            <svg viewBox="0 0 24 24">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
              <circle cx="12" cy="12" r="4"/>
              <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>
            </svg>
          </div>
        </div>
      </footer>

      {/* ── Modal Términos y Condiciones ── */}
      <Modal
        isOpen={showTermsModal}
        onClose={() => setShowTermsModal(false)}
        title="Términos y Condiciones"
        width="560px"
      >
        <div className="terms-content">
          <div className="terms-scroll">
            <h3>1. Aceptación de los términos</h3>
            <p>
              Al acceder y utilizar SAIP (Sistema Administrativo Integral de Productos), 
              usted acepta estar sujeto a estos términos y condiciones. Si no está de 
              acuerdo con alguno de estos términos, por favor no utilice el sistema.
            </p>

            <h3>2. Descripción del servicio</h3>
            <p>
              SAIP es una plataforma de gestión administrativa diseñada para el control 
              de inventario y productos de panadería. El sistema permite administrar 
              usuarios, productos, unidades de medida y demás elementos relacionados 
              con la operación del negocio.
            </p>

            <h3>3. Cuenta de usuario</h3>
            <p>
              Para acceder al sistema, cada usuario recibirá credenciales de acceso 
              personalizadas (correo electrónico y contraseña). El usuario es responsable 
              de mantener la confidencialidad de sus credenciales y de todas las 
              actividades que ocurran bajo su cuenta.
            </p>

            <h3>4. Uso adecuado</h3>
            <p>
              El usuario se compromete a utilizar el sistema únicamente para fines 
              legítimos y de acuerdo con las políticas internas de la organización. 
              Queda prohibido utilizar el sistema para actividades ilegales o no 
              autorizadas.
            </p>

            <h3>5. Protección de datos</h3>
            <p>
              Sus datos personales serán tratados de acuerdo con las políticas de 
              privacidad de la organización. Nos comprometemos a proteger su 
              información y utilizarla únicamente para los fines contemplados 
              en este servicio.
            </p>

            <h3>6. Modificaciones del servicio</h3>
            <p>
              SAIP se reserva el derecho de modificar o discontinuar el servicio 
              en cualquier momento, con o sin previo aviso. No nos haremos 
              responsables por la pérdida de datos derivada de estas modificaciones.
            </p>

            <h3>7. Limitación de responsabilidad</h3>
            <p>
              El sistema se proporciona "tal cual". No garantizamos que el servicio 
              sea ininterrumpido, seguro o libre de errores. El usuario utiliza el 
              sistema bajo su propia responsabilidad.
            </p>

            <h3>8. Ley aplicable</h3>
            <p>
              Estos términos se rigen por las leyes vigentes. Cualquier disputa 
              derivada del uso del sistema será resuelta de acuerdo con los 
              procedimientos legales aplicables.
            </p>
          </div>
          <div className="terms-actions">
            <button
              type="button"
              className="btn-submit"
              onClick={() => {
                termsAcceptedRef.current = true;
                setShowTermsModal(false);
                document.querySelector<HTMLFormElement>(".login-form")?.requestSubmit();
              }}
            >
              Aceptar y continuar
            </button>
          </div>
        </div>
      </Modal>

      <Alerta
        show={showAlert}
        type={alertType}
        message={alertMessage}
        onClose={() => setShowAlert(false)}
      />
    </div>
  );
}