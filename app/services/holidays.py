# app/Webhandler/holidays.py
from datetime import date, datetime, timedelta
import requests
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")  # your Calendarific API key
COUNTRY = os.getenv("COUNTRY", "IN")  # default country

# Function to fetch holidays from Calendarific API
def fetch_holidays(country: str = COUNTRY, year: int = None) -> set[date]:
    if year is None:
        year = date.today().year
    url = f"https://calendarific.com/api/v2/holidays?api_key={API_KEY}&country={country}&year={year}"
    resp = requests.get(url)
    resp.raise_for_status()  # Raise exception if API fails
    data = resp.json()
    # Extract holiday dates as a set of date objects
    holidays = {datetime.fromisoformat(h['date']['iso']).date() for h in data['response']['holidays']}
    return holidays

# Function to calculate working days excluding holidays and weekends
def workdays(start: date, end: date, holidays: set[date]) -> int:
    days = 0
    current = start
    while current <= end:
        if current.weekday() < 5 and current not in holidays:  # Monday=0, Sunday=6
            days += 1
        current += timedelta(days=1)
    return days
