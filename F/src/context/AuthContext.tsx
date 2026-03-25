import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { getMe, UserProfile } from "../utils/api";

interface AuthContextType {
  currentUser: UserProfile | null;
  loading: boolean;
  setCurrentUser: (user: UserProfile | null) => void;
}

const AuthContext = createContext<AuthContextType>({
  currentUser: null,
  loading: true,
  setCurrentUser: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  // Lee el usuario del localStorage inmediatamente para mostrarlo sin esperar el fetch
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("session_token");
    if (!token) {
      setLoading(false);
      return;
    }
    // Fetch en segundo plano para obtener datos frescos del backend
    getMe()
      .then((me) => {
        if (me) {
          setCurrentUser(me);
          localStorage.setItem("user", JSON.stringify(me));
        }
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{ currentUser, loading, setCurrentUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}