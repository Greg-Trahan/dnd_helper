
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models.edition import Edition
from app.models.source import Source
from app.models.feature import Feature
from app.models.background import Background


INPUT_DIR = PROJECT_ROOT / "data" / "imports" / "backgrounds"

DOCUMENTS = {
    "a5e-ag": {
        "edition_code": "a5e",
        "game_system_key": "a5e",
        "source_name": "Adventurer's Guide",
    },
    "a5e-ddg": {
        "edition_code": "a5e",
        "game_system_key": "a5e",
        "source_name": "Dungeon Delver’s Guide",
    },
    "a5e-gpg": {
        "edition_code": "a5e",
        "game_system_key": "a5e",
        "source_name": "Gate Pass Gazette",
    },
    "open5e": {
        "edition_code": "2014",
        "game_system_key": "5e-2014",
        "source_name": "Open5e Originals",
    },
    "srd-2014": {
        "edition_code": "2014",
        "game_system_key": "5e-2014",
        "source_name": "System Reference Document 5.1",
    },
    "srd-2024": {
        "edition_code": "2024",
        "game_system_key": "5e-2024",
        "source_name": "System Reference Document 5.2",
    },
    "tdcs": {
        "edition_code": "2014",
        "game_system_key": "5e-2014",
        "source_name": "Tal'dorei Campaign Setting",
    },
    "toh": {
        "edition_code": "2014",
        "game_system_key": "5e-2014",
        "source_name": "Tome of Heroes",
    },
}

EDITION_CONFIG = {
    "2014": {
        "name": "D&D 5th Edition (2014)",
        "year": 2014,
        "description": "D&D 5th Edition rules published in 2014.",
    },
    "2024": {
        "name": "D&D 5th Edition (2024)",
        "year": 2024,
        "description": "D&D 5th Edition revised rules published in 2024.",
    },
    "a5e": {
        "name": "Advanced 5th Edition",
        "year": None,
        "description": "Advanced 5th Edition by EN Publishing.",
    },
}

BATCH_SIZE = 500
FEATURE_TYPE = "background_feature"
EXPECTED_TOTAL = 58


def load_document(document_key):
    path = INPUT_DIR / f"open5e_{document_key}_backgrounds.json"

    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")

    with path.open(encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError(f"{path.name}: invalid response.")

    records = payload.get("results")

    if not isinstance(records, list):
        raise ValueError(f"{path.name}: missing results list.")

    if payload.get("next") is not None:
        raise ValueError(f"{path.name}: contains additional pages.")

    if payload.get("count") != len(records):
        raise ValueError(f"{path.name}: count mismatch.")

    config = DOCUMENTS[document_key]
    seen_keys = set()

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"{path.name}: invalid record {index}.")

        key = record.get("key")
        name = record.get("name")

        if not isinstance(key, str) or not key:
            raise ValueError(f"{path.name}: record {index} has no key.")

        if key in seen_keys:
            raise ValueError(f"{path.name}: duplicate key {key}.")

        seen_keys.add(key)

        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{key}: invalid name.")

        document = record.get("document") or {}

        if document.get("key") != document_key:
            raise ValueError(f"{key}: unexpected document key.")

        if document.get("name") != config["source_name"]:
            raise ValueError(
                f"{key}: expected source {config['source_name']!r}, "
                f"got {document.get('name')!r}."
            )

        game_system = document.get("gamesystem") or {}

        if game_system.get("key") != config["game_system_key"]:
            raise ValueError(
                f"{key}: unexpected game system "
                f"{game_system.get('key')!r}."
            )

        if not isinstance(record.get("benefits"), list):
            raise ValueError(f"{key}: benefits must be a list.")

        description = record.get("desc")

        if description is not None and not isinstance(description, str):
            raise ValueError(f"{key}: invalid description.")

        for benefit in record["benefits"]:
            if not isinstance(benefit, dict):
                raise ValueError(f"{key}: invalid benefit.")

            for field in ("name", "desc", "type"):
                if not isinstance(benefit.get(field), str):
                    raise ValueError(
                        f"{key}: benefit has invalid {field}."
                    )

    return records


def load_all_data():
    data = {}

    for document_key in DOCUMENTS:
        filename = f"open5e_{document_key}_backgrounds.json"
        print(f"\nReading {filename}...")

        records = load_document(document_key)
        data[document_key] = records

        print(f"Validated: {len(records)} records.")

    total = sum(len(records) for records in data.values())

    if total != EXPECTED_TOTAL:
        raise ValueError(
            f"Expected {EXPECTED_TOTAL} backgrounds, found {total}."
        )

    return data


