
import argparse
import json
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
INPUT_DIR = PROJECT_ROOT / "data" / "imports" / "conditions"

sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models.condition import Condition
from app.models.edition import Edition
from app.models.source import Source


DOCUMENTS = {
    "a5e-ag": {
        "edition": "a5e",
        "game_system": "a5e",
        "source_name": "Adventurer's Guide",
        "expected_count": 20,
        "filename": "open5e_a5e-ag_conditions.json",
    },
    "srd-2014": {
        "edition": "2014",
        "game_system": "5e-2014",
        "source_name": "System Reference Document 5.1",
        "expected_count": 15,
        "filename": "open5e_srd-2014_conditions.json",
    },
    "srd-2024": {
        "edition": "2024",
        "game_system": "5e-2024",
        "source_name": "System Reference Document 5.2",
        "expected_count": 15,
        "filename": "open5e_srd-2024_conditions.json",
    },
}


def load_document(document_key, config):
    path = INPUT_DIR / config["filename"]

    if not path.is_file():
        raise FileNotFoundError(path)

    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError(f"{path.name}: invalid JSON payload.")

    records = payload.get("results")

    if not isinstance(records, list):
        raise ValueError(f"{path.name}: missing results list.")

    if payload.get("count") != config["expected_count"]:
        raise ValueError(
            f"{document_key}: expected count "
            f"{config['expected_count']}, "
            f"found {payload.get('count')!r}."
        )

    if len(records) != config["expected_count"]:
        raise ValueError(
            f"{document_key}: expected "
            f"{config['expected_count']} records, "
            f"found {len(records)}."
        )

    if payload.get("next") is not None:
        raise ValueError(
            f"{document_key}: input file is not complete."
        )

    normalized = []
    seen_keys = set()
    seen_names = set()

    for record in records:
        if not isinstance(record, dict):
            raise ValueError(
                f"{document_key}: invalid record."
            )

        external_id = record.get("key")
        name = record.get("name")
        description = record.get("description")

        if not isinstance(external_id, str) or not external_id.strip():
            raise ValueError(
                f"{document_key}: invalid condition key."
            )

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"{document_key}/{external_id}: invalid name."
            )

        if (
            not isinstance(description, str)
            or not description.strip()
        ):
            raise ValueError(
                f"{document_key}/{external_id}: "
                "missing description."
            )

        if record.get("document_key") != document_key:
            raise ValueError(
                f"{document_key}/{external_id}: "
                "document key mismatch."
            )

        if record.get("game_system") != config["game_system"]:
            raise ValueError(
                f"{document_key}/{external_id}: "
                "game system mismatch."
            )

        if external_id in seen_keys:
            raise ValueError(
                f"{document_key}: duplicate key {external_id}."
            )

        if name.casefold() in seen_names:
            raise ValueError(
                f"{document_key}: duplicate condition name {name}."
            )

        if len(external_id) > 160:
            raise ValueError(
                f"{document_key}/{external_id}: key exceeds 160 characters."
            )

        if len(name) > 100:
            raise ValueError(
                f"{document_key}/{external_id}: name exceeds 100 characters."
            )

        seen_keys.add(external_id)
        seen_names.add(name.casefold())

        normalized.append({
            "external_id": external_id,
            "name": name.strip(),
            "description": description.strip(),
            "document_key": document_key,
            "edition_code": config["edition"],
            "source_name": config["source_name"],
        })

    return normalized


def load_all_documents():
    records = []

    print("=" * 60)
    print("OPEN5E CONDITION IMPORT")
    print("=" * 60)

    for document_key, config in DOCUMENTS.items():
        document_records = load_document(
            document_key,
            config,
        )

        print(
            f"\n{document_key}: "
            f"{len(document_records)} conditions"
        )

        records.extend(document_records)

    if len(records) != 50:
        raise ValueError(
            f"Expected 50 total conditions, found {len(records)}."
        )

    identities = set()
    edition_names = set()

    for record in records:
        identity = (
            record["document_key"],
            record["external_id"],
        )

        edition_name = (
            record["edition_code"],
            record["name"].casefold(),
        )

        if identity in identities:
            raise ValueError(
                f"Duplicate source identity: {identity}"
            )

        if edition_name in edition_names:
            raise ValueError(
                f"Duplicate condition within edition: {edition_name}"
            )

        identities.add(identity)
        edition_names.add(edition_name)

    return records


