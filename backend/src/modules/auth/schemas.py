from datetime import datetime

from pydantic import BaseModel, EmailStr

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


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
