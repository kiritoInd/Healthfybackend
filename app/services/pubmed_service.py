import requests
from app.core.config import settings

PUBMED_API_BASE = settings.PUBMED_API_BASE

def search_pubmed(ingredient: str, max_results: int = 3):
    search_url = f"{PUBMED_API_BASE}/esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': f'"{ingredient}"[Title/Abstract]',
        'retmode': 'json',
        'retmax': max_results
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {"pmid_list": data.get('esearchresult', {}).get('idlist', [])[:max_results]}
    else:
        raise Exception(f"Error: {response.text}")

def get_pubmed_article(pmid: str):
    fetch_url = f"{PUBMED_API_BASE}/efetch.fcgi"
    params = {
        'db': 'pubmed',
        'id': pmid,
        'retmode': 'xml'
    }
    response = requests.get(fetch_url, params=params)
    content = response.text
    title = re.search(r'(.*?)', content)
    abstract = re.search(r'(.*?)', content)
    return {
        'title': title.group(1) if title else "No title found",
        'abstract': abstract.group(1) if abstract else "No abstract found",
        'link': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    }