from pydantic import BaseModel, EmailStr
from  typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    position: str
    phone: Optional[str] = None
    is_admin: bool = False