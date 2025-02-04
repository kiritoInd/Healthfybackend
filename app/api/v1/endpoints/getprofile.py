from fastapi import APIRouter, Depends, HTTPException
from app.services.auth_service import get_current_user
from app.core.config import settings
from pymongo import MongoClient

router = APIRouter()

# MongoDB connection
mongo_client = MongoClient(settings.MONGO_URI)
db = mongo_client["Health"]
collection = db["users"]

@router.get("/health-data")
async def get_health_data(current_user: str = Depends(get_current_user)):
    """
    Retrieve health data for the authenticated user.
    """
    user_data = collection.find_one({"username": current_user}, {"_id": 0, "health_data": 1})

    if not user_data or "health_data" not in user_data:
        raise HTTPException(status_code=404, detail="No health data found for this user")

    return {"username": current_user, "health_data": user_data["health_data"]}
