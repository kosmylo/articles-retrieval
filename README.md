# Articles-Retrieval

A Docker Compose–based pipeline to collect, parse, and unify energy-related content from Wikipedia, the GNews API, arXiv, and EU government sites into JSON-Lines files. Ideal for building datasets to train or fine-tune energy-domain LLM models.

## 🚀 Features

- **Multi-source scraping**:  
  - Wikipedia via `wikipedia` library  
  - News via the `GNews` API with full article text retrieval
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
├── README.md
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
- A GNews API key from [gnews.io](https://gnews.io) (required)
- Internet access from the VM to fetch web resources

## ⚙️ Configuration

Control each scraper via environment variables in your `.env`:

```yaml
NEWS_API_KEY="API KEY"
MAX_WIKI_ARTICLES=500
MAX_NEWS_ARTICLES=500
MAX_ARXIV_PAPERS=300
MAX_GOV_PAGES=500
MAX_GOV_DEPTH=6
RUN_WIKI=0
RUN_NEWS=1
RUN_ARXIV=0
RUN_GOV=0
WIKI_RELEVANCE_THRESHOLD=0.8
RUN_WIKI_COUNTRY_ONLY=0
```

**Topic lists** for Wikipedia, news, and arXiv and **governmental/regulatory bodies URLs** are defined at the top of `main.py`. Adjust those arrays to refine your coverage.

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

2. **Run the service** using Docker Compose. Define your `NEWS_API_KEY` and any scraper flags in a `.env` file (see above), then start the container:

   ```bash
   docker-compose up
   ```

   All scraper settings can be customized via environment variables in `.env`.

3. **Stop the service** when finished:

   ```bash
   docker-compose down
   ```

The scraped records are written to `output/*.jsonl`. 