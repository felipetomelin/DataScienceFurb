# Assignment 1 — Dataset Motivation and Contextualization

## Dataset: F1 2026 Season — Lap Times & Telemetry

**Source:** [Kaggle — stevefza/f1-2026-bahrain-testing-day-2](https://www.kaggle.com/datasets/stevefza/f1-2026-bahrain-testing-day-2)

---

## Domain and Context

Formula 1 (F1) is the highest class of single-seater auto racing sanctioned by the Fédération Internationale de l'Automobile (FIA). Each season comprises approximately 24 race weekends structured into practice sessions (FP1, FP2, FP3), qualifying (Q), and the race itself. Pre-season testing in Bahrain precedes the official calendar to allow teams to develop and validate car setups.

The dataset covers the **2026 F1 season**, including pre-season testing at Bahrain International Circuit and the Australian Grand Prix weekend at Melbourne's Albert Park Circuit. It consists of multiple CSV files with **lap-level records and high-frequency telemetry data** for all participating drivers across sessions:

- **8 CSV files**, ranging from ~128 KB to ~116 MB each
- **Over 8,200 individual lap records** in total across all files
- **22 drivers** from the current grid (e.g., VER, NOR, LEC, HAM, SAI, RUS, ALO, among others)
- **4 session types**: FP1, FP2, FP3, and Qualifying
- **3 tyre compounds**: SOFT, MEDIUM, HARD

Each row represents one driven lap. The richer files include an embedded JSON telemetry field sampled at 2 Hz (every 0.5 seconds), capturing: **speed, throttle input, brake input, gear, engine RPM, DRS activation state, and cartesian coordinates (x, y, z)** of the car on track.

---

## Relevance

The relevance of this dataset is simultaneously **technical, scientific, and economic**:

- **Technical:** F1 is one of the most data-intensive sports in the world. Teams collect terabytes of telemetry per race weekend. This dataset offers a window into that world, enabling analysis of driver behavior, car performance, and circuit characteristics from a data-driven perspective.

- **Scientific:** Telemetry data enables the application of time-series analysis, signal processing, and machine learning at high fidelity. The granularity of the data (sub-second intervals with multi-dimensional features) makes it suitable for rigorous quantitative study.

- **Economic:** Performance analytics in F1 is directly tied to competitive outcomes and significant financial stakes. Teams spend hundreds of millions of dollars annually, and marginal improvements in lap time — often measured in thousandths of a second — are the difference between winning and losing championships.

---

## Potential Analytical Use Cases

The dataset is well-suited for a variety of analytical approaches:

- **Predictive analysis:** Predicting lap times based on tyre compound, stint number, and telemetry features; forecasting qualifying performance from practice session data.
- **Classification:** Identifying driving style clusters among drivers based on throttle/brake patterns; classifying lap types (hot lap vs. in/out lap vs. slow lap).
- **Descriptive analysis:** Comparing driver and team performance across sessions; visualizing speed traces per sector; mapping car trajectories using (x, y) coordinates; analyzing tyre degradation patterns over stints.
- **Anomaly detection:** Identifying unusual laps (e.g., safety car periods, mechanical issues) based on lap time outliers or telemetry deviations.

---

## Dataset Characteristics

| Property       | Details |
|----------------|---------|
| **Type**       | Mixed — structured (tabular CSVs) + semi-structured (embedded JSON telemetry) |
| **Size**       | ~8 files, total ~203 MB; 8,200+ lap records |
| **Structure**  | Each row = one lap; columns: `season`, `event_name`, `circuit`, `session_type`, `driver`, `driver_number`, `lap_number`, `lap_time`, `lap_duration`, `compound`, `tyre_age`, `stint_number`, `telemetry` (JSON array) |
| **Coverage**   | 2026 F1 pre-season testing (Bahrain) + Australian GP weekend |
| **Granularity**| Lap-level metadata + 2 Hz intra-lap telemetry (speed, throttle, brake, gear, RPM, DRS, x/y/z) |
| **Format**     | CSV with embedded JSON (semi-structured within structured container) |
| **Quality**    | Real data collected via the FastF1 Python library from official F1 live timing APIs |
