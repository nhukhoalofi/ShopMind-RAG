"""Build the canonical ShopMind raw and evaluation datasets."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd
from datasets import load_from_disk


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = PROJECT_ROOT / "data" / "external"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
EVALUATION_DIR = PROJECT_ROOT / "data" / "evaluation"
POLICIES_DIR = RAW_DIR / "policies"

DEFAULT_ORDER_SAMPLE_SIZE = 5_000
DEFAULT_RETURN_SAMPLE_SIZE = 2_000
DEFAULT_SHIPPING_SAMPLE_SIZE = 2_000
RANDOM_SEED = 42

FAQ_SOURCES = (
    (
        "maktek_customer_support_faqs",
        EXTERNAL_DIR / "maktek_customer_support_faqs" / "csv" / "train.csv",
        "question",
        "answer",
    ),
    (
        "harishvs_ecommerce_faq_qa",
        EXTERNAL_DIR / "harishvs_ecommerce_faq_qa" / "csv" / "train.csv",
        "instruction",
        "response",
    ),
    (
        "andyrasika_ecommerce_faq",
        EXTERNAL_DIR / "andyrasika_ecommerce_faq" / "csv" / "train.csv",
        "question",
        "answer",
    ),
)

POLICIES = {
    "return_policy.md": """# Return Policy

ShopMind accepts return requests within 30 calendar days of delivery.

## Eligibility

- Items must be unused, complete, and returned with original packaging and accessories.
- Proof of purchase or an order number is required.
- Final-sale, personalized, downloadable, and hygiene-sensitive items are not returnable unless defective.
- Damaged, defective, or incorrect items should be reported within 7 days of delivery.

## Process

1. Open the order in your ShopMind account and select **Request return**.
2. Choose the item and return reason, then upload photos when the item is damaged or incorrect.
3. Wait for return authorization and shipping instructions before sending the item.
4. Keep the carrier receipt until the return is completed.

Approved returns must be handed to the carrier within 7 days after authorization.
""",
    "refund_policy.md": """# Refund Policy

Refunds are issued after an approved cancellation or after a returned item passes inspection.

## Timing

- ShopMind completes return inspection within 3 business days after receipt.
- Approved refunds are sent to the original payment method.
- Banks and payment providers may need an additional 5 to 10 business days to post the credit.

Original shipping fees are not refundable for preference-based returns. ShopMind covers reasonable
return shipping costs for damaged, defective, or incorrect items. Promotional discounts are not
refunded as cash, and the refund cannot exceed the amount paid for the returned item.
""",
    "shipping_policy.md": """# Shipping Policy

ShopMind displays available shipping methods, estimated delivery dates, and fees during checkout.
Estimates begin after payment verification and order processing.

## Delivery

- Standard processing normally takes 1 to 2 business days.
- Tracking is added to the order page after the carrier accepts the package.
- Address changes are only possible before the order enters packing or ships.
- Carrier delays, weather, customs, and peak periods may affect the displayed estimate.

Contact support when tracking has not updated for 3 business days or when an order is 2 business
days past its estimated delivery date. Report a package marked delivered but not received within
48 hours.
""",
    "payment_policy.md": """# Payment Policy

ShopMind accepts major credit cards, debit cards, and supported digital wallets shown at checkout.
Available methods may vary by country and currency.

Payment is authorized when the order is placed and captured when processing begins. A failed or
expired authorization may cancel the order automatically. ShopMind does not request full card
numbers, passwords, or one-time verification codes through chat or email.

For duplicate or unfamiliar charges, first compare the amount with pending authorizations in the
order history. Contact support with the order number and charge date; contact the payment provider
immediately when fraud is suspected.
""",
    "warranty_policy.md": """# Warranty Policy

Eligible ShopMind products include a limited warranty against manufacturing defects. The warranty
period shown on the product page or invoice starts on the delivery date.

The warranty does not cover normal wear, accidental damage, misuse, unauthorized repair, lost
items, or consumable parts. A claim requires the order number, a description of the fault, and
photos or video when relevant.

After review, ShopMind or the manufacturer may repair the item, replace it with an equivalent item,
or refund the purchase price when repair and replacement are unavailable.
""",
    "account_policy.md": """# Account Policy

