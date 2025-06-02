# Articles-Retrieval

A Docker Compose–based pipeline to collect, parse, and unify energy-related content from Wikipedia, News API, arXiv, and EU government sites into JSON-Lines files. Ideal for building datasets to train or fine-tune energy-domain LLM models.

## 🚀 Features

- **Multi-source scraping**:  
  - Wikipedia via `wikipedia` library  
  - News via gnews API with title-only and full-text fallbacks 
  - arXiv via `arxiv` Python client, converting PDFs to text with PyMuPDF
  - EU government sites via BeautifulSoup with PDF text extraction via PyMuPDF
- **Streaming output**: appends each record to per-scraper `*.jsonl` files for immediate availability  
- **Per-scraper toggles**: enable/disable any collector with environment flags (`RUN_WIKI`, `RUN_NEWS`, `RUN_ARXIV`, `RUN_GOV`)  
- **Robust logging**: combined console + file logging (`logs/app.log`) with INFO-level tracing and warnings  

## 🗂 Repository Structure

```text
articles_collection
├── .env
├── .gitignore
├── Dockerfile
├── README
├── docker-compose.yaml
├── logs
│   └── app.log
├── main.py
├── output
│   ├── arxiv.jsonl
│   ├── gov.jsonl
│   ├── news.jsonl
│   └── wiki.jsonl
├── requirements.txt
└── scripts
    ├── arxiv_scraper.py
    ├── gov_scraper.py
    ├── news_scraper.py
    └── wikipedia_scraper.py
```

- **`main.py`**: orchestrates all scrapers and writes to `output/*.jsonl`  
- **`scripts/`**: modular collectors for each source  
- **`docker-compose.yaml`**: defines service, volumes, and environment flags  
- **`Dockerfile`**: builds the container with required system and Python dependencies  

## 🔧 Prerequisites

- Docker & Docker Compose installed locally 
- (Optional) A NewsAPI key (free for development) 
- Internet access from the VM to fetch web resources  

## ⚙️ Configuration

Control each scraper via environment variables in your `docker-compose.yaml`:

```yaml
services:
  collector:
    environment:
      - RUN_WIKI=1        # toggle Wikipedia scraper (1=on, 0=off)
      - RUN_NEWS=1        # toggle NewsAPI scraper
      - RUN_ARXIV=1       # toggle arXiv scraper
      - RUN_GOV=1         # toggle Government scraper
      - MAX_WIKI_ARTICLES=100
      - MAX_NEWS_ARTICLES=100
      - MAX_ARXIV_PAPERS=50
      - MAX_GOV_PAGES=60
      - MAX_GOV_DEPTH=3
```

**NewsAPI** uses `qInTitle` first (tight headline matches), then falls back to `q` if no results.

**Topic lists** for Wikipedia, NewsAPI, and arXiv are defined at the top of `main.py`. Adjust those arrays to refine your coverage.

## 📂 Output

The pipeline writes four JSON-Lines files into the `output/` directory:

`output/wiki.jsonl`

`output/news.jsonl`

`output/arxiv.jsonl`

`output/gov.jsonl`

Each line in these files is a standalone JSON object:

```json
{ 
  "title": "...", 
  "url": "...", 
  "document_type": "...", 
  "content": "..." 
}
```

## 🐳 Build & Run

1. **Build the image** (run from the repository root):

   ```bash
   docker build -t articles-collector .
   ```

2. **Run with Docker Compose** and pass your `NEWS_API_KEY`:

   ```bash
   NEWS_API_KEY=YOUR_KEY docker-compose up
   ```

   All scraper settings (`RUN_WIKI`, `RUN_NEWS`, etc.) can be overridden in the `docker-compose.yaml` or via environment variables on the command line.

3. **Stop the service** when finished:

   ```bash
   docker-compose down
   ```

The scraped records are written to `output/*.jsonl`. 

Topic arrays for Wikipedia, NewsAPI, and arXiv live near the top of `main.py`. Modify those lists to change what the collectors search for.