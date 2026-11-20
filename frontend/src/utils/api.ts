const API_URL = import.meta.env.VITE_API_URL;

interface ApiFetchOptions extends RequestInit {
  skipAuthRedirect?: boolean;
}

/** Clave para avisar, tras una recarga, que la sesión había expirado. */
export const SESSION_NOTICE_KEY = "session_notice";

const STATUS_MESSAGES: Record<number, string> = {
  400: "La solicitud no es válida.",
  401: "Tu sesión ha expirado. Inicia sesión nuevamente.",
  403: "No tienes permisos para realizar esta acción.",
  404: "El recurso solicitado no existe.",
  409: "La operación entra en conflicto con el estado actual del registro.",
  410: "El recurso ya no está disponible.",
  422: "Los datos enviados no son válidos.",
  429: "Demasiados intentos. Espera un momento y vuelve a intentarlo.",
  500: "Error interno del servidor. Intenta de nuevo.",
  503: "El servicio no está disponible. Intenta de nuevo.",
};

/** Error de la API con el código HTTP y un mensaje en español. */
export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/**
 * Convierte una respuesta fallida en un ``ApiError``.
 * Usa el ``detail`` del backend si existe; si no, un mensaje genérico
 * por código de estado (401/403/429 incluidos).
 */
export async function toApiError(response: Response): Promise<ApiError> {
  let detail = "";
  try {
    const data = await response.json();
    if (typeof data?.detail === "string") detail = data.detail;
  } catch {
    // Respuesta sin cuerpo JSON: se usa el mensaje por defecto.
  }
  return new ApiError(
    response.status,
    detail ||
      STATUS_MESSAGES[response.status] ||
      `Error del servidor (${response.status}).`
  );
}

export async function apiFetch(endpoint: string, options?: ApiFetchOptions): Promise<Response> {
  const token = localStorage.getItem("session_token");

  const isFormData = options?.body instanceof FormData;

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "session-token": token ?? "",
      ...(!isFormData ? { "Content-Type": "application/json" } : {}),
      ...options?.headers,
    },
  });

  if (response.status === 401 && !options?.skipAuthRedirect) {
    // La recarga borra el estado en memoria: se limpia todo y se deja el
    // aviso el último para que AlertContext lo muestre en la siguiente
    // pantalla.
    localStorage.clear();
    localStorage.setItem(
      SESSION_NOTICE_KEY,
      "Tu sesión ha expirado. Inicia sesión nuevamente."
    );
    window.location.href = "/";
  }

  return response;
}

export async function logout(): Promise<void> {
  try {
    await apiFetch("/session/logout", { method: "POST" });
  } finally {
    localStorage.clear();
    window.location.href = "/login";
  }
}

export interface UserProfile {
  id: number;
  first_name: string;
  last_name: string;
  phone: string | null;
  email: string;
  role: { name: string };
  is_admin: boolean;
  created_at: string;
}

export async function getMe(): Promise<UserProfile | null> {
  try {
    const res = await apiFetch("/users/me");
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}
