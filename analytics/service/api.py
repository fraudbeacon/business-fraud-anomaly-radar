import sys
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import pandas as pd
import io

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from detection_engine import AnomalyDetectionPipeline

app = FastAPI(
    title="Business Fraud & Anomaly Radar - Detection API",
    description="Microservice providing hybrid rule-based and Isolation Forest anomaly scoring for transactions.",
    version="1.0.0"
)

# Initialize pipeline
pipeline = AnomalyDetectionPipeline()

# Load baseline if available
baseline_path = os.path.join(os.path.dirname(__file__), "..", "data", "clean_baseline.csv")
if os.path.exists(baseline_path):
    base_df = pd.read_csv(baseline_path)
    pipeline.fit(base_df)
    print(f"Loaded and fitted baseline from {baseline_path}")

class TransactionItem(BaseModel):
    transaction_id: str
    timestamp: str
    employee_id: str
    customer_id: str
    branch_id: str
    amount: float
    discount_percent: float = 0.0
    refund_amount: float = 0.0
    payment_method: str = "Cash"
    category: Optional[str] = "General"

class AnomalyResponse(BaseModel):
    transaction_id: str
    risk_score: int
    severity: str
    detector_type: str
    rule_score: int
    ml_score: int
    reasons: List[str]
    reason_summary: str

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Fraud & Anomaly Radar Detection Service",
        "pipeline_fitted": pipeline.is_trained
    }

@app.post("/api/v1/detect/batch", response_model=List[AnomalyResponse])
def detect_batch(transactions: List[TransactionItem]):
    """
    Accepts a list of transaction objects and returns anomaly scores with explainability reasons.
    """
    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions provided")
        
    records = [t.dict() for t in transactions]
    df = pd.DataFrame(records)
    
    try:
        scored_df = pipeline.detect(df)
        results = []
        for _, row in scored_df.iterrows():
            results.append(AnomalyResponse(
                transaction_id=str(row["transaction_id"]),
                risk_score=int(row["risk_score"]),
                severity=str(row["severity"]),
                detector_type=str(row["detector_type"]),
                rule_score=int(row["rule_score"]),
                ml_score=int(row["ml_score"]),
                reasons=row["reasons"],
                reason_summary=str(row["reason_summary"])
            ))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")

@app.post("/api/v1/detect/upload-csv")
async def detect_csv_upload(file: UploadFile = File(...)):
    """
    Accepts a CSV file upload, runs detection, and returns flagged high-risk anomalies.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
        scored_df = pipeline.detect(df)
        
        # Filter for flagged alerts (MEDIUM, HIGH, CRITICAL)
        alerts_df = scored_df[scored_df["risk_score"] >= 30]
        
        return {
            "total_transactions": len(scored_df),
            "alerts_generated": len(alerts_df),
            "severity_summary": scored_df["severity"].value_counts().to_dict(),
            "top_alerts": alerts_df.head(20).to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
