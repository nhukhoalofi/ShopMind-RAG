"""
scripts/download_datasets.py

Download external datasets for ShopMind RAG.

This script downloads:
1. Hugging Face datasets
2. Kaggle datasets

Output folder:
data/external/

Important:
- Do not push large raw datasets to GitHub.
- Check dataset licenses before publishing data.
- Some Hugging Face datasets may require login or access approval.
- Kaggle requires kaggle.json configured.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

import pandas as pd
from datasets import DatasetDict, Dataset, load_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = PROJECT_ROOT / "data" / "external"


HF_DATASETS = {
    "qgyd_ecommerce_customer_service": {
        "hf_id": "qgyd2021/e_commerce_customer_service",
        "description": "Core e-commerce customer service knowledge base",
    },
    "maktek_customer_support_faqs": {
        "hf_id": "MakTek/Customer_support_faqs_dataset",
        "description": "Customer support FAQ dataset",
    },
    "rjac_ecommerce_support_qa": {
        "hf_id": "rjac/e-commerce-customer-support-qa",
        "description": "E-commerce customer support conversations and scenarios",
    },
    "csconda_vietnamese_customer_support": {
        "hf_id": "ura-hcmut/Vietnamese-Customer-Support-QA",
        "description": "Vietnamese customer support QA dataset",
    },
}


KAGGLE_DATASETS = {
    "synthetic_ecommerce": {
        "slug": "imranalishahh/comprehensive-synthetic-e-commerce-dataset",
        "description": "Synthetic e-commerce product/order/customer data",
    },
    "synthetic_returns": {
        "slug": "sayalikhot21/synthetic-dataset-for-e-commerce-return-analysis",
        "description": "Synthetic e-commerce return/refund data",
    },
    "shipping_data": {
        "slug": "prachi13/customer-analytics",
        "description": "E-commerce shipping/customer analytics data",
    },
}


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def object_to_json_string(value: Any) -> Any:
    """
    Convert list/dict objects to JSON strings before saving to CSV.
    This prevents pandas from writing unreadable Python object formats.
    """
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def save_split_to_csv(dataset: Dataset, output_path: Path) -> None:
    """
    Save a Hugging Face Dataset split to CSV safely.
    Nested/list/dict columns are serialized to JSON strings.
    """
    df = dataset.to_pandas()

    for col in df.columns:
        df[col] = df[col].apply(object_to_json_string)

    df.to_csv(output_path, index=False, encoding="utf-8-sig")


def save_hf_dataset(dataset_name: str, hf_id: str, output_dir: Path) -> None:
    """
    Download one Hugging Face dataset and save it in two formats:
    1. Hugging Face native format: hf_disk/
    2. CSV files by split: csv/
    """
    ensure_directory(output_dir)

    print("\n" + "=" * 80)
    print(f"Downloading Hugging Face dataset: {hf_id}")
    print(f"Target folder: {output_dir}")
    print("=" * 80)

    try:
        dataset = load_dataset(hf_id)
    except Exception as exc:
        print(f"[FAILED] Could not download {hf_id}")
        print(f"Reason: {exc}")
        print("")
        print("Possible fixes:")
        print("1. Check your internet connection.")
        print("2. Run: huggingface-cli login")
        print("3. Open the dataset page and accept access conditions if required.")
        print("4. Check if the dataset name has changed.")
        return

    hf_disk_dir = output_dir / "hf_disk"
    csv_dir = output_dir / "csv"
    ensure_directory(csv_dir)

    try:
        dataset.save_to_disk(str(hf_disk_dir))
        print(f"[OK] Saved Hugging Face disk format: {hf_disk_dir}")
    except Exception as exc:
        print(f"[WARNING] Could not save HF disk format for {hf_id}: {exc}")

    try:
        if isinstance(dataset, DatasetDict):
            for split_name, split_dataset in dataset.items():
                csv_path = csv_dir / f"{split_name}.csv"
                save_split_to_csv(split_dataset, csv_path)
                print(f"[OK] Saved CSV split: {csv_path}")

        elif isinstance(dataset, Dataset):
            csv_path = csv_dir / "data.csv"
            save_split_to_csv(dataset, csv_path)
            print(f"[OK] Saved CSV: {csv_path}")

        else:
            print(f"[WARNING] Unsupported dataset type for CSV export: {type(dataset)}")

    except Exception as exc:
        print(f"[WARNING] Could not export CSV for {hf_id}: {exc}")

    metadata = {
        "dataset_name": dataset_name,
        "hf_id": hf_id,
        "source": "huggingface",
        "output_dir": str(output_dir),
    }

    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[OK] Saved metadata: {metadata_path}")


def get_kaggle_command() -> list[str] | None:
    """
    Find Kaggle CLI command.
    """
    kaggle_path = shutil.which("kaggle")

    if kaggle_path:
        return [kaggle_path]

    # Fallback: try python -m kaggle
    return [sys.executable, "-m", "kaggle"]


def download_kaggle_dataset(dataset_name: str, slug: str, output_dir: Path) -> None:
    """
    Download and unzip a Kaggle dataset into the target folder.
    """
    ensure_directory(output_dir)

    print("\n" + "=" * 80)
    print(f"Downloading Kaggle dataset: {slug}")
    print(f"Target folder: {output_dir}")
    print("=" * 80)

    kaggle_cmd = get_kaggle_command()

    command = kaggle_cmd + [
        "datasets",
        "download",
        "-d",
        slug,
        "-p",
        str(output_dir),
        "--unzip",
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            capture_output=True,
        )

        if result.stdout:
            print(result.stdout)

        print(f"[OK] Downloaded and unzipped Kaggle dataset: {slug}")

    except subprocess.CalledProcessError as exc:
        print(f"[FAILED] Could not download Kaggle dataset: {slug}")
        print("Command:")
        print(" ".join(command))
        print("")
        print("STDOUT:")
        print(exc.stdout)
        print("")
        print("STDERR:")
        print(exc.stderr)
        print("")
        print("Possible fixes:")
        print("1. Install Kaggle API: pip install kaggle")
        print("2. Create Kaggle API token from your Kaggle account.")
        print("3. Put kaggle.json in: C:\\Users\\<YourName>\\.kaggle\\kaggle.json")
        print("4. Or set KAGGLE_USERNAME and KAGGLE_KEY environment variables.")
        print("5. Open the dataset page and accept terms if required.")
        return

    except Exception as exc:
        print(f"[FAILED] Unexpected error while downloading {slug}: {exc}")
        return

    metadata = {
        "dataset_name": dataset_name,
        "kaggle_slug": slug,
        "source": "kaggle",
        "output_dir": str(output_dir),
    }

    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[OK] Saved metadata: {metadata_path}")


def download_huggingface_datasets() -> None:
    for folder_name, info in HF_DATASETS.items():
        output_dir = EXTERNAL_DIR / folder_name
        save_hf_dataset(
            dataset_name=folder_name,
            hf_id=info["hf_id"],
            output_dir=output_dir,
        )


def download_kaggle_datasets() -> None:
    for folder_name, info in KAGGLE_DATASETS.items():
        output_dir = EXTERNAL_DIR / folder_name
        download_kaggle_dataset(
            dataset_name=folder_name,
            slug=info["slug"],
            output_dir=output_dir,
        )


def create_external_folders() -> None:
    ensure_directory(EXTERNAL_DIR)

    for folder_name in HF_DATASETS.keys():
        ensure_directory(EXTERNAL_DIR / folder_name)

    for folder_name in KAGGLE_DATASETS.keys():
        ensure_directory(EXTERNAL_DIR / folder_name)


def print_summary() -> None:
    print("\n" + "=" * 80)
    print("Download summary")
    print("=" * 80)

    for folder in sorted(EXTERNAL_DIR.iterdir()):
        if folder.is_dir():
            files = list(folder.rglob("*"))
            file_count = len([item for item in files if item.is_file()])
            print(f"{folder.name}: {file_count} files")

    print("\nExternal data folder:")
    print(EXTERNAL_DIR)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download external datasets for ShopMind RAG."
    )

    parser.add_argument(
        "--hf-only",
        action="store_true",
        help="Download Hugging Face datasets only.",
    )

    parser.add_argument(
        "--kaggle-only",
        action="store_true",
        help="Download Kaggle datasets only.",
    )

    parser.add_argument(
        "--create-folders-only",
        action="store_true",
        help="Only create external data folders without downloading datasets.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("Project root:", PROJECT_ROOT)
    print("External data dir:", EXTERNAL_DIR)

    create_external_folders()

    if args.create_folders_only:
        print("[OK] Created external folders only.")
        print_summary()
        return

    if args.hf_only and args.kaggle_only:
        raise ValueError("Use either --hf-only or --kaggle-only, not both.")

    if args.hf_only:
        download_huggingface_datasets()
        print_summary()
        return

    if args.kaggle_only:
        download_kaggle_datasets()
        print_summary()
        return

    download_huggingface_datasets()
    download_kaggle_datasets()
    print_summary()


if __name__ == "__main__":
    main()