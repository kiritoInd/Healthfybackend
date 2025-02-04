from fastapi import APIRouter
from app.services.pubmed_service import search_pubmed, get_pubmed_article

router = APIRouter()

@router.get("/search/{ingredient}")
async def search_pubmed_endpoint(ingredient: str, max_results: int = 3):
    return search_pubmed(ingredient, max_results)

@router.get("/citation/{pmid}")
async def get_citation_endpoint(pmid: str):
    return get_pubmed_article(pmid)