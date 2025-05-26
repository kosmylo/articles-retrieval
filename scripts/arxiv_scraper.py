import logging
import requests
import tempfile
import os
import arxiv
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat

def download_and_parse_pdf_docling(pdf_url):
    logging.info(f"Downloading PDF: {pdf_url}")
    resp = requests.get(pdf_url, timeout=10)
    if resp.status_code != 200:
        raise Exception(f"PDF download failed: {resp.status_code}")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(resp.content)
        path = tmp.name
    try:
        conv = DocumentConverter(allowed_formats=[InputFormat.PDF]).convert(path)
        return conv.document.export_to_markdown()
    finally:
        os.remove(path)

def search_arxiv_papers(query="renewable energy", max_papers=2):
    logging.info(f"arXiv: searching '{query}' (max {max_papers})")
    search = arxiv.Search(
        query=query,
        max_results=max_papers,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    papers = []
    for res in search.results():
        paper = {
            "title": res.title,
            "url": res.pdf_url,
            "document_type": "arxiv"
        }
        try:
            paper["content"] = download_and_parse_pdf_docling(res.pdf_url)
        except Exception as e:
            logging.warning(f"arXiv PDF fallback for '{res.title}': {e}")
            paper["content"] = res.summary
        papers.append(paper)
    return papers