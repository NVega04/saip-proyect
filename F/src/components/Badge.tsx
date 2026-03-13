import "./Badge.css";

type BadgeVariant = "access" | "active" | "inactive" | "warning";

interface BadgeProps {
  label: string;
  variant?: BadgeVariant;
}

export default function Badge({ label, variant = "access" }: BadgeProps) {
  return (
    <span className={`saip-badge saip-badge--${variant}`}>
      {label}
    </span>
  );
}
