import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler

class MLAnomalyDetector:
    """
    Isolation Forest-based multi-dimensional statistical anomaly detector.
    Outputs calibrated anomaly scores (0 - 40 pts) and statistical explanations.
    """
    def __init__(
        self,
        contamination: float = 0.035,
        n_estimators: int = 150,
        random_state: int = 42,
        max_ml_score: int = 40
    ):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.max_ml_score = max_ml_score
        
        self.scaler = RobustScaler()
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.feature_names: List[str] = []
        self.feature_means: Dict[str, float] = {}
        self.feature_stds: Dict[str, float] = {}
        self.is_fitted: bool = False

    def fit(self, X: pd.DataFrame) -> None:
        """
        Fits the scaler, Isolation Forest, and baseline distribution stats.
        """
        self.feature_names = list(X.columns)
        
        # Track feature baselines for explainability
        for col in self.feature_names:
            self.feature_means[col] = float(X[col].mean())
            std_val = float(X[col].std())
            self.feature_stds[col] = max(1e-4, std_val if not np.isnan(std_val) else 1.0)
            
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_fitted = True

    def score(self, X: pd.DataFrame) -> Tuple[List[int], List[List[str]]]:
        """
        Scores input records and produces human-readable reasons for top deviating features.
        Returns:
            ml_scores: List of scores bounded between 0 and max_ml_score (40)
            ml_reasons: List of explanation strings
        """
        if not self.is_fitted:
            raise RuntimeError("MLAnomalyDetector must be fitted before scoring.")

        X_scaled = self.scaler.transform(X)
        raw_scores = self.model.decision_function(X_scaled)  # Lower/negative is anomalous
        
        # Calibration:
        # decision_function typically lies in [-0.3, 0.2]
        # We define an anomaly cutoff around 0.0
        ml_scores = []
        ml_reasons = []
        
        for i, raw_score in enumerate(raw_scores):
            if raw_score >= 0.08:
                # Highly normal
                score = 0
            elif raw_score >= 0.0:
                # Mild border case
                score = int((0.08 - raw_score) / 0.08 * 12)
            else:
                # True anomaly region (< 0.0)
                # Map -0.0 to -0.25 -> 12 to 40
                depth = abs(raw_score)
                score = min(self.max_ml_score, int(12 + (depth / 0.20) * 28))
                
            ml_scores.append(score)
            
            # Explainability: Check which features have the largest Z-score deviation
            row_reasons = []
            if score >= 15:
                row_vals = X.iloc[i]
                deviations = []
                for col in self.feature_names:
                    z = (row_vals[col] - self.feature_means[col]) / self.feature_stds[col]
                    if abs(z) >= 2.2:
                        deviations.append((col, z, abs(z)))
                
                # Sort by highest deviation
                deviations.sort(key=lambda item: item[2], reverse=True)
                top_devs = deviations[:2]
                
                if top_devs:
                    dev_strs = [
                        f"{col.replace('_', ' ')} ({'+' if z > 0 else ''}{z:.1f}σ)"
                        for col, z, _ in top_devs
                    ]
                    row_reasons.append(
                        f"Statistical outlier detected by Isolation Forest driven by: {', '.join(dev_strs)}"
                    )
                else:
                    row_reasons.append(
                        "Multi-variate statistical anomaly detected across combined features"
                    )
                    
            ml_reasons.append(row_reasons)
            
        return ml_scores, ml_reasons
