import React, { useState } from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [activeMenu, setActiveMenu] = useState<string>("inventario");

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Roboto', sans-serif; background: #f5f0ea; }
      `}</style>

      <div style={styles.root}>
        <Navbar />

        <div style={styles.body}>
          <Sidebar activeMenu={activeMenu} onMenuChange={setActiveMenu} />
          <main style={styles.content}>
            {children}
          </main>
        </div>

        <footer style={styles.footer}>
          <div style={styles.footerLinks}>
            <a href="#" style={styles.footerLink}>Contacto</a>
            <a href="#" style={styles.footerLink}>SAIP</a>
          </div>
          <div style={styles.footerSocial}>
            <div style={styles.footerIcon}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#9e7e62" strokeWidth="1.5">
                <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
              </svg>
            </div>
            <div style={styles.footerIcon}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#9e7e62" strokeWidth="1.5">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
                <circle cx="12" cy="12" r="4"/>
                <circle cx="17.5" cy="6.5" r="1" fill="#9e7e62" stroke="none"/>
              </svg>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}

const styles: Record<string, React.CSSProperties> = {
  root: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    background: "#f5f0ea",
  },
  body: {
    display: "flex",
    flex: 1,
  },
  content: {
    flex: 1,
    padding: "2rem 2.5rem",
    overflowY: "auto",
  },
  footer: {
    background: "#ffffff",
    borderTop: "1px solid #cfc0b066",
    padding: "1rem 3rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    fontFamily: "'Roboto', sans-serif",
  },
  footerLinks: {
    display: "flex",
    gap: "2rem",
  },
  footerLink: {
    fontSize: "0.75rem",
    fontWeight: 400,
    color: "#9e7e62",
    textDecoration: "none",
  },
  footerSocial: {
    display: "flex",
    gap: "0.75rem",
    alignItems: "center",
  },
  footerIcon: {
    width: "28px",
    height: "28px",
    borderRadius: "50%",
    border: "1px solid #cfc0b0",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
  },
};