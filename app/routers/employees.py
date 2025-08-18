# app/routers/employees.py
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List



from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.Webhandler.oauth2 import get_current_user
from app.core.db import get_db
from app.models.employee import Employee
from app.models.user import User
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.schemas.leave import LeaveOut
from app.services.leave_service import LeaveService

router = APIRouter()



@router.post("/", response_model=EmployeeOut, status_code=201)
def add_employee(
    payload: EmployeeCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)  # ✅ get logged-in user
):
    if current_user.role != "admin":  # ✅ check role
        raise HTTPException(status_code=403, detail="Not authorized to add employees")

    if db.query(Employee).filter(Employee.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")

    emp = Employee(
        name=payload.name,
        email=payload.email,
        department=payload.department,
        joining_date=payload.joining_date,
        annual_allocation=payload.annual_allocation or 24,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp

@router.get("/", response_model=List[EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).order_by(Employee.id).all()

@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).get(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

# ✅ Cancel leave (before approval)
@router.delete("/{leave_id}/cancel")
def cancel_leave(
    leave_id: int,
    employee_id: int = Query(..., description="Employee ID performing the cancellation"),
    db: Session = Depends(get_db)
):
    return LeaveService.cancel_leave(leave_id, employee_id, db)

# ✅ Modify leave (before approval)
@router.put("/{leave_id}/modify", response_model=LeaveOut)
def modify_leave(
    leave_id: int,
    employee_id: int = Query(..., description="Employee ID performing the modification"),
    start_date: date = Query(...),
    end_date: date = Query(...),
    reason: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return LeaveService.modify_leave(leave_id, employee_id, start_date, end_date, reason, db)
