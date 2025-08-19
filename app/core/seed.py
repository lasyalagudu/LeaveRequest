# Inside a script, e.g. seed.py
from app.core.db import SessionLocal
from app.models.leave_type import LeaveType

def seed_leave_types():
    db = SessionLocal()
    types = [
        LeaveType(name="Annual Leave", description="Paid annual leave", default_balance=20, carry_forward=True),
        LeaveType(name="Sick Leave", description="Paid sick leave", default_balance=10, carry_forward=False),
        LeaveType(name="Casual Leave", description="Unpaid casual leave", default_balance=5, carry_forward=False),
    ]
    db.add_all(types)
    db.commit()
    db.close()

seed_leave_types()
