
import argparse
import json
import sys
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models import Monster


INPUT_DIR = PROJECT_ROOT / "data" / "imports" / "monsters"

DOCUMENT_EDITIONS = {
    "a5e-mm": "a5e",
    "bfrd": "2014",
    "ccdx": "2014",
    "srd-2014": "2014",
    "srd-2024": "2024",
    "tdcs": "2014",
    "tob": "2014",
    "tob-2023": "2014",
    "tob2": "2014",
    "tob3": "2014",
}

BATCH_SIZE = 500

ACTION_CATEGORIES = {
    "ACTION": "actions",
    "BONUS_ACTION": "bonus_actions",
    "REACTION": "reactions",
    "LEGENDARY_ACTION": "legendary_actions",
    "MYTHIC_ACTION": "mythic_actions",
}


def get_name(value):
    if isinstance(value, dict):
        return value.get("name")
    return value


def normalize_monster(data):
    document = data.get("document") or {}
    document_key = document.get("key")

    if document_key not in DOCUMENT_EDITIONS:
        raise ValueError(
            f"Unexpected Open5e document key: {document_key}"
        )

    if not data.get("key"):
        raise ValueError(f"Monster has no external key: {data.get('name')}")

    abilities = {}

    if data.get("traits"):
        abilities["traits"] = data["traits"]

    for action in data.get("actions") or []:
        action_type = action.get("action_type", "ACTION")
        category = ACTION_CATEGORIES.get(action_type, "actions")

        abilities.setdefault(category, []).append(action)

    return {
        "name": data["name"],
        "edition": DOCUMENT_EDITIONS[document_key],
        "source_key": document_key,
        "source_id": data["key"],
        "source": (
            document.get("display_name")
            or document.get("name")
            or "Open5e"
        ),
        "size": get_name(data.get("size")),
        "creature_type": get_name(data.get("type")),
        "alignment": data.get("alignment"),
        "challenge_rating": data.get("challenge_rating"),
        "armor_class": data.get("armor_class"),
        "hit_points": data.get("hit_points"),
        "speed": data.get("speed"),
        "ability_scores": data.get("ability_scores"),
        "abilities": abilities,
        "description": data.get("desc"),
        "raw_data": data,
    }


def load_file(document_key):
    file_path = (
        INPUT_DIR / f"open5e_{document_key}_creatures.json"
    )

    if not file_path.exists():
        raise FileNotFoundError(f"Missing input file: {file_path}")

    with file_path.open(encoding="utf-8") as file:
        response = json.load(file)

    if not isinstance(response, dict):
        raise ValueError(f"Invalid response in {file_path.name}")

    monsters = response.get("results")

    if not isinstance(monsters, list):
        raise ValueError(f"Missing results in {file_path.name}")

    if response.get("count") != len(monsters):
        raise ValueError(f"Count mismatch in {file_path.name}")

    if response.get("next") is not None:
        raise ValueError(f"File is not a complete download: {file_path}")

    return monsters


def import_monsters(monsters, dry_run=False):
    records = [normalize_monster(monster) for monster in monsters]

    if not records:
        return 0

    imported = 0

    with SessionLocal() as session:
        try:
            for start in range(0, len(records), BATCH_SIZE):
                batch = records[start:start + BATCH_SIZE]

                statement = insert(Monster).values(batch)

                update_fields = {
                    key: getattr(statement.excluded, key)
                    for key in batch[0]
                    if key not in ("source_key", "source_id")
                }

                statement = statement.on_conflict_do_update(
                    index_elements=["source_key", "source_id"],
                    set_=update_fields,
                )

                session.execute(statement)
                imported += len(batch)

            if dry_run:
                session.rollback()
            else:
                session.commit()

        except Exception:
            session.rollback()
            raise

    return imported


def main():
    parser = argparse.ArgumentParser(
        description="Import all Open5e creatures."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Import and roll back without committing.",
    )
    args = parser.parse_args()

    total = 0

    for document_key in DOCUMENT_EDITIONS:
        print(f"\nReading {document_key}...")

        monsters = load_file(document_key)
        print(f"Found {len(monsters)} creatures.")

        imported = import_monsters(
            monsters,
            dry_run=args.dry_run,
        )

        total += imported
        print(f"Processed: {imported}")

    print("\n" + "=" * 55)
    print("MONSTER IMPORT SUMMARY")
    print("=" * 55)
    print(f"Total processed: {total}")

    if args.dry_run:
        print("Dry run completed. No changes committed.")
    else:
        print("Monster import committed successfully.")


if __name__ == "__main__":
    main()
