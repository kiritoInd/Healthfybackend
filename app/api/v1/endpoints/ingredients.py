from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.ingredient_service import extract_ingredients_from_image

router = APIRouter()

@router.post("/")
async def extract_ingredients(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}, Content-Type: {file.content_type}")
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    try:
        return await extract_ingredients_from_image(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))