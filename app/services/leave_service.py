from datetime import date, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.config import Settings, settings
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest, LeaveStatus
from app.schemas.leave import LeaveApply, LeaveAction, LeaveOut, LeaveBalanceOut
from app.services.holidays import fetch_holidays, workdays


class LeaveService:
    @staticmethod
    def _calc_days(start, end) -> int:
        return (end - start).days + 1

    @staticmethod
    def apply_leave(payload: LeaveApply, db: Session) -> LeaveOut:
        errors: List[Dict[str, str]] = []
        today = date.today()

        emp = db.get(Employee, payload.employee_id)
        if not emp:
            errors.append({"employee_id": "Employee not found"})

        if payload.start_date < today:
            errors.append({"start_date": "Start date cannot be in the past"})
        if payload.end_date < today:
            errors.append({"end_date": "End date cannot be in the past"})

        if not emp and errors:
            raise HTTPException(status_code=400, detail=errors)

        if payload.start_date < emp.joining_date:
            errors.append({"start_date": "Cannot apply leave before joining date"})

        if payload.end_date < payload.start_date:
            errors.append({"date_range": "End date cannot be before start date"})

        overlap_exists = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == emp.id,
            LeaveRequest.status != LeaveStatus.REJECTED,
            LeaveRequest.start_date <= payload.end_date,
            LeaveRequest.end_date >= payload.start_date,
        ).first()
        if overlap_exists:
            errors.append({"overlap": "Overlapping leave request exists"})

        holidays = fetch_holidays(country=settings.COUNTRY, year=payload.start_date.year)
        days = workdays(payload.start_date, payload.end_date, holidays)

        approved_days = sum(
            workdays(l.start_date, l.end_date, fetch_holidays(settings.COUNTRY, l.start_date.year))
            for l in db.query(LeaveRequest).filter(
                LeaveRequest.employee_id == emp.id,
                LeaveRequest.status == LeaveStatus.APPROVED
            ).all()
        )

        remaining = emp.annual_allocation - approved_days
        if days > remaining:
            errors.append({"balance": f"Not enough balance. Remaining: {remaining}"})

        if errors:
            raise HTTPException(status_code=400, detail=errors)

        lr = LeaveRequest(
            employee_id=emp.id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            days=days,
            reason=payload.reason or None,
            status=LeaveStatus.PENDING,
            leave_type_id=payload.leave_type_id, 
        )
        db.add(lr)
        db.commit()
        db.refresh(lr)

        # Return as LeaveOut Pydantic model
        return LeaveOut(
            id=lr.id,
            employee_id=lr.employee_id,
            start_date=lr.start_date,
            end_date=lr.end_date,
            days=days,
            status=lr.status,
            reason=lr.reason,
            created_at=getattr(lr, 'created_at', None),
            approved_at=getattr(lr, 'approved_at', None),
            approver_note=getattr(lr, 'approver_note', None),
        )

    @staticmethod
    def act_on_leave(leave_id: int, payload: LeaveAction, db: Session) -> LeaveOut:
        lr = db.query(LeaveRequest).get(leave_id)
        if not lr:
            raise HTTPException(status_code=404, detail="Leave request not found")

        if lr.status != LeaveStatus.PENDING:
            raise HTTPException(status_code=400, detail="Only PENDING requests can be acted upon")

        action = payload.action.upper()
        if action not in {"APPROVE", "REJECT"}:
            raise HTTPException(status_code=400, detail="action must be APPROVE or REJECT")

        if action == "APPROVE":
            emp = db.query(Employee).get(lr.employee_id)
            approved_days = sum(l.days for l in db.query(LeaveRequest).filter(
                LeaveRequest.employee_id == emp.id,
                LeaveRequest.status == LeaveStatus.APPROVED
            ).all())
            remaining = emp.annual_allocation - approved_days
            if lr.days > remaining:
                raise HTTPException(status_code=400, detail=f"Not enough balance to approve. Remaining: {remaining}")
            lr.status = LeaveStatus.APPROVED
        else:
            lr.status = LeaveStatus.REJECTED

        db.add(lr)
        db.commit()
        db.refresh(lr)

        # Return as LeaveOut Pydantic model with existing lr.days (workdays)
        return LeaveOut(
            id=lr.id,
            employee_id=lr.employee_id,
            start_date=lr.start_date,
            end_date=lr.end_date,
            days=lr.days,
            status=lr.status,
            reason=lr.reason,
            created_at=getattr(lr, 'created_at', None),
            approved_at=getattr(lr, 'approved_at', None),
            approver_note=getattr(lr, 'approver_note', None),
        )

    @staticmethod
    def leave_balance(employee_id: int, db: Session) -> LeaveBalanceOut:
        emp = db.query(Employee).get(employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")

        used = sum(l.days for l in db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status == LeaveStatus.APPROVED
        ).all())

        return LeaveBalanceOut(
            employee_id=employee_id,
            allocation=emp.annual_allocation,
            used=used,
            remaining=emp.annual_allocation - used,
        )

    # ✅ Cancel leave (only PENDING)
    @staticmethod
    def cancel_leave(leave_id: int, employee_id: int, db: Session):
        lr = db.query(LeaveRequest).filter(
            LeaveRequest.id == leave_id,
            LeaveRequest.employee_id == employee_id
        ).first()

        if not lr:
            raise HTTPException(status_code=404, detail="Leave request not found")
        if lr.status != LeaveStatus.PENDING:
            raise HTTPException(status_code=400, detail="Only PENDING leave can be cancelled")

        db.delete(lr)
        db.commit()
        return {"message": "Leave request cancelled successfully"}

    # ✅ Modify leave (only PENDING)
    @staticmethod
    def modify_leave(leave_id: int, employee_id: int, start_date: date, end_date: date, reason: str, db: Session) -> LeaveOut:
        lr = db.query(LeaveRequest).filter(
            LeaveRequest.id == leave_id,
            LeaveRequest.employee_id == employee_id
        ).first()

        if not lr:
            raise HTTPException(status_code=404, detail="Leave request not found")
        if lr.status != LeaveStatus.PENDING:
            raise HTTPException(status_code=400, detail="Only PENDING leave can be modified")

        holidays = fetch_holidays(country=settings.COUNTRY, year=start_date.year)
        days = workdays(start_date, end_date, holidays)

        lr.start_date = start_date
        lr.end_date = end_date
        lr.reason = reason
        lr.days = days

        db.commit()
        db.refresh(lr)

        # Return as LeaveOut Pydantic model
        return LeaveOut(
            id=lr.id,
            employee_id=lr.employee_id,
            start_date=lr.start_date,
            end_date=lr.end_date,
            days=days,
            status=lr.status,
            reason=lr.reason,
            created_at=getattr(lr, 'created_at', None),
            approved_at=getattr(lr, 'approved_at', None),
            approver_note=getattr(lr, 'approver_note', None),
        )
