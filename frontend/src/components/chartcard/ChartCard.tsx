import React from "react";

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}

export default function ChartCard({
  title,
  subtitle,
  children,
}: ChartCardProps): JSX.Element {
  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h3 style={styles.title}>{title}</h3>
        {subtitle && <span style={styles.subtitle}>{subtitle}</span>}
      </div>
      <div style={styles.body}>{children}</div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    background: "#f2f2f2",
    border: "1px solid #bcc7d066",
    borderRadius: "8px",
    padding: "1.25rem 1.5rem",
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
    fontFamily: "'Roboto', sans-serif",
    minWidth: 0,
  },
  header: {
    display: "flex",
    flexDirection: "column",
    gap: "0.15rem",
  },
  title: {
    margin: 0,
    fontSize: "1rem",
    fontWeight: 700,
    color: "#16425b",
  },
  subtitle: {
    fontSize: "0.75rem",
    color: "#647a8a",
  },
  body: {
    flex: 1,
    minWidth: 0,
  },
};
