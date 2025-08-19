# app/routers/employees.py
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic_core import ValidationError
from sqlalchemy.orm import Session
from typing import Optional
from passlib.context import CryptContext
import secrets

from app.Webhandler.oauth2 import get_current_user
from app.core.db import get_db
from app.models.employee import Employee
from app.models.user import User, RoleEnum
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.schemas.leave import LeaveOut
from app.services.leave_service import LeaveService
from app.core.mail import send_password_setup_email

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



@router.post("/", response_model=EmployeeOut, status_code=201)
async def add_employee(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only admin can add employees
    if current_user.role != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Not authorized to add employees")

    payload_dict = await request.json()

    # Validate input manually
    try:
        payload = EmployeeCreate(**payload_dict)
    except ValidationError as e:
        errors = [{"loc": err["loc"], "msg": err["msg"]} for err in e.errors()]
        raise HTTPException(status_code=422, detail=errors)

    # Check duplicate email
    if db.query(Employee).filter(Employee.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")

    # Generate password setup token
    setup_token = secrets.token_urlsafe(32)

    # Create Employee record
    emp = Employee(
        name=payload.name,
        email=payload.email,
        phone_number=payload.phone_number,
        job_type=payload.job_type,
        address=payload.address,
        domain=payload.domain,
        joining_date=payload.joining_date,
        annual_allocation=payload.annual_allocation or 24,
        first_login=True,
        password_setup_token=setup_token,
    )

    db.add(emp)
    db.commit()
    db.refresh(emp)

    # Create corresponding User record
    user = User(
        email=payload.email,
        password=None,  # Will be set after employee sets password
        role=RoleEnum.employee,
    )
    db.add(user)
    db.commit()

    # Send password setup email
    try:
        send_password_setup_email(emp.email, setup_token)
    except Exception as e:
        print("⚠️ Failed to send email:", e)

    return emp

# ✅ Cancel leave (before approval)
@router.delete("/{leave_id}/cancel")
def cancel_leave(
    leave_id: int,
    employee_id: int = Query(..., description="Employee ID performing the cancellation"),
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
):
    return LeaveService.modify_leave(leave_id, employee_id, start_date, end_date, reason, db)
