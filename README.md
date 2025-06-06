# Articles-Retrieval

A Docker Compose–based pipeline to **collect, parse, preprocess, and unify** energy-related content from Wikipedia, the GNews API, arXiv, and EU government sites into clean JSON-Lines files. Ideal for building datasets to train or fine-tune energy-domain LLM models.

## 🚀 Features

- **Multi-source scraping**:  
  - Wikipedia via `wikipedia` library  
  - News via the `GNews` API with full article text retrieval
  - arXiv via `arxiv` Python client, converting PDFs to text with PyMuPDF
  - EU government sites via BeautifulSoup with PDF text extraction via PyMuPDF

- **Data preprocessing pipeline**:
  - HTML content cleanup and normalization using BeautifulSoup
  - Title-based deduplication to remove redundant articles
  - Language filtering (English-only) via `langdetect`
  - Filtering out corrupted text based on non-printable characters
  - Detailed logging showing number of articles removed per preprocessing step

- **Streaming output**: appends each record to per-scraper `*.jsonl` files for immediate availability  

- **Per-scraper and preprocessing toggles**: enable/disable any collector and preprocessing steps with environment flags (`RUN_WIKI`, `RUN_NEWS`, `RUN_ARXIV`, `RUN_GOV`, `RUN_PREPROCESSING`)  

- **Robust logging**: combined console + file logging (`logs/app.log`) with INFO-level tracing, warnings, and detailed preprocessing statistics

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
│   └── processed
│       ├── arxiv.jsonl
│       ├── gov.jsonl
│       ├── news.jsonl
│       └── wiki.jsonl
├── requirements.txt
└── scripts
    ├── arxiv_scraper.py
    ├── gov_scraper.py
    ├── news_scraper.py
    ├── wikipedia_scraper.py
    └── preprocess.py
```

- **`main.py`**: orchestrates all scrapers, optionally triggers preprocessing, and writes results to `output/*.jsonl`  
- **`scripts/`**: modular collectors for each source and preprocessing
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
RUN_PREPROCESSING=1
```

Create your `.env` file in the repository root with:

```bash
touch .env
```

Open the file with a text editor to add your values, for example:

```bash
nano .env
```

Then place your `NEWS_API_KEY` and the other flags in this file.

**Topic lists** for Wikipedia, news, and arXiv and **governmental/regulatory bodies URLs** are defined at the top of `main.py`. Adjust those arrays to refine your coverage.

## 📂 Output

The pipeline writes four JSON-Lines files into the `output/` directory:

`output/wiki.jsonl`

`output/news.jsonl`

`output/arxiv.jsonl`

`output/gov.jsonl`

After preprocessing (if enabled via RUN_PREPROCESSING), cleaned data is stored in:

`output/processed/wiki.jsonl`

`output/processed/news.jsonl`

`output/processed/arxiv.jsonl`

`output/processed/gov.jsonl`

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

The raw and preprocessed records will be saved in the output/ and output/processed/ directories, respectively.