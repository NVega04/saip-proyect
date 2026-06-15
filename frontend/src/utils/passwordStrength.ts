export type StrengthLevel = "vacia" | "debil" | "media" | "fuerte";

interface StrengthResult {
  level: StrengthLevel;
  label: string;
  color: string;
  percent: number;
  hints: string[];
}

export function getPasswordStrength(password: string): StrengthResult {
  if (!password) return { level: "vacia", label: "", color: "transparent", percent: 0, hints: [] };

  const hints: string[] = [];
  if (password.length < 8)       hints.push("Mínimo 8 caracteres");
  if (!/[A-Z]/.test(password))   hints.push("Al menos una mayúscula");
  if (!/[0-9]/.test(password))   hints.push("Al menos un número");

  const passed = 3 - hints.length;

  if (passed === 0) return { level: "debil",  label: "Débil",   color: "#e53935", percent: 25,  hints };
  if (passed === 1) return { level: "debil",  label: "Débil",   color: "#e53935", percent: 33,  hints };
  if (passed === 2) return { level: "media",  label: "Media",   color: "#f59e0b", percent: 66,  hints };
  return             { level: "fuerte", label: "Fuerte",  color: "#16a34a", percent: 100, hints: [] };
}