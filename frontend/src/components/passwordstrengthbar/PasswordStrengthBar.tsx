import { getPasswordStrength } from "../../utils/passwordStrength";
import "./PasswordStrengthBar.css";

interface Props {
  password: string;
}

const icons = {
  debil:  "✕",
  media:  "◐",
  fuerte: "✓",
};

export default function PasswordStrengthBar({ password }: Props) {
  const { level, label, color, hints } = getPasswordStrength(password);

  if (!password) return null;

  return (
    <div className="psb-wrapper">
      <div className="psb-badge" style={{ color, borderColor: color }}>
        <span className="psb-icon">{icons[level as keyof typeof icons]}</span>
        <span className="psb-label">{label}</span>
      </div>
      {hints.length > 0 && (
        <ul className="psb-hints">
          {hints.map((hint) => (
            <li key={hint}>· {hint}</li>
          ))}
        </ul>
      )}
    </div>
  );
}