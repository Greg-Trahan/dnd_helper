
import json
import time
from pathlib import Path

import httpx

API_URL = "https://api.open5e.com/v2/creatures/"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "imports" / "monsters"

DOCUMENTS = (
    "a5e-mm",
    "bfrd",
    "ccdx",
    "srd-2014",
    "srd-2024",
    "tdcs",
    "tob",
    "tob-2023",
    "tob2",
    "tob3",
)

PAGE_SIZE = 100


def get_with_retries(client, url, params=None, max_attempts=5):
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


def fetch_monsters(client, document_key):
    params = {
        "document__key": document_key,
        "limit": PAGE_SIZE,
        "page": 1,
        "ordering": "name",
    }

    url = API_URL
    monsters = []
    expected_count = None
    page_number = 0

    while url:
        response = get_with_retries(client, url, params)
        data = response.json()

        if "results" not in data or "count" not in data:
            raise ValueError("Unexpected Open5e API response.")

        if expected_count is None:
            expected_count = data["count"]

        elif data["count"] != expected_count:
            raise ValueError(
                f"{document_key}: API count changed during download."
            )

        page_number += 1
        page_results = data["results"]
        monsters.extend(page_results)

        print(
            f"  Page {page_number}: "
            f"{len(page_results)} downloaded "
            f"({len(monsters)}/{expected_count})"
        )

        url = data.get("next")
        params = None

    if len(monsters) != expected_count:
        raise ValueError(
            f"{document_key}: expected {expected_count}, "
            f"downloaded {len(monsters)}."
        )

    keys = []

    for monster in monsters:
        actual_document = (monster.get("document") or {}).get("key")

        if actual_document != document_key:
            raise ValueError(
                f"{monster.get('name')}: unexpected document "
                f"{actual_document}."
            )

        key = monster.get("key")

        if not key:
            raise ValueError(
                f"{document_key}: creature without external key."
            )

        keys.append(key)

    if len(keys) != len(set(keys)):
        raise ValueError(
            f"{document_key}: duplicate creature keys."
        )

    return {
        "count": expected_count,
        "next": None,
        "previous": None,
        "results": monsters,
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = 0

    with httpx.Client(timeout=60.0) as client:
        for document_key in DOCUMENTS:
            print(f"\nDownloading {document_key} creatures...")

            data = fetch_monsters(client, document_key)

            output_file = (
                OUTPUT_DIR / f"open5e_{document_key}_creatures.json"
            )
            temporary_file = output_file.with_suffix(".json.tmp")

            with temporary_file.open("w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            temporary_file.replace(output_file)

            total += data["count"]

            print(f"  Total: {data['count']}")
            print(f"  Saved: {output_file}")

    print(f"\nAll downloads completed. Total creatures: {total}")


if __name__ == "__main__":
    main()
