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
  const location = useLocation();
  const activeMenu = location.pathname.replace("/", "") || "dashboard";

  return (
    <div style={styles.root}>
      <Navbar />
      <div style={styles.body}>
        <Sidebar activeMenu={activeMenu} onMenuChange={() => {}} />
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
  },
};