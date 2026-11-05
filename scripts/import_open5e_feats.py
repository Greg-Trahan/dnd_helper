
import json
import sys
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

# Make the backend application importable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models import Feat


INPUT_DIR = PROJECT_ROOT / "data" / "imports" / "feats"

FILES = [
    INPUT_DIR / "open5e_2014.json",
    INPUT_DIR / "open5e_2024.json",
]

VALID_SOURCE_KEYS = ("srd-2014", "srd-2024")


def normalize_feat(data):
    """Convert an Open5e feat into our Feat database format."""

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

        "feat_type": data.get("type"),
        "has_prerequisite": data.get("has_prerequisite"),
        "prerequisite": data.get("prerequisite"),

        "description": data.get("desc"),
        "benefits": data.get("benefits"),

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


def import_feats(feats):
    """Insert or update feats using their source identifiers."""

    records = [normalize_feat(feat) for feat in feats]

    if not records:
        return 0

    imported = 0

    with SessionLocal() as session:
        for start in range(0, len(records), 500):
            batch = records[start:start + 500]

            statement = insert(Feat).values(batch)

            # Map Python attribute names to database column names.
            update_fields = {
                column.name: getattr(statement.excluded, column.key)
                for column in Feat.__table__.columns
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

        feats = load_file(file_path)
        print(f"Found {len(feats)} feats.")

        imported = import_feats(feats)
        total_imported += imported

        print(f"Imported or updated: {imported}")

    print(
        f"\nFinished. Total feat records processed: "
        f"{total_imported}"
    )


if __name__ == "__main__":
    main()
