import { useState } from "react";
import { useLocation } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import Footer from "./Footer";
import Breadcrumb from "./Breadcrumb";

interface BreadcrumbItem {
  label: string;
  to?: string;
}

interface LayoutProps {
  children: React.ReactNode;
  breadcrumbs?: BreadcrumbItem[];
}

export default function Layout({ children, breadcrumbs = [] }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const activeMenu = location.pathname.replace("/", "") || "dashboard";
  const [sidebarHover, setSidebarHover] = useState(false);
  const isSidebarVisible = sidebarOpen || sidebarHover;

  return (
    <div style={styles.root}>
      <Navbar
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        sidebarOpen={sidebarOpen}
      />
      <div style={styles.body}>
        {!sidebarOpen && (
          <div
            onMouseEnter={() => setSidebarHover(true)}
            onMouseLeave={() => setSidebarHover(false)}
            style={{
              position: "fixed",
              top: "58px",
              left: 0,
              width: "10px",
              height: "100vh",
              zIndex: 120,
            }}
          />
        )}
        <Sidebar
          activeMenu={activeMenu}
          onMenuChange={() => {}}
          isOpen={isSidebarVisible}
          onClose={() => setSidebarOpen(false)}
        />
        <main style={styles.content}>
          {breadcrumbs.length > 0 && <Breadcrumb items={breadcrumbs} />}
          {children}
        </main>
      </div>
      <Footer />
    </div>
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
    minWidth: 0,
  },
    floatingButton: {
    position: "fixed",
    top: "70px",
    left: "12px",
    zIndex: 300,
    width: "40px",
    height: "40px",
    borderRadius: "8px",
    border: "none",
    background: "var(--bakery-sidebar-bg)",
    color: "#fff",
    fontSize: "18px",
    cursor: "pointer",
    boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
  },
};
