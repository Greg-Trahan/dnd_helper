
import argparse
import json
import re
import sys
from pathlib import Path

from sqlalchemy import select, tuple_
from sqlalchemy.dialects.postgresql import insert

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models import Edition, Feat, FeatPrerequisite, Source


INPUT_DIR = PROJECT_ROOT / "data" / "imports" / "feats"

DOCUMENTS = {
    "a5e-ag": {
        "edition_code": "a5e",
        "source_name": "Adventurer's Guide",
        "game_system_key": "a5e",
        "expected_count": 59,
    },
    "srd-2014": {
        "edition_code": "2014",
        "source_name": "System Reference Document 5.1",
        "game_system_key": "5e-2014",
        "expected_count": 1,
    },
    "srd-2024": {
        "edition_code": "2024",
        "source_name": "System Reference Document 5.2",
        "game_system_key": "5e-2024",
        "expected_count": 17,
    },
    "toh": {
        "edition_code": "2014",
        "source_name": "Tome of Heroes",
        "game_system_key": "5e-2014",
        "expected_count": 13,
    },
}

BATCH_SIZE = 500

STRING_LIMITS = {
    "external_id": 160,
    "name": 160,
    "feat_type": 60,
    "prerequisite_value": 200,
}

REPEATABLE_PATTERN = re.compile(
    r"\bcan take this feat more than once\b",
    re.IGNORECASE,
)


def load_file(file_path, document_key):
    """Load and validate one Open5e feat response."""

    if not file_path.exists():
        raise FileNotFoundError(f"Could not find {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        response = json.load(file)

    if not isinstance(response, dict):
        raise ValueError(f"Invalid response in {file_path}")

    records = response.get("results")

    if not isinstance(records, list):
        raise ValueError(
            f"Unexpected API response format in {file_path}"
        )

    if response.get("next") is not None:
        raise ValueError(
            f"{file_path.name} contains additional API pages."
        )

    if response.get("count") != len(records):
        raise ValueError(
            f"{file_path.name}: API count does not match "
            "downloaded record count."
        )

    config = DOCUMENTS[document_key]

    if len(records) != config["expected_count"]:
        raise ValueError(
            f"{file_path.name}: expected {config['expected_count']} "
            f"feats, found {len(records)}."
        )

    normalized = []
    seen_ids = set()

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(
                f"{file_path.name}: record {index} is not an object."
            )

        name = record.get("name")

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"{file_path.name}: record {index} has no valid name."
            )

        external_id = record.get("key")

        if not isinstance(external_id, str) or not external_id:
            raise ValueError(
                f"{file_path.name}: record {index} has no source ID."
            )

        if external_id in seen_ids:
            raise ValueError(
                f"{file_path.name}: duplicate source ID {external_id}."
            )

        seen_ids.add(external_id)

        document = record.get("document") or {}

        if document.get("key") != document_key:
            raise ValueError(
                f"{file_path.name}: unexpected document key "
                f"at record {index}: {document.get('key')}"
            )

        if document.get("name") != config["source_name"]:
            raise ValueError(
                f"{file_path.name}: unexpected source name "
                f"for {external_id}: {document.get('name')}"
            )

        game_system = document.get("gamesystem") or {}

        if game_system.get("key") != config["game_system_key"]:
            raise ValueError(
                f"{file_path.name}: unexpected game system "
                f"for {external_id}."
            )

        feat_type = record.get("type")

        if feat_type is not None and not isinstance(feat_type, str):
            raise ValueError(
                f"{file_path.name}: invalid feat type for {external_id}."
            )

        description = record.get("desc")

        if description is None:
            description = ""

        if not isinstance(description, str):
            raise ValueError(
                f"{file_path.name}: invalid description for {external_id}."
            )

        benefits = record.get("benefits") or []

        if not isinstance(benefits, list):
            raise ValueError(
                f"{file_path.name}: invalid benefits for {external_id}."
            )

        normalized_benefits = []

        for benefit_index, benefit in enumerate(benefits):
            if not isinstance(benefit, dict):
                raise ValueError(
                    f"{file_path.name}: invalid benefit "
                    f"{benefit_index} for {external_id}."
                )

            benefit_description = benefit.get("desc")

            if not isinstance(benefit_description, str):
                raise ValueError(
                    f"{file_path.name}: missing benefit description "
                    f"{benefit_index} for {external_id}."
                )

            normalized_benefits.append(benefit_description)

        has_prerequisite = record.get("has_prerequisite")

        if not isinstance(has_prerequisite, bool):
            raise ValueError(
                f"{file_path.name}: invalid has_prerequisite "
                f"for {external_id}."
            )

        prerequisite = record.get("prerequisite") or ""

        if not isinstance(prerequisite, str):
            raise ValueError(
                f"{file_path.name}: invalid prerequisite "
                f"for {external_id}."
            )

        if has_prerequisite and not prerequisite.strip():
            raise ValueError(
                f"{file_path.name}: prerequisite flag is true "
                f"but prerequisite text is empty for {external_id}."
            )

        if not has_prerequisite and prerequisite.strip():
            raise ValueError(
                f"{file_path.name}: prerequisite text exists "
                f"but prerequisite flag is false for {external_id}."
            )

        if len(prerequisite) > STRING_LIMITS["prerequisite_value"]:
            raise ValueError(
                f"{file_path.name}: prerequisite exceeds "
                f"{STRING_LIMITS['prerequisite_value']} characters "
                f"for {external_id}."
            )

        repeatable = any(
            REPEATABLE_PATTERN.search(benefit)
            for benefit in normalized_benefits
        )

        normalized_feat = {
            "external_id": external_id,
            "name": name.strip(),
            "description": description,
            "feat_type": feat_type,
            "repeatable": repeatable,
            "edition_code": config["edition_code"],
            "source_name": config["source_name"],
            "prerequisite": prerequisite.strip() or None,
            "mechanics": {
                "benefits": normalized_benefits,
                "has_prerequisite": has_prerequisite,
                "crossreferences": record.get("crossreferences"),
                "raw_data": record,
            },
        }

        for field, limit in STRING_LIMITS.items():
            value = normalized_feat.get(field)

            if value is not None and len(value) > limit:
                raise ValueError(
                    f"{file_path.name}: {external_id}: "
                    f"{field} exceeds {limit} characters."
                )

        normalized.append(normalized_feat)

    return normalized


