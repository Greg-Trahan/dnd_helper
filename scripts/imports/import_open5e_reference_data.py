import re
import sys
import argparse

from pathlib import Path

import httpx
from sqlalchemy.dialects.postgresql import insert

# Make the backend application importable.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal

from app.models.edition import Edition
from app.models.source import Source
from app.models.condition import Condition
from app.models.damage_type import DamageType
from app.models.language import Language
from app.models.proficiency import Proficiency


BASE_URL = "https://api.open5e.com/v2/"

EDITION_CONFIG = {
    "srd-2014": {
        "code": "2014",
        "name": "D&D 5th Edition (2014)",
        "year": 2014,
    },
    "srd-2024": {
        "code": "2024",
        "name": "D&D 5th Edition (2024)",
        "year": 2024,
    },
}

EDITION_BY_GAMESYSTEM = {
    "5e-2014": "2014",
    "5e-2024": "2024",
}

VALID_SOURCE_KEYS = set(EDITION_CONFIG)


def fetch_all(endpoint):
    """Fetch every page from an Open5e API endpoint."""

    url = f"{BASE_URL}{endpoint}/"
    params = {"limit": 100}
    records = []

    with httpx.Client(timeout=30) as client:
        while url:
            response = client.get(url, params=params)
            response.raise_for_status()

            payload = response.json()

            if not isinstance(payload, dict):
                raise ValueError(
                    f"Unexpected response from {endpoint}"
                )

            results = payload.get("results")

            if not isinstance(results, list):
                raise ValueError(
                    f"Missing results list from {endpoint}"
                )

            records.extend(results)

            url = payload.get("next")
            params = None

    return records


def get_document_key(value):
    """Extract a document key from a string or object."""

    if isinstance(value, dict):
        return value.get("key")

    return value


def get_document_metadata(documents, key):
    """Find a document's metadata by its Open5e key."""

    for document in documents:
        if document.get("key") == key:
            return document

    return None


def make_source_record(document):
    """Convert Open5e document metadata into a Source record."""

    publisher = document.get("publisher") or {}
    gamesystem = document.get("gamesystem") or {}

    description_parts = []

    if publisher.get("name"):
        description_parts.append(
            f"Publisher: {publisher['name']}."
        )

    if gamesystem.get("name"):
        description_parts.append(
            f"Game system: {gamesystem['name']}."
        )

    return {
        "name": document.get("name") or document["display_name"],
        "url": document.get("permalink"),
        "description": " ".join(description_parts) or None,
    }


def upsert_edition(session, config):
    """Insert or update an edition and return its database ID."""

    statement = insert(Edition).values(
        code=config["code"],
        name=config["name"],
        year=config["year"],
        description=(
            f"Open5e game system reference for "
            f"D&D 5th Edition ({config['year']})."
        ),
    )

    statement = statement.on_conflict_do_update(
        index_elements=["code"],
        set_={
            "name": statement.excluded.name,
            "year": statement.excluded.year,
            "description": statement.excluded.description,
        },
    ).returning(Edition.id)

    return session.execute(statement).scalar_one()


def upsert_source(session, record):
    """Insert or update a source and return its database ID."""

    statement = insert(Source).values(**record)

    statement = statement.on_conflict_do_update(
        index_elements=["name"],
        set_={
            "url": statement.excluded.url,
            "description": statement.excluded.description,
        },
    ).returning(Source.id)

    return session.execute(statement).scalar_one()


def upsert_records(
    session,
    model,
    records,
    conflict_fields,
    update_fields,
):
    """Insert or update a collection of reference records."""

    if not records:
        return 0

    statement = insert(model).values(records)

    update_values = {
        field: getattr(statement.excluded, field)
        for field in update_fields
    }

    statement = statement.on_conflict_do_update(
        index_elements=conflict_fields,
        set_=update_values,
    )

    session.execute(statement)

    return len(records)


def get_description_for_document(record, document_key):
    """Find the description belonging to a specific source document."""

    descriptions = record.get("descriptions") or []

    matching = [
        item.get("desc")
        for item in descriptions
        if item.get("document") == document_key
        and item.get("desc")
    ]

    if not matching:
        return None

    return "\n\n".join(matching)


def normalize_conditions(records, edition_ids, source_ids):
    normalized = []

    for record in records:
        for document_key in VALID_SOURCE_KEYS:
            edition_code = EDITION_CONFIG[document_key]["code"]

            description = get_description_for_document(
                record,
                document_key,
            )

            if not description:
                continue

            normalized.append({
                "edition_id": edition_ids[edition_code],
                "name": record["name"],
                "description": description,
                "source_id": source_ids[document_key],
                "external_id": record["key"],
            })

    return normalized


def normalize_damage_types(records, edition_ids):
    normalized = []

    for record in records:
        for document_key in VALID_SOURCE_KEYS:
            edition_code = EDITION_CONFIG[document_key]["code"]

            description = get_description_for_document(
                record,
                document_key,
            )

            if not description:
                continue

            normalized.append({
                "edition_id": edition_ids[edition_code],
                "name": record["name"],
                "description": description,
            })

    return normalized


