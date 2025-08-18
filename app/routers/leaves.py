from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.schemas.leave import LeaveApply, LeaveAction, LeaveOut, LeaveBalanceOut
from app.services.leave_service import LeaveService

router = APIRouter()

@router.post("/", response_model=LeaveOut, status_code=201)
def apply_leave(payload: LeaveApply, db: Session = Depends(get_db)):
    return LeaveService.apply_leave(payload, db)

@router.post("/{leave_id}/action", response_model=LeaveOut)
def act_on_leave(leave_id: int, payload: LeaveAction, db: Session = Depends(get_db)):
    return LeaveService.act_on_leave(leave_id, payload, db)

@router.get("/balance/{employee_id}", response_model=LeaveBalanceOut)
def leave_balance(employee_id: int, db: Session = Depends(get_db)):
    return LeaveService.leave_balance(employee_id, db)
