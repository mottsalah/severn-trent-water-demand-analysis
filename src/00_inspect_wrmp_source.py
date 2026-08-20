from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "Water-resources-market-information22-Strategic-Grid.xlsx"
OUT = ROOT / "outputs" / "source_structure_report.txt"

if not SOURCE.exists():
    raise FileNotFoundError(f"Source workbook not found: {SOURCE}")

xls = pd.ExcelFile(SOURCE)
lines = [
    "Severn Trent WRMP24 Strategic Grid source inspection",
    f"Source: {SOURCE.name}",
    f"Sheets: {len(xls.sheet_names)}",
    "",
]

for sheet in xls.sheet_names:
    df = pd.read_excel(SOURCE, sheet_name=sheet, header=None)
    non_empty_rows = int(df.dropna(how="all").shape[0])
    non_empty_cols = int(df.dropna(axis=1, how="all").shape[1])
    lines.append(f"{sheet}: {non_empty_rows} non-empty rows x {non_empty_cols} non-empty columns")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines), encoding="utf-8")

print("Source inspection complete.")
print(f"Workbook: {SOURCE.name}")
print(f"Sheets found: {len(xls.sheet_names)}")
for name in xls.sheet_names:
    print(f"  - {name}")
print(f"Report: {OUT}")
