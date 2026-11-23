import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch, ApiError, toApiError } from "../utils/api";

/** Envelope paginado del backend: {items, total, page, limit}. */
export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

async function getJson<T>(endpoint: string): Promise<T> {
  const response = await apiFetch(endpoint);
  if (!response.ok) throw await toApiError(response);
  return response.json() as Promise<T>;
}

/**
 * Listado sin paginar (endpoints que aún devuelven arreglo plano).
 * La clave incluye la ruta para poder invalidarla tras una mutación con
 * ``invalidateQueries({ queryKey: ["list", ruta] })``.
 */
export function useListQuery<T>(endpoint: string, enabled = true) {
  return useQuery<T[], ApiError>({
    queryKey: ["list", endpoint],
    queryFn: () => getJson<T[]>(endpoint),
    enabled,
  });
}

export interface PagedParams {
  page: number;
  limit: number;
  search?: string;
}

/**
 * Listado paginado por servidor (``page``/``limit`` + envelope).
 * ``keepPreviousData`` evita parpadeos al cambiar de página.
 */
export function usePagedQuery<T>(basePath: string, params: PagedParams) {
  const query = new URLSearchParams({
    page: String(params.page),
    limit: String(params.limit),
  });
  if (params.search?.trim()) query.set("search", params.search.trim());
  const endpoint = `${basePath}?${query.toString()}`;

  return useQuery<Page<T>, ApiError>({
    queryKey: ["paged", basePath, { ...params }],
    queryFn: () => getJson<Page<T>>(endpoint),
    placeholderData: keepPreviousData,
  });
}
