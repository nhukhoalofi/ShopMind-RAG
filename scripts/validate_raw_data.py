"""
Validate ShopMind raw datasets before document preparation and embedding.

Expected project structure:
    data/raw/
        faq.csv
        products.csv
        orders_sample.csv
        returns_sample.csv
        shipping_sample.csv
        policies/
            return_policy.md
            refund_policy.md
            shipping_policy.md
            payment_policy.md
            warranty_policy.md
            account_policy.md

Output:
    data/processed/validation_report.json

Run from the project root:
    python scripts/validate_raw_data.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_REPORT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "validation_report.json"
)

ALLOWED_FAQ_CATEGORIES = {
    "account",
    "general",
    "order",
    "payment",
    "product",
    "return_refund",
    "shipping",
    "warranty",
}

REQUIRED_POLICIES = {
    "account_policy.md",
    "payment_policy.md",
    "refund_policy.md",
    "return_policy.md",
    "shipping_policy.md",
    "warranty_policy.md",
}

FILE_RULES = {
    "faq.csv": {
        "required_columns": {
            "faq_id",
            "category",
            "question",
            "answer",
            "sources",
            "language",
        },
        "non_empty_columns": {
            "faq_id",
            "category",
            "question",
            "answer",
            "sources",
            "language",
        },
        "unique_columns": {"faq_id"},
    },
    "products.csv": {
        "required_columns": {"product_id"},
        "non_empty_columns": {"product_id"},
        "unique_columns": {"product_id"},
    },
    "orders_sample.csv": {
        "required_columns": {"order_id"},
        "non_empty_columns": {"order_id"},
        "unique_columns": {"order_id"},
    },
    "returns_sample.csv": {
        "required_columns": {"order_id"},
        "non_empty_columns": {"order_id"},
        "unique_columns": {"order_id"},
    },
    "shipping_sample.csv": {
        "required_columns": {"shipment_id"},
        "non_empty_columns": {"shipment_id"},
        "unique_columns": {"shipment_id"},
    },
}


@dataclass
class ValidationReport:
    raw_directory: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    files: dict[str, dict] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not self.errors


def normalize_column_name(name: object) -> str:
    return re.sub(r"\s+", "_", str(name).strip().lower())


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def row_numbers(mask: pd.Series, limit: int = 10) -> list[int]:
    """Return spreadsheet-style row numbers, including the header row."""
    return [int(index) + 2 for index in mask[mask].index[:limit]]


def add_problem(
    target: list[str],
    filename: str,
    message: str,
) -> None:
    target.append(f"{filename}: {message}")


def read_csv_safely(path: Path, report: ValidationReport) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=True)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(
                path,
                dtype=str,
                keep_default_na=True,
                encoding="utf-8-sig",
            )
        except Exception as exc:
            add_problem(report.errors, path.name, f"cannot read CSV ({exc})")
            return None
    except Exception as exc:
        add_problem(report.errors, path.name, f"cannot read CSV ({exc})")
        return None

    original_columns = list(df.columns)
    normalized_columns = [normalize_column_name(col) for col in original_columns]

    if len(set(normalized_columns)) != len(normalized_columns):
        add_problem(
            report.errors,
            path.name,
            "contains duplicate column names after normalization",
        )
        return None

    if original_columns != normalized_columns:
        add_problem(
            report.warnings,
            path.name,
            "column names contain spaces or inconsistent capitalization; "
            "the validator normalized them temporarily",
        )

    df.columns = normalized_columns
    return df


def validate_required_columns(
    filename: str,
    df: pd.DataFrame,
    required_columns: Iterable[str],
    report: ValidationReport,
) -> None:
    missing = sorted(set(required_columns) - set(df.columns))
    if missing:
        add_problem(
            report.errors,
            filename,
            f"missing required columns: {', '.join(missing)}",
        )


def validate_non_empty_columns(
    filename: str,
    df: pd.DataFrame,
    columns: Iterable[str],
    report: ValidationReport,
) -> None:
    for column in sorted(set(columns) & set(df.columns)):
        empty_mask = df[column].map(normalize_text).eq("")
        count = int(empty_mask.sum())
        if count:
            add_problem(
                report.errors,
                filename,
                f"column '{column}' has {count} empty values "
                f"(rows {row_numbers(empty_mask)})",
            )


def validate_unique_columns(
    filename: str,
    df: pd.DataFrame,
    columns: Iterable[str],
    report: ValidationReport,
) -> None:
    for column in sorted(set(columns) & set(df.columns)):
        normalized = df[column].map(normalize_text).str.casefold()
        duplicate_mask = normalized.ne("") & normalized.duplicated(keep=False)
        count = int(duplicate_mask.sum())
        if count:
            add_problem(
                report.errors,
                filename,
                f"column '{column}' has {count} rows containing duplicate values "
                f"(rows {row_numbers(duplicate_mask)})",
            )


def validate_faq(df: pd.DataFrame, report: ValidationReport) -> None:
    filename = "faq.csv"

    if {"question", "answer"}.issubset(df.columns):
        question_key = df["question"].map(normalize_text).str.casefold()
        answer_key = df["answer"].map(normalize_text).str.casefold()
        duplicate_mask = (
            question_key.ne("")
            & answer_key.ne("")
            & pd.DataFrame(
                {"question": question_key, "answer": answer_key}
            ).duplicated(keep=False)
        )
        count = int(duplicate_mask.sum())
        if count:
            add_problem(
                report.warnings,
                filename,
                f"{count} rows contain duplicate question-answer pairs "
                f"(rows {row_numbers(duplicate_mask)})",
            )

        short_question_mask = df["question"].map(normalize_text).str.len().between(1, 9)
        short_answer_mask = df["answer"].map(normalize_text).str.len().between(1, 19)

        if short_question_mask.any():
            add_problem(
                report.warnings,
                filename,
                f"{int(short_question_mask.sum())} questions are shorter than "
                f"10 characters (rows {row_numbers(short_question_mask)})",
            )
        if short_answer_mask.any():
            add_problem(
                report.warnings,
                filename,
                f"{int(short_answer_mask.sum())} answers are shorter than "
                f"20 characters (rows {row_numbers(short_answer_mask)})",
            )

    if "category" in df.columns:
        categories = df["category"].map(normalize_text).str.casefold()
        unknown = sorted(
            value
            for value in categories.unique()
            if value and value not in ALLOWED_FAQ_CATEGORIES
        )
        if unknown:
            add_problem(
                report.warnings,
                filename,
                "contains non-standard categories: " + ", ".join(unknown[:20]),
            )

    if "language" not in df.columns:
        add_problem(
            report.warnings,
            filename,
            "missing optional 'language' column; add language='en' for traceability",
        )
    else:
        languages = {
            value
            for value in df["language"].map(normalize_text).str.casefold()
            if value
        }
        unexpected = sorted(languages - {"en", "english"})
        if unexpected:
            add_problem(
                report.warnings,
                filename,
                "expected English data but found language values: "
                + ", ".join(unexpected),
            )


def validate_csv_file(
    raw_dir: Path,
    filename: str,
    rules: dict,
    report: ValidationReport,
) -> None:
    path = raw_dir / filename

    if not path.exists():
        add_problem(report.errors, filename, "file does not exist")
        report.files[filename] = {"exists": False}
        return

    if path.stat().st_size == 0:
        add_problem(report.errors, filename, "file is empty")
        report.files[filename] = {"exists": True, "size_bytes": 0}
        return

    df = read_csv_safely(path, report)
    if df is None:
        report.files[filename] = {
            "exists": True,
            "size_bytes": path.stat().st_size,
            "readable": False,
        }
        return

    report.files[filename] = {
        "exists": True,
        "readable": True,
        "rows": int(len(df)),
        "columns": list(df.columns),
    }

    if df.empty:
        add_problem(report.errors, filename, "contains no data rows")
        return

    validate_required_columns(
        filename,
        df,
        rules["required_columns"],
        report,
    )
    validate_non_empty_columns(
        filename,
        df,
        rules["non_empty_columns"],
        report,
    )
    validate_unique_columns(
        filename,
        df,
        rules["unique_columns"],
        report,
    )

    if filename == "faq.csv":
        validate_faq(df, report)


def validate_policies(raw_dir: Path, report: ValidationReport) -> None:
    policies_dir = raw_dir / "policies"
    report.files["policies"] = {
        "exists": policies_dir.exists(),
        "files": [],
    }

    if not policies_dir.exists():
        add_problem(report.errors, "policies", "directory does not exist")
        return

    existing = {path.name for path in policies_dir.glob("*.md")}
    report.files["policies"]["files"] = sorted(existing)

    missing = sorted(REQUIRED_POLICIES - existing)
    if missing:
        add_problem(
            report.errors,
            "policies",
            f"missing required files: {', '.join(missing)}",
        )

    for filename in sorted(existing):
        path = policies_dir / filename
        try:
            content = path.read_text(encoding="utf-8-sig").strip()
        except Exception as exc:
            add_problem(
                report.errors,
                filename,
                f"cannot read policy file ({exc})",
            )
            continue

        if not content:
            add_problem(report.errors, filename, "policy file is empty")
        elif len(content) < 100:
            add_problem(
                report.warnings,
                filename,
                "policy is shorter than 100 characters and may lack useful detail",
            )


def save_report(report: ValidationReport, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(report)
    payload["passed"] = report.passed
    payload["summary"] = {
        "error_count": len(report.errors),
        "warning_count": len(report.warnings),
    }
    report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def print_report(report: ValidationReport, report_path: Path) -> None:
    print("\n" + "=" * 72)
    print("SHOPMIND RAW DATA VALIDATION")
    print("=" * 72)

    for filename, details in report.files.items():
        if "rows" in details:
            print(
                f"[FILE] {filename}: {details['rows']} rows, "
                f"{len(details['columns'])} columns"
            )
        elif details.get("exists"):
            print(f"[FILE] {filename}: found")
        else:
            print(f"[FILE] {filename}: missing")

    if report.errors:
        print("\nERRORS")
        for item in report.errors:
            print(f"- {item}")

    if report.warnings:
        print("\nWARNINGS")
        for item in report.warnings:
            print(f"- {item}")

    print("\n" + "-" * 72)
    print(f"Errors: {len(report.errors)}")
    print(f"Warnings: {len(report.warnings)}")
    print(f"Report: {report_path}")
    print("Result: PASSED" if report.passed else "Result: FAILED")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate ShopMind files in data/raw before RAG ingestion."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DEFAULT_RAW_DIR,
        help="Path to the raw data directory.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path for the JSON validation report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_dir = args.raw_dir.resolve()
    report_path = args.report.resolve()
    report = ValidationReport(raw_directory=str(raw_dir))

    if not raw_dir.exists():
        report.errors.append(f"Raw data directory does not exist: {raw_dir}")
    else:
        for filename, rules in FILE_RULES.items():
            validate_csv_file(raw_dir, filename, rules, report)
        validate_policies(raw_dir, report)

    save_report(report, report_path)
    print_report(report, report_path)
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
