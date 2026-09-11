# Transaction Data & Schema Documentation

This directory contains the synthetic datasets, anomaly injection scripts, and API contract payloads for the **Business Fraud & Anomaly Radar** platform.

## Directory Structure

```
data/
├── data_generator.py          # Configurable synthetic transaction & anomaly generator
├── demo_transactions.csv      # 10,070 records with 3.5% injected fraud scenarios
├── clean_baseline.csv         # 5,000 clean baseline records (no anomalies)
├── sample_alerts_payload.json # Exact JSON contract exchanged between Python/Spring Boot/React
└── README.md                  # This documentation
```

## Dataset Schema

Each row in `demo_transactions.csv` represents a point-of-sale retail/SME transaction:

| Column | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `transaction_id` | String | Unique transaction identifier | `TX-100042` |
| `timestamp` | Datetime | ISO timestamp (`YYYY-MM-DD HH:MM:SS`) | `2026-07-04 14:22:15` |
| `employee_id` | String | Cashier/staff member ID | `EMP-003` |
| `customer_id` | String | Customer account/loyalty ID | `CUST-4819` |
| `branch_id` | String | Store location code | `BRANCH-CENTRAL` |
| `category` | String | Item category | `Electronics` |
| `amount` | Float | Transaction amount in USD | `49.99` |
| `discount_percent`| Float | Percentage discount applied | `10.0` |
| `refund_amount` | Float | Value refunded (0.0 for sales) | `0.0` |
| `payment_method` | String | Method of payment | `Mobile Money` |
| `is_anomaly` | Integer | Ground-truth evaluation label (`0` or `1`)| `1` |
| `anomaly_type` | String | Injected category label | `EXCESSIVE_DISCOUNT` |

## Injected Fraud Archetypes

1. **`DUPLICATE`**: Repeated transaction with identical amount, customer, and employee within minutes.
2. **`EXCESSIVE_DISCOUNT`**: Extreme discount overrides between 55% and 90%.
3. **`REFUND_FRAUD`**: Unusual refund values or surges in refund frequency.
4. **`OFF_HOURS`**: Cash register transactions executed between 01:00 AM and 04:45 AM.
5. **`AMOUNT_SPIKE`**: Extreme single-basket total 6.5× to 14× above employee historical median.

## Regenerating Data

To generate a new dataset with custom parameters:

```bash
python data_generator.py --records 10000 --anomaly-rate 0.035 --output demo_transactions.csv
```
