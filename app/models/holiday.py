from sqlalchemy import Column, Integer, Date, String, UniqueConstraint
from app.core.db import Base

class Holiday(Base):
    __tablename__ = "holiday"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    name = Column(String(100), nullable=False)

    __table_args__ = (UniqueConstraint("date", name="uq_holiday_date"),)