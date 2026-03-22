import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { logout } from "../utils/api";
import { useAuth } from "../context/AuthContext";


interface NavbarProps {
  onToggleSidebar?: () => void;
  sidebarOpen?: boolean;
}

export default function Navbar({ onToggleSidebar, sidebarOpen }: NavbarProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isMobile, setIsMobile]   = useState(false);
  const [scrolled, setScrolled]   = useState(false);
  const menuRef                   = useRef<HTMLDivElement>(null);
  const navigate                  = useNavigate();

  // ── Usuario desde contexto global (reemplaza getMe) ──────────────────────
  const { currentUser } = useAuth();

  const user = currentUser
    ? {
        nombre:  `${currentUser.first_name} ${currentUser.last_name}`,
        rol:     currentUser.role.name,
        isAdmin: currentUser.is_admin,
      }
    : null;

  // ── Responsive ────────────────────────────────────────────────────────────
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // ── Scroll ────────────────────────────────────────────────────────────────
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 4);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = async () => {
    setMenuOpen(false);
    await logout();
  };

  const initials = user
    ? `${user.nombre.split(" ")[0]?.[0] ?? ""}${user.nombre.split(" ")[1]?.[0] ?? ""}`.toUpperCase()
    : "";

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        .saip-link {
          position: relative;
          font-family: 'Outfit', system-ui, sans-serif;
          font-size: .82rem; font-weight: 400;
          color: var(--light, #b07248);
          text-decoration: none; padding-bottom: 2px;
          transition: color .2s;
        }
        .saip-link::after {
          content: ''; position: absolute;
          bottom: -2px; left: 0; width: 0; height: 1.5px;
          background: var(--medium, #6b3a18);
          transition: width .25s ease;
        }
        .saip-link:hover { color: var(--dark, #3b1f08); }
        .saip-link:hover::after { width: 100%; }
        .saip-trigger:hover { background: var(--bg, #faf4ec) !important; }
        .saip-dd-item {
          display: flex; align-items: center; gap: 9px;
          width: 100%; padding: 11px 14px;
          background: none; border: none; cursor: pointer;
          font-size: .82rem; font-family: 'Outfit', system-ui, sans-serif;
          text-align: left; transition: background .15s, color .15s;
        }
        .saip-dd-item:hover { background: var(--bg, #faf4ec) !important; color: var(--dark, #3b1f08) !important; }
        .saip-dd-danger { color: var(--danger, #a01818) !important; }
        .saip-dd-danger:hover { background: var(--danger-pale, #fce0e0) !important; }
        .saip-hbg:hover { background: var(--bg, #faf4ec) !important; }
        @keyframes saip-drop {
          from { opacity: 0; transform: translateY(-6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      <nav style={{
        height: "58px",
        background: "var(--white, #fff)",
        borderBottom: scrolled
          ? "1px solid var(--border-s, rgba(107,58,24,0.30))"
          : "1px solid var(--border, rgba(107,58,24,0.18))",
        boxShadow: scrolled ? "0 1px 8px rgba(59,31,8,0.09)" : "none",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 1.5rem",
        position: "sticky", top: 0, zIndex: 100,
        fontFamily: "'Outfit', system-ui, sans-serif",
        transition: "box-shadow 0.25s ease, border-color 0.25s ease",
      }}>

        {/* ── Izquierda ── */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.65rem" }}>
          {isMobile && (
            <button
              className="saip-hbg"
              onClick={onToggleSidebar}
              aria-label="Toggle sidebar"
              style={{
                display: "flex", flexDirection: "column",
                justifyContent: "center", alignItems: "center", gap: "4.5px",
                width: "36px", height: "36px",
                border: "1px solid var(--border-s, rgba(107,58,24,0.30))",
                borderRadius: "7px", cursor: "pointer", padding: "6px",
                background: sidebarOpen ? "var(--bg, #faf4ec)" : "transparent",
                transition: "background 0.2s",
              }}
            >
              {[0, 1, 2].map((i) => (
                <span key={i} style={{
                  display: "block", width: "15px", height: "1.5px",
                  background: "var(--medium, #6b3a18)", borderRadius: "2px",
                  transition: "transform 0.25s ease, opacity 0.2s ease",
                  transform: sidebarOpen
                    ? i === 0 ? "rotate(45deg) translate(4px, 4px)"
                    : i === 2 ? "rotate(-45deg) translate(4px, -4px)" : "none"
                    : "none",
                  opacity: sidebarOpen && i === 1 ? 0 : 1,
                }} />
              ))}
            </button>
          )}

          <Link to="/dashboard" style={{ display: "flex", alignItems: "center", gap: "0.6rem", textDecoration: "none" }}>
            <div style={{
              width: "34px", height: "34px",
              background: "var(--bg, #faf4ec)",
              border: "1px solid var(--border-s, rgba(107,58,24,0.30))",
              borderRadius: "7px",
              display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
            }}>
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none"
                stroke="var(--medium, #6b3a18)" strokeWidth="1.7" strokeLinecap="round">
                <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/>
                <path d="M9 21V12h6v9"/>
              </svg>
            </div>
            {!isMobile && (
              <span style={{
                fontFamily: "'Outfit', system-ui, sans-serif",
                fontSize: "1rem", fontWeight: 700,
                color: "var(--dark, #3b1f08)",
                letterSpacing: "0.07em", lineHeight: 1,
              }}>
                SAIP
              </span>
            )}
          </Link>
        </div>

        {/* ── Centro ── */}
        {!isMobile && (
          <div style={{ display: "flex", alignItems: "center", gap: "2rem" }}>
            <a href="/acerca" className="saip-link">Acerca de nosotros</a>
            <a href="/contacto" className="saip-link">Contacto</a>
          </div>
        )}

        {/* ── Derecha ── */}
        <div ref={menuRef} style={{ position: "relative" }}>
          <div
            className="saip-trigger"
            onClick={() => setMenuOpen(!menuOpen)}
            style={{
              display: "flex", alignItems: "center", gap: "0.55rem",
              cursor: "pointer", padding: "5px 8px",
              borderRadius: "11px", transition: "background 0.18s",
            }}
          >
            {!isMobile && (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "2px" }}>
                <span style={{
                  fontSize: "0.82rem", fontWeight: 600,
                  color: "var(--dark, #3b1f08)",
                  fontFamily: "'Outfit', system-ui, sans-serif", lineHeight: 1,
                }}>
                  {user?.nombre ?? "· · ·"}
                </span>
                <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                  <span style={{
                    fontSize: "0.7rem", fontWeight: 300,
                    color: "var(--mid, #8c5530)", lineHeight: 1,
                    fontFamily: "'Outfit', system-ui, sans-serif",
                  }}>
                    {user?.rol ?? ""}
                  </span>
                  {user && (
                    <span style={{
                      fontSize: "0.59rem", fontWeight: 700, letterSpacing: "0.07em",
                      color: user.isAdmin ? "#1e4a18" : "var(--mid, #8c5530)",
                      background: user.isAdmin ? "#b8e0b0" : "var(--bg, #faf4ec)",
                      border: `1px solid ${user.isAdmin ? "#52a844" : "var(--border-s, rgba(107,58,24,0.30))"}`,
                      borderRadius: "99px", padding: "1px 7px",
                      fontFamily: "'Outfit', system-ui, sans-serif",
                    }}>
                      {user.isAdmin ? "ADMIN" : "USER"}
                    </span>
                  )}
                </div>
              </div>
            )}

            <div style={{
              width: "34px", height: "34px", borderRadius: "50%",
              background: "var(--bg, #faf4ec)",
              border: "1.5px solid var(--border-s, rgba(107,58,24,0.30))",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "0.7rem", fontWeight: 700,
              color: "var(--dark, #3b1f08)",
              fontFamily: "'Outfit', system-ui, sans-serif",
              flexShrink: 0, userSelect: "none",
            }}>
              {initials || (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                  stroke="var(--medium, #6b3a18)" strokeWidth="1.8">
                  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              )}
            </div>

            <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
              stroke="var(--pale, #c99870)" strokeWidth="2.2"
              style={{ transition: "transform 0.2s", transform: menuOpen ? "rotate(180deg)" : "none", flexShrink: 0 }}>
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>

          {menuOpen && (
            <div style={{
              position: "absolute", right: 0, top: "calc(100% + 8px)",
              background: "var(--white, #fff)",
              border: "1px solid var(--border-s, rgba(107,58,24,0.30))",
              borderRadius: "11px",
              boxShadow: "0 4px 20px rgba(59,31,8,0.12)",
              minWidth: "190px", zIndex: 300, overflow: "hidden",
              animation: "saip-drop 0.18s ease",
            }}>
              {isMobile && user && (
                <>
                  <div style={{ padding: "12px 14px 8px", display: "flex", flexDirection: "column", gap: "2px" }}>
                    <span style={{
                      fontSize: "0.83rem", fontWeight: 600,
                      color: "var(--dark, #3b1f08)",
                      fontFamily: "'Outfit', system-ui, sans-serif",
                    }}>
                      {user.nombre}
                    </span>
                    <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                      <span style={{ fontSize: "0.7rem", color: "var(--mid, #8c5530)" }}>{user.rol}</span>
                      <span style={{
                        fontSize: "0.59rem", fontWeight: 700, letterSpacing: "0.07em",
                        color: user.isAdmin ? "#1e4a18" : "var(--mid, #8c5530)",
                        background: user.isAdmin ? "#b8e0b0" : "var(--bg, #faf4ec)",
                        border: `1px solid ${user.isAdmin ? "#52a844" : "var(--border-s, rgba(107,58,24,0.30))"}`,
                        borderRadius: "99px", padding: "1px 7px",
                        fontFamily: "'Outfit', system-ui, sans-serif",
                      }}>
                        {user.isAdmin ? "ADMIN" : "USER"}
                      </span>
                    </div>
                  </div>
                  <div style={{ height: "1px", background: "var(--bg, #faf4ec)", margin: "0 12px" }} />
                </>
              )}

              <button
                className="saip-dd-item"
                style={{ color: "var(--dark, #3b1f08)" }}
                onClick={() => { navigate("/perfil"); setMenuOpen(false); }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                  stroke="var(--mid, #8c5530)" strokeWidth="1.8" strokeLinecap="round">
                  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                Ver perfil
              </button>

              <div style={{ height: "1px", background: "var(--bg, #faf4ec)", margin: "0 12px" }} />

              <button className="saip-dd-item saip-dd-danger" onClick={handleLogout}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
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
    </>
  );
}
