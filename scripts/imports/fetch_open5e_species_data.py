
import json
import time
from pathlib import Path

import httpx


API_BASE = "https://api.open5e.com/v2"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "imports" / "species"

DOCUMENTS = {
    "open5e": ("2014", 1),
    "srd-2014": ("2014", 13),
    "srd-2024": ("2024", 9),
    "toh": ("2014", 40),
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

    raise RuntimeError(f"Request failed: {url}")


def fetch_species(client, document_key, expected_count):
    url = f"{API_BASE}/species/"
    params = {
        "document__key": document_key,
        "limit": PAGE_SIZE,
        "ordering": "name",
    }

    records = []
    expected_api_count = None
    seen_keys = set()

    while url:
        response = get_with_retries(client, url, params)
        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError(
                f"{document_key}: invalid API response."
            )

        if "count" not in payload or not isinstance(
            payload.get("results"), list
        ):
            raise ValueError(
                f"{document_key}: unexpected API response structure."
            )

        if expected_api_count is None:
            expected_api_count = payload["count"]
        elif payload["count"] != expected_api_count:
            raise ValueError(
                f"{document_key}: API count changed during pagination."
            )

        for record in payload["results"]:
            document = record.get("document") or {}

            if document.get("key") != document_key:
                raise ValueError(
                    f"Unexpected document in record {record.get('key')}."
                )

            key = record.get("key")

            if not isinstance(key, str) or not key:
                raise ValueError("Species record is missing its key.")

            if key in seen_keys:
                raise ValueError(f"Duplicate species key: {key}")

            if not isinstance(record.get("is_subspecies"), bool):
                raise ValueError(f"{key}: invalid is_subspecies value.")

            if not isinstance(record.get("traits"), list):
                raise ValueError(f"{key}: traits must be a list.")

            seen_keys.add(key)
            records.append(record)

        url = payload.get("next")
        params = None

    if len(records) != expected_api_count:
        raise ValueError(
            f"{document_key}: API reported {expected_api_count} records, "
            f"but downloaded {len(records)}."
        )

    if len(records) != expected_count:
        raise ValueError(
            f"{document_key}: expected {expected_count} records, "
            f"received {len(records)}."
        )

    return {
        "count": len(records),
        "next": None,
        "previous": None,
        "results": records,
    }


def save_records(document_key, payload):
    output_path = OUTPUT_DIR / f"open5e_{document_key}.json"
    temporary_path = output_path.with_suffix(".json.tmp")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
        file.write("\n")

    temporary_path.replace(output_path)

    print(
        f"  {output_path.name}: "
        f"{payload['count']} records saved."
    )


def main():
    print("Fetching Open5e species data...")

    with httpx.Client(timeout=60.0) as client:
        for document_key, (edition, expected_count) in DOCUMENTS.items():
            print(f"\nFetching {document_key} ({edition})...")

            payload = fetch_species(
                client,
                document_key,
                expected_count,
            )

            base_count = sum(
                not record["is_subspecies"]
                for record in payload["results"]
            )
            variant_count = sum(
                record["is_subspecies"]
                for record in payload["results"]
            )

            print(f"  Total:      {payload['count']}")
            print(f"  Base:       {base_count}")
            print(f"  Subspecies: {variant_count}")

            save_records(document_key, payload)

    print("\nSpecies data fetch completed successfully.")


if __name__ == "__main__":
    main()
