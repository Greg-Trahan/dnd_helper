
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from sqlalchemy import select, tuple_
from sqlalchemy.dialects.postgresql import insert

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models import (
    CharacterClass,
    ClassFeatureGrant,
    ClassLevelProgression,
    Edition,
    Feature,
    Source,
    Subclass,
    SubclassFeatureGrant,
)

INPUT_DIR = PROJECT_ROOT / "data" / "imports" / "classes"

DOCUMENTS = {
    "a5e-ag": {
        "edition_code": "a5e",
        "source_name": "Adventurer's Guide",
        "game_system_key": "a5e",
        "expected_classes": 1,
        "expected_subclasses": 3,
    },
    "bfrd": {
        "edition_code": "2014",
        "source_name": "Black Flag SRD",
        "game_system_key": "5e-2014",
        "expected_classes": 1,
        "expected_subclasses": 1,
    },
    "open5e": {
        "edition_code": "2014",
        "source_name": "Open5e Originals",
        "game_system_key": "5e-2014",
        "expected_classes": 0,
        "expected_subclasses": 17,
    },
    "srd-2014": {
        "edition_code": "2014",
        "source_name": "System Reference Document 5.1",
        "game_system_key": "5e-2014",
        "expected_classes": 12,
        "expected_subclasses": 12,
    },
    "srd-2024": {
        "edition_code": "2024",
        "source_name": "System Reference Document 5.2",
        "game_system_key": "5e-2024",
        "expected_classes": 12,
        "expected_subclasses": 12,
    },
    "tdcs": {
        "edition_code": "2014",
        "source_name": "Tal'dorei Campaign Setting",
        "game_system_key": "5e-2014",
        "expected_classes": 0,
        "expected_subclasses": 4,
    },
    "toh": {
        "edition_code": "2014",
        "source_name": "Tome of Heroes",
        "game_system_key": "5e-2014",
        "expected_classes": 0,
        "expected_subclasses": 76,
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

BATCH_SIZE = 250
MAX_LEVEL = 20

STRING_LIMITS = {
    "class_external_id": 160,
    "class_name": 100,
    "subclass_external_id": 160,
    "subclass_name": 120,
    "feature_external_id": 160,
    "feature_name": 160,
    "feature_type": 50,
}


def read_response(path, document_key, expected_subclass):
    """Read and validate one downloaded Open5e response."""

    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")

    response = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(response, dict):
        raise ValueError(f"{path.name}: response must be an object.")

    records = response.get("results")

    if not isinstance(records, list):
        raise ValueError(f"{path.name}: missing results list.")

    if response.get("next") is not None:
        raise ValueError(
            f"{path.name}: additional API pages exist. "
            "Complete the download before importing."
        )

    if response.get("count") != len(records):
        raise ValueError(
            f"{path.name}: API count does not match downloaded records."
        )

    config = DOCUMENTS[document_key]
    expected_count = (
        config["expected_subclasses"]
        if expected_subclass
        else config["expected_classes"]
    )

    if len(records) != expected_count:
        raise ValueError(
            f"{path.name}: expected {expected_count} records, "
            f"found {len(records)}."
        )

    seen_keys = set()

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(
                f"{path.name}: record {index} is not an object."
            )

        key = record.get("key")
        name = record.get("name")

        if not isinstance(key, str) or not key.strip():
            raise ValueError(
                f"{path.name}: record {index} has no valid key."
            )

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"{path.name}: record {index} has no valid name."
            )

        if key in seen_keys:
            raise ValueError(f"{path.name}: duplicate record key {key}.")

        seen_keys.add(key)

        document = record.get("document") or {}

        if document.get("key") != document_key:
            raise ValueError(
                f"{path.name}: unexpected document for {key}: "
                f"{document.get('key')}"
            )

        if document.get("name") != config["source_name"]:
            raise ValueError(
                f"{path.name}: unexpected source name for {key}: "
                f"{document.get('name')}"
            )

        game_system = document.get("gamesystem") or {}

        if game_system.get("key") != config["game_system_key"]:
            raise ValueError(
                f"{path.name}: unexpected game system for {key}."
            )

        parent = record.get("subclass_of")

        if expected_subclass:
            if not isinstance(parent, dict):
                raise ValueError(
                    f"{path.name}: subclass {key} has no parent class."
                )

            if not parent.get("key") or not parent.get("name"):
                raise ValueError(
                    f"{path.name}: subclass {key} has an invalid parent."
                )
        elif parent:
            raise ValueError(
                f"{path.name}: class {key} unexpectedly has a parent."
            )

        features = record.get("features")

        if not isinstance(features, list):
            raise ValueError(
                f"{path.name}: {key} has no valid features list."
            )

        for feature_index, feature in enumerate(features):
            if not isinstance(feature, dict):
                raise ValueError(
                    f"{path.name}: invalid feature {feature_index} "
                    f"on {key}."
                )

            if not isinstance(feature.get("name"), str):
                raise ValueError(
                    f"{path.name}: feature {feature_index} on {key} "
                    "has no name."
                )

            if not isinstance(feature.get("feature_type"), str):
                raise ValueError(
                    f"{path.name}: feature "
                    f"{feature.get('name')} on {key} has no feature type."
                )

            description = feature.get("desc")

            if description is not None and not isinstance(description, str):
                raise ValueError(
                    f"{path.name}: invalid description on "
                    f"{key}/{feature['name']}."
                )

            gained_at = feature.get("gained_at") or []
            table_data = feature.get("data_for_class_table") or []

            if not isinstance(gained_at, list):
                raise ValueError(
                    f"{path.name}: invalid gained_at on "
                    f"{key}/{feature['name']}."
                )

            if not isinstance(table_data, list):
                raise ValueError(
                    f"{path.name}: invalid table data on "
                    f"{key}/{feature['name']}."
                )

            for grant in gained_at:
                if not isinstance(grant, dict):
                    raise ValueError(
                        f"{path.name}: invalid grant on "
                        f"{key}/{feature['name']}."
                    )

                level = grant.get("level")

                if not isinstance(level, int) or not 1 <= level <= MAX_LEVEL:
                    raise ValueError(
                        f"{path.name}: invalid grant level on "
                        f"{key}/{feature['name']}: {level}"
                    )

            for table_entry in table_data:
                if not isinstance(table_entry, dict):
                    raise ValueError(
                        f"{path.name}: invalid table entry on "
                        f"{key}/{feature['name']}."
                    )

                level = table_entry.get("level")

                if not isinstance(level, int) or not 1 <= level <= MAX_LEVEL:
                    raise ValueError(
                        f"{path.name}: invalid table level on "
                        f"{key}/{feature['name']}: {level}"
                    )

    return records


def load_all_data(document_keys):
    """Load every selected file before any database writes."""

    data = {
        "classes": [],
        "subclasses": [],
        "edition_codes": set(),
        "source_names": set(),
    }

    for document_key in document_keys:
        config = DOCUMENTS[document_key]

        for kind, is_subclass in (
            ("classes", False),
            ("subclasses", True),
        ):
            path = INPUT_DIR / f"open5e_{document_key}_{kind}.json"

            print(f"\nReading {path.name}...")

            records = read_response(
                path,
                document_key,
                is_subclass,
            )

            print(f"Validated: {len(records)} records.")

            data[kind].extend(records)

        data["edition_codes"].add(config["edition_code"])
        data["source_names"].add(config["source_name"])

    return data


def validate_source_identifiers(data):
    """Check source identities and edition-level name collisions."""

    for kind in ("classes", "subclasses"):
        identities = [
            (record["document"]["key"], record["key"])
            for record in data[kind]
        ]

        if len(identities) != len(set(identities)):
            raise ValueError(
                f"Duplicate source identities found in {kind}."
            )

    class_names = [
        (
            DOCUMENTS[record["document"]["key"]]["edition_code"],
            record["name"].strip().casefold(),
        )
        for record in data["classes"]
    ]

    if len(class_names) != len(set(class_names)):
        raise ValueError(
            "Duplicate class names within an edition. "
            "Resolve the source-name collision before importing."
        )

    subclass_names = [
        (
            DOCUMENTS[record["document"]["key"]]["edition_code"],
            record["subclass_of"]["name"].strip().casefold(),
            record["name"].strip().casefold(),
        )
        for record in data["subclasses"]
    ]

    if len(subclass_names) != len(set(subclass_names)):
        raise ValueError(
            "Duplicate subclass names within a parent class and edition."
        )


def normalize_text(value):
    if value is None:
        return ""

    if not isinstance(value, str):
        raise ValueError(
            f"Expected text, received {type(value).__name__}."
        )

    return value


def parse_hit_die(record):
    value = record.get("hit_dice")

    if not value:
        value = (record.get("hit_points") or {}).get("hit_dice")

    if value is None:
        return None

    match = re.fullmatch(r"[dD](\d+)", str(value).strip())

    if not match:
        raise ValueError(
            f"Invalid hit die on class {record['key']}: {value}"
        )

    return int(match.group(1))


def normalize_class(record):
    document = record["document"]
    config = DOCUMENTS[document["key"]]

    primary_abilities = record.get("primary_abilities") or []

    if isinstance(primary_abilities, list):
        ability_names = [
            item.get("name") if isinstance(item, dict) else str(item)
            for item in primary_abilities
        ]

        primary_ability = ", ".join(
            value for value in ability_names if value
        ) or None

    elif isinstance(primary_abilities, str):
        primary_ability = primary_abilities or None

    else:
        raise ValueError(
            f"Invalid primary abilities on {record['key']}."
        )

    starting_equipment = [
        feature
        for feature in record["features"]
        if feature["feature_type"] == "STARTING_EQUIPMENT"
    ]

    multiclassing = record.get("multiclassing")

    if multiclassing is not None and not isinstance(
        multiclassing,
        (dict, list),
    ):
        raise ValueError(
            f"Invalid multiclassing data on {record['key']}."
        )

    return {
        "edition_code": config["edition_code"],
        "source_name": config["source_name"],
        "external_id": record["key"],
        "name": record["name"].strip(),
        "description": normalize_text(record.get("desc")),
        "hit_die": parse_hit_die(record),
        "primary_ability": primary_ability,
        "saving_throw_proficiency_ids": None,
        "starting_equipment": starting_equipment or None,
        "multiclassing": multiclassing,
        "is_playable": True,
        "raw": record,
    }


def normalize_subclass(record):
    document = record["document"]
    config = DOCUMENTS[document["key"]]

    return {
        "edition_code": config["edition_code"],
        "source_name": config["source_name"],
        "external_id": record["key"],
        "name": record["name"].strip(),
        "description": normalize_text(record.get("desc")),
        "parent_external_id": record["subclass_of"]["key"],
        "parent_name": record["subclass_of"]["name"].strip(),
        "subclass_level": None,
        "raw": record,
    }


def normalize_features(data):
    """
    Build one Feature per source, edition, name, and feature type.

    Preserve source variants when Open5e supplies multiple definitions
    for the same named feature within one document.
    """

    grouped = defaultdict(list)
    occurrence_lookup = {}

    for kind in ("classes", "subclasses"):
        for parent in data[kind]:
            document_key = parent["document"]["key"]
            config = DOCUMENTS[document_key]

            for order, feature in enumerate(parent["features"]):
                if feature["feature_type"] != "CLASS_LEVEL_FEATURE":
                    continue

                key = feature.get("key")

                if not isinstance(key, str) or not key.strip():
                    raise ValueError(
                        f"Feature {feature['name']} on {parent['key']} "
                        "has no valid source key."
                    )

                name = feature["name"].strip()
                description = normalize_text(feature.get("desc"))

                identity = (
                    config["source_name"],
                    config["edition_code"],
                    name.casefold(),
                    feature["feature_type"],
                )

                grouped[identity].append({
                    "candidate": {
                        "edition_code": config["edition_code"],
                        "source_name": config["source_name"],
                        "external_id": key,
                        "name": name,
                        "feature_type": feature["feature_type"],
                        "description": description,
                        "mechanics": {
                            "crossreferences": feature.get("crossreferences"),
                            "data_for_class_table": (
                                feature.get("data_for_class_table") or []
                            ),
                            "raw_data": feature,
                        },
                    },
                    "parent_key": parent["key"],
                    "parent_kind": kind,
                    "order": order,
                    "gained_at": feature.get("gained_at") or [],
                })

    normalized = []
    candidates = {}
    used_external_ids = {}

    for identity, occurrences in grouped.items():
        source_name, edition_code, _, _ = identity

        chosen = dict(occurrences[0]["candidate"])
        canonical_id = chosen["external_id"]

        if len(canonical_id) > STRING_LIMITS["feature_external_id"]:
            raise ValueError(
                f"Feature source identifier exceeds database limit: "
                f"{canonical_id}"
            )

        source_variants = []
        seen_variants = set()

        for occurrence in occurrences:
            candidate = occurrence["candidate"]
            raw = candidate["mechanics"]["raw_data"]

            signature = (
                candidate["external_id"],
                json.dumps(raw, sort_keys=True, ensure_ascii=False),
            )

            if signature in seen_variants:
                continue

            seen_variants.add(signature)

            source_variants.append({
                "external_id": candidate["external_id"],
                "description": candidate["description"],
                "crossreferences": raw.get("crossreferences"),
                "data_for_class_table": (
                    raw.get("data_for_class_table") or []
                ),
                "raw_data": raw,
            })

        chosen["mechanics"] = {
            **chosen["mechanics"],
            "source_variants": source_variants,
        }

        external_identity = (source_name, canonical_id)
        previous_identity = used_external_ids.get(external_identity)

        if previous_identity is not None and previous_identity != identity:
            raise ValueError(
                f"Canonical feature ID collision: {canonical_id} "
                f"within source {source_name}."
            )

        used_external_ids[external_identity] = identity
        normalized.append(chosen)

        candidates[(source_name, canonical_id)] = occurrences

        for occurrence in occurrences:
            occurrence_lookup[
                (
                    source_name,
                    occurrence["parent_kind"],
                    occurrence["parent_key"],
                    occurrence["order"],
                )
            ] = canonical_id

    # Feature has a unique constraint on edition/name/type. If two
    # different source documents define the same named feature, qualify
    # the names with their source to preserve both definitions.
    name_groups = defaultdict(list)

    for feature in normalized:
        identity = (
            feature["edition_code"],
            feature["name"].casefold(),
            feature["feature_type"],
        )
        name_groups[identity].append(feature)

    for matches in name_groups.values():
        if len(matches) < 2:
            continue

        for feature in matches:
            feature["name"] = (
                f"{feature['name']} ({feature['source_name']})"
            )

            if len(feature["name"]) > STRING_LIMITS["feature_name"]:
                raise ValueError(
                    f"Disambiguated feature name exceeds database limit: "
                    f"{feature['name']}"
                )

    return normalized, occurrence_lookup, candidates


def build_grants(data, occurrence_lookup, candidates):
    class_grants = []
    subclass_grants = []

    for (source_name, _), occurrences in candidates.items():
        for occurrence in occurrences:
            feature_id = occurrence_lookup[
                (
                    source_name,
                    occurrence["parent_kind"],
                    occurrence["parent_key"],
                    occurrence["order"],
                )
            ]

            for gained in occurrence["gained_at"]:
                grant = {
                    "feature_external_id": feature_id,
                    "source_name": source_name,
                    "parent_external_id": occurrence["parent_key"],
                    "character_level": gained["level"],
                    "display_order": occurrence["order"],
                    "grant_notes": gained.get("detail"),
                }

                if occurrence["parent_kind"] == "classes":
                    class_grants.append(grant)
                else:
                    subclass_grants.append(grant)

    def deduplicate(records, identity_fields):
        result = {}

        for record in records:
            identity = tuple(record[field] for field in identity_fields)
            result[identity] = record

        return list(result.values())

    class_grants = deduplicate(
        class_grants,
        (
            "source_name",
            "parent_external_id",
            "feature_external_id",
            "character_level",
        ),
    )

    subclass_grants = deduplicate(
        subclass_grants,
        (
            "source_name",
            "parent_external_id",
            "feature_external_id",
            "character_level",
        ),
    )

    return class_grants, subclass_grants


def build_progressions(data):
    """Build 20 level rows with the correct bonus for each level."""

    progressions = []

    for class_record in data["classes"]:
        document_key = class_record["document"]["key"]
        config = DOCUMENTS[document_key]

        proficiency_values = {}
        tables = {}

        for feature in class_record["features"]:
            feature_type = feature["feature_type"]
            feature_name = feature["name"]
            table_data = feature.get("data_for_class_table") or []

            if feature_type == "PROFICIENCY_BONUS":
                for item in table_data:
                    value = item["column_value"]

                    if value is None:
                        raise ValueError(
                            f"Missing proficiency bonus for "
                            f"{class_record['name']} level {item['level']}."
                        )

                    match = re.fullmatch(r"\+?(\d+)", str(value).strip())

                    if not match:
                        raise ValueError(
                            f"Invalid proficiency bonus {value!r} "
                            f"for {class_record['name']}."
                        )

                    proficiency_values[item["level"]] = int(match.group(1))
                continue

            if table_data:
                feature_key = feature.get("key")

                if not feature_key:
                    raise ValueError(
                        f"Class table feature {feature_name!r} on "
                        f"{class_record['name']} has no source key."
                    )

                table_key = f"{feature_type}:{feature_key}"

                if table_key in tables:
                    raise ValueError(
                        f"Duplicate class table source key {table_key} "
                        f"on {class_record['name']}."
                    )

                tables[table_key] = {
                    str(item["level"]): item.get("column_value")
                    for item in table_data
                }

        if not proficiency_values:
            raise ValueError(
                f"No proficiency bonus table found for "
                f"{class_record['name']} ({document_key})."
            )

        current_bonus = None
        progression_data_by_level = {}

        for level in range(1, MAX_LEVEL + 1):
            if level in proficiency_values:
                current_bonus = proficiency_values[level]

            if current_bonus is None:
                raise ValueError(
                    f"No proficiency bonus available at level {level} "
                    f"for {class_record['name']}."
                )

            level_tables = {}

            for table_key, values in tables.items():
                if str(level) in values:
                    level_tables[table_key] = values[str(level)]

            progression_data_by_level[level] = {
                "tables": level_tables,
                "proficiency_bonus": current_bonus,
            }

        progression_data_by_level[1]["source_metadata"] = {
            "caster_type": class_record.get("caster_type"),
            "hit_points": class_record.get("hit_points"),
            "primary_abilities": class_record.get("primary_abilities"),
            "saving_throws": class_record.get("saving_throws"),
            "proficiencies": [
                feature
                for feature in class_record["features"]
                if feature["feature_type"] == "PROFICIENCIES"
            ],
            "core_traits": [
                feature
                for feature in class_record["features"]
                if feature["feature_type"] == "CORE_TRAITS_TABLE"
            ],
            "class_feature_option_lists": [
                feature
                for feature in class_record["features"]
                if feature["feature_type"] == "CLASS_FEATURE_OPTION_LIST"
            ],
            "other_class_tables": [
                feature
                for feature in class_record["features"]
                if feature["feature_type"] not in (
                    "CLASS_LEVEL_FEATURE",
                    "PROFICIENCY_BONUS",
                    "CLASS_TABLE_DATA",
                    "SPELL_SLOTS",
                    "CORE_TRAITS_TABLE",
                    "CLASS_FEATURE_OPTION_LIST",
                    "PROFICIENCIES",
                    "STARTING_EQUIPMENT",
                )
            ],
        }

        for level in range(1, MAX_LEVEL + 1):
            progression_data = progression_data_by_level[level]

            progressions.append({
                "edition_code": config["edition_code"],
                "source_name": config["source_name"],
                "class_external_id": class_record["key"],
                "level": level,
                "proficiency_bonus": progression_data["proficiency_bonus"],
                "features_summary": None,
                "progression_data": progression_data,
            })

    return progressions


def seed_references(session, data):
    """Upsert editions and sources from the Open5e document metadata."""

    for edition_code in sorted(data["edition_codes"]):
        config = EDITION_CONFIG[edition_code]

        statement = insert(Edition).values(
            code=edition_code,
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
        )

        session.execute(statement)

    documents = {}

    for kind in ("classes", "subclasses"):
        for record in data[kind]:
            document = record["document"]
            documents[document["key"]] = document

    for document_key, document in documents.items():
        config = DOCUMENTS[document_key]
        publisher = document.get("publisher") or {}
        game_system = document.get("gamesystem") or {}

        description_parts = []

        if publisher.get("name"):
            description_parts.append(
                f"Publisher: {publisher['name']}."
            )

        if game_system.get("name"):
            description_parts.append(
                f"Game system: {game_system['name']}."
            )

        statement = insert(Source).values(
            name=config["source_name"],
            url=document.get("permalink"),
            description=" ".join(description_parts) or None,
        )

        statement = statement.on_conflict_do_update(
            index_elements=["name"],
            set_={
                "url": statement.excluded.url,
                "description": statement.excluded.description,
            },
        )

        session.execute(statement)

    edition_codes = data["edition_codes"]
    source_names = data["source_names"]

    editions = {
        item.code: item.id
        for item in session.scalars(
            select(Edition).where(Edition.code.in_(edition_codes))
        )
    }

    sources = {
        item.name: item.id
        for item in session.scalars(
            select(Source).where(Source.name.in_(source_names))
        )
    }

    if edition_codes - editions.keys():
        raise ValueError(
            f"Missing editions: {sorted(edition_codes - editions.keys())}"
        )

    if source_names - sources.keys():
        raise ValueError(
            f"Missing sources: {sorted(source_names - sources.keys())}"
        )

    return editions, sources


def make_class_values(records, editions, sources):
    return [
        {
            "edition_id": editions[record["edition_code"]],
            "source_id": sources[record["source_name"]],
            "external_id": record["external_id"],
            "name": record["name"],
            "description": record["description"],
            "hit_die": record["hit_die"],
            "primary_ability": record["primary_ability"],
            "saving_throw_proficiency_ids": (
                record["saving_throw_proficiency_ids"]
            ),
            "starting_equipment": record["starting_equipment"],
            "multiclassing": record["multiclassing"],
            "is_playable": record["is_playable"],
        }
        for record in records
    ]


def make_subclass_values(records, editions, sources, parent_class_ids):
    values = []

    for record in records:
        edition_id = editions[record["edition_code"]]
        parent_key = (
            edition_id,
            record["parent_name"].casefold(),
        )

        if parent_key not in parent_class_ids:
            raise ValueError(
                f"Could not resolve parent class "
                f"{record['parent_name']!r} for subclass "
                f"{record['name']!r} ({record['source_name']}). "
                f"Expected a class in edition {record['edition_code']}."
            )

        values.append({
            "class_id": parent_class_ids[parent_key],
            "edition_id": edition_id,
            "source_id": sources[record["source_name"]],
            "external_id": record["external_id"],
            "name": record["name"],
            "description": record["description"],
            "subclass_level": record["subclass_level"],
        })

    return values


def make_feature_values(records, editions, sources):
    return [
        {
            "edition_id": editions[record["edition_code"]],
            "source_id": sources[record["source_name"]],
            "external_id": record["external_id"],
            "name": record["name"],
            "feature_type": record["feature_type"],
            "description": record["description"],
            "mechanics": record["mechanics"],
        }
        for record in records
    ]


def upsert_records(session, model, records, conflict_columns):
    """Insert or update source-owned records in batches."""

    if not records:
        return

    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start:start + BATCH_SIZE]
        statement = insert(model).values(batch)

        update_fields = {
            column.key: getattr(statement.excluded, column.key)
            for column in model.__table__.columns
            if column.key in batch[0]
            and column.key not in conflict_columns
            and column.key != "id"
        }

        statement = statement.on_conflict_do_update(
            index_elements=list(conflict_columns),
            set_=update_fields,
        )

        session.execute(statement)


