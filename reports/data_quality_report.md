# FinSightAI - Data Quality Report

**Generated:** 2026-11-22 20:58:14 UTC

## 1. Executive Summary

- Total financial transactions: **6**
- Total counted validation issues: **0**
- Potential duplicate groups: **0**
- Transactions without vendor information: **0**

> Validation issue counts represent individual checks. A transaction can contribute to more than one issue, so these counts must not be interpreted as unique bad records.

## 2. Transaction Quality Checks

| Quality Check | Records Found |
|---|---:|
| Missing descriptions | 0 |
| Missing vendor information | 0 |
| Invalid amounts | 0 |
| Invalid transaction types | 0 |
| Invalid statuses | 0 |
| Invalid project references | 0 |
| Invalid category references | 0 |
| Invalid vendor references | 0 |

## 3. Transactions by Status

| Status | Count |
|---|---:|
| APPROVED | 4 |
| PENDING | 2 |

## 4. Transactions by Type

| Type | Count | Total Amount |
|---|---:|---:|
| EXPENSE | 6 | 135001 |

## 5. Expenses by Category

| Category ID | Count | Total Amount |
|---|---:|---:|
| 1 | 3 | 70001 |
| 2 | 3 | 65000 |

## 6. Potential Duplicate Transactions

Potential duplicate groups identified: **0**

These are candidates for manual review. They are not automatically classified as errors or deleted.

| Project | Category | Amount | Date | Description | Occurrences |
|---|---|---:|---|---|---:|

## 7. Import Batch Summary

| Batch ID | File | Total | Imported | Rejected | Unresolved Vendors | Status |
|---:|---|---:|---:|---:|---:|---|
| 3 | test_transactions.csv | 5 | 1 | 4 | 0 | COMPLETED |
| 2 | test_transactions.csv | 3 | 0 | 3 | 0 | PROCESSING |
| 1 | financial_transactions.csv | 10 | 0 | 2 | 0 | PROCESSING |

## 8. MongoDB Invoice Quality

- Total invoices: **2**
- Invoices with confidence below 0.80: **0**

| Extraction Status | Count |
|---|---:|
| COMPLETED | 1 |
| None | 1 |

## 9. Sample SQL Queries

### Total transactions

```sql
SELECT COUNT(*)
FROM financial_transactions;
```

### Transactions by status

```sql
SELECT status, COUNT(*) AS total
FROM financial_transactions
GROUP BY status;
```

### Potential duplicate transactions

```sql
SELECT project_id, category_id, amount, transaction_date,
       LOWER(TRIM(description)) AS description,
       transaction_type, COUNT(*) AS occurrences
FROM financial_transactions
GROUP BY project_id, category_id, amount, transaction_date,
         LOWER(TRIM(description)), transaction_type
HAVING COUNT(*) > 1;
```

## 10. Recommendations

- Review transactions with missing vendor information.
- Investigate potential duplicate transaction groups.
- Monitor rejected records across import batches.
- Resolve invalid project and category references.
- Review invoices with low extraction confidence.
- Run this report periodically to monitor data quality.

---

End of report.