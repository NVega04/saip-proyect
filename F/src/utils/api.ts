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