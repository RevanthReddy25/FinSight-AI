from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def execute_scalar(db: Session, query: str):
    """Execute a query and return its first scalar result."""
    return db.execute(text(query)).scalar() or 0


def execute_rows(db: Session, query: str):
    """Execute a query and return rows as dictionaries."""
    result = db.execute(text(query))
    return [dict(row._mapping) for row in result]


def collect_sqlite_quality_metrics(db: Session) -> dict:
    """
    Collect data-quality metrics from the SQLite database.
    """

    metrics = {}

    # 1. Total transaction count
    metrics["total_transactions"] = execute_scalar(
        db,
        """
        SELECT COUNT(*)
        FROM financial_transactions
        """
    )

    # 2. Transactions with missing descriptions
    metrics["missing_descriptions"] = execute_scalar(
        db,
        """
        SELECT COUNT(*)
        FROM financial_transactions
        WHERE description IS NULL
           OR TRIM(description) = ''
        """
    )

    # 3. Transactions without resolved vendor information
    metrics["missing_vendor_information"] = execute_scalar(
        db,
        """
        SELECT COUNT(*)
        FROM financial_transactions
        WHERE vendor_id IS NULL
          AND (
              vendor_name_raw IS NULL
              OR TRIM(vendor_name_raw) = ''
          )
        """
    )

    # 4. Invalid transaction amounts
    metrics["invalid_amounts"] = execute_scalar(
        db,
        """
        SELECT COUNT(*)
        FROM financial_transactions
        WHERE amount <= 0
        """
    )

    # 5. Invalid transaction types
    metrics["invalid_transaction_types"] = execute_scalar(
        db,
        """
        SELECT COUNT(*)
        FROM financial_transactions
        WHERE transaction_type NOT IN ('EXPENSE', 'INCOME')
        """
    )

    # 6. Invalid transaction statuses
    metrics["invalid_statuses"] = execute_scalar(
        db,
        """
        SELECT COUNT(*)
        FROM financial_transactions
        WHERE status NOT IN (
            'PENDING',
            'APPROVED',
            'REJECTED',
            'PAID'
        )
        """
    )

    # 7. Transactions with invalid project references
    metrics["invalid_project_references"] = execute_scalar(
        db,
        """
        SELECT COUNT(*)
        FROM financial_transactions t
        LEFT JOIN financial_projects p
            ON t.project_id = p.project_id
        WHERE p.project_id IS NULL
        """
    )

    # 8. Transactions with invalid category references
    metrics["invalid_category_references"] = execute_scalar(
        db,
        """
        SELECT COUNT(*)
        FROM financial_transactions t
        LEFT JOIN categories c
            ON t.category_id = c.category_id
        WHERE c.category_id IS NULL
        """
    )

    # 9. Transactions with invalid vendor references
    metrics["invalid_vendor_references"] = execute_scalar(
        db,
        """
        SELECT COUNT(*)
        FROM financial_transactions t
        LEFT JOIN vendors v
            ON t.vendor_id = v.vendor_id
        WHERE t.vendor_id IS NOT NULL
          AND v.vendor_id IS NULL
        """
    )

    # 10. Transaction counts by status
    metrics["transactions_by_status"] = execute_rows(
        db,
        """
        SELECT
            status,
            COUNT(*) AS transaction_count
        FROM financial_transactions
        GROUP BY status
        ORDER BY transaction_count DESC
        """
    )

    # 11. Transaction counts by type
    metrics["transactions_by_type"] = execute_rows(
        db,
        """
        SELECT
            transaction_type,
            COUNT(*) AS transaction_count,
            SUM(amount) AS total_amount
        FROM financial_transactions
        GROUP BY transaction_type
        ORDER BY transaction_type
        """
    )

    # 12. Expenses by category
    metrics["expenses_by_category"] = execute_rows(
        db,
        """
        SELECT
            category_id,
            COUNT(*) AS transaction_count,
            SUM(amount) AS total_amount
        FROM financial_transactions
        WHERE transaction_type = 'EXPENSE'
        GROUP BY category_id
        ORDER BY total_amount DESC
        """
    )

    # 13. Potential duplicate transaction groups
    metrics["potential_duplicate_groups"] = execute_rows(
        db,
        """
        SELECT
            project_id,
            category_id,
            amount,
            transaction_date,
            LOWER(TRIM(description)) AS normalized_description,
            transaction_type,
            COUNT(*) AS occurrence_count
        FROM financial_transactions
        GROUP BY
            project_id,
            category_id,
            amount,
            transaction_date,
            LOWER(TRIM(description)),
            transaction_type
        HAVING COUNT(*) > 1
        ORDER BY occurrence_count DESC
        """
    )

    # 14. Import batch summary
    metrics["import_batches"] = execute_rows(
        db,
        """
        SELECT
            batch_id,
            file_name,
            total_records,
            imported_records,
            rejected_records,
            unresolved_vendor_count,
            status,
            created_at
        FROM import_batches
        ORDER BY created_at DESC
        """
    )

    return metrics


