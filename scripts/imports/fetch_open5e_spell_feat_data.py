import json
import time
from pathlib import Path

import httpx


API_BASE = "https://api.open5e.com/v2"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "imports"

EDITIONS = {
    "srd-2014": "2014",
    "srd-2024": "2024",
}

RESOURCES = ("spells", "feats")

PAGE_SIZE = 100


def get_with_retries(client, url, params=None, max_attempts=5):
    """Retry temporary network and server errors."""

    for attempt in range(max_attempts):
        try:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as error:
            if error.response.status_code not in (429, 500, 502, 503, 504):
                raise

            if attempt == max_attempts - 1:
                raise

        except httpx.TransportError:
            if attempt == max_attempts - 1:
                raise

        delay = 2 ** (attempt + 1)
        print(f"  Request failed. Retrying in {delay} seconds...")
        time.sleep(delay)


def fetch_records(client, resource, source_key):
    """Retrieve every page of one resource for one SRD edition."""

    url = f"{API_BASE}/{resource}/"

    params = {
        "document__key": source_key,
        "limit": PAGE_SIZE,
        "page": 1,
        "ordering": "name",
    }

    records = []
    expected_count = None
    page_number = 0

    while url:
        response = get_with_retries(client, url, params)
        data = response.json()

        if "results" not in data or "count" not in data:
            raise ValueError(
                f"Unexpected Open5e response for {resource}"
            )

        if expected_count is None:
            expected_count = data["count"]

        page_number += 1
        page_results = data["results"]
        records.extend(page_results)

        print(
            f"  Page {page_number}: "
            f"downloaded {len(page_results)} {resource} "
            f"({len(records)}/{expected_count})"
        )

        url = data.get("next")
        params = None

    if len(records) != expected_count:
        raise ValueError(
            f"Expected {expected_count} {resource}, "
            f"but downloaded {len(records)}"
        )

    # Verify edition and source identifiers.
    for record in records:
        actual_key = (record.get("document") or {}).get("key")

        if actual_key != source_key:
            raise ValueError(
                f"Unexpected document key {actual_key} "
                f"for {record.get('name')}"
            )

    keys = [record.get("key") for record in records]

    if None in keys or len(keys) != len(set(keys)):
        raise ValueError(
            f"Missing or duplicate keys found in {resource}"
        )

    return {
        "count": expected_count,
        "next": None,
        "previous": None,
        "results": records,
    }


def main():
    with httpx.Client(timeout=60.0) as client:

        for resource in RESOURCES:
            resource_dir = OUTPUT_DIR / resource
            resource_dir.mkdir(parents=True, exist_ok=True)

            for source_key, edition in EDITIONS.items():
                print(f"\nDownloading {resource} — {edition}...")

                data = fetch_records(
                    client,
                    resource,
                    source_key,
                )

                output_file = (
                    resource_dir / f"open5e_{edition}.json"
                )

                temporary_file = output_file.with_suffix(
                    ".json.tmp"
                )

                with temporary_file.open(
                    "w", encoding="utf-8"
                ) as file:
                    json.dump(
                        data,
                        file,
                        indent=2,
                        ensure_ascii=False,
                    )

                temporary_file.replace(output_file)

                print(f"Total records: {data['count']}")
                print(f"Saved to: {output_file}")

    print("\nAll downloads completed successfully.")


if __name__ == "__main__":
    main()