def resolve_duplicate_names(data):
    """Append source names only when names collide within an edition."""

    occurrences = defaultdict(list)

    for document_key, records in data.items():
        edition_code = DOCUMENTS[document_key]["edition_code"]

        for record in records:
            occurrences[
                (edition_code, record["name"].strip().casefold())
            ].append((document_key, record))

    resolved = {}

    for document_key, records in data.items():
        source_name = DOCUMENTS[document_key]["source_name"]
        resolved[document_key] = []

        for record in records:
            normalized = dict(record)
            edition_code = DOCUMENTS[document_key]["edition_code"]
            key = (edition_code, record["name"].strip().casefold())

            if len(occurrences[key]) > 1:
                normalized["import_name"] = (
                    f"{record['name']} ({source_name})"
                )
            else:
                normalized["import_name"] = record["name"]

            if len(normalized["import_name"]) > 140:
                raise ValueError(
                    f"Disambiguated background name exceeds 140 "
                    f"characters: {normalized['import_name']}"
                )

            resolved[document_key].append(normalized)

    return resolved


def normalize_background(record):
    fields = {
        "skill_proficiencies": [],
        "tool_proficiencies": [],
        "languages": [],
        "starting_equipment": [],
        "ability_score_rules": [],
    }

    type_mapping = {
        "skill_proficiency": "skill_proficiencies",
        "tool_proficiency": "tool_proficiencies",
        "language": "languages",
        "equipment": "starting_equipment",
        "ability_score": "ability_score_rules",
    }

    feature_benefits = []
    additional_benefits = []

    for index, benefit in enumerate(record["benefits"]):
        benefit_type = benefit["type"].lower()

        normalized = {
            "name": benefit["name"],
            "text": benefit["desc"],
            "type": benefit_type,
        }

        if benefit_type in type_mapping:
            fields[type_mapping[benefit_type]].append(normalized)

        elif benefit_type == "feature":
            feature_benefits.append({
                **normalized,
                "external_id": (
                    f"background:{record['key']}:benefit:{index}"
                ),
            })

        else:
            additional_benefits.append(normalized)

    if len(feature_benefits) > 1:
        raise ValueError(
            f"{record['key']} has multiple feature benefits, "
            "but Background supports only one feature_id."
        )

    description = record.get("desc") or ""

    if additional_benefits:
        sections = ["## Additional Benefits"]

        for benefit in additional_benefits:
            sections.append(
                f"### {benefit['name']}\n\n{benefit['text']}"
            )

        description = (
            f"{description}\n\n{'\\n\\n'.join(sections)}".strip()
        )

    return {
        "external_id": record["key"],
        "name": record["import_name"],
        "description": description,
        **{
            key: value or None
            for key, value in fields.items()
        },
        "feature_benefits": feature_benefits,
    }


def normalize_all(data):
    return {
        document_key: [
            normalize_background(record)
            for record in records
        ]
        for document_key, records in data.items()
    }


def upsert_edition(session, code, config):
    statement = insert(Edition).values(
        code=code,
        name=config["name"],
        year=config["year"],
        description=config["description"],
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


def upsert_source(session, document):
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

    values = {
        "name": document["name"],
        "url": document.get("permalink"),
        "description": " ".join(description_parts) or None,
    }

    statement = insert(Source).values(**values)

    statement = statement.on_conflict_do_update(
        index_elements=["name"],
        set_={
            "url": statement.excluded.url,
            "description": statement.excluded.description,
        },
    ).returning(Source.id)

    return session.execute(statement).scalar_one()


def make_background_values(records, edition_id, source_id):
    return [
        {
            "edition_id": edition_id,
            "source_id": source_id,
            "external_id": record["external_id"],
            "name": record["name"],
            "description": record["description"],
            "skill_proficiencies": record["skill_proficiencies"],
            "tool_proficiencies": record["tool_proficiencies"],
            "languages": record["languages"],
            "starting_equipment": record["starting_equipment"],
            "ability_score_rules": record["ability_score_rules"],
        }
        for record in records
    ]


def make_feature_values(records, edition_id, source_id):
    values = []

    for record in records:
        for benefit in record["feature_benefits"]:
            feature_name = (
                f"{record['name']}: {benefit['name']}"
            )[:160]

            values.append({
                "edition_id": edition_id,
                "source_id": source_id,
                "external_id": benefit["external_id"],
                "name": feature_name,
                "feature_type": FEATURE_TYPE,
                "description": benefit["text"],
                "rules_text": benefit["text"],
                "mechanics": {
                    "background_external_id": record["external_id"],
                    "benefit_name": benefit["name"],
                    "benefit_type": benefit["type"],
                },
            })

    return values


def upsert_records(session, model, records, conflict_columns):
    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start:start + BATCH_SIZE]
        statement = insert(model).values(batch)

        update_columns = {
            column: getattr(statement.excluded, column)
            for column in batch[0]
            if column not in conflict_columns
        }

        statement = statement.on_conflict_do_update(
            index_elements=[
                getattr(model, column)
                for column in conflict_columns
            ],
            set_=update_columns,
        )

        session.execute(statement)


