import pandas as pd
from typing import Tuple, Dict, Any, List
from .feature_engineering import FeatureEngineer
from .rule_engine import RuleEngine
from .ml_detector import MLAnomalyDetector
from .hybrid_scorer import HybridScorer

class AnomalyDetectionPipeline:
    """
    Unified end-to-end pipeline for SME Business Fraud & Anomaly Detection.
    Coordinates Feature Engineering, Rule Checks, Isolation Forest scoring,
    and calibrated Risk Score aggregation with explainability reasons.
    """
    def __init__(
        self,
        contamination: float = 0.035,
        duplicate_window_seconds: int = 600,
        high_discount_threshold: float = 35.0,
        high_refund_threshold: float = 150.0,
        amount_spike_multiple: float = 4.0,
        off_hours_start: int = 22,
        off_hours_end: int = 6
    ):
        self.feature_engineer = FeatureEngineer(
            off_hours_start=off_hours_start,
            off_hours_end=off_hours_end
        )
        self.rule_engine = RuleEngine(
            duplicate_window_seconds=duplicate_window_seconds,
            high_discount_threshold=high_discount_threshold,
            high_refund_threshold=high_refund_threshold,
            amount_spike_multiple=amount_spike_multiple,
            off_hours_start=off_hours_start,
            off_hours_end=off_hours_end
        )
        self.ml_detector = MLAnomalyDetector(contamination=contamination)
        self.hybrid_scorer = HybridScorer()
        self.is_trained = False

    def fit(self, baseline_df: pd.DataFrame) -> "AnomalyDetectionPipeline":
        """
        Calibrates employee baselines and fits the Isolation Forest model on historical/baseline data.
        """
        self.feature_engineer.fit_profiles(baseline_df)
        enriched = self.feature_engineer.transform(baseline_df)
        X_ml, _ = self.feature_engineer.get_ml_features(enriched)
        self.ml_detector.fit(X_ml)
        self.is_trained = True
        return self

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Runs the full detection suite on input transactions.
        Returns enriched DataFrame with risk scores, severities, detector types, and reasons.
        """
        if not self.is_trained:
            # Auto-fit on provided dataset if not pre-trained
            self.fit(df)

        enriched = self.feature_engineer.transform(df)
        
        # 1. Rule Engine Evaluation (0 - 60 pts)
        rule_scores, rule_reasons = self.rule_engine.evaluate(enriched)
        
        # 2. ML Isolation Forest Evaluation (0 - 40 pts)
        X_ml, _ = self.feature_engineer.get_ml_features(enriched)
        ml_scores, ml_reasons = self.ml_detector.score(X_ml)
        
        # 3. Hybrid Aggregation & Severity Mapping (0 - 100 pts)
        results_df = self.hybrid_scorer.combine(
            df=enriched,
            rule_scores=rule_scores,
            rule_reasons=rule_reasons,
            ml_scores=ml_scores,
            ml_reasons=ml_reasons
        )
        
        return results_df

__all__ = [
    "FeatureEngineer",
    "RuleEngine",
    "MLAnomalyDetector",
    "HybridScorer",
    "AnomalyDetectionPipeline"
]
