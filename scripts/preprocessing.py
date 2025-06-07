import json
import re
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
import string
import shelve

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
    original_count = dedup_removed = lang_removed = corruption_removed = final_count = 0

    with shelve.open(str(input_path) + "_dedup.db") as seen_titles, \
         input_path.open("r", encoding="utf-8") as fin, \
         output_path.open("w", encoding="utf-8") as fout:

        for line in fin:
            original_count += 1

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            title = obj.get("title", "").strip()
            if not title:
                dedup_removed += 1
                continue

            # Deduplication using shelve (efficient disk-based set)
            if title in seen_titles:
                dedup_removed += 1
                continue
            seen_titles[title] = True  # Mark title as seen

            # Replace HTML immediately
            content = strip_html(obj.get("content", "").strip())

            # Language filtering
            if len(content) >= 50 and not is_english(content):
                lang_removed += 1
                continue

            # Corruption filtering
            if is_text_corrupted(content):
                corruption_removed += 1
                continue

            # Write clean record immediately
            obj["content"] = content
            json.dump(obj, fout, ensure_ascii=False)
            fout.write("\n")
            final_count += 1

            if original_count % 10000 == 0:
                logging.info(f"Processed {original_count} lines from {input_path.name}...")

    # Log final results clearly
    logging.info(f"Deduplication removed {dedup_removed} articles from {input_path.name}")
    logging.info(f"Language filtering removed {lang_removed} articles from {input_path.name}")
    logging.info(f"Corruption filtering removed {corruption_removed} articles from {input_path.name}")
    logging.info(f"Processed {input_path.name}: {original_count} -> {final_count} articles")