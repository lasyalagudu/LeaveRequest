# app/services/leave_service.py
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from fastapi import HTTPException
# app/services/leave_service.py
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.leave_request import LeaveRequest, LeaveStatus
from app.core.config import settings
from fastapi import HTTPException

from app.services.holidays import fetch_holidays

class LeaveService:

    @staticmethod
    def cancel_leave(leave_id: int, employee_id: int, db: Session):
        leave = db.query(LeaveRequest).filter(
            LeaveRequest.id == leave_id, 
            LeaveRequest.employee_id == employee_id
        ).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Leave request not found")
        if leave.status != LeaveStatus.PENDING:
            raise HTTPException(status_code=400, detail="Cannot cancel approved/rejected leave")

        leave.status = LeaveStatus.REJECTED  # or "CANCELLED" if you want a separate status
        db.commit()
        return {"message": "Leave request cancelled successfully."}

    @staticmethod
    def modify_leave(leave_id: int, employee_id: int, start_date: date, end_date: date, reason: str, db: Session):
        leave = db.query(LeaveRequest).filter(
            LeaveRequest.id == leave_id, 
            LeaveRequest.employee_id == employee_id
        ).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Leave request not found")
        if leave.status != LeaveStatus.PENDING:
            raise HTTPException(status_code=400, detail="Cannot modify approved/rejected leave")
        if start_date < date.today() or end_date < date.today():
            raise HTTPException(status_code=400, detail="Leave dates cannot be in the past")
        if end_date < start_date:
            raise HTTPException(status_code=400, detail="End date cannot be before start date")

        # Check public holidays
        holidays = fetch_holidays(country=settings.COUNTRY, year=start_date.year)
        working_days = sum(
            1 for d in (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))
            if d.weekday() < 5 and d not in holidays
        )
        if working_days <= 0:
            raise HTTPException(status_code=400, detail="No working days in selected range")

        leave.start_date = start_date
        leave.end_date = end_date
        leave.reason = reason
        leave.days = working_days
        db.commit()
        return {"message": "Leave request updated successfully.", "updated_days": working_days}
