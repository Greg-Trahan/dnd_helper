
import json
import sys
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

# Make the backend application importable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models import Spell


INPUT_DIR = PROJECT_ROOT / "data" / "imports" / "spells"

FILES = [
    INPUT_DIR / "open5e_2014.json",
    INPUT_DIR / "open5e_2024.json",
]

VALID_SOURCE_KEYS = ("srd-2014", "srd-2024")


def get_name(value):
    """Extract a name from an Open5e object or return a string."""
    if isinstance(value, dict):
        return value.get("name")
    return value


def get_key(value):
    """Extract a key from an Open5e object."""
    if isinstance(value, dict):
        return value.get("key")
    return None


def normalize_spell(data):
    """Convert an Open5e spell into our Spell database format."""

    document = data.get("document") or {}
    document_key = document.get("key")

    if document_key not in VALID_SOURCE_KEYS:
        raise ValueError(
            f"Unexpected Open5e document key: {document_key}"
        )

    return {
        "name": data["name"],
        "edition": document_key.replace("srd-", ""),
        "source_key": document_key,
        "source_id": data["key"],
        "source": document.get("display_name") or "Open5e",

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


def load_file(file_path):
    """Load and validate one Open5e API response file."""

    if not file_path.exists():
        raise FileNotFoundError(f"Could not find {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        response = json.load(file)

    if not isinstance(response, dict) or not isinstance(
        response.get("results"), list
    ):
        raise ValueError(
            f"Unexpected API response format in {file_path}"
        )

    return response["results"]


def import_spells(spells):
    """Insert or update spells using their source identifiers."""

    records = [normalize_spell(spell) for spell in spells]

    if not records:
        return 0

    imported = 0

    with SessionLocal() as session:
        for start in range(0, len(records), 500):
            batch = records[start:start + 500]

            statement = insert(Spell).values(batch)

            update_fields = {
                column.name: getattr(statement.excluded, column.key)
                for column in Spell.__table__.columns
                if column.key in batch[0]
                and column.key not in ("source_key", "source_id")
            }

            statement = statement.on_conflict_do_update(
                index_elements=["source_key", "source_id"],
                set_=update_fields,
            )

            session.execute(statement)
            imported += len(batch)

        session.commit()

    return imported


def main():
    total_imported = 0

    for file_path in FILES:
        print(f"\nReading {file_path.name}...")

        spells = load_file(file_path)
        print(f"Found {len(spells)} spells.")

        imported = import_spells(spells)
        total_imported += imported

        print(f"Imported or updated: {imported}")

    print(
        f"\nFinished. Total spell records processed: "
        f"{total_imported}"
    )


if __name__ == "__main__":
    main()