def load_all_feats(document_keys):
    """Load and validate all selected document files."""

    records = []

    for document_key in document_keys:
        file_path = INPUT_DIR / f"open5e_{document_key}.json"

        print(f"\nReading {file_path.name}...")

        feats = load_file(file_path, document_key)

        print(f"Validated: {len(feats)} feats.")

        records.extend(feats)

    identifiers = [
        (record["edition_code"], record["name"])
        for record in records
    ]

    if len(identifiers) != len(set(identifiers)):
        raise ValueError(
            "Duplicate feat names found within the same edition."
        )

    external_identifiers = [
        (record["source_name"], record["external_id"])
        for record in records
    ]

    if len(external_identifiers) != len(set(external_identifiers)):
        raise ValueError(
            "Duplicate source identifiers across selected files."
        )

    return records


def resolve_reference_records(session, records):
    """Resolve existing editions and sources."""

    edition_codes = {
        record["edition_code"]
        for record in records
    }

    source_names = {
        record["source_name"]
        for record in records
    }

    editions = {
        edition.code: edition.id
        for edition in session.scalars(
            select(Edition).where(Edition.code.in_(edition_codes))
        )
    }

    sources = {
        source.name: source.id
        for source in session.scalars(
            select(Source).where(Source.name.in_(source_names))
        )
    }

    missing_editions = edition_codes - editions.keys()
    missing_sources = source_names - sources.keys()

    if missing_editions:
        raise ValueError(
            f"Missing edition records: {sorted(missing_editions)}"
        )

    if missing_sources:
        raise ValueError(
            f"Missing source records: {sorted(missing_sources)}"
        )

    return [
        {
            "edition_id": editions[record["edition_code"]],
            "source_id": sources[record["source_name"]],
            "external_id": record["external_id"],
            "name": record["name"],
            "description": record["description"],
            "feat_type": record["feat_type"],
            "repeatable": record["repeatable"],
            "mechanics": record["mechanics"],
            "prerequisite": record["prerequisite"],
        }
        for record in records
    ]


def find_existing_feats(session, records):
    identifiers = [
        (record["source_id"], record["external_id"])
        for record in records
    ]

    existing = set()

    for start in range(0, len(identifiers), BATCH_SIZE):
        batch = identifiers[start:start + BATCH_SIZE]

        statement = select(
            Feat.source_id,
            Feat.external_id,
        ).where(
            tuple_(Feat.source_id, Feat.external_id).in_(batch)
        )

        existing.update(session.execute(statement).all())

    return existing


