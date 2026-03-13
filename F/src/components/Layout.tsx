import { useState } from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import Footer from "./Footer"; // ← componente nuevo

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [activeMenu, setActiveMenu] = useState<string>("dashboard");

  return (
    <>


      <div style={styles.root}>
        <Navbar />
        <div style={styles.body}>
          <Sidebar activeMenu={activeMenu} onMenuChange={setActiveMenu} />
          <main style={styles.content}>
            {children}
          </main>
        </div>
        <Footer /> {/* ← reemplaza el <footer> inline que tenías */}
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
};