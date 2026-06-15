"""Translate ShopMind evaluation JSONL files from English to Vietnamese."""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_DIR = PROJECT_ROOT / "data" / "evaluation"
CACHE_PATH = EVALUATION_DIR / ".translation_cache_vi.json"
TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
SOURCE_FILES = ("eval_questions.jsonl", "hard_cases.jsonl")

PLACEHOLDER_PATTERN = re.compile(r"<[A-Z_]+>")
TERM_REPLACEMENTS = {
    "hủy bỏ và trả hàng": "hủy đơn và đổi trả",
    "đăng nhập và tài khoản": "đăng nhập và tài khoản",
    "vận chuyển": "giao hàng",
    "nhân viên hỗ trợ": "nhân viên chăm sóc khách hàng",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_cache() -> dict[str, str]:
    if not CACHE_PATH.exists():
        return {}
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))


def save_cache(cache: dict[str, str]) -> None:
    temporary_path = CACHE_PATH.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(CACHE_PATH)


def protect_placeholders(text: str) -> tuple[str, dict[str, str]]:
    replacements: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        token = f"SHOPMINDTOKEN{len(replacements)}"
        replacements[token] = match.group(0)
        return token

    return PLACEHOLDER_PATTERN.sub(replace, text), replacements


def restore_placeholders(text: str, replacements: dict[str, str]) -> str:
    for token, placeholder in replacements.items():
        text = re.sub(re.escape(token), placeholder, text, flags=re.IGNORECASE)
    return text


def normalize_translation(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    for original, replacement in TERM_REPLACEMENTS.items():
        text = re.sub(
            re.escape(original),
            replacement,
            text,
            flags=re.IGNORECASE,
        )
    return text


def translate_text(text: str, timeout: int = 30) -> str:
    protected_text, placeholders = protect_placeholders(text)
    query = urlencode(
        {
            "client": "gtx",
            "sl": "en",
            "tl": "vi",
            "dt": "t",
            "q": protected_text,
        }
    )
    request = Request(
        f"{TRANSLATE_URL}?{query}",
        headers={"User-Agent": "ShopMind-RAG/1.0"},
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    translated = "".join(part[0] for part in payload[0] if part[0])
    return normalize_translation(restore_placeholders(translated, placeholders))


def get_translation(
    text: str,
    cache: dict[str, str],
    retries: int,
) -> str:
    if not text:
        return text
    if text in cache:
        return cache[text]

    for attempt in range(retries):
        try:
            translated = translate_text(text)
            if not translated:
                raise ValueError("Translation service returned empty text.")
            cache[text] = translated
            return translated
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("Translation retries exhausted.")


def collect_translatable_texts(
    datasets: dict[str, list[dict[str, Any]]],
) -> list[str]:
    texts: set[str] = set()
    for records in datasets.values():
        for record in records:
            texts.add(record["question"])
            texts.add(record["reference_answer"])
            texts.add(record["category"])
            texts.add(record["difficulty"])
            for value in record["metadata"].values():
                if isinstance(value, str):
                    texts.add(value)
            if isinstance(record.get("hard_case_reason"), str):
                texts.add(record["hard_case_reason"])
    return sorted(texts)


def translate_record(
    record: dict[str, Any],
    cache: dict[str, str],
) -> dict[str, Any]:
    translated = dict(record)
    translated["question_en"] = record["question"]
    translated["reference_answer_en"] = record["reference_answer"]
    translated["question"] = cache[record["question"]]
    translated["reference_answer"] = cache[record["reference_answer"]]
    translated["category_en"] = record["category"]
    translated["category"] = cache[record["category"]]
    translated["difficulty_en"] = record["difficulty"]
    translated["difficulty"] = cache[record["difficulty"]]
    translated["language"] = "vi"

    metadata = {}
    for key, value in record["metadata"].items():
        metadata[key] = cache[value] if isinstance(value, str) else value
    translated["metadata"] = metadata

    if isinstance(record.get("hard_case_reason"), str):
        translated["hard_case_reason_en"] = record["hard_case_reason"]
        translated["hard_case_reason"] = cache[record["hard_case_reason"]]
    return translated


def validate_translation(
    source: list[dict[str, Any]],
    translated: list[dict[str, Any]],
) -> None:
    if len(source) != len(translated):
        raise ValueError("Translated file has a different row count.")
    if [row["id"] for row in source] != [row["id"] for row in translated]:
        raise ValueError("Translated file changed record IDs or ordering.")
    for row in translated:
        if not row["question"] or not row["reference_answer"]:
            raise ValueError(f"Record {row['id']} has empty translated text.")
        expected_placeholders = set(
            PLACEHOLDER_PATTERN.findall(
                f"{row['question_en']} {row['reference_answer_en']}"
            )
        )
        actual_placeholders = set(
            PLACEHOLDER_PATTERN.findall(
                f"{row['question']} {row['reference_answer']}"
            )
        )
        if expected_placeholders != actual_placeholders:
            raise ValueError(f"Record {row['id']} changed protected placeholders.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--save-every", type=int, default=25)
    parser.add_argument("--delay", type=float, default=0.05)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    datasets = {
        filename: read_jsonl(EVALUATION_DIR / filename)
        for filename in SOURCE_FILES
    }
    cache = load_cache()
    texts = collect_translatable_texts(datasets)
    pending = [text for text in texts if text not in cache]

    print(f"Unique texts: {len(texts)}")
    print(f"Already cached: {len(texts) - len(pending)}")
    print(f"Pending: {len(pending)}")

    for index, text in enumerate(pending, start=1):
        get_translation(text, cache, args.retries)
        if index % args.save_every == 0:
            save_cache(cache)
            print(f"Translated {index}/{len(pending)} pending texts")
        time.sleep(args.delay)
    save_cache(cache)

    for filename, records in datasets.items():
        translated = [translate_record(record, cache) for record in records]
        validate_translation(records, translated)
        output_path = EVALUATION_DIR / filename.replace(".jsonl", "_vi.jsonl")
        write_jsonl(output_path, translated)
        print(f"Created {output_path.relative_to(PROJECT_ROOT)}: {len(translated)} rows")


if __name__ == "__main__":
    main()
