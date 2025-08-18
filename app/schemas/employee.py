# app/schemas/employee.py
from pydantic import BaseModel, EmailStr, field_validator
from datetime import date

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    department: str
    joining_date: date
    annual_allocation: int | None = None

    @field_validator("annual_allocation")
    @classmethod
    def non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("annual_allocation must be >= 0")
        return v

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    joining_date: date
    annual_allocation: int

    class Config:
        from_attributes = True
