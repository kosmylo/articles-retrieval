import logging
import wikipedia
import re
from collections import Counter
from wikipedia.exceptions import DisambiguationError, PageError 

# Define keywords and categories for energy relevance scoring
ENERGY_KEYWORDS = [
    "energy", "electricity", "power", "renewable", "solar", "wind",
    "photovoltaic", "hydro", "hydrogen", "battery", "storage", "grid",
    "smart", "microgrid", "meter", "tariff", "pricing", "prosumer",
    "demand", "efficiency", "building", "insulation", "heat pump",
    "emissions", "carbon", "subsidy", "fund", "transition", "policy"
]

CATEGORY_HINTS = [
    "energy", "electric", "power", "renewable", "climate",
    "sustainable", "decarbonisation", "environmental policy"
]

_kw_re = re.compile(r"|".join(map(re.escape, ENERGY_KEYWORDS)), re.I)
_cat_re = re.compile(r"|".join(map(re.escape, CATEGORY_HINTS)), re.I)

def _score_page(page) -> float:
    """Compute a relevance score for a Wikipedia page."""
    score = 0.0
    title = page.title.lower()
    lead = page.content[:800].lower()  # first ~paragraph

    # Base score if keywords are in title or lead
    if _kw_re.search(title) or _kw_re.search(lead):
        score += 0.4

    # Category matches
    cat_hits = sum(bool(_cat_re.search(c.lower())) for c in getattr(page, "categories", []))
    score += 0.6 * cat_hits

    # Keyword density in the first 500 words
    words = re.findall(r"\w+", lead)[:500]
    counts = Counter(words)
    hits = sum(counts[k] for k in ENERGY_KEYWORDS if k in counts)
    score += min(hits, 10) * 0.1  # cap keyword density score at 1.0

    return score

def get_energy_articles(query="energy", max_articles=5, threshold=1.0, exact=False):
    logging.info(f"Wikipedia: searching '{query}' (max {max_articles})")

    if exact:
        results = [query]
    else:
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

        score = _score_page(page)
        if score >= threshold:
            articles.append({
                "title": page.title,
                "url": page.url,
                "document_type": "wikipedia",
                "categories": getattr(page, "categories", []),
                "content": page.content
            })
            logging.info(f"Accepted: '{page.title}' (score: {score:.2f})")
        else:
            logging.info(f"Rejected: '{page.title}' (score: {score:.2f})")

    logging.info(f"Total kept for '{query}': {len(articles)}")

    return articles