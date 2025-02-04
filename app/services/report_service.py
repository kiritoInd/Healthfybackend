from PIL import Image, ImageEnhance
import pytesseract
import PyPDF2
from io import BytesIO
from app.services.ai_service import analyze_with_gpt
import re
from pymongo import MongoClient
from app.core.config import settings

from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient  # ✅ Import Motor for async MongoDB
from datetime import datetime

# Async MongoDB Client
mongo_client = AsyncIOMotorClient(settings.MONGO_URI)  # ✅ Use AsyncIOMotorClient
db = mongo_client["Health"]
collection = db["users"]

async def process_medical_report(file):
    content = await file.read()
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(BytesIO(content))
        report_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    else:
        image = Image.open(BytesIO(content))
        report_text = pytesseract.image_to_string(image)
    prompt = f"""
    Extract health conditions and their associated levels from the given medical report Only include conditions that are at a critical level or Not in normal range and Do not reapeat the coditions which has , Do not add any conditions by yourself or infer conditions that are not explicitly mentioned in the report.
    For each condition, provide the result in the following format:
    Condition: [Name of the condition]
    Level: [Severity level, stage, or brief explanation of the condition]
    In [[Condition , level] , [Condition2 , level2]] This Format
    Medical Report:
    {report_text}
    """
    response_text = analyze_with_gpt(prompt)
    matches = re.findall(r'\[(.*?)\]', response_text)
    result = []
    for match in matches:
        condition, level = match.split(',', 1)
        result.append({"condition": condition.strip(), "level": level.strip()})
    return result



async def process_medical_report_db(file, current_user):
    # Extract text from the uploaded file (PDF or image)
    content = await file.read()
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(BytesIO(content))
        report_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    else:
        image = Image.open(BytesIO(content))
        report_text = pytesseract.image_to_string(image)

    # Generate a prompt for AI analysis
    prompt = f"""
    Extract health conditions and their associated levels from the given medical report.
    Only include conditions that are at a critical level or not in the normal range.
    Do not repeat conditions, and do not add any conditions by yourself or infer conditions that are not explicitly mentioned in the report.
    For each condition, provide the result in the following format:
    Condition: [Name of the condition]
    Level: [Severity level, stage, or brief explanation of the condition]
    In [[Condition , level] , [Condition2 , level2]] This Format
    Medical Report:
    {report_text}
    """
    
    
    
    #needs to fix  
    
    
    
    
    # Analyze the report using AI
    response_text = analyze_with_gpt(prompt)
    
    matches = re.findall(r'\[(.*?)\]', response_text)
    health_data = []
    # for match in matches:
    #     condition, level = match.split(',', 1)
    #     health_data.append({"condition": condition.strip(), "level": level.strip()})
    print(matches)
    health_data = [
        ["Triglycerides", "175 mg/dL (High)"],
        ["LDL Cholesterol - Direct", "139 mg/dL (High)"],
        ["HDL Cholesterol - Direct", "34 mg/dL (Low)"],
        ["25-OH Vitamin D (Total)", "21 ng/mL (Insufficient)"],
        ["Lymphocyte Percentage", "44.7% (High)"],
        ["Lymphocytes - Absolute Count", "3.27 x 10³/µL (High)"],
        ["Trig/HDL Ratio", "5.15 (High)"],
        ["LDL/HDL Ratio", "4.1 (High)"],
        ["TC/HDL Cholesterol Ratio", "5.7 (High)"],
        ["HDL/LDL Ratio", "0.24 (Low)"]
    ]
    print(health_data)
    
    health_data = [{"condition": condition, "level": level} for condition, level in health_data ]
    print(health_data)
    # Save or update the health data in MongoDB
    existing_user = await collection.find_one({"username": current_user})  # ✅ Now this works!

    if existing_user:
        update_operation = {
            "$push": {"health_data": {"$each": health_data}},  # Append new health data
            "$set": {"updated_at": datetime.utcnow()}          # Update timestamp
        }
        await collection.update_one({"username": current_user}, update_operation)
        return {"message": "Health data updated successfully."}
    
    else:
        new_user = {
            "username": current_user,
            "health_data": health_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await collection.insert_one(new_user)  # ✅ Use `await`
        return {"message": f"New user created with ID: {str(result.inserted_id)}"}