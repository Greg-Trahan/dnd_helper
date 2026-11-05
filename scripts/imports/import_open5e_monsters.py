import json
import sys
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

# Make the backend application importable when running this script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models import Monster


INPUT_DIR = PROJECT_ROOT / "data" / "imports" / "monsters"

FILES = [
    INPUT_DIR / "open5e_2014.json",
    INPUT_DIR / "open5e_2024.json",
]

# These structured fields will be preserved in the abilities JSON column.
ABILITY_FIELDS = [
    "actions",
    "bonus_actions",
    "reactions",
    "legendary_actions",
    "mythic_actions",
    "traits",
]


def get_name(value):
    """Extract a name from an Open5e object or return a string unchanged."""
    if isinstance(value, dict):
        return value.get("name")
    return value


def normalize_monster(data):
    """Convert an Open5e creature record into our Monster database format."""

    document = data.get("document") or {}
    document_key = document.get("key")

    if document_key not in ("srd-2014", "srd-2024"):
        raise ValueError(f"Unexpected Open5e document key: {document_key}")

    # Organize traits and actions into their appropriate categories.
    abilities = {}

    # Traits are stored separately by Open5e.
    if data.get("traits"):
        abilities["traits"] = data["traits"]

    # Open5e stores multiple action types in one actions array.
    action_categories = {
        "ACTION": "actions",
        "BONUS_ACTION": "bonus_actions",
        "REACTION": "reactions",
        "LEGENDARY_ACTION": "legendary_actions",
        "MYTHIC_ACTION": "mythic_actions",
    }

    for action in data.get("actions") or []:
        action_type = action.get("action_type", "ACTION")
        category = action_categories.get(action_type, "actions")

        abilities.setdefault(category, []).append(action)

    return {
        "name": data["name"],
        "edition": document_key.replace("srd-", ""),
        "source_key": document_key,
        "source_id": data["key"],
        "source": document.get("display_name") or "Open5e",
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


def load_file(file_path):
    """Load and validate one Open5e API response file."""

    if not file_path.exists():
        raise FileNotFoundError(f"Could not find {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        response = json.load(file)

    if not isinstance(response, dict) or not isinstance(
        response.get("results"), list
    ):
        raise ValueError(f"Unexpected API response format in {file_path}")

    return response["results"]


def import_monsters(monsters):
    """Insert or update monsters using their source identifiers."""

    records = [normalize_monster(monster) for monster in monsters]

    if not records:
        return 0

    # Keep each database operation to a manageable batch.
    imported = 0

    with SessionLocal() as session:
        for start in range(0, len(records), 500):
            batch = records[start : start + 500]

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

        session.commit()

    return imported


def main():
    total_imported = 0

    for file_path in FILES:
        print(f"\nReading {file_path.name}...")

        monsters = load_file(file_path)
        print(f"Found {len(monsters)} monsters.")

        imported = import_monsters(monsters)
        total_imported += imported

        print(f"Imported or updated: {imported}")

    print(f"\nFinished. Total records processed: {total_imported}")


if __name__ == "__main__":
    main()
