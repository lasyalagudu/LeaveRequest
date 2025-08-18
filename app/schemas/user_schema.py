from pydantic import BaseModel, EmailStr
import enum

class RoleEnum(str, enum.Enum):
    employee = "employee"
    admin = "admin"

class UserCreate(BaseModel):
    email: EmailStr   # ✅ email instead of username
    password: str
    role: RoleEnum = RoleEnum.employee

class UserLogin(BaseModel):
    email: EmailStr   # ✅ email instead of username
    password: str
