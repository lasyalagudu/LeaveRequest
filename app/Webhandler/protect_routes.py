# app/Webhandler/protected_routes.py
from fastapi import APIRouter, Depends
from app.Webhandler.oauth2 import get_current_user
from app.models.user import User


router = APIRouter()

@router.get("/profile")
def profile(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "role": current_user.role}
