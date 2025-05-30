import logging
import requests
import tempfile
import os
import arxiv
import fitz

def download_pdf(pdf_url):
    logging.info(f"Downloading PDF: {pdf_url}")
    resp = requests.get(pdf_url, timeout=10)
    resp.raise_for_status()
    return resp.content

def pdf_to_text(pdf_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        pdf_path = tmp.name

    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    finally:
        doc.close()
        os.remove(pdf_path)

def download_and_parse_pdf(pdf_url):
    pdf_bytes = download_pdf(pdf_url)
    raw_text = pdf_to_text(pdf_bytes)
    return raw_text

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
            paper["content"] = download_and_parse_pdf(res.pdf_url)
        except Exception as e:
            logging.warning(f"arXiv PDF fallback for '{res.title}': {e}")
            paper["content"] = res.summary
        papers.append(paper)
    return papers
