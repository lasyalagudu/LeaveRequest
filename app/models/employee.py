# app/models/employee.py
from sqlalchemy import Column, Integer, String, Date, DateTime, func
from app.core.db import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    department = Column(String(100), nullable=False)
    joining_date = Column(Date, nullable=False)
    annual_allocation = Column(Integer, nullable=False, default=24)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
