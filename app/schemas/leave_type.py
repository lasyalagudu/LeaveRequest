from pydantic import BaseModel, Field
from typing import Optional

class LeaveTypeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    default_balance: int = Field(..., ge=0, description="Default number of leave days")
    carry_forward: bool = False

class LeaveTypeCreate(LeaveTypeBase):
    pass

class LeaveTypeOut(LeaveTypeBase):
    id: int

    class Config:
        from_attributes = True