def collect_mongodb_quality_metrics() -> dict:
    """
    Collect invoice quality metrics from MongoDB.

    MongoDB is optional for this report.
    If it is unavailable, the SQLite report still succeeds.
    """

    metrics = {
        "available": False,
        "total_invoices": 0,
        "low_confidence_invoices": 0,
        "invoices_by_status": [],
        "error": None,
        "message": None
    }

    try:
        from app.mongodb.collections import invoice_collection

        metrics["total_invoices"] = invoice_collection.count_documents({})

        metrics["low_confidence_invoices"] = (
            invoice_collection.count_documents({
                "extraction.confidence": {"$lt": 0.80}
            })
        )

        pipeline = [
            {
                "$group": {
                    "_id": "$extraction.status",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]

        metrics["invoices_by_status"] = list(
            invoice_collection.aggregate(pipeline)
        )

        metrics["available"] = True

    except Exception as error:
        logger.error(
            "MongoDB data-quality metrics collection failed: %s",
            type(error).__name__
        )

        metrics["available"] = False
        metrics["message"] = (
            "MongoDB metrics are temporarily unavailable."
        )

    return metrics

def build_markdown_report(
    sqlite_metrics: dict,
    mongodb_metrics: dict
) -> str:
    """
    Convert collected metrics into a Markdown report.
    """

    total = sqlite_metrics["total_transactions"]

    invalid_categories = [
        "missing_descriptions",
        "invalid_amounts",
        "invalid_transaction_types",
        "invalid_statuses",
        "invalid_project_references",
        "invalid_category_references",
        "invalid_vendor_references"
    ]

    total_quality_issues = sum(
        sqlite_metrics[key]
        for key in invalid_categories
    )

    generated_at = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    lines = [
        "# FinSightAI - Data Quality Report",
        "",
        f"**Generated:** {generated_at}",
        "",
        "## 1. Executive Summary",
        "",
        f"- Total financial transactions: **{total}**",
        f"- Total counted validation issues: **{total_quality_issues}**",
        f"- Potential duplicate groups: "
        f"**{len(sqlite_metrics['potential_duplicate_groups'])}**",
        f"- Transactions without vendor information: "
        f"**{sqlite_metrics['missing_vendor_information']}**",
        "",
        "> Validation issue counts represent individual checks. "
        "A transaction can contribute to more than one issue, "
        "so these counts must not be interpreted as unique bad records.",
        "",
        "## 2. Transaction Quality Checks",
        "",
        "| Quality Check | Records Found |",
        "|---|---:|"
    ]

    quality_labels = {
        "missing_descriptions": "Missing descriptions",
        "missing_vendor_information": "Missing vendor information",
        "invalid_amounts": "Invalid amounts",
        "invalid_transaction_types": "Invalid transaction types",
        "invalid_statuses": "Invalid statuses",
        "invalid_project_references": "Invalid project references",
        "invalid_category_references": "Invalid category references",
        "invalid_vendor_references": "Invalid vendor references"
    }

    for key, label in quality_labels.items():
        lines.append(
            f"| {label} | {sqlite_metrics[key]} |"
        )

    lines.extend([
        "",
        "## 3. Transactions by Status",
        "",
        "| Status | Count |",
        "|---|---:|"
    ])

    for row in sqlite_metrics["transactions_by_status"]:
        lines.append(
            f"| {row['status']} | {row['transaction_count']} |"
        )

    lines.extend([
        "",
        "## 4. Transactions by Type",
        "",
        "| Type | Count | Total Amount |",
        "|---|---:|---:|"
    ])

    for row in sqlite_metrics["transactions_by_type"]:
        lines.append(
            f"| {row['transaction_type']} | "
            f"{row['transaction_count']} | "
            f"{row['total_amount']} |"
        )

    lines.extend([
        "",
        "## 5. Expenses by Category",
        "",
        "| Category ID | Count | Total Amount |",
        "|---|---:|---:|"
    ])

    for row in sqlite_metrics["expenses_by_category"]:
        lines.append(
            f"| {row['category_id']} | "
            f"{row['transaction_count']} | "
            f"{row['total_amount']} |"
        )

    lines.extend([
        "",
        "## 6. Potential Duplicate Transactions",
        "",
        f"Potential duplicate groups identified: "
        f"**{len(sqlite_metrics['potential_duplicate_groups'])}**",
        "",
        "These are candidates for manual review. "
        "They are not automatically classified as errors or deleted.",
        "",
        "| Project | Category | Amount | Date | Description | Occurrences |",
        "|---|---|---:|---|---|---:|"
    ])

    for row in sqlite_metrics["potential_duplicate_groups"]:
        lines.append(
            f"| {row['project_id']} | "
            f"{row['category_id']} | "
            f"{row['amount']} | "
            f"{row['transaction_date']} | "
            f"{row['normalized_description']} | "
            f"{row['occurrence_count']} |"
        )

    lines.extend([
        "",
        "## 7. Import Batch Summary",
        "",
        "| Batch ID | File | Total | Imported | Rejected | Unresolved Vendors | Status |",
        "|---:|---|---:|---:|---:|---:|---|"
    ])

    for row in sqlite_metrics["import_batches"]:
        lines.append(
            f"| {row['batch_id']} | "
            f"{row['file_name']} | "
            f"{row['total_records']} | "
            f"{row['imported_records']} | "
            f"{row['rejected_records']} | "
            f"{row['unresolved_vendor_count']} | "
            f"{row['status']} |"
        )

    lines.extend([
        "",
        "## 8. MongoDB Invoice Quality",
        ""
    ])

    if mongodb_metrics["available"]:

        lines.extend([
            f"- Total invoices: **{mongodb_metrics['total_invoices']}**",
            f"- Invoices with confidence below 0.80: "
            f"**{mongodb_metrics['low_confidence_invoices']}**",
            "",
            "| Extraction Status | Count |",
            "|---|---:|"
        ])

        for row in mongodb_metrics["invoices_by_status"]:
            lines.append(
                f"| {row['_id']} | {row['count']} |"
            )

    else:
        lines.append(
            "MongoDB metrics could not be collected. "
            "The relational database report was generated successfully."
        )

        if not mongodb_metrics.get("available", False):

            lines.extend([
                "MongoDB metrics could not be collected.",
                "",
                mongodb_metrics.get(
                    "message",
                    "MongoDB metrics are temporarily unavailable."
                ),
                ""
            ])

    lines.extend([
        "",
        "## 9. Sample SQL Queries",
        "",
        "### Total transactions",
        "",
        "```sql",
        "SELECT COUNT(*)",
        "FROM financial_transactions;",
        "```",
        "",
        "### Transactions by status",
        "",
        "```sql",
        "SELECT status, COUNT(*) AS total",
        "FROM financial_transactions",
        "GROUP BY status;",
        "```",
        "",
        "### Potential duplicate transactions",
        "",
        "```sql",
        "SELECT project_id, category_id, amount, transaction_date,",
        "       LOWER(TRIM(description)) AS description,",
        "       transaction_type, COUNT(*) AS occurrences",
        "FROM financial_transactions",
        "GROUP BY project_id, category_id, amount, transaction_date,",
        "         LOWER(TRIM(description)), transaction_type",
        "HAVING COUNT(*) > 1;",
        "```",
        "",
        "## 10. Recommendations",
        "",
        "- Review transactions with missing vendor information.",
        "- Investigate potential duplicate transaction groups.",
        "- Monitor rejected records across import batches.",
        "- Resolve invalid project and category references.",
        "- Review invoices with low extraction confidence.",
        "- Run this report periodically to monitor data quality.",
        "",
        "---",
        "",
        "End of report."
    ])

    return "\n".join(lines)


def generate_data_quality_report(
    db: Session,
    output_path: str = "reports/data_quality_report.md",
    include_mongodb: bool = True
) -> str:
    """
    Generate and save the complete data-quality report.
    """

    sqlite_metrics = collect_sqlite_quality_metrics(db)

    if include_mongodb:
        mongodb_metrics = collect_mongodb_quality_metrics()
    else:
        mongodb_metrics = {
            "available": False,
            "total_invoices": 0,
            "low_confidence_invoices": 0,
            "invoices_by_status": [],
            "error": "MongoDB checks disabled."
        }

    report = build_markdown_report(
        sqlite_metrics,
        mongodb_metrics
    )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_file.write_text(
        report,
        encoding="utf-8"
    )

    return str(output_file.resolve())