def validate_name_conflicts(session, records):
    """Prevent collisions with the edition/name unique constraint."""

    for record in records:
        existing = session.scalar(
            select(Feat).where(
                Feat.edition_id == record["edition_id"],
                Feat.name == record["name"],
            )
        )

        if existing is None:
            continue

        same_source_record = (
            existing.source_id == record["source_id"]
            and existing.external_id == record["external_id"]
        )

        if not same_source_record:
            raise ValueError(
                "Feat name conflict: "
                f"{record['name']} in edition "
                f"{record['edition_id']} already belongs to a "
                "different source record."
            )


def upsert_feats(session, records):
    """Insert new feats and update existing source-owned records."""

    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start:start + BATCH_SIZE]

        values = [
            {
                key: value
                for key, value in record.items()
                if key != "prerequisite"
            }
            for record in batch
        ]

        statement = insert(Feat).values(values)

        update_fields = {
            column.key: getattr(statement.excluded, column.key)
            for column in Feat.__table__.columns
            if column.key in values[0]
            and column.key not in ("source_id", "external_id")
        }

        statement = statement.on_conflict_do_update(
            index_elements=["source_id", "external_id"],
            set_=update_fields,
        )

        session.execute(statement)


def sync_source_text_prerequisites(session, records):
    """Synchronize importer-owned source_text prerequisite records."""

    identifiers = [
        (record["source_id"], record["external_id"])
        for record in records
    ]

    feat_lookup = {}

    for start in range(0, len(identifiers), BATCH_SIZE):
        batch = identifiers[start:start + BATCH_SIZE]

        statement = select(
            Feat.id,
            Feat.source_id,
            Feat.external_id,
        ).where(
            tuple_(Feat.source_id, Feat.external_id).in_(batch)
        )

        for feat_id, source_id, external_id in session.execute(statement):
            feat_lookup[(source_id, external_id)] = feat_id

    for record in records:
        identifier = (record["source_id"], record["external_id"])
        feat_id = feat_lookup.get(identifier)

        if feat_id is None:
            raise ValueError(
                f"Could not find imported feat {record['external_id']}."
            )

        existing = list(
            session.scalars(
                select(FeatPrerequisite).where(
                    FeatPrerequisite.feat_id == feat_id,
                    FeatPrerequisite.prerequisite_type == "source_text",
                )
            )
        )

        if len(existing) > 1:
            raise ValueError(
                f"Feat {record['external_id']} has multiple "
                "source_text prerequisite records."
            )

        prerequisite = record["prerequisite"]

        if prerequisite is None:
            if existing:
                session.delete(existing[0])
            continue

        if existing:
            existing[0].operator = "eq"
            existing[0].value = prerequisite
            existing[0].description = None
            existing[0].is_hard_requirement = True
        else:
            session.add(
                FeatPrerequisite(
                    feat_id=feat_id,
                    prerequisite_type="source_text",
                    operator="eq",
                    value=prerequisite,
                    description=None,
                    is_hard_requirement=True,
                )
            )


def import_feats(records, dry_run=False):
    if not records:
        print("\nNo records to import.")
        return

    with SessionLocal() as session:
        transaction = session.begin()

        try:
            resolved = resolve_reference_records(session, records)
            existing = find_existing_feats(session, resolved)

            validate_name_conflicts(session, resolved)

            inserted = len(resolved) - len(existing)
            updated = len(existing)

            upsert_feats(session, resolved)
            sync_source_text_prerequisites(session, resolved)

            print("\n" + "=" * 50)
            print("FEAT IMPORT SUMMARY")
            print("=" * 50)
            print(f"Records processed: {len(resolved)}")
            print(f"New records:       {inserted}")
            print(f"Existing records:  {updated}")
            print(
                "Prerequisites:     "
                f"{sum(r['prerequisite'] is not None for r in resolved)}"
            )
            print(
                "Repeatable feats:  "
                f"{sum(r['repeatable'] for r in resolved)}"
            )

            if dry_run:
                transaction.rollback()
                print("\nDRY RUN: All database changes rolled back.")
            else:
                transaction.commit()
                print("\nFeat import committed successfully.")

        except Exception:
            if transaction.is_active:
                transaction.rollback()
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Import Open5e feats into the D&D database."
    )

    parser.add_argument(
        "--document",
        nargs="+",
        choices=sorted(DOCUMENTS),
        default=sorted(DOCUMENTS),
        help="Document(s) to import. Defaults to all four.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute database operations and roll back all changes.",
    )

    args = parser.parse_args()

    records = load_all_feats(args.document)

    print(f"\nTotal validated feats: {len(records)}")

    import_feats(records, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
