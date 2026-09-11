import pandas as pd
from typing import List, Dict, Tuple

class RuleEngine:
    """
    Evaluates business policy checks and assigns rule-based risk sub-scores (0 - 60).
    Produces human-readable explanation strings for each triggered violation.
    """
    def __init__(
        self,
        duplicate_window_seconds: int = 600,
        high_discount_threshold: float = 35.0,
        high_refund_threshold: float = 150.0,
        amount_spike_multiple: float = 4.0,
        off_hours_start: int = 22,
        off_hours_end: int = 6,
        max_rule_score: int = 60
    ):
        self.duplicate_window_seconds = duplicate_window_seconds
        self.high_discount_threshold = high_discount_threshold
        self.high_refund_threshold = high_refund_threshold
        self.amount_spike_multiple = amount_spike_multiple
        self.off_hours_start = off_hours_start
        self.off_hours_end = off_hours_end
        self.max_rule_score = max_rule_score

    def evaluate(self, df: pd.DataFrame) -> Tuple[List[int], List[List[str]]]:
        """
        Evaluates rules against an enriched transaction DataFrame.
        Returns:
            scores: list of rule scores clamped to max_rule_score (0-60)
            reasons: list of human-readable explanation string arrays per record
        """
        records = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(records["timestamp"]):
            records["dt"] = pd.to_datetime(records["timestamp"])
        else:
            records["dt"] = records["timestamp"]

        n = len(records)
        scores = [0] * n
        all_reasons = [[] for _ in range(n)]

        # Sort for fast duplicate detection
        sorted_indices = records.sort_values("dt").index.tolist()

        # 1. Rule: Duplicate Transaction
        # Check adjacent records within window with identical employee, customer, and amount
        for i in range(len(sorted_indices)):
            curr_idx = sorted_indices[i]
            curr_row = records.loc[curr_idx]
            curr_dt = curr_row["dt"]

            # Look back
            for j in range(i - 1, -1, -1):
                prev_idx = sorted_indices[j]
                prev_row = records.loc[prev_idx]
                time_diff = (curr_dt - prev_row["dt"]).total_seconds()

                if time_diff > self.duplicate_window_seconds:
                    break

                if (
                    curr_row["employee_id"] == prev_row["employee_id"]
                    and curr_row["customer_id"] == prev_row["customer_id"]
                    and abs(curr_row["amount"] - prev_row["amount"]) < 0.01
                ):
                    scores[curr_idx] += 35
                    all_reasons[curr_idx].append(
                        f"Duplicate transaction detected: identical amount (${curr_row['amount']:.2f}) "
                        f"processed within {int(time_diff)}s of prior transaction ({prev_row['transaction_id']})"
                    )
                    break

        # 2, 3, 4, 5: Single-record checks
        for idx in range(n):
            row = records.iloc[idx]
            hour = row["dt"].hour
            amt = float(row["amount"])
            disc = float(row.get("discount_percent", 0.0))
            refund = float(row.get("refund_amount", 0.0))
            ratio = float(row.get("amount_to_median_ratio", 1.0))

            # Rule: Off-Hours Activity
            if hour >= self.off_hours_start or hour < self.off_hours_end:
                scores[idx] += 25
                all_reasons[idx].append(
                    f"Transaction processed during irregular off-hours ({hour:02d}:{row['dt'].minute:02d})"
                )

            # Rule: Excessive Discount
            if disc >= self.high_discount_threshold:
                scores[idx] += 25
                all_reasons[idx].append(
                    f"Excessive discount applied ({disc:.1f}%), surpassing the {self.high_discount_threshold}% threshold"
                )

            # Rule: Unusual Refund
            if refund >= self.high_refund_threshold or (refund > 0 and refund >= amt * 1.5):
                scores[idx] += 30
                all_reasons[idx].append(
                    f"Unusual refund value recorded (${refund:.2f}) exceeding standard return limits"
                )

            # Rule: Sudden Amount Spike
            if ratio >= self.amount_spike_multiple:
                scores[idx] += 25
                all_reasons[idx].append(
                    f"Transaction amount (${amt:.2f}) is {ratio:.1f}x higher than employee's historical median"
                )

            # Clamp rule score
            scores[idx] = min(self.max_rule_score, scores[idx])

        return scores, all_reasons
