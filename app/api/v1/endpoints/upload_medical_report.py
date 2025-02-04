from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.services.report_service import process_medical_report_db
from app.db.schemas import User
from app.services.auth_service import get_current_user

router = APIRouter()

@router.post("/")
async def upload_medical_report(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)  # Get the logged-in user
):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    try:
        return await process_medical_report_db(file, current_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))