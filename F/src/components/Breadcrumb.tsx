import { Link } from "react-router-dom";
import "./Breadcrumb.css";

interface BreadcrumbItem {
  label: string;
  to?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export default function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav className="saip-breadcrumb" aria-label="breadcrumb">
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <span key={index} className="saip-breadcrumb__item">
            {!isLast && item.to ? (
              <Link to={item.to} className="saip-breadcrumb__link">
                {item.label}
              </Link>
            ) : (
              <span className="saip-breadcrumb__current">{item.label}</span>
            )}

            {!isLast && <span className="saip-breadcrumb__separator">/</span>}
          </span>
        );
      })}
    </nav>
  );
}