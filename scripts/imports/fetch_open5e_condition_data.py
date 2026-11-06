import json
import time
from pathlib import Path

import httpx


API_URL = "https://api.open5e.com/v2/conditions/"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "imports" / "conditions"

DOCUMENTS = {
    "a5e-ag": {
        "edition": "a5e",
        "game_system": "a5e",
        "expected": 20,
    },
    "srd-2014": {
        "edition": "2014",
        "game_system": "5e-2014",
        "expected": 15,
    },
    "srd-2024": {
        "edition": "2024",
        "game_system": "5e-2024",
        "expected": 15,
    },
}

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

                delay = 2 ** (attempt + 1)
                print(f"  Request failed. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue

            response.raise_for_status()
            return response

        except httpx.TransportError:
            if attempt == MAX_RETRIES - 1:
                raise

            delay = 2 ** (attempt + 1)
            print(f"  Connection failed. Retrying in {delay} seconds...")
            time.sleep(delay)

    raise RuntimeError("Condition API request failed.")


def fetch_all(client):
    url = API_URL
    params = {"limit": PAGE_SIZE, "page": 1}

    records = []
    expected_count = None
    seen_keys = set()
    page_number = 0

    while url:
        response = get_with_retries(client, url, params)
        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError("Invalid conditions API response.")

        results = payload.get("results")
        if not isinstance(results, list):
            raise ValueError("Conditions response has no results list.")

        if not isinstance(payload.get("count"), int):
            raise ValueError("Conditions response has no valid count.")

        if expected_count is None:
            expected_count = payload["count"]
        elif payload["count"] != expected_count:
            raise ValueError("API count changed during pagination.")

        page_number += 1

        for record in results:
            if not isinstance(record, dict):
                raise ValueError("API returned a non-object condition.")

            key = record.get("key")
            name = record.get("name")

            if not isinstance(key, str) or not key.strip():
                raise ValueError("Condition has an invalid key.")

            if key in seen_keys:
                raise ValueError(f"Duplicate condition key: {key}")

            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"{key}: invalid condition name.")

            descriptions = record.get("descriptions")
            if not isinstance(descriptions, list):
                raise ValueError(f"{key}: missing descriptions list.")

            seen_keys.add(key)
            records.append(record)

        print(f"  Page {page_number}: {len(records)}/{expected_count}")

        url = payload.get("next")
        params = None

    if len(records) != expected_count:
        raise ValueError(
            f"API reported {expected_count} conditions, "
            f"downloaded {len(records)}."
        )

    return records


def partition_records(records):
    grouped = {
        document_key: []
        for document_key in DOCUMENTS
    }

    for record in records:
        for description in record["descriptions"]:
            document_key = description.get("document")

            if document_key not in DOCUMENTS:
                continue

            config = DOCUMENTS[document_key]

            if description.get("gamesystem") != config["game_system"]:
                raise ValueError(
                    f"{record['key']}: unexpected game system for "
                    f"{document_key}: {description.get('gamesystem')!r}"
                )

            text = description.get("desc")

            if not isinstance(text, str) or not text.strip():
                raise ValueError(
                    f"{record['key']}: empty description for "
                    f"{document_key}."
                )

            grouped[document_key].append({
                "key": record["key"],
                "name": record["name"],
                "description": text,
                "document_key": document_key,
                "game_system": config["game_system"],
            })

    for document_key, config in DOCUMENTS.items():
        document_records = grouped[document_key]
        expected = config["expected"]

        if len(document_records) != expected:
            raise ValueError(
                f"{document_key}: expected {expected} descriptions, "
                f"found {len(document_records)}."
            )

        keys = [record["key"] for record in document_records]

        if len(keys) != len(set(keys)):
            raise ValueError(
                f"{document_key}: duplicate condition keys."
            )

        document_records.sort(
            key=lambda record: (record["name"].casefold(), record["key"])
        )

    return grouped


def save_records(document_key, records):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = (
        OUTPUT_DIR / f"open5e_{document_key}_conditions.json"
    )
    temporary_path = output_path.with_suffix(".json.tmp")

    payload = {
        "count": len(records),
        "next": None,
        "previous": None,
        "results": records,
    }

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
        file.write("\n")

    temporary_path.replace(output_path)

    print(f"  Saved {output_path.relative_to(PROJECT_ROOT)}")


def main():
    print("=" * 60)
    print("OPEN5E CONDITION DATA FETCH")
    print("=" * 60)

    with httpx.Client(timeout=60.0) as client:
        records = fetch_all(client)

    print(f"\nAPI condition records: {len(records)}")

    grouped = partition_records(records)

    total = 0

    for document_key, document_records in grouped.items():
        print(f"\n{document_key}: {len(document_records)} descriptions")

        for record in document_records:
            print(f"  {record['name']}")

        save_records(document_key, document_records)
        total += len(document_records)

    if total != 50:
        raise ValueError(f"Expected 50 condition entries, found {total}.")

    print("\n" + "=" * 60)
    print(f"Total source-specific condition entries: {total}")
    print("Condition data fetch completed successfully.")


if __name__ == "__main__":
    main()
