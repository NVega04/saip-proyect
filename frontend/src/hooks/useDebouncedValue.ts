import { useEffect, useState } from "react";

/**
 * Devuelve ``value`` después de ``delay`` ms sin cambios.
 * Evita disparar una petición por cada tecla en los buscadores.
 */
export function useDebouncedValue<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