Customers are responsible for keeping account contact information and passwords current. Use a
unique password and never share verification codes.

Email or phone verification may be required for sign-in, checkout, sensitive profile changes, and
account recovery. ShopMind support will not ask for a password or one-time code.

Customers may request profile correction, password reset, or account closure through account
settings or support. Some transaction records may be retained when required for fraud prevention,
tax, warranty, or legal obligations.
""",
}


def normalize_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalized_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def categorize_faq(question: str, answer: str) -> str:
    question_text = question.lower()
    text = f"{question} {answer}".lower()
    availability_keywords = (
        "out of stock",
        "sold out",
        "coming soon",
        "temporarily unavailable",
        "on hold",
        "product request",
        "restock",
    )
    if any(keyword in question_text for keyword in availability_keywords):
        return "product"

    category_keywords = (
        ("return_refund", ("return", "refund", "exchange", "money back")),
        ("shipping", ("shipping", "delivery", "track", "shipment", "courier")),
        ("payment", ("payment", "credit card", "debit card", "paypal", "charge", "invoice")),
        ("warranty", ("warranty", "guarantee", "defect", "repair")),
        ("account", ("account", "password", "login", "sign up", "email", "newsletter")),
        ("order", ("order", "cancel", "purchase", "checkout")),
        ("product", ("product", "item", "stock", "size", "color")),
    )
    for category, keywords in category_keywords:
        if any(keyword in text for keyword in keywords):
            return category
    return "general"


def redact_identifiers(value: str) -> str:
    text = normalize_text(value)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "<EMAIL>", text)
    text = re.sub(r"(?i)\border\s*#?\s*[A-Z0-9-]{4,}\b", "order <ORDER_ID>", text)
    text = re.sub(
        r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)",
        "<PHONE>",
        text,
    )
    return text


def require_files(paths: list[Path]) -> None:
    missing = [path for path in paths if not path.exists()]
    if missing:
        formatted = "\n".join(f"- {path.relative_to(PROJECT_ROOT)}" for path in missing)
        raise FileNotFoundError(f"Required source files are missing:\n{formatted}")


def build_faq() -> pd.DataFrame:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)

    for source, csv_path, question_column, answer_column in FAQ_SOURCES:
        frame = pd.read_csv(csv_path)
        for row in frame.to_dict("records"):
            question = normalize_text(row[question_column])
            answer = normalize_text(row[answer_column])
            if question and answer:
                grouped[normalized_key(question)].append(
                    {"question": question, "answer": answer, "source": source}
                )

    records = []
    for candidates in grouped.values():
        selected = candidates[0]
        sources = sorted({candidate["source"] for candidate in candidates})
        records.append(
            {
                "question": selected["question"],
                "answer": selected["answer"],
                "category": categorize_faq(selected["question"], selected["answer"]),
                "sources": "|".join(sources),
                "language": "en",
            }
        )

    faq = pd.DataFrame(records).sort_values(
        ["category", "question"], key=lambda column: column.str.lower()
    )
    faq.insert(0, "faq_id", [f"faq_{index:04d}" for index in range(1, len(faq) + 1)])
    return faq.reset_index(drop=True)


def build_products(transactions: pd.DataFrame) -> pd.DataFrame:
    frame = transactions.copy()
    discount_denominator = (1 - frame["Discount_Applied"]).replace(0, pd.NA)
    frame["estimated_unit_price"] = (
        frame["Revenue"] / frame["Units_Sold"] / discount_denominator
    )

    products = (
        frame.groupby(["Product_ID", "Category"], as_index=False)
        .agg(
            unit_price=("estimated_unit_price", "median"),
            avg_discount_rate=("Discount_Applied", "mean"),
            transaction_count=("Transaction_ID", "nunique"),
            total_units_sold=("Units_Sold", "sum"),
            regions=("Region", lambda values: "|".join(sorted(set(values)))),
        )
        .rename(columns={"Product_ID": "product_id", "Category": "category"})
    )
    products["name"] = products.apply(
        lambda row: f"{row['category']} {row['product_id'].replace('_', ' ')}",
        axis=1,
    )
    products["unit_price"] = products["unit_price"].round(2)
    products["avg_discount_rate"] = products["avg_discount_rate"].round(4)
    products["source"] = "synthetic_ecommerce"
    return products[
        [
            "product_id",
            "name",
            "category",
            "unit_price",
            "avg_discount_rate",
            "transaction_count",
            "total_units_sold",
            "regions",
            "source",
        ]
    ].sort_values("product_id")


def build_orders(transactions: pd.DataFrame, sample_size: int) -> pd.DataFrame:
    sample_size = min(sample_size, len(transactions))
    orders = transactions.sample(n=sample_size, random_state=RANDOM_SEED).rename(
        columns={
            "Transaction_ID": "order_id",
            "Customer_ID": "customer_id",
            "Transaction_Date": "order_date",
            "Product_ID": "product_id",
            "Units_Sold": "quantity",
            "Discount_Applied": "discount_rate",
            "Revenue": "revenue",
            "Region": "region",
        }
    )
    orders["source"] = "synthetic_ecommerce"
    return orders[
        [
            "order_id",
            "customer_id",
            "order_date",
            "product_id",
            "quantity",
            "discount_rate",
            "revenue",
            "region",
            "source",
        ]
    ].sort_values(["order_date", "order_id"])


def build_returns(sample_size: int) -> pd.DataFrame:
    source_path = (
        EXTERNAL_DIR
        / "synthetic_returns"
        / "ecommerce_returns_synthetic_data.csv"
    )
    frame = pd.read_csv(source_path)
    sample_size = min(sample_size, len(frame))
    returns = frame.sample(n=sample_size, random_state=RANDOM_SEED).rename(
        columns={
            "Order_ID": "order_id",
            "Product_ID": "product_id",
            "User_ID": "customer_id",
            "Order_Date": "order_date",
            "Return_Date": "return_date",
            "Product_Category": "product_category",
            "Product_Price": "product_price",
            "Order_Quantity": "quantity",
            "Return_Reason": "return_reason",
            "Return_Status": "return_status",
            "Days_to_Return": "days_to_return",
            "Payment_Method": "payment_method",
            "Shipping_Method": "shipping_method",
            "Discount_Applied": "discount_applied",
        }
    )
    returns["source"] = "synthetic_returns"
    return returns[
        [
            "order_id",
            "product_id",
            "customer_id",
            "order_date",
            "return_date",
            "product_category",
            "product_price",
            "quantity",
            "return_reason",
            "return_status",
            "days_to_return",
            "payment_method",
            "shipping_method",
            "discount_applied",
            "source",
        ]
    ].sort_values(["order_date", "order_id"])


def build_shipping(sample_size: int) -> pd.DataFrame:
    source_path = EXTERNAL_DIR / "shipping_data" / "Train.csv"
    frame = pd.read_csv(source_path)
    sample_size = min(sample_size, len(frame))
    shipping = frame.sample(n=sample_size, random_state=RANDOM_SEED).rename(
        columns={
            "ID": "shipment_id",
            "Warehouse_block": "warehouse_block",
            "Mode_of_Shipment": "shipment_mode",
            "Customer_care_calls": "customer_care_calls",
            "Customer_rating": "customer_rating",
            "Cost_of_the_Product": "product_cost",
            "Prior_purchases": "prior_purchases",
            "Product_importance": "product_importance",
            "Gender": "customer_gender",
            "Discount_offered": "discount_offered",
            "Weight_in_gms": "weight_grams",
            "Reached.on.Time_Y.N": "is_delayed",
        }
    )
    shipping["source"] = "shipping_data"
    return shipping[
        [
            "shipment_id",
            "warehouse_block",
            "shipment_mode",
            "customer_care_calls",
            "customer_rating",
            "product_cost",
            "prior_purchases",
            "product_importance",
            "customer_gender",
            "discount_offered",
            "weight_grams",
            "is_delayed",
            "source",
        ]
    ].sort_values("shipment_id")


def iter_rjac_examples() -> list[dict[str, Any]]:
    source_path = EXTERNAL_DIR / "rjac_ecommerce_support_qa" / "csv" / "train.csv"
    frame = pd.read_csv(source_path)
    examples = []

    for row_index, row in frame.iterrows():
        knowledge_items = json.loads(row["qa"]).get("knowledge", [])
        for knowledge_index, item in enumerate(knowledge_items):
            question = redact_identifiers(item.get("customer_summary_question", ""))
            answer = redact_identifiers(item.get("agent_summary_solution", ""))
            if not question or not answer:
                continue
            examples.append(
                {
                    "id": f"rjac_{row_index + 1:04d}_{knowledge_index + 1:02d}",
                    "question": question,
                    "reference_answer": answer,
                    "category": normalize_text(row["issue_area"]),
                    "difficulty": normalize_text(row["issue_complexity"]),
                    "source": "rjac_ecommerce_support_qa",
                    "metadata": {
                        "issue_category": normalize_text(row["issue_category"]),
                        "issue_sub_category": normalize_text(row["issue_sub_category"]),
                        "customer_sentiment": normalize_text(row["customer_sentiment"]),
                        "product_category": normalize_text(row["product_category"]),
                        "product_sub_category": normalize_text(row["product_sub_category"]),
                    },
                }
            )
    return examples


def build_hard_cases(rjac_examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hard_cases = [
        {**example, "hard_case_reason": "high_complexity_or_negative_sentiment"}
        for example in rjac_examples
        if example["difficulty"] == "high"
        or example["metadata"]["customer_sentiment"] in {"negative", "frustrated"}
    ]

    dataset_path = (
        EXTERNAL_DIR / "kazkozdev_synth_customer_support" / "hf_disk"
    )
    dataset = load_from_disk(str(dataset_path))["train"]
    for row_index, row in enumerate(dataset):
        user_messages = [
            redact_identifiers(message["content"])
            for message in row["messages"]
            if message["role"] == "user"
        ]
        assistant_messages = [
            redact_identifiers(message["content"])
            for message in row["messages"]
            if message["role"] == "assistant"
        ]
        if not user_messages or not assistant_messages:
            continue
        hard_cases.append(
            {
                "id": f"kazkozdev_{row_index + 1:04d}",
                "question": user_messages[0],
                "reference_answer": assistant_messages[-1],
                "category": "customer_support",
                "difficulty": "hard",
                "source": "kazkozdev_synth_customer_support",
                "metadata": row["metadata"],
                "hard_case_reason": "synthetic_escalation_or_edge_case",
            }
        )
    return hard_cases


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_policies() -> None:
    POLICIES_DIR.mkdir(parents=True, exist_ok=True)
    for filename, content in POLICIES.items():
        (POLICIES_DIR / filename).write_text(content.strip() + "\n", encoding="utf-8")


def validate_frame(
    name: str,
    frame: pd.DataFrame,
    expected_columns: list[str],
    id_column: str,
) -> None:
    if list(frame.columns) != expected_columns:
        raise ValueError(f"{name} has an unexpected schema: {list(frame.columns)}")
    if frame.empty:
        raise ValueError(f"{name} must not be empty.")
    if frame[id_column].isna().any() or frame[id_column].duplicated().any():
        raise ValueError(f"{name} contains missing or duplicate {id_column} values.")


def validate_jsonl_records(name: str, records: list[dict[str, Any]]) -> None:
    required_keys = {
        "id",
        "question",
        "reference_answer",
        "category",
        "difficulty",
        "source",
        "metadata",
    }
    if not records:
        raise ValueError(f"{name} must not be empty.")
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{name} contains duplicate IDs.")
    for record in records:
        if not required_keys.issubset(record):
            raise ValueError(f"{name} record {record.get('id')} has missing fields.")
        if not record["question"] or not record["reference_answer"]:
            raise ValueError(f"{name} record {record['id']} has empty text.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", type=int, default=DEFAULT_ORDER_SAMPLE_SIZE)
    parser.add_argument("--returns", type=int, default=DEFAULT_RETURN_SAMPLE_SIZE)
    parser.add_argument("--shipping", type=int, default=DEFAULT_SHIPPING_SAMPLE_SIZE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if min(args.orders, args.returns, args.shipping) <= 0:
        raise ValueError("Sample sizes must be positive integers.")

    required_paths = [source[1] for source in FAQ_SOURCES] + [
        EXTERNAL_DIR / "synthetic_ecommerce" / "synthetic_ecommerce_data.csv",
        EXTERNAL_DIR
        / "synthetic_returns"
        / "ecommerce_returns_synthetic_data.csv",
        EXTERNAL_DIR / "shipping_data" / "Train.csv",
        EXTERNAL_DIR / "rjac_ecommerce_support_qa" / "csv" / "train.csv",
        EXTERNAL_DIR
        / "kazkozdev_synth_customer_support"
        / "hf_disk"
        / "dataset_dict.json",
    ]
    require_files(required_paths)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

    transactions = pd.read_csv(
        EXTERNAL_DIR / "synthetic_ecommerce" / "synthetic_ecommerce_data.csv"
    )
    outputs = {
        RAW_DIR / "faq.csv": build_faq(),
        RAW_DIR / "products.csv": build_products(transactions),
        RAW_DIR / "orders_sample.csv": build_orders(transactions, args.orders),
        RAW_DIR / "returns_sample.csv": build_returns(args.returns),
        RAW_DIR / "shipping_sample.csv": build_shipping(args.shipping),
    }
    schemas = {
        "faq.csv": (
            ["faq_id", "question", "answer", "category", "sources", "language"],
            "faq_id",
        ),
        "products.csv": (
            [
                "product_id",
                "name",
                "category",
                "unit_price",
                "avg_discount_rate",
                "transaction_count",
                "total_units_sold",
                "regions",
                "source",
            ],
            "product_id",
        ),
        "orders_sample.csv": (
            [
                "order_id",
                "customer_id",
                "order_date",
                "product_id",
                "quantity",
                "discount_rate",
                "revenue",
                "region",
                "source",
            ],
            "order_id",
        ),
        "returns_sample.csv": (
            [
                "order_id",
                "product_id",
                "customer_id",
                "order_date",
                "return_date",
                "product_category",
                "product_price",
                "quantity",
                "return_reason",
                "return_status",
                "days_to_return",
                "payment_method",
                "shipping_method",
                "discount_applied",
                "source",
            ],
            "order_id",
        ),
        "shipping_sample.csv": (
            [
                "shipment_id",
                "warehouse_block",
                "shipment_mode",
                "customer_care_calls",
                "customer_rating",
                "product_cost",
                "prior_purchases",
                "product_importance",
                "customer_gender",
                "discount_offered",
                "weight_grams",
                "is_delayed",
                "source",
            ],
            "shipment_id",
        ),
    }
    for output_path, frame in outputs.items():
        columns, id_column = schemas[output_path.name]
        validate_frame(output_path.name, frame, columns, id_column)
        frame.to_csv(output_path, index=False, encoding="utf-8")

    write_policies()
    eval_questions = iter_rjac_examples()
    hard_cases = build_hard_cases(eval_questions)
    validate_jsonl_records("eval_questions.jsonl", eval_questions)
    validate_jsonl_records("hard_cases.jsonl", hard_cases)
    write_jsonl(EVALUATION_DIR / "eval_questions.jsonl", eval_questions)
    write_jsonl(EVALUATION_DIR / "hard_cases.jsonl", hard_cases)

    manifest = {
        "random_seed": RANDOM_SEED,
        "files": {
            path.relative_to(PROJECT_ROOT).as_posix(): len(frame)
            for path, frame in outputs.items()
        },
        "data/evaluation/eval_questions.jsonl": len(eval_questions),
        "data/evaluation/hard_cases.jsonl": len(hard_cases),
        "policies": sorted(POLICIES),
    }
    manifest_path = RAW_DIR / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("Canonical ShopMind data created:")
    for path, count in manifest["files"].items():
        print(f"- {path}: {count} rows")
    print(f"- data/evaluation/eval_questions.jsonl: {len(eval_questions)} rows")
    print(f"- data/evaluation/hard_cases.jsonl: {len(hard_cases)} rows")
    print(f"- data/raw/policies/: {len(POLICIES)} files")
    print("- data/raw/manifest.json")


if __name__ == "__main__":
    main()