def normalize_languages(records, edition_ids, source_ids):
    normalized = []

    for record in records:
        document = record.get("document") or {}
        document_key = get_document_key(document)

        if document_key != "core":
            continue

        gamesystem = document.get("gamesystem") or {}
        gamesystem_key = gamesystem.get("key")

        edition_code = EDITION_BY_GAMESYSTEM.get(gamesystem_key)

        if not edition_code:
            continue

        description = record.get("desc")

        normalized.append({
            "edition_id": edition_ids[edition_code],
            "name": record["name"],
            "typical_speakers": description,
            "script": record.get("script_language"),
            "description": None,
            "source_id": source_ids["core"],
            "external_id": record["key"],
        })

    return normalized


def normalize_proficiencies(records, edition_ids, source_ids):
    normalized = []

    for record in records:
        for document_key in VALID_SOURCE_KEYS:
            edition_code = EDITION_CONFIG[document_key]["code"]

            description = get_description_for_document(
                record,
                document_key,
            )

            if not description:
                continue

            normalized.append({
                "edition_id": edition_ids[edition_code],
                "name": record["name"],
                "category": "skill",
                "description": description,
                "source_id": source_ids[document_key],
                "external_id": record["key"],
            })

    return normalized


def main():
    parser = argparse.ArgumentParser(
        description="Import Open5e reference data."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute imports but roll back all database changes.",
    )

    args = parser.parse_args()

    print("Fetching Open5e reference data...")

    if args.dry_run:
        print("DRY RUN ENABLED: Database changes will be rolled back.")
    documents = fetch_all("documents")
    conditions = fetch_all("conditions")
    damage_types = fetch_all("damagetypes")
    languages = fetch_all("languages")
    skills = fetch_all("skills")

    print(f"Documents: {len(documents)}")
    print(f"Conditions: {len(conditions)}")
    print(f"Damage types: {len(damage_types)}")
    print(f"Languages: {len(languages)}")
    print(f"Skills: {len(skills)}")

    # Build source metadata from the documents endpoint.
    source_documents = {}

    for document_key in VALID_SOURCE_KEYS:
        document = get_document_metadata(
            documents,
            document_key,
        )

        if not document:
            raise ValueError(
                f"Open5e document not found: {document_key}"
            )

        source_documents[document_key] = document

    # The shared core language document may be embedded in language
    # records rather than returned as a separate document.
    core_document = None

    for record in languages:
        document = record.get("document")

        if (
            isinstance(document, dict)
            and document.get("key") == "core"
        ):
            core_document = document
            break

    if not core_document:
        raise ValueError(
            "Could not find Open5e core document metadata."
        )

    source_documents["core"] = core_document

    # Validate source metadata before writing anything.
    source_records = {
        key: make_source_record(document)
        for key, document in source_documents.items()
    }

    for key, record in source_records.items():
        if not record["name"]:
            raise ValueError(
                f"Missing source name for document {key}"
            )

    with SessionLocal() as session:
        try:
            # Seed editions.
            edition_ids = {}

            for document_key, config in EDITION_CONFIG.items():
                edition_ids[config["code"]] = upsert_edition(
                    session,
                    config,
                )

            # Seed source publications.
            source_ids = {}

            for document_key, record in source_records.items():
                source_ids[document_key] = upsert_source(
                    session,
                    record,
                )

            # Normalize all reference data.
            condition_records = normalize_conditions(
                conditions,
                edition_ids,
                source_ids,
            )

            damage_type_records = normalize_damage_types(
                damage_types,
                edition_ids,
            )

            language_records = normalize_languages(
                languages,
                edition_ids,
                source_ids,
            )

            proficiency_records = normalize_proficiencies(
                skills,
                edition_ids,
                source_ids,
            )

            # Validate expected edition coverage before inserting.
            if not condition_records:
                raise ValueError("No SRD conditions were found.")

            if not damage_type_records:
                raise ValueError("No SRD damage types were found.")

            if not language_records:
                raise ValueError("No core languages were found.")

            if not proficiency_records:
                raise ValueError("No SRD skills were found.")

            # Import conditions.
            condition_count = upsert_records(
                session,
                Condition,
                condition_records,
                conflict_fields=["source_id", "external_id"],
                update_fields=[
                    "edition_id",
                    "name",
                    "description",
                ],
            )

            # Import damage types.
            damage_type_count = upsert_records(
                session,
                DamageType,
                damage_type_records,
                conflict_fields=["edition_id", "name"],
                update_fields=["description"],
            )

            # Import languages.
            language_count = upsert_records(
                session,
                Language,
                language_records,
                conflict_fields=["source_id", "external_id"],
                update_fields=[
                    "edition_id",
                    "name",
                    "typical_speakers",
                    "script",
                    "description",
                ],
            )

            # Import skills as proficiencies.
            proficiency_count = upsert_records(
                session,
                Proficiency,
                proficiency_records,
                conflict_fields=["source_id", "external_id"],
                update_fields=[
                    "edition_id",
                    "name",
                    "category",
                    "description",
                ],
            )

            if args.dry_run:
                session.rollback()
                print("\nDRY RUN: All database changes rolled back.")
            else:
                session.commit()
                print("\nDatabase transaction committed.")

        except Exception:
            session.rollback()
            raise

    print("\nImport complete.")
    print(f"Editions seeded: {len(edition_ids)}")
    print(f"Sources seeded: {len(source_ids)}")
    print(f"Conditions processed: {condition_count}")
    print(f"Damage types processed: {damage_type_count}")
    print(f"Languages processed: {language_count}")
    print(f"Proficiencies processed: {proficiency_count}")

    if args.dry_run:
        print("No database changes were retained.")

if __name__ == "__main__":
    main()
