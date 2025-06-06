import json
import re
import logging
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def strip_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()

def is_english(text: str) -> bool:
    DetectorFactory.seed = 0
    try:
        return detect(text) == "en"
    except Exception:
        return False

def preprocess_jsonl_file(input_path: Path, output_path: Path):
    records = []
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                records.append(obj)
            except json.JSONDecodeError:
                continue

    df = pd.DataFrame.from_records(records)
    original_count = len(df)

    # Deduplication based on title
    df_before_dedup = len(df)
    df = df.drop_duplicates(subset=["title"], keep="first")
    dedup_removed = df_before_dedup - len(df)
    logging.info(f"Deduplication removed {dedup_removed} articles from {input_path.name}")

    # Strip HTML content
    df["content"] = df["content"].fillna("").apply(strip_html)

    # Language filtering
    df_before_lang = len(df)
    df = df[df["title"].apply(is_english) & df["content"].apply(lambda x: is_english(x) or len(x) < 50)]
    lang_removed = df_before_lang - len(df)
    logging.info(f"Language filtering removed {lang_removed} articles from {input_path.name}")

    final_count = len(df)
    logging.info(f"Processed {input_path.name}: {original_count} -> {final_count} articles")

    with output_path.open("w", encoding="utf-8") as fout:
        for row in df.to_dict(orient="records"):
            json.dump(row, fout, ensure_ascii=False)
            fout.write("\n")