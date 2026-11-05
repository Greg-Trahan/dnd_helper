import json
import time
from pathlib import Path

import httpx

API_URL = "https://api.open5e.com/v2/creatures/"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "imports" / "monsters"

EDITIONS = {
    "srd-2014": "2014",
    "srd-2024": "2024",
}

PAGE_SIZE = 100


def fetch_monsters(client, source_key):
    """Retrieve every page of monsters for one SRD edition."""

    params = {
        "document__key": source_key,
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
        response.raise_for_status()

        data = response.json()

        if "results" not in data or "count" not in data:
            raise ValueError("Unexpected Open5e API response format")

        if expected_count is None:
            expected_count = data["count"]

        page_number += 1
        page_results = data["results"]

        monsters.extend(page_results)

        print(
            f"  Page {page_number}: "
            f"downloaded {len(page_results)} monsters "
            f"({len(monsters)}/{expected_count})"
        )

        # The API supplies the complete URL for the next page.
        url = data.get("next")
        params = None

    if len(monsters) != expected_count:
        raise ValueError(
            f"Expected {expected_count} monsters, "
            f"but downloaded {len(monsters)}"
        )

    # Verify that every record belongs to the requested edition.
    for monster in monsters:
        actual_key = (monster.get("document") or {}).get("key")
        if actual_key != source_key:
            raise ValueError(
                f"Unexpected document key {actual_key} "
                f"for monster {monster.get('name')}"
            )

    # Verify that the API did not return duplicate creature keys.
    keys = [monster.get("key") for monster in monsters]

    if len(keys) != len(set(keys)):
        raise ValueError(f"Duplicate monster keys found for {source_key}")

    return {
        "count": expected_count,
        "next": None,
        "previous": None,
        "results": monsters,
    }

def get_with_retries(client, url, params=None, max_attempts=5):
    """Retry temporary network and server errors."""

    for attempt in range(max_attempts):
        try:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as error:
            # Retry rate limits and temporary server errors.
            if error.response.status_code not in (429, 500, 502, 503, 504):
                raise

            if attempt == max_attempts - 1:
                raise

        except httpx.TransportError:
            # Includes connection resets and other transport failures.
            if attempt == max_attempts - 1:
                raise

        delay = 2 ** (attempt + 1)
        print(f"  Request failed. Retrying in {delay} seconds...")
        time.sleep(delay)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=60.0) as client:
        for source_key, edition in EDITIONS.items():
            print(f"\nDownloading {edition} monsters...")

            data = fetch_monsters(client, source_key)

            output_file = OUTPUT_DIR / f"open5e_{edition}.json"
            temporary_file = OUTPUT_DIR / f"open5e_{edition}.json.tmp"

            with temporary_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)

            # Replace the previous full dataset only after a successful download.
            temporary_file.replace(output_file)

            print(f"Total monsters: {data['count']}")
            print(f"Saved to: {output_file}")

    print("\nAll downloads completed successfully.")


if __name__ == "__main__":
    main()
