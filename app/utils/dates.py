from datetime import date, timedelta
from typing import Iterable

def daterange(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur = cur + timedelta(days=1)

WEEKENDS = {5, 6}  # Saturday=5, Sunday=6 (Python: Monday=0)

def business_days_between(start: date, end: date, holidays: Iterable[date] = ()) -> int:
    holidays_set = set(holidays)
    return sum(1 for d in daterange(start, end) if d.weekday() not in WEEKENDS and d not in holidays_set)

def overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return not (a_end < b_start or b_end < a_start)