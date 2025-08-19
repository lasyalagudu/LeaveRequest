# app/schemas/employee.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional
import re

class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Employee's full name")
    email: EmailStr
    domain: str
    joining_date: date
    annual_allocation: int | None = None
    phone_number: int = Field(..., description="10-digit phone number")  # required int
    job_type: Optional[str] = None
    address: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):
        if not re.fullmatch(r"[A-Za-z ]+", v.strip()):
            raise ValueError("name must contain only alphabets and spaces")
        return v

    @field_validator("annual_allocation")
    @classmethod
    def non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("annual_allocation must be >= 0")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: int):
        # ensure it's exactly 10 digits
        if len(str(v)) != 10:
            raise ValueError("phone_number must be exactly 10 digits")
        return v


class EmployeeCreate(EmployeeBase):
    """Used when HR/Admin creates a new employee"""
    pass


class EmployeeOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    domain: str
    joining_date: date
    annual_allocation: int
    first_login: bool
    phone_number: int  # required, not optional anymore
    job_type: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeWithTempPassword(EmployeeOut):
    """Optional schema when returning info with temp password (internal use only)"""
    temp_password: Optional[str] = None
    password_setup_token: Optional[str] = None
