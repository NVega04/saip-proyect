import { MENSAJES_VALIDACION } from "../constants/validations.constants";

/**
 * Valida que un campo de texto no esté vacío (ignorando espacios).
 * Devuelve el mensaje de error o `undefined` si el campo es válido.
 */
export function validarCampoRequerido(
  valor: string,
  mensajeError: string = MENSAJES_VALIDACION.nombreRequerido
): string | undefined {
  return valor.trim() ? undefined : mensajeError;
}

/**
 * Valida que un valor de texto no exceda la longitud máxima permitida.
 * Devuelve el mensaje de error o `undefined` si el valor es válido.
 */
export function validarLongitudMaxima(
  valor: string,
  longitudMaxima: number
): string | undefined {
  return valor.length > longitudMaxima
    ? MENSAJES_VALIDACION.maximoCaracteres(longitudMaxima)
    : undefined;
}
