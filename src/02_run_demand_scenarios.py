from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASELINE_FILE = ROOT / "data" / "processed" / "strategic_grid_baseline.csv"
SCENARIO_FILE = ROOT / "config" / "scenarios.csv"
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(BASELINE_FILE)
scenarios = pd.read_csv(SCENARIO_FILE)

results = []
for _, s in scenarios.iterrows():
    x = base.copy()
    start_year = int(s["start_year"])
    end_year = int(s["end_year"])
    denom = max(end_year - start_year, 1)
    ramp = ((x["year_start"] - start_year) / denom).clip(lower=0, upper=1)

    pop_change = float(s["population_change_end_pct"]) / 100.0
    nhh_change = float(s["nhh_change_end_pct"]) / 100.0
    leakage_change = float(s["leakage_change_end_pct"]) / 100.0

    x["scenario_name"] = s["scenario_name"]
    x["scenario_description"] = s["description"]
    x["ramp_factor"] = ramp

    x["scenario_population_000"] = x["population_000"] * (1 + ramp * pop_change)

    if pd.notna(s["pcc_target_lhd"]):
        target = float(s["pcc_target_lhd"])
        baseline_end_pcc = float(x.loc[x["year_start"] <= end_year, "pcc_avg_lhd"].iloc[-1])
        additional_delta = target - baseline_end_pcc
        x["scenario_pcc_lhd"] = x["pcc_avg_lhd"] + ramp * additional_delta
    else:
        x["scenario_pcc_lhd"] = x["pcc_avg_lhd"]

    population_ratio = x["scenario_population_000"] / x["population_000"]
    pcc_ratio = x["scenario_pcc_lhd"] / x["pcc_avg_lhd"]
    x["scenario_household_consumption_ml_d"] = x["household_consumption_ml_d"] * population_ratio * pcc_ratio
    x["scenario_non_household_consumption_ml_d"] = x["non_household_consumption_ml_d"] * (1 + ramp * nhh_change)
    x["scenario_leakage_ml_d"] = x["leakage_ml_d"] * (1 + ramp * leakage_change)
    x["scenario_residual_other_demand_ml_d"] = x["residual_other_demand_ml_d"]

    x["scenario_distribution_input_ml_d"] = (
        x["scenario_household_consumption_ml_d"]
        + x["scenario_non_household_consumption_ml_d"]
        + x["scenario_leakage_ml_d"]
        + x["scenario_residual_other_demand_ml_d"]
    )
    x["demand_change_vs_baseline_ml_d"] = x["scenario_distribution_input_ml_d"] - x["distribution_input_ml_d"]
    x["demand_change_vs_baseline_pct"] = x["demand_change_vs_baseline_ml_d"] / x["distribution_input_ml_d"]
    x["scenario_sdb_ml_d"] = x["total_wafu_ml_d"] - x["scenario_distribution_input_ml_d"] - x["target_headroom_ml_d"]
    x["sdb_improvement_vs_baseline_ml_d"] = x["scenario_sdb_ml_d"] - x["published_sdb_ml_d"]
    x["deficit_flag"] = np.where(x["scenario_sdb_ml_d"] < 0, "Deficit", "Surplus")
    results.append(x)

all_results = pd.concat(results, ignore_index=True)
all_results.to_csv(OUTPUTS / "scenario_results.csv", index=False)

# Summarise the final forecast year for an interview-ready comparison table.
last_year = int(base["year_start"].max())
summary = all_results[all_results["year_start"] == last_year][[
    "scenario_name", "financial_year", "scenario_population_000", "scenario_pcc_lhd",
    "scenario_household_consumption_ml_d", "scenario_non_household_consumption_ml_d",
    "scenario_leakage_ml_d", "scenario_distribution_input_ml_d", "demand_change_vs_baseline_ml_d",
    "demand_change_vs_baseline_pct", "scenario_sdb_ml_d", "sdb_improvement_vs_baseline_ml_d", "deficit_flag"
]].copy()
summary = summary.sort_values("scenario_distribution_input_ml_d")
summary.to_csv(OUTPUTS / "scenario_summary.csv", index=False)

# Small QA report.
qa = []
qa.append(("All scenarios produced", len(summary) == len(scenarios), f"{len(summary)} of {len(scenarios)} scenarios"))
qa.append(("No missing scenario demand", all_results["scenario_distribution_input_ml_d"].notna().all(), "Scenario DI complete"))
qa.append(("Published baseline unchanged", all_results.loc[all_results["scenario_name"] == "Published Baseline", "demand_change_vs_baseline_ml_d"].abs().max() < 1e-8, "Baseline delta is zero"))
qa.append(("SDB formula reconciles", ((all_results["total_wafu_ml_d"] - all_results["scenario_distribution_input_ml_d"] - all_results["target_headroom_ml_d"]) - all_results["scenario_sdb_ml_d"]).abs().max() < 1e-8, "SDB formula exact"))
qa_df = pd.DataFrame([{"check":a,"status":"PASS" if b else "FAIL","detail":c} for a,b,c in qa])
qa_df.to_csv(OUTPUTS / "scenario_validation.csv", index=False)

print("Demand scenario analysis complete.")
print(f"Scenarios: {len(scenarios)}")
print(f"Years per scenario: {len(base)}")
print(f"Scenario rows: {len(all_results)}")
print(f"Validation checks: {(qa_df['status']=='PASS').sum()}/{len(qa_df)} PASS")
print(f"Summary year: {summary['financial_year'].iloc[0]}")
print(f"Output: {OUTPUTS / 'scenario_results.csv'}")
print(f"Output: {OUTPUTS / 'scenario_summary.csv'}")
if not (qa_df["status"] == "PASS").all():
    raise SystemExit("FAIL: scenario validation failed.")
print("PASS: scenario engine completed and validated.")
