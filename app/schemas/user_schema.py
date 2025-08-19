from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr
import enum

class RoleEnum(str, enum.Enum):
    employee = "employee"
    admin = "admin"

PasswordStr = constr(min_length=6)

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: RoleEnum = RoleEnum.employee

class UserLogin(BaseModel):
    email: EmailStr   # ✅ email instead of username
    password: str
