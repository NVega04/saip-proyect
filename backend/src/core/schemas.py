from pydantic import BaseModel, field_validator


class UppercaseMixin:
    EXCLUDE_FIELDS = {
        "email",
        "description",
        "password",
        "token",
        "new_password",
        "current_password",
        "notas",
        "observaciones",
        "status",
    }

    @field_validator("*", mode="before")
    @classmethod
    def uppercase_strings(cls, v, info):
        if info.field_name in cls.EXCLUDE_FIELDS:
            return v
        if isinstance(v, str) and v.strip():
            return v.upper().strip()
        return v


class BulkRowError(BaseModel):
    fila: int
    mensaje: str


class BulkImportResult(BaseModel):
    total: int
    creados: int
    actualizados: int = 0
    errores: list[BulkRowError] = []
