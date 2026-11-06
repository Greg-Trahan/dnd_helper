
import argparse
import json
import sys
from pathlib import Path

from sqlalchemy import select, tuple_
from sqlalchemy.dialects.postgresql import insert

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models import Spell


INPUT_DIR = PROJECT_ROOT / "data" / "imports" / "spells"

DOCUMENTS = {
    "a5e-ag": {
        "edition": "a5e",
        "source_name": "Adventurer's Guide",
        "game_system": "a5e",
        "expected_count": 371,
    },
    "deepm": {
        "edition": "2014",
        "source_name": "Deep Magic",
        "game_system": "5e-2014",
        "expected_count": 515,
    },
    "deepmx": {
        "edition": "2014",
        "source_name": "Deep Magic Extended",
        "game_system": "5e-2014",
        "expected_count": 64,
    },
    "kp": {
        "edition": "2014",
        "source_name": "Kobold Press Compilation",
        "game_system": "5e-2014",
        "expected_count": 31,
    },
    "open5e": {
        "edition": "2014",
        "source_name": "Open5e Originals",
        "game_system": "5e-2014",
        "expected_count": 2,
    },
    "spells-that-dont-suck": {
        "edition": "2014",
        "source_name": "Spells That Don't Suck",
        "game_system": "5e-2014",
        "expected_count": 180,
    },
    "srd-2014": {
        "edition": "2014",
        "source_name": "System Reference Document 5.1",
        "game_system": "5e-2014",
        "expected_count": 319,
    },
    "srd-2024": {
        "edition": "2024",
        "source_name": "System Reference Document 5.2",
        "game_system": "5e-2024",
        "expected_count": 339,
    },
    "toh": {
        "edition": "2014",
        "source_name": "Tome of Heroes",
        "game_system": "5e-2014",
        "expected_count": 91,
    },
    "wz": {
        "edition": "2014",
        "source_name": "Warlock Zine",
        "game_system": "5e-2014",
        "expected_count": 43,
    },
}

BATCH_SIZE = 500

STRING_LIMITS = {
    "name": 150,
    "edition": 10,
    "source_key": 100,
    "source_id": 150,
    "source": 150,
    "school": 50,
    "school_key": 50,
    "target_type": 100,
    "range_text": 100,
    "range_unit": 30,
    "shape_type": 50,
    "shape_size_unit": 30,
    "casting_time": 100,
    "duration": 100,
    "saving_throw_ability": 30,
    "damage_roll": 100,
}


def get_name(value):
    if isinstance(value, dict):
        return value.get("name")
    return value


def get_key(value):
    if isinstance(value, dict):
        return value.get("key")
    return None


def normalize_spell(data):
    document = data.get("document") or {}
    document_key = document.get("key")

    if document_key not in DOCUMENTS:
        raise ValueError(
            f"Unexpected Open5e document key: {document_key}"
        )

    config = DOCUMENTS[document_key]

    return {
        "name": data["name"].strip(),
        "edition": config["edition"],
        "source_key": document_key,
        "source_id": data["key"],
        "source": document.get("display_name")
        or document.get("name")
        or config["source_name"],

        "school": get_name(data.get("school")),
        "school_key": get_key(data.get("school")),
        "classes": data.get("classes"),
        "casting_options": data.get("casting_options"),

        "level": data.get("level"),
        "description": data.get("desc"),
        "higher_level": data.get("higher_level"),

        "target_type": data.get("target_type"),
        "target_count": data.get("target_count"),

        "range_value": data.get("range"),
        "range_text": data.get("range_text"),
        "range_unit": data.get("range_unit"),

        "shape_type": data.get("shape_type"),
        "shape_size": data.get("shape_size"),
        "shape_size_unit": data.get("shape_size_unit"),

        "casting_time": data.get("casting_time"),
        "reaction_condition": data.get("reaction_condition"),
        "duration": data.get("duration"),

        "ritual": data.get("ritual"),
        "concentration": data.get("concentration"),

        "verbal": data.get("verbal"),
        "somatic": data.get("somatic"),
        "material": data.get("material"),
        "material_specified": data.get("material_specified"),
        "material_cost": data.get("material_cost"),
        "material_consumed": data.get("material_consumed"),

        "saving_throw_ability": data.get("saving_throw_ability"),
        "attack_roll": data.get("attack_roll"),
        "damage_roll": data.get("damage_roll"),
        "damage_types": data.get("damage_types"),

        "crossreferences": data.get("crossreferences"),
        "raw_data": data,
    }


