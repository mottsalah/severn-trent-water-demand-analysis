# Severn Trent Water Demand Forecasting and Scenario Analysis

Independent public-data analytical project using Severn Trent's published WRMP24 Strategic Grid planning information to explore long-term water demand, demand-management sensitivities and supply-demand balance.

![Severn Trent Demand Scenario Explorer](Report%20Screenshots/Severn_Trent_Demand_Scenario_Explorer.png)

## Project Overview

This project explores how changes in household water consumption, population growth, non-household demand and leakage could affect the long-term demand position of Severn Trent's Strategic Grid Water Resource Zone.

The project combines Python-based data extraction, validation and scenario modelling with an Excel assurance workbook and an interactive Power BI dashboard.

The analysis uses the published Severn Trent Strategic Grid planning baseline and applies five independent illustrative sensitivities. These sensitivity scenarios are analytical assumptions created for this project and are not Severn Trent forecasts.

## Project Objective

The objective was to build a transparent and reproducible analytical workflow that:

- extracts and standardises published WRMP planning information
- reconciles the Strategic Grid baseline
- analyses household and non-household water demand
- explores the impact of PCC, population, leakage and non-household demand assumptions
- recalculates long-term demand under alternative sensitivities
- assesses the effect on supply-demand balance
- separates published data from independent scenario assumptions
- performs automated validation checks
- produces auditable Excel outputs
- presents the results through an interactive Power BI dashboard

## Data Source

The primary source is Severn Trent's published WRMP24 market information workbook for the Strategic Grid Water Resource Zone.

The source workbook is stored under:

`data/raw/Water-resources-market-information22-Strategic-Grid.xlsx`

The workbook is used as the public analytical input to this independent prototype.

## Forecast Coverage

The extracted baseline covers:

- 2020-21 to 2044-45
- 25 financial years
- Strategic Grid Water Resource Zone
- household consumption
- non-household consumption
- population
- PCC
- leakage
- distribution input
- deployable output and Water Available For Use measures
- target headroom
- supply-demand balance

## Analytical Workflow

The workflow is split into three Python stages.

### 1. Source Inspection

`src/00_inspect_wrmp_source.py`

Inspects the published workbook structure before transformation.

The source workbook contains 10 worksheets:

- Cover sheet
- Change log
- Table 1
- Table 2
- Table 3
- Table 4
- Table 5
- Table 6
- Table 7
- Table 8

The inspection output is written to:

`outputs/source_structure_report.txt`

### 2. Baseline Dataset

`src/01_build_baseline_dataset.py`

Extracts and standardises the Strategic Grid planning data and creates the baseline analytical dataset.

The completed baseline contains:

- 25 financial years
- 2020-21 to 2044-45
- household demand
- non-household demand
- PCC
- population
- leakage
- supply variables
- demand variables
- calculated supply-demand balance

Baseline validation result:

**8 / 8 checks passed**

Primary output:

`data/processed/strategic_grid_baseline.csv`

### 3. Scenario Analysis

`src/02_run_demand_scenarios.py`

Applies the scenario assumptions to the baseline and recalculates long-term demand and supply-demand balance.

Completed scenario model:

- 6 scenarios
- 25 years per scenario
- 150 scenario-year records

Scenario validation result:

**4 / 4 checks passed**

Primary outputs:

- `outputs/scenario_results.csv`
- `outputs/scenario_summary.csv`
- `outputs/scenario_validation.csv`

## Scenario Framework

Scenario definitions are stored separately in:

`config/scenarios.csv`

This allows assumptions to be changed without modifying the underlying modelling code.

The six scenarios are:

### Published Baseline

Uses the extracted Severn Trent Strategic Grid planning baseline without additional sensitivity adjustments.

### PCC 110

Explores the effect of reducing household per-capita consumption to 110 litres per head per day.

### Higher Population Stress

Tests the effect of stronger population growth on long-term household demand.

### Non-Household Efficiency

Applies a reduction in non-household water consumption.

### Combined Efficiency

Combines:

- lower PCC
- lower non-household demand
- lower leakage

### Growth plus Efficiency

Tests whether demand-management improvements can offset stronger population growth.

Except for the Published Baseline, all scenario adjustments are independent illustrative sensitivities and should not be interpreted as Severn Trent forecasts.

## Key Findings

The primary comparison year is 2044-45.

### Published Baseline

Projected demand:

**1,273.5 Ml/d**

Supply-demand balance:

**-235.1 Ml/d**

### PCC 110

Projected demand reduction:

**82.3 Ml/d**

Equivalent reduction:

**6.5%**

Supply-demand balance:

**-152.8 Ml/d**

### Combined Efficiency

Projected demand:

**1,112.4 Ml/d**

Demand reduction versus baseline:

**161.1 Ml/d**

Equivalent reduction:

**12.7%**

Supply-demand balance:

**-73.9 Ml/d**

The approximate 2044-45 demand reductions within the Combined Efficiency sensitivity are:

- Household demand: **82.3 Ml/d**
- Leakage: **54.4 Ml/d**
- Non-household demand: **24.4 Ml/d**

### Higher Population Stress

