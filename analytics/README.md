# Analytics & Anomaly Detection Engine

This directory contains the machine learning and rule-based anomaly detection subsystem for the **Business Fraud & Anomaly Radar**.

## Architecture Overview

The system uses a **Hybrid Scoring Strategy** combining policy rules and statistical machine learning:

$$\text{Final Risk Score} = \min(100, \text{Rule Score}_{[0-60]} + \text{ML Score}_{[0-40]})$$

### Severity Tiers:
* **`LOW`** (0 – 29): Standard transaction behavior.
* **`MEDIUM`** (30 – 59): Minor policy warning or statistical irregularity.
* **`HIGH`** (60 – 79): Prioritized anomaly with multiple compounding flags.
* **`CRITICAL`** (80 – 100): High-confidence suspicious pattern requiring immediate review.

---

## Directory Structure

```
analytics/
├── detection_engine/          # Core Python detection package
│   ├── __init__.py            # AnomalyDetectionPipeline coordinator
│   ├── feature_engineering.py # Temporal features & employee baselines
│   ├── rule_engine.py         # Business rule checks (0–60 pts)
│   ├── ml_detector.py         # Isolation Forest & explainability generator (0–40 pts)
│   └── hybrid_scorer.py       # Score aggregation and severity bucketing
├── notebooks/
│   └── fraud_anomaly_radar_exploration.ipynb # Interactive EDA & evaluation notebook
├── service/
│   └── api.py                 # FastAPI microservice for Spring Boot integration
├── requirements.txt           # Python dependencies
└── README.md                  # This documentation
```

---

## Quickstart

### 1. Install Dependencies
```bash
cd analytics
pip install -r requirements.txt
```

### 2. Run the Jupyter Notebook in PyCharm
Open `notebooks/fraud_anomaly_radar_exploration.ipynb` in PyCharm and execute all cells to inspect charts, feature distributions, and detection benchmark metrics.

### 3. Run the FastAPI Detection Microservice
```bash
uvicorn service.api:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger documentation will be available at `http://localhost:8000/docs`.

#### Endpoints:
* `GET /health` — Service health and pipeline training status.
* `POST /api/v1/detect/batch` — Scored batch of transaction JSON items.
* `POST /api/v1/detect/upload-csv` — Direct CSV ingestion and alert generation.
