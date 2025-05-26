import logging
import requests
from newspaper import Article, Config
from bs4 import BeautifulSoup  

# mimic a real browser
_nlp_config = Config()
_nlp_config.browser_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
)
_nlp_config.request_timeout = 10  # seconds

def get_energy_news(api_key, query="renewable energy", max_articles=5, language="en"):
    logging.info(f"NewsAPI: querying '{query}' (max {max_articles})")
    url = "https://newsapi.org/v2/everything"
    params = {
        "qInTitle": query,
        "language": language,
        "pageSize": max_articles,
        "sortBy": "relevancy",
        "apiKey": api_key
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        logging.error(f"NewsAPI failed: {resp.status_code} {resp.text}")
        raise Exception("News API request failed")
    data = resp.json()

    articles = []
    for item in data.get("articles", []):
        title = item.get("title")
        news_url = item.get("url")
        # start with description or content from the API
        text = item.get("content") or item.get("description") or ""

        # 1st attempt: newspaper3k
        try:
            art = Article(news_url, config=_nlp_config)
            art.download()
            art.parse()
            if art.text:
                text = art.text

        except Exception as e:
            logging.warning(f"Scrape fallback for '{title}': {e}")

            # 2nd attempt: manual GET + newspaper
            try:
                manual = requests.get(
                    news_url,
                    headers={"User-Agent": _nlp_config.browser_user_agent},
                    timeout=_nlp_config.request_timeout
                )
                if manual.status_code == 200:
                    art2 = Article(news_url, config=_nlp_config)
                    art2.download(input_html=manual.text)
                    art2.parse()
                    if art2.text:
                        text = art2.text
                else:
                    logging.warning(
                        f"Manual GET failed ({manual.status_code}) for '{title}'"
                    )
            except Exception as e2:
                logging.warning(f"Manual fallback also failed for '{title}': {e2}")

                # 3rd attempt: BeautifulSoup direct parse
                try:
                    soup = BeautifulSoup(manual.text if 'manual' in locals() else "", "html.parser")
                    paras = soup.find_all("p")
                    if paras:
                        bs_text = "\n".join(p.get_text(strip=True) for p in paras if p.get_text(strip=True))
                        if bs_text:
                            text = bs_text
                            logging.info(f"BeautifulSoup fallback succeeded for '{title}'")  
                except Exception as e3:
                    logging.debug(f"BS fallback error for '{title}': {e3}")  

        articles.append({
            "title": title,
            "url": news_url,
            "document_type": "news",
            "content": text
        })

    return articles