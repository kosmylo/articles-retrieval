import os
import re
import time
import logging
import tempfile
import requests
import fitz 
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def is_english_link(url):
    if url.endswith('_en'):
        return True
    if re.search(r'_[a-z]{2}$', url) and not url.endswith('_en'):
        return False
    return True

def is_english_pdf(url):
    if not url.lower().endswith('.pdf'):
        return False
    path = urlparse(url).path.lower()
    non_eng = [
      '/fr/','/de/','/es/','/it/','/nl/','/da/','/sv/','/fi/','/pt/','/el/',
      '_fr','_de','_es','_it','_nl','_da','_sv','_fi','_pt','_el'
    ]
    for ind in non_eng:
        if ind in path:
            return False
    return any(ind in path for ind in ['/en/','_en','english'])

def extract_page_content(url):
    logging.info(f"Gov crawl: fetching {url}")
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            logging.warning(f"Failed {url}: {resp.status_code}")
            return "", [], ""
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else url
        elems = soup.find_all(['p','h1','h2','h3','li'])
        text = "\n".join(e.get_text(strip=True) for e in elems if e.get_text(strip=True))
        pdfs = []
        for a in soup.find_all('a', href=True):
            href = urljoin(url, a['href'])
            if href.lower().endswith('.pdf') and is_english_pdf(href):
                pdfs.append(href)
        return text, list(set(pdfs)), title
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return "", [], ""

def get_links_from_url(url, base_domain):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        out = []
        for a in soup.find_all('a', href=True):
            href = urljoin(url, a['href'])
            if base_domain in urlparse(href).netloc and is_english_link(href):
                out.append(href)
        return list(set(out))
    except Exception as e:
        logging.error(f"Link extraction failed for {url}: {e}")
        return []

def crawl_site(start_url, max_pages=30, max_depth=3):
    base = urlparse(start_url).netloc
    to_visit = [(start_url, 0)]
    visited = set()
    data = {}
    while to_visit and len(visited) < max_pages:
        url, depth = to_visit.pop(0)
        if url in visited:
            continue
        links = get_links_from_url(url, base)
        text, pdfs, title = extract_page_content(url)
        data[url] = {"links": links, "text": text, "pdfs": pdfs, "title": title}
        visited.add(url)
        if depth < max_depth:
            for link in links:
                if link not in visited:
                    to_visit.append((link, depth+1))
        time.sleep(1)
    return data

def get_government_documents(start_url, max_pages=30, max_depth=3):
    logging.info(f"Starting gov crawl at {start_url}")
    site = crawl_site(start_url, max_pages, max_depth)
    docs = []
    for url, d in site.items():
        if d["text"]:
            docs.append({
                "title": d["title"],
                "url": url,
                "document_type": "government",
                "content": d["text"]
            })
        for i, pdf in enumerate(d["pdfs"], 1):
            try:
                pdf_text = download_and_parse_pdf_fitz(pdf)
                docs.append({
                    "title": f"{d['title']} (PDF {i})",
                    "url": pdf,
                    "document_type": "government",
                    "content": pdf_text
                })
            except Exception:
                logging.error(f"Failed to parse PDF {pdf}")
    return docs

def download_and_parse_pdf_fitz(pdf_url):
    resp = requests.get(pdf_url, timeout=15)
    if resp.status_code != 200:
        raise Exception("PDF download failed")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(resp.content)
        pdf_path = tmp.name
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            text = "\n\n".join(page.get_text("text") for page in doc)
    finally:
        os.remove(pdf_path)
    return text