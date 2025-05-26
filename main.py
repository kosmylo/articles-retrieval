import os
import json
import logging
from scripts.wikipedia_scraper import get_energy_articles
from scripts.news_scraper import get_energy_news
from scripts.arxiv_scraper import search_arxiv_papers
from scripts.gov_scraper import get_government_documents

def configure_logging():
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler()
        ])
    
def append_records(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def main():
    configure_logging()
    logging.info("=== Starting EU-Energy Article Collection ===")
    
    RUN_WIKI  = os.getenv("RUN_WIKI", "1")  == "1"  # set to "0" to disable
    RUN_NEWS  = os.getenv("RUN_NEWS", "1")  == "1"
    RUN_ARXIV = os.getenv("RUN_ARXIV", "1") == "1"
    RUN_GOV   = os.getenv("RUN_GOV", "1")   == "1"
    logging.info(f"RUN_WIKI: {RUN_WIKI}, RUN_NEWS: {RUN_NEWS}, RUN_ARXIV: {RUN_ARXIV}, RUN_GOV: {RUN_GOV}")

    # 1. All topics (same list for wiki, news, arXiv)
    # topics = [
    #   # Policy & Governance
    #   "European Green Deal",
    #   "Energy Union",
    #   "Renewable Energy Directive",
    #   "National Energy and Climate Plans",
    #   "Just Transition Fund",
    #   # Markets & Pricing
    #   "Energy market liberalisation in the European Union",
    #   "Electricity pricing",
    #   "Net metering",
    #   "Feed-in tariff",
    #   "Wholesale electricity market",
    #   "Capacity market",
    #   # Renewables & Storage
    #   "Solar photovoltaic energy",
    #   "Wind power",
    #   "Energy storage",
    #   "Electric vehicle",
    #   "Vehicle-to-grid",
    #   "Smart grid",
    #   "Microgrid",
    #   # Efficiency & Buildings
    #   "Passive house",
    #   "Nearly zero-energy building",
    #   "Energy Performance of Buildings Directive",
    #   "Heat pump",
    #   "Energy efficiency",
    #   # Poverty & Equity
    #   "Energy poverty",
    #   "Just energy transition",
    #   "Consumer rights in energy",
    #   # Prosumer & Community
    #   "Prosumer",
    #   "Citizen energy community",
    #   "Energy cooperative",
    #   "Peer-to-peer energy",
    #   "Demand response",
    #   # Funding & Incentives
    #   "Horizon Europe",
    #   "LIFE programme",
    #   "Energy Service Company",
    #   "Grants for home renovation"
    # ]

    # Wikipedia-optimized topics (exact/official article titles)
    wiki_topics = [
        # Policy & Governance
        "European Green Deal",
        "Energy Union",
        "Renewable Energy Directive (EU)",
        "National Energy and Climate Plans",
        "Just Transition Fund",
        # Markets & Pricing
        "Energy market liberalization in the European Union",
        "Electricity pricing",
        "Net metering",
        "Feed-in tariff",
        "Wholesale electricity market",
        "Capacity market",
        # Renewables & Storage
        "Solar photovoltaic energy",
        "Wind power",
        "Energy storage",
        "Electric vehicle",
        "Vehicle-to-grid",
        "Smart grid",
        "Microgrid",
        # Efficiency & Buildings
        "Passive house",
        "Nearly zero-energy building",
        "Energy Performance of Buildings Directive",
        "Heat pump",
        "Energy efficiency",
        # Poverty & Equity
        "Energy poverty",
        "Just energy transition",
        "Consumer rights in energy",
        # Prosumer & Community
        "Prosumer (energy)",
        "Citizen energy community",
        "Renewable energy cooperative",
        "Peer-to-peer energy",
        "Demand-side management",
        # Funding & Incentives
        "Horizon Europe",
        "LIFE programme",
        "Energy Service Company",
        "Grants for home renovation"
    ]

    # NewsAPI-optimized topics (short, headline-friendly keywords/phrases)
    news_topics = [
        # Policy & Governance
        "Green Deal",
        "Energy Union",
        "Renewable Energy Directive",
        "National Energy and Climate Plans",
        "Just Transition Fund",
        # Markets & Pricing
        "Electricity prices",
        "Net metering",
        "Feed-in tariff",
        "Energy market",
        "Capacity market",
        # Renewables & Storage
        "Solar panels",
        "Wind farms",
        "Energy storage",
        "Electric vehicles",
        "Vehicle to grid",
        "Smart grid",
        "Microgrids",
        # Efficiency & Buildings
        "Passive house",
        "Nearly zero-energy buildings",
        "Building performance",
        "Heat pumps",
        "Energy efficiency measures",
        # Poverty & Equity
        "Energy poverty",
        "Just transition",
        "Consumer energy rights",
        # Prosumer & Community
        "Prosumers",
        "Citizen energy communities",
        "Energy cooperatives",
        "Peer-to-peer energy",
        "Demand response program",
        # Funding & Incentives
        "Horizon Europe",
        "LIFE programme",
        "Energy service companies",
        "Home renovation grants"
    ]

    arxiv_topics = [
        'ti:"renewable energy sources"',
        'ti:"solar photovoltaic systems"',
        'ti:"wind energy harvesting"',
        'ti:"battery energy storage systems"',
        'ti:"thermal energy storage"',
        'ti:"hydrogen energy storage"',
        'ti:"power-to-gas"',
        'ti:"smart grid technologies"',
        'ti:"microgrid control"',
        'ti:"distributed energy resources"',
        'ti:"demand-side management"',
        'ti:"peer-to-peer energy trading"',
        'ti:"electric vehicle integration"',
        'ti:"vehicle-to-grid"',
        'ti:"building energy modeling"',
        'ti:"energy efficiency in buildings"',
        'ti:"heat pump systems"',
        'ti:"energy consumption forecasting"',
        'ti:"electricity pricing mechanisms"',
        'ti:"energy market optimization"',
        'ti:"capacity market design"',
        'ti:"grid stability and reliability"',
        'ti:"power system resilience"',
        'ti:"renewable energy economics"',
        'ti:"carbon neutrality strategies"',
        'ti:"decarbonization pathways"',
        'ti:"machine learning for energy systems"',
        'ti:"IoT in smart metering"',
        'ti:"energy data analytics"',
        'ti:"renewable energy policy modeling"',
        'ti:"energy poverty assessment"',
        'ti:"energy transition modeling"',
        'ti:"energy performance of buildings"',
        'ti:"electrical vehicle charging infrastructure"',
        'ti:"sustainable power systems"'
    ]

    # 2. EU & national gov/reg URLs
    gov_urls = [
      "https://energy.ec.europa.eu/index_en",     # EU portal
      "https://acer.europa.eu/",                  # ACER
      "https://www.bmk.gv.at/en.html",            # Austria
      "https://economie.fgov.be/en/themes/energy",# Belgium
      "https://www.me.government.bg/en",          # Bulgaria
      "https://meci.gov.cy",                      # Cyprus
      "https://ens.dk/en",                        # Denmark
      "https://www.mpo.cz/en/",                   # Czech Republic
      "https://mkm.ee/en",                        # Estonia
      "https://tem.fi/en/energy",                 # Finland
      "https://www.cre.fr/en",                    # France
      "https://www.bmwi.de/Navigation/EN/Home/home.html",  # Germany
      "https://www.ypengreenpolicy.gr/t-en",      # Greece
      "http://www.mekh.hu/",                      # Hungary
      "https://www.gov.ie/en/organisation/department-of-the-environment-climate-and-communications/", # Ireland
      "https://www.arera.it/EN/",                 # Italy
      "https://www.sprk.gov.lv/en",               # Latvia
      "https://enmin.lrv.lt/en/",                 # Lithuania
      "https://meco.gouvernement.lu/en/domaines-activites/energie.html",  # Luxembourg
      "https://www.rews.org.mt/",                 # Malta
      "https://www.government.nl/topics/renewable-energy",              # Netherlands
      "https://www.ure.gov.pl/en",                # Poland
      "https://www.erse.pt/en/home/",             # Portugal
      "https://anre.ro/",                         # Romania
      "https://www.urso.gov.sk/",                 # Slovakia
      "https://www.agen-rs.si/en",                # Slovenia
      "https://www.cnmc.es/",                     # Spain
      "https://www.energimyndigheten.se/en/"      # Sweden
    ]

    # env-controlled maxima
    mw = int(os.getenv("MAX_WIKI_ARTICLES", 5))
    mn = int(os.getenv("MAX_NEWS_ARTICLES", 5))
    ma = int(os.getenv("MAX_ARXIV_PAPERS", 5))
    mp = int(os.getenv("MAX_GOV_PAGES", 30))
    md = int(os.getenv("MAX_GOV_DEPTH", 3))

    # NewsAPI key
    news_key = os.getenv("NEWS_API_KEY")
    if not news_key:
        logging.error("Missing NEWS_API_KEY—exiting.")
        return

    # -- Wikipedia --
    if RUN_WIKI:
        for t in wiki_topics:
            try:
                w = get_energy_articles(query=t, max_articles=mw)
                append_records("output/wiki.jsonl", w)
                logging.info(f"Wiki '{t}': {len(w)} articles")
            except Exception as e:
                logging.error(f"Wiki '{t}' failed: {e}")

    # -- News --
    if RUN_NEWS:
        for t in news_topics:
            try:
                n = get_energy_news(api_key=news_key, query=t, max_articles=mn)
                append_records("output/news.jsonl", n)
                logging.info(f"News '{t}': {len(n)} articles")
            except Exception as e:
                logging.error(f"News '{t}' failed: {e}")

    # -- arXiv --
    if RUN_ARXIV:
        for t in arxiv_topics:
            try:
                a = search_arxiv_papers(query=t, max_papers=ma)
                append_records("output/arxiv.jsonl", a)
                logging.info(f"arXiv '{t}': {len(a)} papers")
            except Exception as e:
                logging.error(f"arXiv '{t}' failed: {e}")

    # -- Government / Regulatory --
    if RUN_GOV:
        for url in gov_urls:
            try:
                g = get_government_documents(start_url=url, max_pages=mp, max_depth=md)
                append_records("output/gov.jsonl", g)
                logging.info(f"Gov '{url}': {len(g)} docs")
            except Exception as e:
                logging.error(f"Gov '{url}' failed: {e}")

    logging.info("=== Collection complete. Check output/*.jsonl for results. ===")
    
if __name__ == "__main__":
    main()