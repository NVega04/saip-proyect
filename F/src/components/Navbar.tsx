import React from "react";

export default function Navbar() {
  return (
    <nav style={styles.navbar}>
      <a href="#" style={styles.brand}>
        <div style={styles.logoBox}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.5">
            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
          </svg>
        </div>
      </a>

      <div style={styles.links}>
        <a href="#" style={styles.link}>Acerca de nosotros</a>
        <a href="#" style={styles.link}>Contacto</a>
      </div>

      <div style={styles.avatar}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7d5a3c" strokeWidth="1.5">
          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
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
};