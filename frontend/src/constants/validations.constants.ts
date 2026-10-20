/**
 * Constantes de validación de formularios.
 *
 * `LONGITUDES_MAX` replica los `max_length` definidos en los modelos del
 * backend (SQLModel). Centralizarlas aquí evita números mágicos
 * hardcodeados en cada página y garantiza un único punto de mantenimiento.
 */
export const LONGITUDES_MAX = {
  name: 100,
  abbreviation: 20,
  description: 255,
} as const;

/**
 * Mensajes de error de validación compartidos entre formularios.
 */
export const MENSAJES_VALIDACION = {
  nombreRequerido: "El nombre es requerido",
  abreviaturaRequerida: "La abreviatura es requerida",
  cantidadNegativa: "La cantidad no puede ser negativa",
  maximoCaracteres: (maximo: number): string => `Maximo ${maximo} caracteres`,
} as const;
