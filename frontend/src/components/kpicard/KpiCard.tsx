import React from "react";

interface KpiCardProps {
  label: string;
  value: string | number;
  accent?: "default" | "warning" | "danger" | "success";
  hint?: string;
  variant?: "info" | "alert";
}

export default function KpiCard({
  label,
  value,
  accent = "default",
  hint,
  variant = "info",
}: KpiCardProps): JSX.Element {
  const accentColor = ACCENTS[accent] ?? ACCENTS.default;
  const isAlert = variant === "alert";

  return (
    <div
      style={{
        ...styles.card,
        borderLeft: `${isAlert ? "6px" : "4px"} solid ${accentColor}`,
        background: isAlert ? ALERT_BG[accent] ?? "#fdf0ef" : "#f2f2f2",
      }}
    >
      <span style={{ ...styles.value, color: accentColor }}>{value}</span>
      <span style={{ ...styles.label, ...(isAlert ? { color: accentColor } : {}) }}>
        {label}
      </span>
      {hint && <span style={styles.hint}>{hint}</span>}
    </div>
  );
}

const ACCENTS: Record<string, string> = {
  default: "#3a7ca5",
  warning: "#d99a2b",
  danger: "#c0392b",
  success: "#27ae60",
};

const ALERT_BG: Record<string, string> = {
  danger: "#fdf0ef",
  warning: "#fef9e7",
  success: "#edf7ed",
  default: "#f2f2f2",
};

const styles: Record<string, React.CSSProperties> = {
  card: {
    background: "#f2f2f2",
    border: "1px solid #bcc7d066",
    borderRadius: "8px",
    padding: "1.1rem 1.4rem",
    display: "flex",
    flexDirection: "column",
    gap: "0.2rem",
    fontFamily: "'Roboto', sans-serif",
    minWidth: 0,
  },
  value: {
    fontSize: "1.7rem",
    fontWeight: 700,
    lineHeight: 1.2,
  },
  label: {
    fontSize: "0.85rem",
    fontWeight: 700,
    color: "#16425b",
  },
  hint: {
    fontSize: "0.72rem",
    color: "#647a8a",
  },
};
