from fastapi import APIRouter
from app.api.v1.endpoints.ai_analysis import router as ai_analysis_router
from app.api.v1.endpoints.pubmed import router as pubmed_router
from app.api.v1.endpoints.medical_report import router as medical_report_router
from app.api.v1.endpoints.ingredients import router as ingredients_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.upload_medical_report import router as upload_medical_report
from app.api.v1.endpoints.getprofile import router as get_info

api_router = APIRouter()

api_router.include_router(ai_analysis_router, prefix="/analyze", tags=["AI Analysis"])
api_router.include_router(pubmed_router, prefix="/pubmed", tags=["PubMed"])
api_router.include_router(medical_report_router, prefix="/medical-report", tags=["Medical Report"])
api_router.include_router(ingredients_router, prefix="/ingredients", tags=["Ingredients"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(upload_medical_report , prefix = "/upload-medical-report" , tags=["Upload Medical By User"])
api_router.include_router(get_info , prefix = "/get_info" , tags=["info from data"])