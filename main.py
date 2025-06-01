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

    WIKI_THRESHOLD = float(os.getenv("WIKI_RELEVANCE_THRESHOLD", 1.0))

    RUN_WIKI  = os.getenv("RUN_WIKI", "1")  == "1"  # set to "0" to disable
    RUN_NEWS  = os.getenv("RUN_NEWS", "1")  == "1"
    RUN_ARXIV = os.getenv("RUN_ARXIV", "1") == "1"
    RUN_GOV   = os.getenv("RUN_GOV", "1")   == "1"
    logging.info(f"RUN_WIKI: {RUN_WIKI}, RUN_NEWS: {RUN_NEWS}, RUN_ARXIV: {RUN_ARXIV}, RUN_GOV: {RUN_GOV}")


    # Wikipedia-optimized topics (exact/official article titles)
    wiki_topics = [
        # Policy & Governance
        "European Green Deal",
        "Fit for 55 (European Union)", 
        "European Climate Law",
        "European Green Deal Industrial Plan",
        "European Climate Pact",
        "European Energy Security Strategy",
        "European Union Emissions Trading System",
        "European Climate Adaptation Strategy",
        "European Union Renewable Energy Directive",
        "European Union Energy Efficiency Directive",
        "European Union Energy Performance of Buildings Directive",
        "EU taxonomy for sustainable activities",
        "Energy Union",
        "Renewable Energy Directive (EU)",
        "European Union National Energy and Climate Plans",
        "National Energy and Climate Plans",
        "Just Transition Fund",
        # Markets & Pricing
        "Energy market liberalization in the European Union",
        "European Network of Transmission System Operators for Electricity (ENTSO-E)",
        "European Network of Transmission System Operators for Gas (ENTSOG)",
        "European Union Agency for the Cooperation of Energy Regulators (ACER)",    
        "Electricity market in the European Union",
        "Electricity pricing",
        "Net metering",
        "Feed-in tariff",
        "Energy market",
        "Wholesale electricity market",
        "Capacity market",
        # Renewables & Storage
        "Solar photovoltaic energy",
        "Offshore wind power",
        "Onshore wind power",
        "Green hydrogen", 
        "Hydrogen economy",
        "European Battery Alliance",
        "Net-Zero Industry Act", 
        "Wind power",
        "Energy storage",
        "Electric vehicle",
        "Vehicle-to-grid",
        "Smart grid",
        "Microgrid",
        "Distributed energy resources",
        "Demand-side management",
        "Peer-to-peer energy trading",
        "Electric vehicle integration",
        # Efficiency & Buildings
        "Passive house",
        "Nearly zero-energy building",
        "European Union energy label",
        "Energy Performance of Buildings Directive",
        "Heat pump",
        "Renovation Wave",
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
        "Grants for home renovation",
        "Modernisation Fund",
        "Social Climate Fund",
        "Next Generation EU",
        "Just Transition Mechanism" 
    ]

    eu_countries = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "the Czech Republic",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary",
    "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta",
    "the Netherlands", "Poland", "Portugal", "Romania", "Slovakia",
    "Slovenia", "Spain", "Sweden"
    ]

    country_level_topics = [
    "Energy in {}",
    "Electricity sector in {}",
    "Renewable energy in {}",
    "List of power stations in {}",
    "Wind power in {}",
    "Solar power in {}",
    "Hydroelectricity in {}",
    "Geothermal power in {}",
    "Nuclear power in {}",
    "Coal in {}",
    "Natural gas in {}",
    "Climate change in {}",
    "Energy policy of {}",
    "Plug-in electric vehicles in {}"
    ]

    country_energy_topics = [
    topic.format(country) for country in eu_countries for topic in country_level_topics
    ]

    # NewsAPI-optimized topics (short, headline-friendly keywords/phrases)
    news_topics = [
        # Policy & Governance
        "Green Deal",
        "European Green Deal",
        "Energy Union",
        "Renewable Energy Directive",
        "National Energy and Climate Plans",
        "Just Transition Fund",
        "EU climate policy",
        "Fit for 55",
        "EU emissions targets",
        "carbon neutrality",
        "net zero",
        "carbon tax",
        "climate law",
        "emissions trading",

        # Markets & Pricing
        "Electricity prices",
        "gas prices",
        "energy bills",
        "rising energy bills",
        "energy crisis",
        "gas crisis",
        "cost of living crisis",
        "energy subsidies",
        "energy market",
        "capacity market",
        "net metering",
        "feed in tariff",

        # Renewables & Storage
        "solar panels",
        "rooftop solar",
        "solar power",
        "wind farms",
        "offshore wind",
        "energy storage",
        "battery storage",
        "electric vehicles",
        "electric cars",
        "EV charging",
        "vehicle to grid",
        "smart grid",
        "microgrids",
        "green hydrogen",
        "renewable energy investment",
        "green energy projects",
        "energy independence",

        # Efficiency & Buildings
        "energy efficiency",
        "energy efficiency measures",
        "energy saving tips",
        "passive house",
        "nearly zero energy buildings",
        "building performance",
        "home insulation",
        "heat pumps",
        "smart meters",

        # Poverty & Equity
        "energy poverty",
        "fuel poverty",
        "just transition",
        "consumer energy rights",
        "heating costs",

        # Prosumer & Community
        "prosumers",
        "citizen energy communities",
        "community energy",
        "energy cooperatives",
        "peer to peer energy",
        "demand response",
        "community solar",

        # Funding & Incentives
        "Horizon Europe",
        "LIFE programme",
        "Energy service companies",
        "home renovation grants",
        "solar panel grants",
        "heat pump incentives",
        "energy efficiency funding",
        "renovation wave",

        # Climate Impacts & Extreme Weather
        "heatwave",
        "drought",
        "wildfires",
        "floods",
        "extreme weather",
        "climate crisis",

        # Fossil Fuels and Transition
        "coal phase out",
        "fossil fuel subsidies",
        "oil prices",
        "natural gas shortage",
        "Russian gas",
        "energy security",
        "gas imports",
        "renewables vs fossil fuels"
    ]

    arxiv_topics = [
        'all:"renewable energy sources"',
        'all:"solar photovoltaic systems"',
        'all:"wind energy harvesting"',
        'all:"battery energy storage systems"',
        'all:"thermal energy storage"',
        'all:"hydrogen energy storage"',
        'all:"power-to-gas"',
        'all:"smart grid technologies"',
        'all:"microgrid control"',
        'all:"distributed energy resources"',
        'all:"demand-side management"',
        'all:"peer-to-peer energy trading"',
        'all:"electric vehicle integration"',
        'all:"vehicle-to-grid"',
        'all:"building energy modeling"',
        'all:"energy efficiency in buildings"',
        'all: "net zero energy buildings"',
        'all:"heat pump systems"',
        'all:"energy consumption forecasting"',
        'all:"electricity pricing mechanisms"',
        'all:"energy market optimization"',
        'all:"capacity market design"',
        'all:"grid stability and reliability"',
        'all:"power system resilience"',
        'all:"renewable energy economics"',
        'all:"carbon neutrality strategies"',
        'all:"decarbonization pathways"',
        'all:"machine learning for energy systems"',
        'all:"IoT in smart metering"',
        'all:"energy data analytics"',
        'all:"renewable energy policy modeling"',
        'all:"energy poverty"',
        'all:"energy justice"',
        'all:"energy democracy"',
        'all:"just transition"',
        'all:"prosumer behavior"',
        'all:"household energy decision-making"',
        'all:"energy consumption behavior"',
        'all:"energy awareness"',
        'all:"energy literacy"',
        'all:"social acceptance of renewable energy"',
        'all:"energy communities"',
        'all:"citizen energy communities"',
        'all:"energy behavior change"',
        'all:"renewable energy adoption"',
        'all:"energy poverty assessment"',
        'all:"energy transition modeling"',
        'all:"energy performance of buildings"',
        'all:"local energy markets"',
        'all:"transactive energy"',
        'all:"electrical vehicle charging infrastructure"',
        'all:"European green deal"',
        'all:"Fit for 55"',
        'all:"REPowerEU"',
        'all:"clean energy package"',
        'all:"renewable energy directive"',
        'all:"EU climate policy"',
        'all:"EU energy policy"',
        'all:"energy union"',
        'all:"European electricity market"',
        'all:"European energy security"',
        'all:"European energy transition"',
        'all:"sustainable power systems"'
    ]

    # 2. EU & national gov/reg URLs
    gov_urls = [
        # EU-level Institutions
        "https://energy.ec.europa.eu/index_en",                   # EU DG Energy portal
        "https://acer.europa.eu/",                                # Agency for Cooperation of Energy Regulators (ACER)
        "https://ceer.eu/",                                       # Council of European Energy Regulators (CEER)
        "https://entsoe.eu/",                                     # European Network of TSOs for Electricity (ENTSO-E)
        "https://entsog.eu/",                                     # European Network of TSOs for Gas (ENTSO-G)
        "https://cinea.ec.europa.eu/",                            # European Climate, Infrastructure and Environment Executive Agency (CINEA)
        "https://cordis.europa.eu/",                              # CORDIS – EU research projects portal
        "https://ec.europa.eu/programmes/horizon2020/",           # Horizon Europe funding program
        "https://www.energy-community.org/",                      # Energy Community Treaty Organization

        # National Energy Regulatory and Government Bodies
        "https://www.e-control.at/en",                            # Austria (E-Control)
        "https://www.creg.be/en",                                 # Belgium (CREG)
        "https://www.dker.bg/en/home/",                           # Bulgaria (Energy & Water Regulatory Commission - EWRC)
        "https://hera.hr/en/html/",                               # Croatia (Croatian Energy Regulatory Agency - HERA)
        "https://www.cera.org.cy/en-gb/home/",                    # Cyprus (Energy Regulatory Authority - CERA)
        "https://www.eru.cz/en/",                                 # Czech Republic (Energy Regulatory Office - ERÚ)
        "https://www.konkurentsiamet.ee/en",                      # Estonia (Estonian Competition Authority)
        "https://energiavirasto.fi/en/frontpage",                 # Finland (Energy Authority)
        "https://www.cre.fr/en",                                  # France (Commission de Régulation de l'Énergie - CRE)
        "https://www.bundesnetzagentur.de/EN/",                   # Germany (Federal Network Agency - BNetzA)
        "https://www.rae.gr/en/",                                 # Greece (Regulatory Authority for Energy - RAE)
        "https://www.mekh.hu/home",                               # Hungary (Energy and Public Utility Regulatory Authority - MEKH)
        "https://www.cru.ie/",                                    # Ireland (Commission for Regulation of Utilities - CRU)
        "https://www.arera.it/en/",                               # Italy (ARERA)
        "https://www.sprk.gov.lv/en",                             # Latvia (Public Utilities Commission - SPRK)
        "https://www.vert.lt/en/Pages/updates.aspx",              # Lithuania (National Energy Regulatory Council - VERT)
        "https://web.ilr.lu/EN/",                                 # Luxembourg (Institute of Regulation - ILR)
        "https://www.rews.org.mt/",                               # Malta (Regulator for Energy and Water Services - REWS)
        "https://www.acm.nl/en",                                  # Netherlands (Authority for Consumers & Markets - ACM)
        "https://www.ure.gov.pl/en",                              # Poland (Energy Regulatory Office - URE)
        "https://www.erse.pt/en/home/",                           # Portugal (Energy Services Regulatory Authority - ERSE)
        "https://www.urso.gov.sk/en/",                            # Slovakia (Regulatory Office for Network Industries - ÚRSO)
        "https://www.agen-rs.si/en",                              # Slovenia (Energy Agency - AGEN-RS)
        "https://ei.se/ei-in-english",                            # Sweden (Swedish Energy Markets Inspectorate - Ei)
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
    RUN_WIKI_COUNTRY_ONLY = os.getenv("RUN_WIKI_COUNTRY_ONLY", "0") == "1"

    if RUN_WIKI_COUNTRY_ONLY:
        active_wiki_topics = country_energy_topics          
        wiki_exact = True                                   
    else:
        active_wiki_topics = wiki_topics                    
        wiki_exact = False

    if RUN_WIKI:
        for t in active_wiki_topics:
            try:
                w = get_energy_articles(query=t, max_articles=mw, threshold=WIKI_THRESHOLD, exact=wiki_exact)
                append_records("output/wiki.jsonl", w)
                logging.info(f"Wiki '{t}': {len(w)} articles")
            except Exception as e:
                logging.error(f"Wiki '{t}' failed: {e}")

    # -- News --
    if RUN_NEWS:

        for t in news_topics:
            try:
                n = get_energy_news(api_key=news_key, query=t, max_articles=mn, language="en", from_date="2022-01-01T00:00:00Z")
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