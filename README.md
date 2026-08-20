# Severn Trent Water Demand Forecasting and Scenario Analysis

Interview-focused portfolio project using published Severn Trent WRMP24 Strategic Grid market information data.

## What the project demonstrates
- water demand data extraction and standardisation
- household and non-household consumption analysis
- PCC, leakage, population and metering trend analysis
- baseline supply-demand balance reconciliation
- scenario and sensitivity modelling
- automated data-quality checks
- Excel/Power BI-ready analytical outputs

## Primary source
Severn Trent WRMP24 market information workbook for the Strategic Grid Water Resource Zone.

Source page/files are publicly available from Severn Trent's WRMP publications. The workbook included here is used only as the public analytical input to this independent prototype.

## Run
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python src\00_inspect_wrmp_source.py
python src\01_build_baseline_dataset.py
python src\02_run_demand_scenarios.py
```

## Outputs
- `data/processed/strategic_grid_baseline.csv`
- `outputs/baseline_validation.csv`
- `outputs/scenario_results.csv`
- `outputs/scenario_summary.csv`
- `outputs/scenario_validation.csv`

## Scenario assumptions
Scenario definitions are intentionally transparent and editable in `config/scenarios.csv`. Except for the published baseline, scenario adjustments are illustrative analytical sensitivities and should not be presented as Severn Trent forecasts.
