**Leave Management API**
Overview

This project is a Leave Management API built with FastAPI and SQLAlchemy to handle employee leave requests, approvals, and leave balance management.

Setup Steps

**Clone the repository**

git clone <repo-url>
cd <repo-directory>


**Create a virtual environment**

python -m venv venv
cd venv
cd scripts
activate
source venv/bin/activate  # On Windows use `venv\Scripts\activate`


**Install dependencies**

pip install -r requirements.txt


**Create .env file**

Copy .env.example to .env

Fill in the required environment variables (database URL, secret keys, etc.)

Example:

DB_HOST=localhost
DB_USER=youruser
DB_PASS=yourpassword
DB_NAME=leavemanagement
SECRET_KEY=your_secret_key
COUNTRY=IN


**Run database migrations (if applicable)**

alembic upgrade head


(Or any other migration tool you use)

Start the FastAPI server

uvicorn app.main:app --reload


**Access the API documentation**
Open http://127.0.0.1:8000/docs
 in your browser for Swagger UI.
**In Postman **
1) http://127.0.0.1:8000/auth/signup
{
  "email":"krishna@example.com",
  "password": "test123",
  "role": "admin"
}

2) http://127.0.0.1:8000/auth/login
{
  "email": "krishna@example.com",
  "password": "test123"
}
copy the generated token and paste in authorization header and verify 
**add employee by admin/hr**
**post**
http://127.0.0.1:8000/employees/
{
    "name": "Disha",
    "email": "dishajain326@gmail.com",
    "phone_number": "9876543210",
    "job_type": "Intern",
    "address": "123 Main Street, Cityville",
    "domain": "intern",
    "joining_date": "2025-08-19",
    "annual_allocation": 24,
    "hashed_password": "$2b$12$7bG9eE1j6kS0hXYlB1h6xu2FfRldXhIo3FppG5ZOCj5o2mYxF8z1f", 
    "first_login": true,
    "password_setup_token": "random_token_here"
}
check for leave balance
{
  "employee_id": 1,
  "start_date": "2025-09-01",
  "end_date": "2025-09-05",
  "reason": "Family vacation",
  "leave_type_id": 1
}



**Edge Cases Handled**
1)Add email notifications on adding new employee so that employee can reset password
2)Validation of leave applications with start or end dates in the past.
3)Prevent overlapping leave requests for the same employee.
4)Reject leave if days requested exceed remaining leave balance.
5)Validation ensures end date is not before start date.
6)Validation for leave modification and cancellation only if leave status is PENDING.
7)Prevent approving or rejecting leave requests not in PENDING state.
8)Validation of leave days in response to ensure consistency with date range.
9)Pagination and filtering support on leave search.
10)Duplicate leave IDs and invalid IDs rejected in bulk actions.
11)Implemented role-based access control (e.g., employee vs. HR).
12)Stored Passwords securely bcrypting them
13)Support for carry-forward leave balance and leave expiry.


<img width="901" height="685" alt="Screenshot 2025-08-19 234003" src="https://github.com/user-attachments/assets/e3f18b74-ca76-4465-857a-cce15300b5d2" />
