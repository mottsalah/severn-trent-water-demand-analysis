from pathlib import Path
import re
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "Water-resources-market-information22-Strategic-Grid.xlsx"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
PROCESSED.mkdir(parents=True, exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)

YEAR_RE = re.compile(r"^\d{4}-\d{2,4}$")

def extract_table(sheet_name: str) -> pd.DataFrame:
    df = pd.read_excel(SOURCE, sheet_name=sheet_name, header=None)
    header_row = None
    for idx in range(min(15, len(df))):
        vals = [str(v).strip() for v in df.iloc[idx].tolist() if pd.notna(v)]
        if any(v == "Line" for v in vals) and any(YEAR_RE.match(v) for v in vals):
            header_row = idx
            break
    if header_row is None:
        raise ValueError(f"Could not find year header in {sheet_name}")

    year_cols = []
    for col_idx, value in enumerate(df.iloc[header_row].tolist()):
        if pd.notna(value) and YEAR_RE.match(str(value).strip()):
            year_cols.append((col_idx, str(value).strip()))

    records = []
    for row_idx in range(header_row + 1, len(df)):
        line = df.iat[row_idx, 1] if df.shape[1] > 1 else np.nan
        requirement = df.iat[row_idx, 2] if df.shape[1] > 2 else np.nan
        units = df.iat[row_idx, 4] if df.shape[1] > 4 else np.nan
        if pd.isna(line) or pd.isna(requirement):
            continue
        try:
            line_num = int(float(line))
        except Exception:
            continue
        for col_idx, year in year_cols:
            value = df.iat[row_idx, col_idx]
            if pd.notna(value):
                records.append({
                    "sheet": sheet_name,
                    "line": line_num,
                    "data_requirement": str(requirement).strip(),
                    "units": str(units).strip() if pd.notna(units) else "",
                    "financial_year": year,
                    "year_start": int(year[:4]),
                    "value": float(value),
                })
    return pd.DataFrame(records)


t3 = extract_table("Table 3")
t2 = extract_table("Table 2")
t4 = extract_table("Table 4")

# Map the published WRMP rows to compact analytical field names.
MAP3 = {
    1: "nhh_metered_ml_d",
    2: "nhh_unmetered_ml_d",
    3: "hh_metered_ml_d",
    4: "hh_unmetered_ml_d",
    5: "pcc_metered_lhd",
    6: "pcc_unmetered_lhd",
    7: "pcc_avg_lhd",
    8: "leakage_ml_d",
    9: "leakage_l_prop_d",
    10: "metered_properties_000",
    11: "total_properties_000",
    12: "population_000",
    13: "metered_occupancy_h_prop",
    14: "unmetered_occupancy_h_prop",
    15: "metering_penetration",
}
MAP2 = {
    1: "deployable_output_ml_d",
    2: "climate_change_supply_impact_ml_d",
    3: "sustainability_reduction_ml_d",
    4: "other_supply_change_ml_d",
    5: "raw_treatment_losses_ml_d",
    6: "outage_allowance_ml_d",
}
MAP4 = {
    1: "distribution_input_ml_d",
    2: "wafu_own_sources_ml_d",
    3: "total_wafu_ml_d",
    4: "target_headroom_ml_d",
    5: "published_sdb_ml_d",
}

def pivot_fields(df, mapping):
    x = df[df["line"].isin(mapping)].copy()
    x["field"] = x["line"].map(mapping)
    return x.pivot_table(index=["financial_year", "year_start"], columns="field", values="value", aggfunc="first").reset_index()

baseline = pivot_fields(t3, MAP3)
for part in (pivot_fields(t2, MAP2), pivot_fields(t4, MAP4)):
    baseline = baseline.merge(part, on=["financial_year", "year_start"], how="outer")

baseline = baseline.sort_values("year_start").reset_index(drop=True)
baseline["wrz"] = "Strategic Grid"
baseline["household_consumption_ml_d"] = baseline["hh_metered_ml_d"] + baseline["hh_unmetered_ml_d"]
baseline["non_household_consumption_ml_d"] = baseline["nhh_metered_ml_d"] + baseline["nhh_unmetered_ml_d"]
baseline["customer_consumption_ml_d"] = baseline["household_consumption_ml_d"] + baseline["non_household_consumption_ml_d"]
baseline["residual_other_demand_ml_d"] = baseline["distribution_input_ml_d"] - baseline["customer_consumption_ml_d"] - baseline["leakage_ml_d"]
baseline["calculated_sdb_ml_d"] = baseline["total_wafu_ml_d"] - baseline["distribution_input_ml_d"] - baseline["target_headroom_ml_d"]
baseline["sdb_reconciliation_error_ml_d"] = baseline["calculated_sdb_ml_d"] - baseline["published_sdb_ml_d"]
baseline["di_reconciliation_error_ml_d"] = (
    baseline["customer_consumption_ml_d"] + baseline["leakage_ml_d"] + baseline["residual_other_demand_ml_d"] - baseline["distribution_input_ml_d"]
)

# Validation checks.
checks = []
def add_check(name, passed, detail):
    checks.append({"check": name, "status": "PASS" if bool(passed) else "FAIL", "detail": detail})

add_check("Source years extracted", len(baseline) >= 20, f"{len(baseline)} annual rows")
add_check("No duplicate years", baseline["financial_year"].is_unique, f"{baseline['financial_year'].nunique()} unique years")
add_check("Population positive", (baseline["population_000"] > 0).all(), "All extracted population values > 0")
add_check("Distribution input positive", (baseline["distribution_input_ml_d"] > 0).all(), "All extracted DI values > 0")
add_check("PCC plausible", baseline["pcc_avg_lhd"].between(80, 200).all(), "Average PCC between 80 and 200 l/h/d")
add_check("Metering penetration in range", baseline["metering_penetration"].between(0, 1).all(), "All values between 0 and 1")
add_check("SDB reconciles to published", baseline["sdb_reconciliation_error_ml_d"].abs().max() < 0.01, f"Max error {baseline['sdb_reconciliation_error_ml_d'].abs().max():.6f} Ml/d")
add_check("Demand components reconcile", baseline["di_reconciliation_error_ml_d"].abs().max() < 1e-6, f"Max error {baseline['di_reconciliation_error_ml_d'].abs().max():.8f} Ml/d")

validation = pd.DataFrame(checks)

baseline.to_csv(PROCESSED / "strategic_grid_baseline.csv", index=False)
t3.to_csv(PROCESSED / "wrmp_table3_long.csv", index=False)
t2.to_csv(PROCESSED / "wrmp_table2_long.csv", index=False)
t4.to_csv(PROCESSED / "wrmp_table4_long.csv", index=False)
validation.to_csv(OUTPUTS / "baseline_validation.csv", index=False)

print("Baseline dataset build complete.")
print(f"Years: {baseline['financial_year'].iloc[0]} to {baseline['financial_year'].iloc[-1]}")
print(f"Rows: {len(baseline)}")
print(f"Validation checks: {(validation['status']=='PASS').sum()}/{len(validation)} PASS")
print(f"Output: {PROCESSED / 'strategic_grid_baseline.csv'}")
if not (validation["status"] == "PASS").all():
    raise SystemExit("FAIL: one or more baseline validation checks failed.")
print("PASS: published Strategic Grid baseline extracted and reconciled.")