A higher end-period population increases projected demand by approximately:

**21.7 Ml/d**

Supply-demand balance:

**-256.7 Ml/d**

## Interpretation

The scenario analysis indicates that demand-management measures could materially improve the long-term Strategic Grid position within this simplified model.

The Combined Efficiency sensitivity produces the largest improvement, reducing projected 2044-45 demand by approximately 161 Ml/d.

However, all six modelled scenarios remain in deficit by 2044-45.

This suggests that, within the boundaries of the prototype, demand reduction can make a substantial contribution to improving the supply-demand position but does not eliminate the long-term challenge by itself.

## Excel Assurance Workbook

The project includes an Excel assurance workbook:

`outputs/Water_Demand_Model_Assurance.xlsx`

The workbook contains:

- Executive Summary
- Baseline Forecast
- Scenario Comparison
- Assumptions
- Data Quality Checks
- Source Register

The workbook is designed to make the analytical assumptions, outputs and validation process easier to review.

## Power BI Dashboard

The completed Power BI model is stored at:

`powerbi/Severn_Trent_Demand_Scenario_Model.pbix`

The main report page is:

**Demand Scenario Explorer**

It includes:

- scenario selector
- forecast-year selector
- selected scenario demand
- published baseline demand
- absolute demand change
- percentage demand change
- supply-demand balance
- PCC
- baseline versus selected demand trend
- demand change by component
- baseline versus selected supply-demand balance trend

Dashboard screenshot:

`Report Screenshots/Severn_Trent_Demand_Scenario_Explorer.png`

## Data Quality and Validation

Validation is built into both the baseline extraction and scenario modelling stages.

### Baseline Validation

**8 / 8 checks passed**

### Scenario Validation

**4 / 4 checks passed**

Validation outputs are stored under:

`outputs/`

These include:

- `baseline_validation.csv`
- `scenario_validation.csv`
- `source_structure_report.txt`

The project also checks reconciliation between extracted source values and calculated analytical measures.

## Project Structure

```text
Severn_Trent_Water_Demand_Forecasting/
|
|-- config/
|   `-- scenarios.csv
|
|-- data/
|   |-- raw/
|   |   `-- Water-resources-market-information22-Strategic-Grid.xlsx
|   |
|   `-- processed/
|       |-- strategic_grid_baseline.csv
|       |-- wrmp_table2_long.csv
|       |-- wrmp_table3_long.csv
|       `-- wrmp_table4_long.csv
|
|-- docs/
|   `-- KPI_DEFINITIONS.md
|
|-- outputs/
|   |-- Water_Demand_Model_Assurance.xlsx
|   |-- baseline_validation.csv
|   |-- scenario_results.csv
|   |-- scenario_summary.csv
|   |-- scenario_validation.csv
|   `-- source_structure_report.txt
|
|-- powerbi/
|   `-- Severn_Trent_Demand_Scenario_Model.pbix
|
|-- Report Screenshots/
|   `-- Severn_Trent_Demand_Scenario_Explorer.png
|
|-- src/
|   |-- 00_inspect_wrmp_source.py
|   |-- 01_build_baseline_dataset.py
|   `-- 02_run_demand_scenarios.py
|
|-- .gitignore
|-- PROJECT_SCOPE.md
|-- README.md
`-- requirements.txt
```

## Running the Project

### 1. Create a Virtual Environment

From the project root:

```cmd
python -m venv .venv
```

Activate it on Windows:

```cmd
.venv\Scripts\activate.bat
```

### 2. Install Dependencies

```cmd
python -m pip install -r requirements.txt
```

### 3. Inspect the Source Workbook

```cmd
python src\00_inspect_wrmp_source.py
```

### 4. Build the Baseline Dataset

```cmd
python src\01_build_baseline_dataset.py
```

Expected completed-project result:

```text
Years: 2020-21 to 2044-45
Rows: 25
Validation checks: 8/8 PASS
```

### 5. Run Scenario Analysis

```cmd
python src\02_run_demand_scenarios.py
```

Expected completed-project result:

```text
Scenarios: 6
Years per scenario: 25
Scenario rows: 150
Validation checks: 4/4 PASS
```

## Tools and Technologies

- Python
- pandas
- Excel
- Power BI
- DAX
- Git
- GitHub

## Skills Demonstrated

This project demonstrates practical experience in:

- data extraction and transformation
- water-demand analysis
- scenario planning
- sensitivity analysis
- long-term forecasting
- household consumption analysis
- non-household consumption analysis
- PCC analysis
- leakage analysis
- supply-demand balance analysis
- assumption management
- automated validation
- analytical reconciliation
- Excel assurance reporting
- Power BI dashboard development
- DAX measure development
- technical documentation
- reproducible analytical workflows

## Model Boundary

This project is an independent public-data analytical prototype.

It does not reproduce Severn Trent's internal demand forecasting models, proprietary systems, customer-level datasets, operational telemetry or confidential planning assumptions.

The Published Baseline is derived from publicly available Severn Trent planning information.

The other five scenarios are independently created analytical sensitivities intended to demonstrate scenario modelling and should not be presented as Severn Trent forecasts.