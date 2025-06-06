import json
import re
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
import string

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

def is_text_corrupted(text, threshold=0.3):
    printable_chars = set(string.printable)
    if not text:
        return True
    non_printable_count = sum(1 for c in text if c not in printable_chars)
    corruption_ratio = non_printable_count / len(text)
    return corruption_ratio > threshold

def preprocess_jsonl_file(input_path: Path, output_path: Path):
    original_count = 0
    dedup_removed = 0
    lang_removed = 0
    corruption_removed = 0
    final_count = 0

    seen_titles = set()
    temp_records = []

    # Step 1: Replace HTML with plain text and collect records
    with input_path.open("r", encoding="utf-8") as fin:
        for line in fin:
            original_count += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            title = obj.get("title", "").strip()
            content = obj.get("content", "").strip()
            obj["content"] = strip_html(content)
            
            temp_records.append(obj)

            if original_count % 10000 == 0:
                logging.info(f"HTML stripped from {original_count} lines...")

    # Step 2: Remove duplicates based on title
    unique_records = []
    for obj in temp_records:
        title = obj.get("title", "").strip()
        if not title or title in seen_titles:
            dedup_removed += 1
            continue
        seen_titles.add(title)
        unique_records.append(obj)

    logging.info(f"Deduplication removed {dedup_removed} articles from {input_path.name}")

    # Step 3: Check language based on content
    lang_filtered_records = []
    for obj in unique_records:
        content = obj["content"]
        if len(content) < 50 or is_english(content):
            lang_filtered_records.append(obj)
        else:
            lang_removed += 1

    logging.info(f"Language filtering removed {lang_removed} articles from {input_path.name}")

    # Step 4: Remove corrupted content lines
    with output_path.open("w", encoding="utf-8") as fout:
        for obj in lang_filtered_records:
            content = obj["content"]
            if is_text_corrupted(content):
                corruption_removed += 1
                continue
            json.dump(obj, fout, ensure_ascii=False)
            fout.write("\n")
            final_count += 1

    # Logging final stats
    logging.info(f"Corruption filtering removed {corruption_removed} articles from {input_path.name}")
    logging.info(f"Processed {input_path.name}: {original_count} -> {final_count} articles")