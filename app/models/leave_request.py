# app/models/leave_request.py
from sqlalchemy import Column, Integer, Date, Enum, DateTime, ForeignKey, String, func
import enum
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.leave_type import LeaveType

class LeaveStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    status = Column(Enum(LeaveStatus), nullable=False, default=LeaveStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    leave_type = relationship("LeaveType", back_populates="leave_requests")
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)

