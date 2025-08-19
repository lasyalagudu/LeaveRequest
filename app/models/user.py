from sqlalchemy import Column, Integer, String, Enum
from app.core.db import Base
import enum

class RoleEnum(str, enum.Enum):
    employee = "employee"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)  # ✅ replaced username with email
    password = Column(String, nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.employee)
