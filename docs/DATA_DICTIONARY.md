# 📖 Data Dictionary — F1 2026 Season: Lap Times & Telemetry

**Dataset:** F1 2026 Season — Lap Times & Telemetry  
**Source:** [Kaggle — stevefza/f1-2026-bahrain-testing-day-2](https://www.kaggle.com/datasets/stevefza/f1-2026-bahrain-testing-day-2)  
**Prepared by:** Felipe Tomelin  
**Course:** Data Science — FURB  
**Last updated:** April 2026  

---

## Overview

This dictionary documents all fields present in the dataset **after Data Preparation**, including original fields from the raw CSVs and derived (engineered) features added during the preparation pipeline.

The dataset covers F1 2026 pre-season testing and early-season race weekends, capturing detailed lap-by-lap timing and telemetry data for all drivers.

---

## Field Reference

### 🏁 Core Identification Fields

| Field | Type | Unit | Description | Example | Notes |
|---|---|---|---|---|---|
| `driver` | string | — | Driver full name or abbreviation | `VER`, `HAM` | Standardized to uppercase 3-letter code |
| `driver_number` | integer | — | Official FIA car number | `1`, `44` | Unique per driver per season |
| `team` | string | — | Constructor / team name | `Red Bull Racing` | Standardized to official name |
| `session` | string | — | Session type | `FP1`, `Qualifying`, `Race` | See `session_tag` for derived version |
| `session_tag` | string | — | **[Derived]** Session category inferred from source file | `Pre-Season Testing`, `Practice`, `Qualifying`, `Race`, `Unknown` | Added during data preparation |
| `event` | string | — | Grand Prix or event name | `Bahrain Grand Prix` | — |
| `year` | integer | — | Championship year | `2026` | — |
| `lap_number` | integer | — | Lap number within the session | `1`, `12`, `45` | Converted to integer; `NaN` rows dropped |

---

### ⏱️ Lap Time Fields

| Field | Type | Unit | Description | Example | Notes |
|---|---|---|---|---|---|
| `laptime` | float | seconds | Total lap time in seconds | `91.452` | Parsed from `M:SS.mmm` format if string |
| `laptime_formatted` | string | MM:SS.mmm | **[Derived]** Human-readable lap time | `1:31.452` | Added during feature engineering |
| `sector1_time` | float | seconds | Sector 1 elapsed time | `28.341` | Parsed from string if needed |
| `sector2_time` | float | seconds | Sector 2 elapsed time | `33.109` | — |
| `sector3_time` | float | seconds | Sector 3 elapsed time | `30.002` | — |
| `personal_best` | boolean | — | Whether this lap is the driver's personal best in session | `True` / `False` | — |
| `is_accurate` | boolean | — | FIA accuracy flag (lap counted as valid) | `True` / `False` | Laps marked `False` should be excluded from timing analysis |

---

### 🏎️ Tyre & Compound Fields

| Field | Type | Unit | Description | Example | Notes |
|---|---|---|---|---|---|
| `compound` | string | — | Tyre compound used | `SOFT`, `MEDIUM`, `HARD`, `INTERMEDIATE`, `WET` | Standardized to uppercase |
| `tyre_life` | integer | laps | Number of laps completed on this tyre set | `3`, `18`, `42` | — |
| `fresh_tyre` | boolean | — | Whether the tyre was new at the start of the stint | `True` / `False` | — |
| `tyre_life_category` | string | — | **[Derived]** Categorical bin for tyre life | `New (0-5)`, `Used (6-15)`, `High-Life (16-30)`, `Old (30+)` | Added during feature engineering using IQR-based binning |

---

### 🔧 Pit Stop Fields

| Field | Type | Unit | Description | Example | Notes |
|---|---|---|---|---|---|
| `pit_in_time` | float | seconds | Time of pit entry within session | `3621.5` | Relative to session start |
| `pit_out_time` | float | seconds | Time of pit exit within session | `3681.0` | — |
| `pit_duration` | float | seconds | Total time spent in pit lane | `59.5` | Derived from `pit_out_time - pit_in_time` when not directly provided |

---

### 📡 Telemetry / Speed Fields

| Field | Type | Unit | Description | Example | Notes |
|---|---|---|---|---|---|
| `speed_i1` | float | km/h | Speed trap at Intermediate 1 | `287.4` | — |
| `speed_i2` | float | km/h | Speed trap at Intermediate 2 | `263.1` | — |
| `speed_fl` | float | km/h | Speed trap at Finish Line | `305.8` | — |
| `speed_st` | float | km/h | Speed trap at Speed Trap (longest straight) | `321.0` | — |
| `speed_i1_delta_pct` | float | % | **[Derived]** % deviation of `speed_i1` from session median | `+2.15` | Added during feature engineering |
| `speed_i2_delta_pct` | float | % | **[Derived]** % deviation of `speed_i2` from session median | `-1.03` | — |
| `speed_fl_delta_pct` | float | % | **[Derived]** % deviation of `speed_fl` from session median | `+0.74` | — |
| `speed_st_delta_pct` | float | % | **[Derived]** % deviation of `speed_st` from session median | `+3.21` | — |

---

### 📊 Position & Stint Fields

| Field | Type | Unit | Description | Example | Notes |
|---|---|---|---|---|---|
| `position` | integer | — | Track position at the end of the lap | `1`, `5`, `20` | May be `NaN` in practice sessions |
| `stint` | integer | — | Stint number (increments after each pit stop) | `1`, `2`, `3` | — |
| `track_status` | string | — | Track condition during lap | `1` (Clear), `2` (Yellow), `4` (SC), `5` (Red) | FIA status codes |
| `deleted` | boolean | — | Whether the lap time was deleted by stewards | `True` / `False` | Laps with `deleted=True` should be excluded from performance analysis |
| `deleted_reason` | string | — | Reason for lap deletion | `Track Limits`, `Speeding in Pit Lane` | `Unknown` when not available |

---

## Derived Features Summary

The following fields were **created during Data Preparation** and do not exist in the original raw CSVs:

| Field | Origin | Description |
|---|---|---|
| `laptime_formatted` | `laptime` | Human-readable `MM:SS.mmm` lap time string |
| `tyre_life_category` | `tyre_life` | Ordinal category for tyre wear stage |
| `speed_i1_delta_pct` | `speed_i1` | % deviation from session median speed at I1 |
| `speed_i2_delta_pct` | `speed_i2` | % deviation from session median speed at I2 |
| `speed_fl_delta_pct` | `speed_fl` | % deviation from session median speed at FL |
| `speed_st_delta_pct` | `speed_st` | % deviation from session median speed at ST |
| `session_tag` | `_source_file` | Inferred session category from CSV filename |

---

## Data Quality Notes

| Issue | Treatment Applied |
|---|---|
| Column names with spaces/special chars | Normalized to `snake_case` (lowercase, underscores) |
| Missing values < 20% — numeric | Median imputation |
| Missing values < 20% — categorical | Mode imputation or `"Unknown"` |
| Missing values ≥ 80% | Column dropped |
| Lap time stored as `"M:SS.mmm"` string | Parsed to float seconds |
| Duplicate rows | Removed with `drop_duplicates()` |
| Outliers (3×IQR method) | Winsorized (capped at fence values — rows not removed) |
| Boolean columns stored as strings | Mapped to Python `bool` type |

---

## Source Files

| File | Rows | Size | Session |
|---|---|---|---|
| `Bahrain Testing Day 2.csv` | 972 | 128 KB | Pre-Season Testing |
| `F1 2026 Bahrain Testing Day 2.csv` | 972 | 148 KB | Pre-Season Testing (extended) |
| `Australia - FP1 FP2 FP3 Quali.csv` | 1,759 | 39 MB | Australian GP Weekend |
| `All Laps update 20260306.csv` | 1,029 | 24 MB | Multiple sessions |
| `Laptimes Update 20260221.csv` | 578 | 12 MB | Multiple sessions |
| `All Laps - 8 March Update.csv` | 9 | 448 KB | Multiple sessions |
| `All Laps 15032026.csv` | 323 | 12 MB | Multiple sessions |
| `All Laps Update 13032026.csv` | 3,563 | 116 MB | Multiple sessions |

> **Note:** Raw CSV files are **not committed** to this repository due to size constraints (~203 MB total). Please download from [Kaggle](https://www.kaggle.com/datasets/stevefza/f1-2026-bahrain-testing-day-2).

---

## Track Status Codes

| Code | Meaning |
|---|---|
| `1` | Clear — Normal racing conditions |
| `2` | Yellow — Yellow flag sector |
| `4` | Safety Car deployed |
| `5` | Red Flag — Session stopped |
| `6` | Virtual Safety Car (VSC) |
| `7` | VSC Ending |

---

## Tyre Compound Reference

| Compound | Colour | Characteristic |
|---|---|---|
| `SOFT` | Red | Fastest, lowest durability |
| `MEDIUM` | Yellow | Balanced performance |
| `HARD` | White | Slowest, highest durability |
| `INTERMEDIATE` | Green | Wet track, no standing water |
| `WET` | Blue | Heavy rain / standing water |
