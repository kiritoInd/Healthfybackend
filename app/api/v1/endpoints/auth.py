from fastapi import APIRouter, Depends, HTTPException
from app.services.auth_service import register_user, authenticate_user, create_access_token, get_current_user
from app.db.schemas import User, Token
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=dict)
async def register(user: User):
    return register_user(user)

@router.post("/login", response_model=Token)
async def login(user: User):
    return authenticate_user(user)

@router.get("/home", response_model=dict)
async def home(current_user: str = Depends(get_current_user)):
    return {"message": f"Welcome , {current_user}!"}

