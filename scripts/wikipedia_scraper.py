import logging
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError 

def get_energy_articles(query="energy", max_articles=5):
    logging.info(f"Wikipedia: searching '{query}' (max {max_articles})")
    results = wikipedia.search(query, results=max_articles)
    articles = []

    for title in results:
        try:
            page = wikipedia.page(title, auto_suggest=False)

        except DisambiguationError as e: 
            # pick the first disambiguation option (or you could loop over a few)
            choice = e.options[0]
            logging.info(f"Disambiguation for '{title}', trying '{choice}'")
            try:
                page = wikipedia.page(choice, auto_suggest=False)
            except Exception as e2:
                logging.warning(f"Failed to resolve '{choice}' for '{title}': {e2}")
                continue

        except PageError as e:  
            logging.warning(f"No Wikipedia page for '{title}', skipping.")
            continue

        except Exception as e:
            logging.warning(f"Wikipedia error for '{title}': {e}")
            continue

        articles.append({
            "title": page.title,
            "url": page.url,
            "document_type": "wikipedia",
            "content": page.content
        })

    return articles