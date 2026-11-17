"""Excepciones de dominio.

Los servicios lanzan estas excepciones en lugar de ``HTTPException``. Un
handler global en ``main.py`` las traduce a respuestas HTTP con el mismo
formato (``{"detail": ...}``) y código que tenían los routers originales.
"""


class DomainError(Exception):
    status_code = 400

    def __init__(self, detail: str, status_code: int | None = None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail)


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class BusinessRuleError(DomainError):
    status_code = 400


class UnauthorizedError(DomainError):
    status_code = 401


class PermissionDeniedError(DomainError):
    status_code = 403


class LockedError(DomainError):
    status_code = 423


class GoneError(DomainError):
    status_code = 410


class UnprocessableError(DomainError):
    status_code = 422


class ServerError(DomainError):
    status_code = 500
