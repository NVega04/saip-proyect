const MODULE_ALIASES: Record<string, string> = {
  "sales-history": "sales",
};

export function getAllowedModules(): string[] {
  const raw = localStorage.getItem("modules");
  if (!raw) return [];
  return JSON.parse(raw) as string[];
}

export function canAccessModule(moduleId: string, allowedModules: string[]): boolean {
  if (allowedModules.includes("all")) return true;
  if (["dashboard", "acerca", "contacto"].includes(moduleId)) return true;
  const effectiveId = MODULE_ALIASES[moduleId] ?? moduleId;
  return allowedModules.includes(effectiveId);
}
