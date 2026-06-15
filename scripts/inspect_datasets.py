from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = PROJECT_ROOT / "data" / "external"


def inspect_csv_file(csv_path: Path) -> None:
    print("\n" + "=" * 100)
    print(f"FILE: {csv_path.relative_to(PROJECT_ROOT)}")
    print("=" * 100)

    try:
        df = pd.read_csv(csv_path)
    except Exception as exc:
        print(f"[ERROR] Cannot read CSV: {exc}")
        return

    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print("\nSample rows:")

    if len(df) == 0:
        print("[EMPTY FILE]")
        return

    sample = df.head(3)

    for idx, row in sample.iterrows():
        print(f"\n--- Row {idx} ---")
        for col in df.columns:
            value = str(row[col])
            if len(value) > 300:
                value = value[:300] + "..."
            print(f"{col}: {value}")


def main() -> None:
    print(f"Scanning external datasets at: {EXTERNAL_DIR}")

    csv_files = list(EXTERNAL_DIR.rglob("*.csv"))

    if not csv_files:
        print("No CSV files found.")
        return

    for csv_path in csv_files:
        inspect_csv_file(csv_path)


if __name__ == "__main__":
    main()