export type StrengthLevel = "vacia" | "debil" | "media" | "fuerte";

interface StrengthResult {
  level: StrengthLevel;
  label: string;
  color: string;
  percent: number;
  hints: string[];
}

/** Mismos criterios y mensajes que `backend/src/core/password.py`. */
export const PASSWORD_POLICY_MESSAGE =
  "La contraseña debe tener al menos 12 caracteres, una mayúscula, una minúscula, un número y un carácter especial.";

const RULES = [
  { hint: "Mínimo 12 caracteres", isValid: (p: string) => p.length >= 12 },
  { hint: "Al menos una mayúscula", isValid: (p: string) => /[A-Z]/.test(p) },
  { hint: "Al menos una minúscula", isValid: (p: string) => /[a-z]/.test(p) },
  { hint: "Al menos un número", isValid: (p: string) => /[0-9]/.test(p) },
  {
    hint: "Al menos un carácter especial",
    isValid: (p: string) => /[^A-Za-z0-9]/.test(p),
  },
];

export function getPasswordStrength(password: string): StrengthResult {
  if (!password) {
    return { level: "vacia", label: "", color: "transparent", percent: 0, hints: [] };
  }

  const hints = RULES.filter((rule) => !rule.isValid(password)).map((rule) => rule.hint);
  const passed = RULES.length - hints.length;
  const percent = passed * 20;

  if (passed <= 2) {
    return { level: "debil", label: "Débil", color: "#e53935", percent, hints };
  }
  if (passed < RULES.length) {
    return { level: "media", label: "Media", color: "#f59e0b", percent, hints };
  }
  return { level: "fuerte", label: "Fuerte", color: "#16a34a", percent: 100, hints: [] };
}
