import pandas as pd
from typing import List, Dict, Any

class HybridScorer:
    """
    Combines rule-based sub-scores (0 - 60) and ML anomaly sub-scores (0 - 40)
    into a calibrated 0 - 100 Risk Score with severity classifications and reasons.
    """
    def __init__(
        self,
        low_threshold: int = 30,
        high_threshold: int = 60,
        critical_threshold: int = 80
    ):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.critical_threshold = critical_threshold

    def get_severity(self, score: int) -> str:
        if score >= self.critical_threshold:
            return "CRITICAL"
        elif score >= self.high_threshold:
            return "HIGH"
        elif score >= self.low_threshold:
            return "MEDIUM"
        else:
            return "LOW"

    def combine(
        self,
        df: pd.DataFrame,
        rule_scores: List[int],
        rule_reasons: List[List[str]],
        ml_scores: List[int],
        ml_reasons: List[List[str]]
    ) -> pd.DataFrame:
        """
        Merges scores and builds final alert dataset.
        """
        results = []
        for i in range(len(df)):
            r_score = rule_scores[i]
            m_score = ml_scores[i]
            total_score = min(100, r_score + m_score)
            
            # Combine reasons
            reasons = rule_reasons[i] + ml_reasons[i]
            if not reasons and total_score >= self.low_threshold:
                reasons.append("Elevated risk composite score across multiple signals")
                
            # Determine detector type
            if r_score > 0 and m_score > 0:
                detector_type = "HYBRID"
            elif r_score > 0:
                detector_type = "RULE"
            elif m_score > 0:
                detector_type = "ML"
            else:
                detector_type = "BASELINE"
                
            results.append({
                "transaction_id": df.iloc[i]["transaction_id"],
                "risk_score": total_score,
                "severity": self.get_severity(total_score),
                "detector_type": detector_type,
                "rule_score": r_score,
                "ml_score": m_score,
                "reasons": reasons,
                "reason_summary": " | ".join(reasons) if reasons else "Normal transaction behavior"
            })
            
        res_df = pd.DataFrame(results)
        # Merge back with original columns
        return pd.concat([df.reset_index(drop=True), res_df.drop(columns=["transaction_id"])], axis=1)
