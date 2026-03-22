import { useLocation } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import Footer from "./Footer"; // ← componente nuevo

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  // Deriva el activeMenu desde la ruta actual en lugar de estado local
  const activeMenu = location.pathname.replace("/", "") || "dashboard";

  return (
    <>
      <div style={styles.root}>
        <Navbar />
        <div style={styles.body}>
          <Sidebar activeMenu={activeMenu} onMenuChange={() => {}} />
          <main style={styles.content}>
            {children}
          </main>
        </div>
        <Footer />
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