# app/models/leave_type.py
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.db import Base

class LeaveType(Base):
    __tablename__ = "leave_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    default_balance = Column(Integer, nullable=False, default=0)
    carry_forward = Column(Boolean, nullable=False, default=False)

    leave_requests = relationship("LeaveRequest", back_populates="leave_type")
