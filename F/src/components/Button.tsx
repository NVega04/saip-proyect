import React from "react";
import "./Button.css";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

interface SAIPButtonProps {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  onClick?: () => void;
  disabled?: boolean;
  type?: "button" | "submit" | "reset";
  icon?: React.ReactNode;
  className?: string;
}

export default function Button({
  children,
  variant = "ghost",
  size = "md",
  onClick,
  disabled = false,
  type = "button",
  icon,
  className = "",
}: SAIPButtonProps) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`saip-btn saip-btn--${variant} saip-btn--${size} ${className}`}
    >
      {icon && <span className="saip-btn__icon">{icon}</span>}
      {children}
    </button>
  );
}