def fetch_class_ids(session, records, sources):
    identifiers = [
        (sources[record["source_name"]], record["external_id"])
        for record in records
    ]

    result = {}

    for start in range(0, len(identifiers), BATCH_SIZE):
        batch = identifiers[start:start + BATCH_SIZE]

        statement = select(
            CharacterClass.id,
            CharacterClass.source_id,
            CharacterClass.external_id,
        ).where(
            tuple_(
                CharacterClass.source_id,
                CharacterClass.external_id,
            ).in_(batch)
        )

        for class_id, source_id, external_id in session.execute(statement):
            result[(source_id, external_id)] = class_id

    return result


def fetch_parent_class_ids(session, edition_ids):
    """Fetch all classes in the selected editions for subclass linking."""

    result = {}

    statement = select(
        CharacterClass.id,
        CharacterClass.edition_id,
        CharacterClass.name,
    ).where(
        CharacterClass.edition_id.in_(set(edition_ids))
    )

    for class_id, edition_id, name in session.execute(statement):
        key = (edition_id, name.casefold())

        if key in result and result[key] != class_id:
            raise ValueError(
                f"Ambiguous parent class name in edition: {name}"
            )

        result[key] = class_id

    return result


def fetch_subclass_ids(session, records, sources):
    identifiers = [
        (sources[record["source_name"]], record["external_id"])
        for record in records
    ]

    result = {}

    for start in range(0, len(identifiers), BATCH_SIZE):
        batch = identifiers[start:start + BATCH_SIZE]

        statement = select(
            Subclass.id,
            Subclass.source_id,
            Subclass.external_id,
        ).where(
            tuple_(
                Subclass.source_id,
                Subclass.external_id,
            ).in_(batch)
        )

        for subclass_id, source_id, external_id in session.execute(statement):
            result[(source_id, external_id)] = subclass_id

    return result


