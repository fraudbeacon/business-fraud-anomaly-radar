import pandas as pd
import numpy as np
from typing import Dict, Tuple

class FeatureEngineer:
    """
    Extracts behavioral, temporal, and historical deviation features from raw transactions.
    """
    def __init__(self, off_hours_start: int = 21, off_hours_end: int = 7):
        self.off_hours_start = off_hours_start
        self.off_hours_end = off_hours_end
        self.employee_profiles: Dict[str, Dict[str, float]] = {}

    def fit_profiles(self, df: pd.DataFrame) -> None:
        """
        Computes baseline behavioral metrics per employee from training/historical data.
        """
        clean_df = df[df["is_anomaly"] == 0] if "is_anomaly" in df.columns else df
        
        for emp_id, group in clean_df.groupby("employee_id"):
            median_amt = float(group["amount"].median())
            std_amt = float(group["amount"].std()) if len(group) > 1 else 1.0
            avg_discount = float(group["discount_percent"].mean())
            self.employee_profiles[emp_id] = {
                "median_amount": max(1.0, median_amt),
                "std_amount": max(1.0, std_amt if not np.isnan(std_amt) else 1.0),
                "avg_discount": avg_discount if not np.isnan(avg_discount) else 0.0
            }

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriches transactions with temporal and ratio-based deviation features.
        """
        res = df.copy()
        res["dt"] = pd.to_datetime(res["timestamp"])
        res["hour_of_day"] = res["dt"].dt.hour
        res["day_of_week"] = res["dt"].dt.dayofweek
        
        # Off hours indicator: e.g. 21:00 to 07:00
        res["is_off_hours"] = res["hour_of_day"].apply(
            lambda h: 1 if (h >= self.off_hours_start or h < self.off_hours_end) else 0
        )
        
        # Employee baselines
        overall_median = float(res["amount"].median())
        overall_discount = float(res["discount_percent"].mean())
        
        medians = []
        discount_diffs = []
        ratios = []
        
        for _, row in res.iterrows():
            emp = row["employee_id"]
            amt = float(row["amount"])
            disc = float(row["discount_percent"])
            
            profile = self.employee_profiles.get(emp, {
                "median_amount": overall_median,
                "avg_discount": overall_discount
            })
            
            emp_median = profile["median_amount"]
            ratio = amt / emp_median
            disc_diff = max(0.0, disc - profile["avg_discount"])
            
            medians.append(emp_median)
            ratios.append(ratio)
            discount_diffs.append(disc_diff)
            
        res["employee_median_amount"] = medians
        res["amount_to_median_ratio"] = ratios
        res["discount_deviation"] = discount_diffs
        res["refund_ratio"] = res["refund_amount"] / (res["amount"] + 1e-5)
        
        return res

    def get_ml_features(self, df_transformed: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
        """
        Returns numeric feature matrix ready for scikit-learn models.
        """
        feature_cols = [
            "amount",
            "discount_percent",
            "refund_amount",
            "hour_of_day",
            "is_off_hours",
            "amount_to_median_ratio",
            "discount_deviation",
            "refund_ratio"
        ]
        return df_transformed[feature_cols].fillna(0.0), feature_cols