def resolve_database_ids(session, records):
    edition_codes = {
        record["edition_code"]
        for record in records
    }

    source_names = {
        record["source_name"]
        for record in records
    }

    editions = session.execute(
        select(Edition).where(Edition.code.in_(edition_codes))
    ).scalars().all()

    sources = session.execute(
        select(Source).where(Source.name.in_(source_names))
    ).scalars().all()

    edition_ids = {
        edition.code: edition.id
        for edition in editions
    }

    source_ids = {
        source.name: source.id
        for source in sources
    }

    missing_editions = edition_codes - edition_ids.keys()
    missing_sources = source_names - source_ids.keys()

    if missing_editions:
        raise ValueError(
            f"Missing database editions: {sorted(missing_editions)}"
        )

    if missing_sources:
        raise ValueError(
            f"Missing database sources: {sorted(missing_sources)}"
        )

    for record in records:
        record["edition_id"] = edition_ids[
            record["edition_code"]
        ]
        record["source_id"] = source_ids[
            record["source_name"]
        ]

    return edition_ids, source_ids


def validate_existing_records(session, records):
    source_ids = {
        record["source_id"]
        for record in records
    }

    edition_ids = {
        record["edition_id"]
        for record in records
    }

    existing = session.execute(
        select(Condition).where(
            Condition.source_id.in_(source_ids),
        )
    ).scalars().all()

    existing_by_identity = {
        (condition.source_id, condition.external_id): condition
        for condition in existing
    }

    existing_by_edition_name = {
        (condition.edition_id, condition.name.casefold()): condition
        for condition in session.execute(
            select(Condition).where(
                Condition.edition_id.in_(edition_ids)
            )
        ).scalars().all()
    }

    new_count = 0
    existing_count = 0

    for record in records:
        identity = (
            record["source_id"],
            record["external_id"],
        )

        edition_name = (
            record["edition_id"],
            record["name"].casefold(),
        )

        existing_identity = existing_by_identity.get(identity)
        existing_name = existing_by_edition_name.get(edition_name)

        if existing_name and (
            existing_name.source_id != record["source_id"]
            or existing_name.external_id != record["external_id"]
        ):
            raise ValueError(
                f"Condition name conflict: "
                f"{record['name']} already exists in edition "
                f"{record['edition_code']} under another source."
            )

        if existing_identity:
            existing_count += 1
        else:
            new_count += 1

    return new_count, existing_count


def import_conditions(session, records, dry_run=False):
    new_count, existing_count = validate_existing_records(
        session,
        records,
    )

    print("\nImport summary:")
    print(f"  New conditions:      {new_count:>5}")
    print(f"  Existing conditions: {existing_count:>5}")
    print(f"  Total conditions:    {len(records):>5}")

    if dry_run:
        print("\nDry run completed. No changes committed.")
        return

    database_records = [
        {
            "edition_id": record["edition_id"],
            "name": record["name"],
            "description": record["description"],
            "source_id": record["source_id"],
            "external_id": record["external_id"],
        }
        for record in records
    ]

    statement = insert(Condition).values(database_records)

    statement = statement.on_conflict_do_update(
        index_elements=["source_id", "external_id"],
        set_={
            "edition_id": statement.excluded.edition_id,
            "name": statement.excluded.name,
            "description": statement.excluded.description,
        },
    )

    session.execute(statement)

    print("\nCondition import committed successfully.")
    print(f"  Condition records: {len(records)}")


def main():
    parser = argparse.ArgumentParser(
        description="Import Open5e condition data."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report without committing changes.",
    )

    args = parser.parse_args()

    records = load_all_documents()

    if args.dry_run:
        print("\nDRY RUN ENABLED: No database changes will be made.")

    with SessionLocal() as session:
        with session.begin():
            resolve_database_ids(session, records)

            import_conditions(
                session,
                records,
                dry_run=args.dry_run,
            )


if __name__ == "__main__":
    main()
