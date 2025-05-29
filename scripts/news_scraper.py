import logging
import requests

def get_energy_news(api_key, query="renewable energy", max_articles=10, language="en", from_date=None):
    logging.info(f"GNews: querying '{query}' (max {max_articles}, lang={language})")

    url = "https://gnews.io/api/v4/search"
    articles = []
    page_size = 10  # Maximum allowed per request by GNews
    total_retrieved = 0
    
    for page in range(1, (max_articles // page_size) + 2):  # +2 to ensure coverage

        params = {
            "q": query,
            "lang": language,
            "max": page_size,
            "token": api_key,
            "expand": "content",
            "page": page
        }

        if from_date:
            params["from"] = from_date

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            page_articles = data.get("articles", [])

            if not page_articles:
                logging.info(f"No more articles found for '{query}' at page {page}.")
                break  # No more articles available

            for item in page_articles:
                title = item.get("title")
                news_url = item.get("url")
                content = item.get("content") or item.get("description") or ""

                articles.append({
                    "title": title,
                    "url": news_url,
                    "publishedAt": item.get("publishedAt"),
                    "source": item.get("source", {}).get("name"),
                    "document_type": "news",
                    "content": content
                })

            total_retrieved += len(page_articles)

            if total_retrieved >= max_articles:
                logging.info(f"Reached requested max articles ({max_articles}) for '{query}'.")
                break

        except requests.RequestException as e:
            logging.error(f"GNews API request error (page {page}): {e}")
            break

    logging.info(f"Total articles retrieved for '{query}': {len(articles)}")

    return articles[:max_articles]  # Ensure exact max_articles