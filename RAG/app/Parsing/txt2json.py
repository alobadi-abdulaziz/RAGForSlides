# Simple TXT -> JSON converter
# - Split pages on <<<\f
# - Remove URL-only lines and standalone page-number lines
# - Title = first non-empty, non-URL, non-page-number line
# - Store cleaned full page text in "text"

import json
import re
from pathlib import Path

# ==== Adjust these values as needed ====
INPUT_TXT   = r"C:\RAG\05 Fundementals - String.txt"    # Source TXT file
OUTPUT_JSON = r"C:\RAG\05 Fundementals - String.json"   # Output JSON file

COURSE_NAME   = "<<< اكتب اسم الكورس هنا >>>"
CHAPTER_NAME  = "<<< اكتب اسم الفصل هنا >>>"
NUMBER_OF_SLIDES = None  # Set an int manually or leave None to auto-count(number of slides or pages)
# ======================================

def split_pages(text: str):
    """Split on '<<<\\f' (form feed is \\x0c); trim empty pages."""
    pages = re.split(r"<<<\s*\x0c", text)
    pages = [p.strip() for p in pages if p and p.strip()]
    return pages

def is_url_line(line: str) -> bool:
    """Return True if the line looks like a URL."""
    return bool(re.match(r"\s*https?://", line.strip(), flags=re.IGNORECASE))

def is_standalone_page_number(line: str) -> bool:
    """Return True if the line is only a short integer (e.g., '13')(so we can delete it)."""
    return bool(re.fullmatch(r"\s*\d{1,4}\s*", line))

def clean_page_text(page: str) -> str:
    """
    Remove URL-only lines and standalone page-number lines.
    Keep everything else as-is.
    """
    cleaned_lines = []
    for line in page.splitlines():
        if is_url_line(line):
            continue
        if is_standalone_page_number(line):
            continue
        cleaned_lines.append(line)
    # Join back and strip extra whitespace
    return "\n".join(cleaned_lines).strip()

def infer_title(cleaned_page_text: str) -> str:
    """Pick the first non-empty line as title (after cleaning)."""
    for line in cleaned_page_text.splitlines():
        line = line.strip()
        if line:
            return line[:120]  # simple safety trim
    return "Untitled"

def main():
    text = Path(INPUT_TXT).read_text(encoding="utf-8", errors="ignore")
    pages_raw = split_pages(text)

    slides = []
    for i, raw_page in enumerate(pages_raw, start=1):
        page_text = clean_page_text(raw_page)
        title = infer_title(page_text)
        slides.append({
            "page_number": i,
            "title": title,
            "text": page_text  # cleaned full page text
        })

    num_slides = NUMBER_OF_SLIDES if NUMBER_OF_SLIDES is not None else len(slides)

    data = {
        "course_name": COURSE_NAME,
        "chapter_name": CHAPTER_NAME,
        "number_of_slides": num_slides,
        "slides": slides
    }

    Path(OUTPUT_JSON).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created: {OUTPUT_JSON}")
    print(f"Pages: {len(slides)}")

if __name__ == "__main__":
    main()
