import json
import re

# Input/Output paths
txt_file = r"C:\RAG\06 Selection2.txt"
json_file = r"C:\RAG\06 Selection2.json"

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def parse_table(lines):
    table_lines = []
    description = []
    figure = None

    for line in lines:
        norm = normalize_whitespace(line)
        if re.search(r"\s{2,}|\t|\|", line):  # looks like a table row
            table_lines.append(norm)
        elif "fig." in norm.lower():
            figure = norm
        else:
            description.append(norm)

    if table_lines:
        split_rows = [re.split(r"\s{2,}|\t|\|", row) for row in table_lines]
        headers = [normalize_whitespace(h) for h in split_rows[0]]
        rows = []
        for row in split_rows[1:]:
            row_data = {headers[i]: normalize_whitespace(row[i]) if i < len(row) else "" for i in range(len(headers))}
            rows.append(row_data)

        return {
            "description": " ".join(description),
            "table": {
                "headers": headers,
                "rows": rows
            },
            "figure": figure
        }
    return None

# Read file
with open(txt_file, "r", encoding="utf-8") as f:
    raw_content = f.read()

# Split slides by the marker "<<<"
raw_slides = [s.strip() for s in raw_content.split("<<<") if s.strip()]

slides = []
for i, block in enumerate(raw_slides, start=1):
    lines = [normalize_whitespace(l) for l in block.splitlines() if l.strip()]
    if not lines:
        continue

    # Heuristic: first non-empty line is the title
    title = lines[0]
    text_lines = lines[1:]

    table_json = parse_table(text_lines)

    slide_data = {
        "page_number": i,
        "title": title,
        "text": " ".join(text_lines) if not table_json else None
    }

    if table_json:
        slide_data.update(table_json)

    slides.append(slide_data)

# Final JSON
output = {
    "course_name": "Your Course Name",
    "chapter_name": "06 Selection",
    "number_of_slides": len(slides),
    "slides": slides
}

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print(f"JSON saved to {json_file}")
