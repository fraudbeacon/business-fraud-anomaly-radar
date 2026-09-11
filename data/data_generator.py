import random
import datetime
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np

def generate_synthetic_transactions(
    num_records: int = 10000,
    anomaly_rate: float = 0.035,
    start_date: datetime.datetime = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates a realistic retail/SME transaction dataset with injected fraud and anomaly scenarios.
    
    Ground-truth labels:
      - is_anomaly: 0 (normal) or 1 (anomaly)
      - anomaly_type: 'NONE', 'DUPLICATE', 'EXCESSIVE_DISCOUNT', 'REFUND_FRAUD', 'OFF_HOURS', 'AMOUNT_SPIKE'
    """
    np.random.seed(seed)
    random.seed(seed)
    
    if start_date is None:
        start_date = datetime.datetime(2026, 7, 1, 8, 0, 0)
        
    num_anomalies = int(num_records * anomaly_rate)
    num_normal = num_records - num_anomalies
    
    employees = [f"EMP-{i:03d}" for i in range(1, 9)]
    branches = ["BRANCH-CENTRAL", "BRANCH-EAST", "BRANCH-WEST"]
    categories = ["Groceries", "Electronics", "Apparel", "Hardware", "Services"]
    payment_methods = ["Cash", "Mobile Money", "Credit Card", "Debit Card"]
    
    # Employee base profiles (typical average transaction amount)
    emp_profiles = {
        emp: {
            "branch": random.choice(branches),
            "median_amt": random.uniform(35.0, 75.0),
            "avg_discount": random.uniform(2.0, 8.0)
        }
        for emp in employees
    }
    
    records: List[Dict] = []
    
    # 1. Generate Normal Transactions
    curr_time = start_date
    for i in range(num_normal):
        # Step forward in time (typical inter-transaction arrival 1 to 15 minutes)
        inter_arrival_secs = int(np.random.exponential(scale=240))
        curr_time += datetime.timedelta(seconds=max(20, inter_arrival_secs))
        
        # If outside 08:00 - 20:30, advance to next business day morning
        if curr_time.hour >= 21 or curr_time.hour < 8:
            days_to_add = 1 if curr_time.hour >= 21 else 0
            curr_time = curr_time.replace(hour=8, minute=random.randint(5, 30), second=random.randint(0, 59))
            if days_to_add:
                curr_time += datetime.timedelta(days=1)
                
        emp = random.choice(employees)
        branch = emp_profiles[emp]["branch"]
        cust = f"CUST-{random.randint(1000, 9999)}"
        category = random.choice(categories)
        
        # Log-normal distribution for amounts
        base_amt = emp_profiles[emp]["median_amt"]
        amount = float(np.random.lognormal(mean=np.log(base_amt), sigma=0.45))
        amount = round(max(5.0, amount), 2)
        
        # Normal discount: 0% most of the time, occasionally up to 15%
        if random.random() < 0.25:
            discount_pct = round(random.uniform(3.0, 15.0), 1)
        else:
            discount_pct = 0.0
            
        # Normal refunds: rare (< 2.5%), amount is less than typical basket
        is_refund = random.random() < 0.025
        if is_refund:
            refund_amount = round(random.uniform(5.0, min(amount, 80.0)), 2)
        else:
            refund_amount = 0.0
            
        pay_method = random.choice(payment_methods)
        
        records.append({
            "transaction_id": f"TX-{100000 + i}",
            "timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
            "employee_id": emp,
            "customer_id": cust,
            "branch_id": branch,
            "category": category,
            "amount": amount,
            "discount_percent": discount_pct,
            "refund_amount": refund_amount,
            "payment_method": pay_method,
            "is_anomaly": 0,
            "anomaly_type": "NONE"
        })
        
    # 2. Generate Injected Anomalies
    # Evenly split across 5 archetypes
    types = [
        "DUPLICATE",
        "EXCESSIVE_DISCOUNT",
        "REFUND_FRAUD",
        "OFF_HOURS",
        "AMOUNT_SPIKE"
    ]
    
    anomalies_per_type = num_anomalies // len(types)
    tx_counter = 100000 + num_normal
    
    for anom_type in types:
        for _ in range(anomalies_per_type):
            tx_counter += 1
            # Pick a random point in time
            random_offset_days = random.randint(1, 45)
            anom_time = start_date + datetime.timedelta(days=random_offset_days)
            emp = random.choice(employees)
            branch = emp_profiles[emp]["branch"]
            cust = f"CUST-{random.randint(1000, 9999)}"
            category = random.choice(categories)
            pay_method = random.choice(payment_methods)
            
            amt = round(float(np.random.lognormal(mean=np.log(emp_profiles[emp]["median_amt"]), sigma=0.45)), 2)
            disc = 0.0
            ref = 0.0
            
            if anom_type == "DUPLICATE":
                # Regular daytime, but clone of another transaction within 2 minutes
                anom_time = anom_time.replace(hour=random.randint(10, 18), minute=random.randint(5, 50))
                records.append({
                    "transaction_id": f"TX-{tx_counter}",
                    "timestamp": anom_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "employee_id": emp,
                    "customer_id": cust,
                    "branch_id": branch,
                    "category": category,
                    "amount": amt,
                    "discount_percent": disc,
                    "refund_amount": 0.0,
                    "payment_method": pay_method,
                    "is_anomaly": 0,
                    "anomaly_type": "NONE"
                })
                tx_counter += 1
                dup_time = anom_time + datetime.timedelta(seconds=random.randint(30, 120))
                records.append({
                    "transaction_id": f"TX-{tx_counter}",
                    "timestamp": dup_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "employee_id": emp,
                    "customer_id": cust,
                    "branch_id": branch,
                    "category": category,
                    "amount": amt,
                    "discount_percent": disc,
                    "refund_amount": 0.0,
                    "payment_method": pay_method,
                    "is_anomaly": 1,
                    "anomaly_type": "DUPLICATE"
                })
                continue
                
            elif anom_type == "EXCESSIVE_DISCOUNT":
                # High discount 50% to 90%
                anom_time = anom_time.replace(hour=random.randint(9, 19))
                disc = round(random.uniform(55.0, 90.0), 1)
                amt = round(random.uniform(120.0, 600.0), 2)
                
            elif anom_type == "REFUND_FRAUD":
                # Unusual refund value
                anom_time = anom_time.replace(hour=random.randint(9, 19))
                ref = round(random.uniform(250.0, 850.0), 2)
                amt = round(random.uniform(10.0, 50.0), 2)
                
            elif anom_type == "OFF_HOURS":
                # Transaction in the middle of the night (01:00 - 04:45 AM)
                anom_time = anom_time.replace(hour=random.randint(1, 4), minute=random.randint(0, 59))
                amt = round(random.uniform(150.0, 950.0), 2)
                
            elif anom_type == "AMOUNT_SPIKE":
                # Huge transaction 6.5x to 14x normal employee median
                anom_time = anom_time.replace(hour=random.randint(10, 19))
                amt = round(emp_profiles[emp]["median_amt"] * random.uniform(6.5, 14.0), 2)
                
            records.append({
                "transaction_id": f"TX-{tx_counter}",
                "timestamp": anom_time.strftime("%Y-%m-%d %H:%M:%S"),
                "employee_id": emp,
                "customer_id": cust,
                "branch_id": branch,
                "category": category,
                "amount": amt,
                "discount_percent": disc,
                "refund_amount": ref,
                "payment_method": pay_method,
                "is_anomaly": 1,
                "anomaly_type": anom_type
            })
            
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df

if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Generate synthetic SME transactions with injected anomalies.")
    parser.add_argument("--records", type=int, default=10000, help="Number of records to generate")
    parser.add_argument("--anomaly-rate", type=float, default=0.035, help="Anomaly proportion (e.g. 0.035 for ~3.5%)")
    parser.add_argument("--output", type=str, default="data/demo_transactions.csv", help="Output CSV path")
    args = parser.parse_args()
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    print(f"Generating {args.records} transactions with {args.anomaly_rate*100:.1f}% anomaly rate...")
    df = generate_synthetic_transactions(num_records=args.records, anomaly_rate=args.anomaly_rate)
    df.to_csv(args.output, index=False)
    print(f"Successfully generated {len(df)} records saved to {args.output}")
    print("\nAnomaly Breakdown:")
    print(df["anomaly_type"].value_counts())
