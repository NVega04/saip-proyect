from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from src.core.password import password_errors
from src.modules.users.schemas import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    accepted_terms: bool = False


class LoginResponse(BaseModel):
    session_token: str
    expires_at: datetime
    user: UserResponse
    terms_required: bool = False


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        errors = password_errors(value)
        if errors:
            raise ValueError("; ".join(errors))
        return value


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        errors = password_errors(value)
        if errors:
            raise ValueError("; ".join(errors))
        return value