def validate_background_conflicts(session, values):
    names_seen = set()

    for record in values:
        key = (record["edition_id"], record["name"].casefold())

        if key in names_seen:
            raise ValueError(
                f"Duplicate normalized background name: {record['name']}."
            )

        names_seen.add(key)

        existing = session.scalar(
            select(Background).where(
                Background.edition_id == record["edition_id"],
                Background.name == record["name"],
            )
        )

        if existing and (
            existing.source_id != record["source_id"]
            or existing.external_id != record["external_id"]
        ):
            raise ValueError(
                f"Background name conflict with existing database record: "
                f"{record['name']}."
            )


def fetch_background_ids(session, records, source_id):
    identifiers = [record["external_id"] for record in records]

    if not identifiers:
        return {}

    rows = session.execute(
        select(Background.external_id, Background.id).where(
            Background.source_id == source_id,
            Background.external_id.in_(identifiers),
        )
    ).all()

    return {external_id: row_id for external_id, row_id in rows}


def fetch_feature_ids(session, feature_values, source_id):
    identifiers = [record["external_id"] for record in feature_values]

    if not identifiers:
        return {}

    rows = session.execute(
        select(Feature.external_id, Feature.id).where(
            Feature.source_id == source_id,
            Feature.external_id.in_(identifiers),
        )
    ).all()

    return {external_id: row_id for external_id, row_id in rows}


def import_all(data, dry_run=False):
    normalized = normalize_all(resolve_duplicate_names(data))

    total_backgrounds = sum(
        len(records) for records in normalized.values()
    )
    total_features = sum(
        len(record["feature_benefits"])
        for records in normalized.values()
        for record in records
    )

    print("\n" + "=" * 58)
    print("VALIDATED BACKGROUND IMPORT PLAN")
    print("=" * 58)
    print(f"Backgrounds:        {total_backgrounds}")
    print(f"Background features: {total_features}")

    with SessionLocal() as session:
        transaction = session.begin()

        try:
            edition_ids = {}

            for code, config in EDITION_CONFIG.items():
                edition_ids[code] = upsert_edition(
                    session,
                    code,
                    config,
                )

            source_ids = {}

            for document_key in DOCUMENTS:
                sample = data[document_key][0]

                source_ids[document_key] = upsert_source(
                    session,
                    sample["document"],
                )

            for document_key, records in normalized.items():
                config = DOCUMENTS[document_key]
                edition_code = config["edition_code"]
                edition_id = edition_ids[edition_code]
                source_id = source_ids[document_key]

                print(f"\nProcessing {document_key}...")

                background_values = make_background_values(
                    records,
                    edition_id,
                    source_id,
                )

                validate_background_conflicts(
                    session,
                    background_values,
                )

                upsert_records(
                    session,
                    Background,
                    background_values,
                    ("source_id", "external_id"),
                )

                background_ids = fetch_background_ids(
                    session,
                    records,
                    source_id,
                )

                if len(background_ids) != len(records):
                    raise ValueError(
                        f"Could not resolve all {document_key} backgrounds."
                    )

                feature_values = make_feature_values(
                    records,
                    edition_id,
                    source_id,
                )

                upsert_records(
                    session,
                    Feature,
                    feature_values,
                    ("source_id", "external_id"),
                )

                feature_ids = fetch_feature_ids(
                    session,
                    feature_values,
                    source_id,
                )

                if len(feature_ids) != len(feature_values):
                    raise ValueError(
                        f"Could not resolve all {document_key} features."
                    )

                linked_features = 0

                for record in records:
                    background_id = background_ids[record["external_id"]]
                    benefits = record["feature_benefits"]

                    feature_id = (
                        feature_ids[benefits[0]["external_id"]]
                        if benefits
                        else None
                    )

                    session.execute(
                        Background.__table__.update()
                        .where(Background.id == background_id)
                        .values(feature_id=feature_id)
                    )

                    if feature_id is not None:
                        linked_features += 1

                print(f"  Backgrounds:  {len(records)}")
                print(f"  Features:     {len(feature_values)}")
                print(f"  Feature links: {linked_features}")

            print("\n" + "=" * 58)
            print("BACKGROUND IMPORT SUMMARY")
            print("=" * 58)
            print(f"Backgrounds: {total_backgrounds}")
            print(f"Features:    {total_features}")

            if dry_run:
                transaction.rollback()
                print("\nDry run completed. No changes committed.")
            else:
                transaction.commit()
                print("\nBackground import committed successfully.")

        except Exception:
            transaction.rollback()
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Import all Open5e backgrounds."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute the import and roll back all changes.",
    )

    args = parser.parse_args()

    data = load_all_data()
    import_all(data, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
