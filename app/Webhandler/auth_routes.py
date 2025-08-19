# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.Webhandler.auth import create_access_token, hash_password, verify_password
from app.core.db import get_db
from app.models.employee import Employee
from app.models.user import RoleEnum, User
from app.schemas.user_schema import UserCreate, UserLogin
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ----------------- Signup -----------------
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already taken")
    
    new_user = User(
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "email": new_user.email,
        "role": new_user.role
    }

# ----------------- Login -----------------
@router.post("/login")
def login(login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Check if linked Employee has first_login = True
    emp = db.query(Employee).filter(Employee.email == login.email).first()
    if emp and emp.first_login:
        raise HTTPException(status_code=403, detail="Password not set yet. Please check your email to setup password.")

    if not verify_password(login.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }

# ----------------- Reset Password -----------------
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    # Find Employee by setup token
    employee = db.query(Employee).filter(Employee.password_setup_token == payload.token).first()
    emp = db.query(Employee).filter(Employee.email == payload.email).first()

    if not user or not emp:
        raise HTTPException(status_code=404, detail="User not found")

    # 2️⃣ Update the password
    hashed_pw = hash_password(payload.new_password)
    user.password = hashed_pw
    emp.hashed_password = hashed_pw

    # 3️⃣ Mark first_login as False
    emp.first_login = False
    emp.password_setup_token = None  # in
    db.commit()

    # Also update User table if exists
    user = db.query(User).filter(User.email == employee.email).first()
    if user:
        user.password = hash_password
        db.commit()

    return {"msg": "Password updated successfully. You can now login with your new password."}