def load_file(file_path, document_key):
    """Load and validate one Open5e spell response."""

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
            f"{file_path.name} contains additional API pages. "
            "Complete the download before importing."
        )

    if response.get("count") != len(records):
        raise ValueError(
            f"{file_path.name}: API count does not match "
            "downloaded record count."
        )

    config = DOCUMENTS[document_key]

    if len(records) != config["expected_count"]:
        raise ValueError(
            f"{file_path.name}: expected "
            f"{config['expected_count']} spells, found {len(records)}."
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

        document = record.get("document") or {}

        if document.get("key") != document_key:
            raise ValueError(
                f"{file_path.name}: unexpected document key "
                f"at record {index}."
            )

        game_system = document.get("gamesystem") or {}

        if game_system.get("key") != config["game_system"]:
            raise ValueError(
                f"{file_path.name}: unexpected game system "
                f"for record {index}."
            )

        source_id = record.get("key")

        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError(
                f"{file_path.name}: record {index} has no source ID."
            )

        if source_id in seen_ids:
            raise ValueError(
                f"{file_path.name}: duplicate source ID {source_id}."
            )

        seen_ids.add(source_id)

        spell = normalize_spell(record)

        for field, limit in STRING_LIMITS.items():
            value = spell.get(field)

            if value is not None and (
                not isinstance(value, str) or len(value) > limit
            ):
                raise ValueError(
                    f"{file_path.name}: {source_id}: invalid "
                    f"{field} (maximum {limit} characters)."
                )

        level = spell["level"]

        if level is not None and (
            not isinstance(level, int) or not 0 <= level <= 9
        ):
            raise ValueError(
                f"{file_path.name}: invalid spell level "
                f"for {source_id}: {level}"
            )

        range_value = spell["range_value"]

        if range_value is not None and not isinstance(range_value, int):
            raise ValueError(
                f"{file_path.name}: invalid range for {source_id}."
            )

        shape_size = spell["shape_size"]

        if shape_size is not None and not isinstance(
            shape_size,
            (int, float),
        ):
            raise ValueError(
                f"{file_path.name}: invalid shape size for {source_id}."
            )

        normalized.append(spell)

    return normalized


def load_all_spells(document_keys):
    """Load and validate every selected document before importing."""

    records = []

    for document_key in document_keys:
        file_path = INPUT_DIR / f"open5e_{document_key}.json"

        print(f"\nReading {file_path.name}...")

        spells = load_file(file_path, document_key)

        print(f"Validated: {len(spells)} spells.")

        records.extend(spells)

    identifiers = [
        (spell["source_key"], spell["source_id"])
        for spell in records
    ]

    if len(identifiers) != len(set(identifiers)):
        raise ValueError(
            "Duplicate source identifiers found across selected files."
        )

    return records


def find_existing_spells(session, records):
    identifiers = [
        (record["source_key"], record["source_id"])
        for record in records
    ]

    existing = set()

    for start in range(0, len(identifiers), BATCH_SIZE):
        batch = identifiers[start:start + BATCH_SIZE]

        statement = select(
            Spell.source_key,
            Spell.source_id,
        ).where(
            tuple_(
                Spell.source_key,
                Spell.source_id,
            ).in_(batch)
        )

        existing.update(session.execute(statement).all())

    return existing


def upsert_spells(session, records):
    """Insert new spells and update existing source-owned records."""

    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start:start + BATCH_SIZE]

        statement = insert(Spell).values(batch)

        update_fields = {
            column.key: getattr(statement.excluded, column.key)
            for column in Spell.__table__.columns
            if column.key in batch[0]
            and column.key not in ("source_key", "source_id")
        }

        statement = statement.on_conflict_do_update(
            index_elements=["source_key", "source_id"],
            set_=update_fields,
        )

        session.execute(statement)


def import_spells(records, dry_run=False):
    if not records:
        print("\nNo records to import.")
        return

    with SessionLocal() as session:
        with session.begin():
            existing = find_existing_spells(session, records)

            inserted = len(records) - len(existing)
            updated = len(existing)

            if not dry_run:
                upsert_spells(session, records)

            print("\n" + "=" * 50)
            print("SPELL IMPORT SUMMARY")
            print("=" * 50)
            print(f"Records processed: {len(records)}")
            print(f"New records:       {inserted}")
            print(f"Existing records:  {updated}")
            print(f"Total after import: {len(records)}")

            if dry_run:
                print("\nDRY RUN: No database changes made.")
            else:
                print("\nImport completed successfully.")

    return inserted, updated


def main():
    parser = argparse.ArgumentParser(
        description="Import Open5e spells into the D&D database."
    )

    parser.add_argument(
        "--document",
        nargs="+",
        choices=sorted(DOCUMENTS),
        default=sorted(DOCUMENTS),
        help="Document(s) to import. Defaults to all ten documents.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report without writing to the database.",
    )

    args = parser.parse_args()

    print("=" * 50)
    print("OPEN5E SPELL IMPORT")
    print("=" * 50)
    print(f"Documents: {', '.join(args.document)}")
    print(f"Dry run:   {args.dry_run}")

    try:
        records = load_all_spells(args.document)

        print(f"\nTotal validated records: {len(records)}")

        import_spells(records, dry_run=args.dry_run)

    except Exception as error:
        print(f"\nIMPORT FAILED: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