def fetch_feature_ids(session, records, sources):
    identifiers = [
        (sources[record["source_name"]], record["external_id"])
        for record in records
    ]

    result = {}

    for start in range(0, len(identifiers), BATCH_SIZE):
        batch = identifiers[start:start + BATCH_SIZE]

        statement = select(
            Feature.id,
            Feature.source_id,
            Feature.external_id,
        ).where(
            tuple_(
                Feature.source_id,
                Feature.external_id,
            ).in_(batch)
        )

        for feature_id, source_id, external_id in session.execute(statement):
            result[(source_id, external_id)] = feature_id

    return result


def validate_database_name_conflicts(
    session,
    class_values,
    subclass_values,
    feature_values,
):
    """Check alternate unique constraints before upserting."""

    for record in class_values:
        existing = session.scalar(
            select(CharacterClass).where(
                CharacterClass.edition_id == record["edition_id"],
                CharacterClass.name == record["name"],
            )
        )

        if existing and (
            existing.source_id != record["source_id"]
            or existing.external_id != record["external_id"]
        ):
            raise ValueError(
                f"Class name conflict: {record['name']}."
            )

    for record in subclass_values:
        existing = session.scalar(
            select(Subclass).where(
                Subclass.class_id == record["class_id"],
                Subclass.name == record["name"],
            )
        )

        if existing and (
            existing.source_id != record["source_id"]
            or existing.external_id != record["external_id"]
        ):
            raise ValueError(
                f"Subclass name conflict: {record['name']}."
            )

    for record in feature_values:
        existing = session.scalar(
            select(Feature).where(
                Feature.edition_id == record["edition_id"],
                Feature.name == record["name"],
                Feature.feature_type == record["feature_type"],
            )
        )

        if existing and (
            existing.source_id != record["source_id"]
            or existing.external_id != record["external_id"]
        ):
            raise ValueError(
                "Feature name/type conflict: "
                f"{record['name']} ({record['feature_type']})."
            )


