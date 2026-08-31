const API_URL = import.meta.env.VITE_API_URL;

interface ApiFetchOptions extends RequestInit {
  skipAuthRedirect?: boolean;
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
    localStorage.clear();
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