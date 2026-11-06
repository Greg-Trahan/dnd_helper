
import json
import time
from pathlib import Path

import httpx


API_BASE = "https://api.open5e.com/v2"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "imports" / "backgrounds"

DOCUMENTS = (
    "a5e-ag",
    "a5e-ddg",
    "a5e-gpg",
    "open5e",
    "srd-2014",
    "srd-2024",
    "tdcs",
    "toh",
)

PAGE_SIZE = 100
MAX_RETRIES = 5
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def get_with_retries(client, url, params=None):
    for attempt in range(MAX_RETRIES):
        try:
            response = client.get(url, params=params)

            if response.status_code in RETRYABLE_STATUS_CODES:
                if attempt == MAX_RETRIES - 1:
                    response.raise_for_status()
                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            return response

        except httpx.TransportError:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(2 ** attempt)

    raise RuntimeError(f"Request failed: {url}")


def fetch_backgrounds(client, document_key):
    url = f"{API_BASE}/backgrounds/"
    params = {
        "document__key": document_key,
        "limit": PAGE_SIZE,
        "ordering": "name",
    }

    records = []
    expected_count = None
    seen_keys = set()

    while url:
        response = get_with_retries(client, url, params)
        payload = response.json()

        if expected_count is None:
            expected_count = payload["count"]
        elif payload["count"] != expected_count:
            raise ValueError(
                f"{document_key}: API count changed during pagination."
            )

        for record in payload["results"]:
            if record.get("document", {}).get("key") != document_key:
                raise ValueError(
                    f"Unexpected document for {record.get('key')}."
                )

            key = record.get("key")

            if not key or key in seen_keys:
                raise ValueError(f"Missing or duplicate background key: {key}")

            if not isinstance(record.get("benefits"), list):
                raise ValueError(f"{key}: benefits must be a list.")

            seen_keys.add(key)
            records.append(record)

        url = payload.get("next")
        params = None

    if len(records) != expected_count:
        raise ValueError(
            f"{document_key}: expected {expected_count}, "
            f"received {len(records)}."
        )

    return {
        "count": len(records),
        "next": None,
        "previous": None,
        "results": records,
    }


def save_records(document_key, payload):
    output_path = (
        OUTPUT_DIR / f"open5e_{document_key}_backgrounds.json"
    )
    temporary_path = output_path.with_suffix(".json.tmp")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
        file.write("\n")

    temporary_path.replace(output_path)

    print(f"{output_path.name}: {payload['count']} records saved.")


def main():
    print("Fetching Open5e background data...")

    total = 0

    with httpx.Client(timeout=30) as client:
        for document_key in DOCUMENTS:
            print(f"\nFetching {document_key}...")
            payload = fetch_backgrounds(client, document_key)

            print(f"  Total: {payload['count']}")

            for record in payload["results"]:
                print(
                    f"  - {record['name']} "
                    f"({len(record['benefits'])} benefits)"
                )

            save_records(document_key, payload)
            total += payload["count"]

    if total != 58:
        raise ValueError(
            f"Expected 58 backgrounds across all documents; got {total}."
        )

    print(f"\nBackground data fetch completed: {total} records.")


if __name__ == "__main__":
    main()
