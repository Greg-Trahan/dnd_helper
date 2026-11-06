
import json
import time
from pathlib import Path

import httpx


API_BASE = "https://api.open5e.com/v2"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "imports"

SPELL_DOCUMENTS = {
    "a5e-ag": ("a5e", 371),
    "deepm": ("2014", 515),
    "deepmx": ("2014", 64),
    "kp": ("2014", 31),
    "open5e": ("2014", 2),
    "spells-that-dont-suck": ("2014", 180),
    "srd-2014": ("2014", 319),
    "srd-2024": ("2024", 339),
    "toh": ("2014", 91),
    "wz": ("2014", 43),
}

FEAT_DOCUMENTS = {
    "a5e-ag": ("a5e", 59),
    "srd-2014": ("2014", 1),
    "srd-2024": ("2024", 17),
    "toh": ("2014", 13),
}

CLASS_DOCUMENTS = {
    "a5e-ag": ("a5e", 1, 3),
    "bfrd": ("2014", 1, 1),
    "open5e": ("2014", 0, 17),
    "srd-2014": ("2014", 12, 12),
    "srd-2024": ("2024", 12, 12),
    "tdcs": ("2014", 0, 4),
    "toh": ("2014", 0, 76),
}

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


def fetch_records(client, resource, source_key, extra_params=None):
    url = f"{API_BASE}/{resource}/"

    params = {
        "document__key": source_key,
        "limit": PAGE_SIZE,
        "page": 1,
        "ordering": "name",
    }

    if extra_params:
        params.update(extra_params)

    records = []
    expected_count = None
    page_number = 0

    while url:
        response = get_with_retries(client, url, params)
        data = response.json()

        if "results" not in data or "count" not in data:
            raise ValueError(
                f"Unexpected Open5e response for {resource}/{source_key}"
            )

        if expected_count is None:
            expected_count = data["count"]
        elif data["count"] != expected_count:
            raise ValueError(
                f"Inconsistent record count for {resource}/{source_key}"
            )

        page_number += 1
        records.extend(data["results"])

        print(f"  Page {page_number}: {len(records)}/{expected_count}")

        url = data.get("next")
        params = None

    if len(records) != expected_count:
        raise ValueError(
            f"{resource}/{source_key}: expected {expected_count}, "
            f"downloaded {len(records)}"
        )

    keys = []

    for record in records:
        document = record.get("document") or {}

        if document.get("key") != source_key:
            raise ValueError(
                f"Unexpected document {document.get('key')} "
                f"for {record.get('name')}"
            )

        keys.append(record.get("key"))

    if None in keys or len(keys) != len(set(keys)):
        raise ValueError(
            f"Missing or duplicate keys in {resource}/{source_key}"
        )

    return {
        "count": expected_count,
        "next": None,
        "previous": None,
        "results": records,
    }


def save_records(resource_dir, filename, data):
    resource_dir.mkdir(parents=True, exist_ok=True)

    output_file = resource_dir / filename
    temporary_file = output_file.with_suffix(".json.tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    temporary_file.replace(output_file)

    print(f"Total records: {data['count']}")
    print(f"Saved to: {output_file}")


def fetch_and_save_feats(client, source_key, edition, expected_count):
    print(f"\nDownloading feats — {source_key}...")

    data = fetch_records(client, "feats", source_key)

    if data["count"] != expected_count:
        raise ValueError(
            f"{source_key}: expected {expected_count} feats, "
            f"received {data['count']}"
        )

    save_records(
        OUTPUT_DIR / "feats",
        f"open5e_{source_key}.json",
        data,
    )


def fetch_and_save_spells(client, source_key, edition, expected_count):
    print(f"\nDownloading spells — {source_key}...")

    data = fetch_records(client, "spells", source_key)

    if data["count"] != expected_count:
        raise ValueError(
            f"{source_key}: expected {expected_count} spells, "
            f"received {data['count']}"
        )

    save_records(
        OUTPUT_DIR / "spells",
        f"open5e_{source_key}.json",
        data,
    )


def fetch_and_save_classes(
    client,
    source_key,
    edition,
    resource_name,
    is_subclass,
    expected_count,
):
    print(f"\nDownloading {resource_name} — {source_key}...")

    data = fetch_records(
        client,
        "classes",
        source_key,
        extra_params={
            "is_subclass": str(is_subclass).lower(),
        },
    )

    if data["count"] != expected_count:
        raise ValueError(
            f"{source_key}: expected {expected_count} {resource_name}, "
            f"received {data['count']}"
        )

    suffix = "subclasses" if is_subclass else "classes"

    save_records(
        OUTPUT_DIR / "classes",
        f"open5e_{source_key}_{suffix}.json",
        data,
    )


def main():
    with httpx.Client(timeout=60.0) as client:

        # Download feats from all four source documents.
        for source_key, (edition, expected_count) in FEAT_DOCUMENTS.items():
            fetch_and_save_feats(
                client,
                source_key,
                edition,
                expected_count,
            )

        # Download spells from all ten source documents.
        for source_key, (edition, expected_count) in SPELL_DOCUMENTS.items():
            fetch_and_save_spells(
                client,
                source_key,
                edition,
                expected_count,
            )

        # Download all class and subclass documents.
        for source_key, (
            edition,
            expected_classes,
            expected_subclasses,
        ) in CLASS_DOCUMENTS.items():

            fetch_and_save_classes(
                client,
                source_key,
                edition,
                "classes",
                False,
                expected_classes,
            )

            fetch_and_save_classes(
                client,
                source_key,
                edition,
                "subclasses",
                True,
                expected_subclasses,
            )

    print("\nAll downloads completed successfully.")


if __name__ == "__main__":
    main()
