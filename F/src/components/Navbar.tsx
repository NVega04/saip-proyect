import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { logout, getMe } from "../utils/api";

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [user, setUser] = useState<{ nombre: string; rol: string } | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // ── Cargar usuario autenticado ────────────────────────────────────────────
  useEffect(() => {
    getMe().then((data) => {
      if (data) {
        setUser({
          nombre: `${data.first_name} ${data.last_name}`,
          rol: data.role.name,
        });
      }
    });
  }, []);

  // ── Cerrar menu al click fuera ────────────────────────────────────────────
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // ── Cerrar sesion ─────────────────────────────────────────────────────────
  const handleLogout = async () => {
    setMenuOpen(false);
    await logout();
  };

  return (
    <nav style={styles.navbar}>
      <Link to="/dashboard" style={styles.brand}>
        <div style={styles.logoBox}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.5">
            <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/>
            <path d="M9 21V12h6v9"/>
          </svg>
        </div>
      </Link>

      <div style={styles.links}>
        <a href="#" style={styles.link}>Acerca de nosotros</a>
        <a href="#" style={styles.link}>Contacto</a>
      </div>

      <div ref={menuRef} style={{ position: "relative" }}>
        <div style={styles.userTrigger} onClick={() => setMenuOpen(!menuOpen)}>
          <div style={styles.userText}>
            <span style={styles.userName}>{user?.nombre ?? "..."}</span> {/* 👈 */}
            <span style={styles.userRole}>{user?.rol ?? ""}</span>       {/* 👈 */}
          </div>
          <div style={styles.avatar}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.5">
              <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
        </div>

        {menuOpen && (
          <div style={styles.dropdown}>
            <button style={styles.dropdownItem} onClick={() => { navigate("/perfil"); setMenuOpen(false); }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              Ver perfil
            </button>
            <div style={styles.divider} />
            <button style={{ ...styles.dropdownItem, color: "#c0392b" }} onClick={handleLogout}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
                <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
              Cerrar sesión
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}

const styles: Record<string, React.CSSProperties> = {
  navbar: {
    height: "56px",
    background: "#ffffff",
    borderBottom: "1px solid #cfc0b088",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 1.5rem",
    position: "sticky",
    top: 0,
    zIndex: 100,
    fontFamily: "'Roboto', sans-serif",
  },
  brand: {
    display: "flex",
    alignItems: "center",
    textDecoration: "none",
  },
  logoBox: {
    width: "36px",
    height: "36px",
    background: "#f5f0ea",
    border: "1px solid #cfc0b0",
    borderRadius: "8px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  links: {
    display: "flex",
    alignItems: "center",
    gap: "2rem",
  },
  link: {
    fontSize: "0.85rem",
    fontWeight: 400,
    color: "#9e7e62",
    textDecoration: "none",
  },
  avatar: {
    width: "34px",
    height: "34px",
    borderRadius: "50%",
    background: "#cfc0b0",
    border: "1px solid #b8a08a",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
  },
  userTrigger: {
    display: "flex",
    alignItems: "center",
    gap: "0.6rem",
    cursor: "pointer",
    padding: "4px 6px",
    borderRadius: "8px",
  },
  userText: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-end",
  },
  userName: {
    fontSize: "0.82rem",
    fontWeight: 500,
    color: "#5c3d1e",
    lineHeight: 1.2,
  },
  userRole: {
    fontSize: "0.72rem",
    fontWeight: 300,
    color: "#9e7e62",
    lineHeight: 1.2,
  },
  dropdown: {
    position: "absolute",
    right: 0,
    top: "calc(100% + 8px)",
    background: "#ffffff",
    border: "1px solid #e8ddd5",
    borderRadius: "8px",
    boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
    minWidth: "160px",
    zIndex: 200,
    overflow: "hidden",
  },
  dropdownItem: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    width: "100%",
    padding: "10px 14px",
    background: "none",
    border: "none",
    cursor: "pointer",
    fontSize: "0.83rem",
    color: "#5c3d1e",
    fontFamily: "'Roboto', sans-serif",
    textAlign: "left",
  },
  divider: {
    height: "1px",
    background: "#f0e8e0",
    margin: "0 10px",
  },
};
