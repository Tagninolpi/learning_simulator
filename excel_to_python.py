import openpyxl
import json

def excel_to_json(excel_path: str, output_path: str):
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active

    words = {}
    for row in ws.iter_rows(min_row=2, values_only=True):  # skip header row
        japanese = row[1]  # column B = index 1
        german_raw = row[2]  # column C = index 2

        if not japanese or not german_raw:
            continue

        # split multiple translations by comma or slash
        translations = [t.strip() for t in str(german_raw).replace("/", ",").split(",") if t.strip()]

        words[str(japanese).strip()] = translations

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(words)} words written to {output_path}")

excel_to_json("wörterliste_N4.xlsx", "words.json")