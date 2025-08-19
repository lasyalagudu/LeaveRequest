# app/models/employee.py
from pydantic import ValidationError
from sqlalchemy import BigInteger, Column, Integer, String, Date, DateTime, func,Boolean
from app.core.db import Base
from app.schemas.employee import EmployeeCreate

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(BigInteger, nullable=True)
    job_type = Column(String(100), nullable=True)
    address = Column(String(100), nullable=True)
    domain = Column(String(100), nullable=False)
    joining_date = Column(Date, nullable=False)
    annual_allocation = Column(Integer, nullable=False, default=24)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    hashed_password = Column(String(255), nullable=True)  # temp password will be hashed
    first_login = Column(Boolean, default=True)           # forces password reset
    password_setup_token = Column(String(255), nullable=True)  # token for password setup
    
