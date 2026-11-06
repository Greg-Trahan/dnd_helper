import json
import time
from pathlib import Path

import httpx


API_BASE = "https://api.open5e.com/v2"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "imports" / "equipment"

DOCUMENTS = {
    "srd-2014": {
        "edition": "2014",
        "game_system": "5e-2014",
        "items": 237,
        "weapons": 37,
        "armor": 12,
    },
    "srd-2024": {
        "edition": "2024",
        "game_system": "5e-2024",
        "items": 203,
        "weapons": 38,
        "armor": 13,
    },
}

RESOURCES = ("items", "weapons", "armor")
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


def fetch_resource(client, resource):
    """Fetch an entire resource without document filters."""

    url = f"{API_BASE}/{resource}/"
    params = {
        "limit": PAGE_SIZE,
        "page": 1,
        "ordering": "name",
    }

    records = []
    expected_api_count = None
    seen_keys = set()
    page_number = 0

    while url:
        response = get_with_retries(client, url, params)
        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError(f"{resource}: invalid API response.")

        if not isinstance(payload.get("results"), list):
            raise ValueError(f"{resource}: missing results list.")

        if not isinstance(payload.get("count"), int):
            raise ValueError(f"{resource}: missing valid count.")

        if expected_api_count is None:
            expected_api_count = payload["count"]
        elif payload["count"] != expected_api_count:
            raise ValueError(
                f"{resource}: API count changed during pagination."
            )

        page_number += 1

        for record in payload["results"]:
            if not isinstance(record, dict):
                raise ValueError(
                    f"{resource}: response contains a non-object record."
                )

            key = record.get("key")
            name = record.get("name")
            document = record.get("document") or {}
            document_key = document.get("key")

            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"{resource}: record has no valid key.")

            if key in seen_keys:
                raise ValueError(
                    f"{resource}: duplicate record key {key}."
                )

            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"{resource}/{key}: invalid name.")

            if document_key not in DOCUMENTS:
                raise ValueError(
                    f"{resource}/{key}: unexpected document "
                    f"{document_key!r}."
                )

            config = DOCUMENTS[document_key]
            game_system = document.get("gamesystem") or {}

            if game_system.get("key") != config["game_system"]:
                raise ValueError(
                    f"{resource}/{key}: unexpected game system "
                    f"{game_system.get('key')!r}."
                )

            seen_keys.add(key)
            records.append(record)

        print(
            f"  Page {page_number}: "
            f"{len(records)}/{expected_api_count}"
        )

        url = payload.get("next")
        params = None

    if len(records) != expected_api_count:
        raise ValueError(
            f"{resource}: API reported {expected_api_count}, "
            f"downloaded {len(records)}."
        )

    return records


def save_records(resource, document_key, records):
    output_dir = OUTPUT_DIR / resource
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"open5e_{document_key}.json"
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
    print("OPEN5E EQUIPMENT DATA FETCH")
    print("=" * 60)

    totals = {
        document_key: {
            resource: 0
            for resource in RESOURCES
        }
        for document_key in DOCUMENTS
    }

    with httpx.Client(timeout=60.0) as client:
        for resource in RESOURCES:
            print(f"\nFetching {resource}...")

            records = fetch_resource(client, resource)

            grouped = {
                document_key: []
                for document_key in DOCUMENTS
            }

            for record in records:
                document_key = record["document"]["key"]
                grouped[document_key].append(record)

            for document_key, config in DOCUMENTS.items():
                document_records = grouped[document_key]
                expected = config[resource]

                print(
                    f"  {document_key}: "
                    f"{len(document_records)} records"
                )

                if len(document_records) != expected:
                    raise ValueError(
                        f"{resource}/{document_key}: expected "
                        f"{expected} records, found "
                        f"{len(document_records)}."
                    )

                totals[document_key][resource] = len(document_records)

                save_records(
                    resource,
                    document_key,
                    document_records,
                )

    print("\n" + "=" * 60)
    print("FETCH SUMMARY")
    print("=" * 60)

    grand_total = 0

    for document_key, counts in totals.items():
        total = sum(counts.values())
        grand_total += total

        print(
            f"{document_key}: "
            f"items={counts['items']}, "
            f"weapons={counts['weapons']}, "
            f"armor={counts['armor']}, "
            f"total={total}"
        )

    print("-" * 60)
    print(f"Total records: {grand_total}")

    if grand_total != 540:
        raise ValueError(
            f"Expected 540 total records, found {grand_total}."
        )

    print("\nEquipment data fetch completed successfully.")


if __name__ == "__main__":
    main()
