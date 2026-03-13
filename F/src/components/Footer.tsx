const styles: Record<string, React.CSSProperties> = {
  footer: {
    background: "#ffffff",
    borderTop: "1px solid #cfc0b066",
    padding: "1.75rem 2.5rem",
    fontFamily: "'Roboto', sans-serif",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1.4fr 1fr 1fr 1fr",
    gap: "1.5rem",
    marginBottom: "1.25rem",
  },
  col: {
    display: "flex",
    flexDirection: "column",
    gap: "0.5rem",
  },
  colTitle: {
    fontSize: "0.72rem",
    fontWeight: 600,
    color: "#5c3d1e",
    textTransform: "uppercase" as const,
    letterSpacing: "0.07em",
    marginBottom: "0.3rem",
  },
  brandRow: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    marginBottom: "0.15rem",
  },
  logoBox: {
    width: "26px",
    height: "26px",
    background: "#f5f0ea",
    border: "1px solid #cfc0b0",
    borderRadius: "6px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  brandName: {
    fontSize: "0.85rem",
    fontWeight: 700,
    color: "#5c3d1e",
  },
  brandDesc: {
    fontSize: "0.72rem",
    fontWeight: 300,
    color: "#9e7e62",
    lineHeight: 1.6,
    maxWidth: "180px",
  },
  linkList: {
    display: "flex",
    flexDirection: "column",
    gap: "0.4rem",
  },
  link: {
    fontSize: "0.78rem",
    fontWeight: 400,
    color: "#9e7e62",
    textDecoration: "none",
  },
  // Columna de redes sociales
  socialTitle: {
    fontSize: "0.72rem",
    fontWeight: 600,
    color: "#5c3d1e",
    textTransform: "uppercase" as const,
    letterSpacing: "0.07em",
    marginBottom: "0.3rem",
  },
  socialIcons: {
    display: "flex",
    gap: "0.5rem",
    flexWrap: "wrap" as const,
  },
  socialIcon: {
    width: "32px",
    height: "32px",
    borderRadius: "8px",
    border: "1px solid #cfc0b0",
    background: "#f5f0ea",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    transition: "all 0.15s ease",
  },
  // Línea inferior
  bottom: {
    borderTop: "1px solid #f0e8e0",
    paddingTop: "1rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  copy: {
    fontSize: "0.68rem",
    color: "#b8a08a",
  },
  bottomLinks: {
    display: "flex",
    gap: "1.25rem",
  },
  bottomLink: {
    fontSize: "0.68rem",
    color: "#b8a08a",
    textDecoration: "none",
  },
};

export default function Footer() {
  return (
    <footer style={styles.footer}>
      <div style={styles.grid}>

        {/* Columna 1: Marca */}
        <div style={styles.col}>
          <div style={styles.brandRow}>
            <div style={styles.logoBox}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                stroke="#7d5a3c" strokeWidth="1.5">
                <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
              </svg>
            </div>
            <span style={styles.brandName}>SAIP</span>
          </div>
          <p style={styles.brandDesc}>
            Sistema Administrativo Integral de Productos. Gestiona tu negocio de forma simple y eficiente.
          </p>
        </div>

        {/* Columna 2: Navegación */}
        <div style={styles.col}>
          <span style={styles.colTitle}>Navegación</span>
          <div style={styles.linkList}>
            <a href="#" style={styles.link}>Inventario</a>
            <a href="#" style={styles.link}>Proveedores</a>
            <a href="#" style={styles.link}>Ventas</a>
            <a href="#" style={styles.link}>Producción</a>
          </div>
        </div>

        {/* Columna 3: Soporte */}
        <div style={styles.col}>
          <span style={styles.colTitle}>Soporte</span>
          <div style={styles.linkList}>
            <a href="#" style={styles.link}>Acerca de SAIP</a>
            <a href="#" style={styles.link}>Contacto</a>
            <a href="#" style={styles.link}>Ayuda</a>
          </div>
        </div>

        {/* Columna 4: Redes sociales */}
        <div style={styles.col}>
          <span style={styles.socialTitle}>Síguenos</span>
          <div style={styles.socialIcons}>
            {/* Instagram */}
            <div style={styles.socialIcon} title="Instagram">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                stroke="#9e7e62" strokeWidth="1.6">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
                <circle cx="12" cy="12" r="4"/>
                <circle cx="17.5" cy="6.5" r="1" fill="#9e7e62" stroke="none"/>
              </svg>
            </div>
            {/* Facebook */}
            <div style={styles.socialIcon} title="Facebook">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                stroke="#9e7e62" strokeWidth="1.6">
                <path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/>
              </svg>
            </div>
            {/* Twitter/X */}
            <div style={styles.socialIcon} title="Twitter">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                stroke="#9e7e62" strokeWidth="1.6">
                <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z"/>
              </svg>
            </div>
            {/* LinkedIn */}
            <div style={styles.socialIcon} title="LinkedIn">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                stroke="#9e7e62" strokeWidth="1.6">
                <path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6z"/>
                <rect x="2" y="9" width="4" height="12"/>
                <circle cx="4" cy="4" r="2"/>
              </svg>
            </div>
          </div>
        </div>

      </div>

      {/* Línea inferior con copyright */}
      <div style={styles.bottom}>
        <span style={styles.copy}>© {new Date().getFullYear()} SAIP — Todos los derechos reservados</span>
        <div style={styles.bottomLinks}>
          <a href="#" style={styles.bottomLink}>Términos de uso</a>
          <a href="#" style={styles.bottomLink}>Privacidad</a>
        </div>
      </div>

    </footer>
  );
}