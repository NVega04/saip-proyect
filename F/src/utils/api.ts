const API_URL = "http://localhost:8000";

export async function apiFetch(endpoint: string, options?: RequestInit): Promise<Response> {
  const token = localStorage.getItem("session_token");

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "session_token": token ?? "",
      ...options?.headers,
    },
  });

  if (response.status === 401) {
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