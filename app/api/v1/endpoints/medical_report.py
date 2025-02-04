from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.report_service import process_medical_report

router = APIRouter()

@router.post("/")
async def upload_medical_report(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    try:
        return await process_medical_report(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))