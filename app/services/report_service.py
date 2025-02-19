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
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB limit

async def process_medical_report(file):
    content_length = request.headers.get('content-length')
    if content_length and int(content_length) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds the 5MB limit")
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
    content_length = request.headers.get('content-length')
    if content_length and int(content_length) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds the 5MB limit")
    content = await file.read()
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(BytesIO(content))
        report_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    else:
        image = Image.open(BytesIO(content))
        report_text = pytesseract.image_to_string(image)

    # Generate a prompt for AI analysis
    prompt = f"""
    Extract health conditions and their associated levels from the given medical report Only include conditions that are at a critical level or Not in normal range and Do not reapeat the coditions which has , Do not add any conditions by yourself or infer conditions that are not explicitly mentioned in the report.
    For each condition, provide the result in the following format:
    Condition: [Name of the condition]
    Level: [Severity level, stage, or brief explanation of the condition]
    
    Here is an example format [[Condition , level] , [Condition2 , level2] .. n].
    do not add anything else on your own only provide the fomated result. 
    
    what are wrong formats: 
    These are example for formating do not use these as result
    1. [['x', 'Not in normal range']] the level should be example "999 units (High , low , Insufficient)"
    Medical Report:
    {report_text}
    """    
    
    
    # Analyze the report using AI
    response_text = analyze_with_gpt(prompt)
    
    matches = re.findall(r'\[(.*?)\]', response_text)
    result = []
    for match in matches:
        condition, level = match.split(',', 1)
        result.append({"condition": condition.strip(), "level": level.strip()})
    # print(result)
    
    health_data = []
    for res in result:
        condition = res['condition'].replace('[', '').replace(']', '')
        level = res['level'].replace('[', '').replace(']', '')
        health_data.append([condition, level])
    
    print(health_data)
    # for match in matches:
    #     condition, level = match.split(',', 1)
    #     health_data.append({"condition": condition.strip(), "level": level.strip()})
    # health_data = [
    #     ["Triglycerides", "175 mg/dL (High)"],
    #     ["LDL Cholesterol - Direct", "139 mg/dL (High)"],
    #     ["HDL Cholesterol - Direct", "34 mg/dL (Low)"],
    #     ["25-OH Vitamin D (Total)", "21 ng/mL (Insufficient)"],
    #     ["Lymphocyte Percentage", "44.7% (High)"],
    #     ["Lymphocytes - Absolute Count", "3.27 x 10³/µL (High)"],
    #     ["Trig/HDL Ratio", "5.15 (High)"],
    #     ["LDL/HDL Ratio", "4.1 (High)"],
    #     ["TC/HDL Cholesterol Ratio", "5.7 (High)"],
    #     ["HDL/LDL Ratio", "0.24 (Low)"]
    # ]
    # print(health_data)
    
    health_data = [{"condition": condition, "level": level} for condition, level in health_data ]
    # print(health_data)
    # # Save or update the health data in MongoDB
    existing_user = await collection.find_one({"username": current_user})  

    if existing_user:
        # Debugging: Print existing user data before updating
        print("Before update:", existing_user)

        update_operation = {
            "$set": {  # Replace entire health_data
                "health_data": health_data,
                "updated_at": datetime.utcnow()
            }
        }
        
        await collection.update_one({"username": current_user}, update_operation)

        # Debugging: Fetch updated document to verify update
        updated_user = await collection.find_one({"username": current_user})
        print("After update:", updated_user)

        return {"message": "Health data updated successfully."}
    
    else:
        new_user = {
            "username": current_user,
            "health_data": health_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(new_user)
        return {"message": f"New user created with ID: {str(result.inserted_id)}"}