def import_all(data, dry_run=False):
    classes = [
        normalize_class(record)
        for record in data["classes"]
    ]

    subclasses = [
        normalize_subclass(record)
        for record in data["subclasses"]
    ]

    features, occurrence_lookup, candidates = normalize_features(data)

    class_grants, subclass_grants = build_grants(
        data,
        occurrence_lookup,
        candidates,
    )

    progressions = build_progressions(data)

    print("\n" + "=" * 55)
    print("VALIDATED IMPORT PLAN")
    print("=" * 55)
    print(f"Classes:                  {len(classes)}")
    print(f"Subclasses:               {len(subclasses)}")
    print(f"Unique features:          {len(features)}")
    print(f"Class feature grants:     {len(class_grants)}")
    print(f"Subclass feature grants:  {len(subclass_grants)}")
    print(f"Class level progressions: {len(progressions)}")

    with SessionLocal() as session:
        transaction = session.begin()

        try:
            editions, sources = seed_references(session, data)

            class_values = make_class_values(
                classes,
                editions,
                sources,
            )

            upsert_records(
                session,
                CharacterClass,
                class_values,
                ("source_id", "external_id"),
            )

            class_ids = fetch_class_ids(session, classes, sources)

            if len(class_ids) != len(classes):
                raise ValueError(
                    "Could not resolve every imported class."
                )

            parent_class_ids = fetch_parent_class_ids(
                session,
                editions.values(),
            )

            subclass_values = make_subclass_values(
                subclasses,
                editions,
                sources,
                parent_class_ids,
            )

            feature_values = make_feature_values(
                features,
                editions,
                sources,
            )

            validate_database_name_conflicts(
                session,
                class_values,
                subclass_values,
                feature_values,
            )

            upsert_records(
                session,
                Subclass,
                subclass_values,
                ("source_id", "external_id"),
            )

            upsert_records(
                session,
                Feature,
                feature_values,
                ("source_id", "external_id"),
            )

            subclass_ids = fetch_subclass_ids(
                session,
                subclasses,
                sources,
            )

            feature_ids = fetch_feature_ids(
                session,
                features,
                sources,
            )

            if len(subclass_ids) != len(subclasses):
                raise ValueError(
                    "Could not resolve every imported subclass."
                )

            if len(feature_ids) != len(features):
                raise ValueError(
                    "Could not resolve every imported feature."
                )

            grant_values = []

            for grant in class_grants:
                source_id = sources[grant["source_name"]]
                class_id = class_ids[
                    (source_id, grant["parent_external_id"])
                ]
                feature_id = feature_ids[
                    (source_id, grant["feature_external_id"])
                ]

                grant_values.append({
                    "class_id": class_id,
                    "feature_id": feature_id,
                    "character_level": grant["character_level"],
                    "display_order": grant["display_order"],
                    "grant_notes": grant["grant_notes"],
                })

            subclass_grant_values = []

            for grant in subclass_grants:
                source_id = sources[grant["source_name"]]
                subclass_id = subclass_ids[
                    (source_id, grant["parent_external_id"])
                ]
                feature_id = feature_ids[
                    (source_id, grant["feature_external_id"])
                ]

                subclass_grant_values.append({
                    "subclass_id": subclass_id,
                    "feature_id": feature_id,
                    "character_level": grant["character_level"],
                    "display_order": grant["display_order"],
                    "grant_notes": grant["grant_notes"],
                })

            progression_values = []

            for progression in progressions:
                source_id = sources[progression["source_name"]]
                class_id = class_ids[
                    (source_id, progression["class_external_id"])
                ]

                progression_values.append({
                    "class_id": class_id,
                    "level": progression["level"],
                    "proficiency_bonus": progression["proficiency_bonus"],
                    "features_summary": progression["features_summary"],
                    "progression_data": progression["progression_data"],
                })

            upsert_records(
                session,
                ClassFeatureGrant,
                grant_values,
                ("class_id", "feature_id", "character_level"),
            )

            upsert_records(
                session,
                SubclassFeatureGrant,
                subclass_grant_values,
                ("subclass_id", "feature_id", "character_level"),
            )

            upsert_records(
                session,
                ClassLevelProgression,
                progression_values,
                ("class_id", "level"),
            )

            print("\n" + "=" * 55)
            print("CLASS IMPORT SUMMARY")
            print("=" * 55)
            print(f"Classes processed:            {len(class_values)}")
            print(f"Subclasses processed:         {len(subclass_values)}")
            print(f"Features processed:           {len(feature_values)}")
            print(f"Class grants synchronized:    {len(grant_values)}")
            print(
                f"Subclass grants synchronized: "
                f"{len(subclass_grant_values)}"
            )
            print(f"Progression rows:              {len(progression_values)}")

            if dry_run:
                transaction.rollback()
                print("\nDRY RUN: All database changes rolled back.")
            else:
                transaction.commit()
                print("\nClass import committed successfully.")

        except Exception:
            if transaction.is_active:
                transaction.rollback()
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Import Open5e classes and subclasses."
    )

    parser.add_argument(
        "--document",
        nargs="+",
        choices=sorted(DOCUMENTS),
        default=sorted(DOCUMENTS),
        help="Document(s) to import. Defaults to all seven documents.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform database operations and roll back all changes.",
    )

    args = parser.parse_args()

    data = load_all_data(args.document)

    validate_source_identifiers(data)

    print("\nInput validation complete.")
    print(f"Documents:  {len(args.document)}")
    print(f"Classes:    {len(data['classes'])}")
    print(f"Subclasses: {len(data['subclasses'])}")

    import_all(data, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
