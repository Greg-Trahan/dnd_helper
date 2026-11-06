
import argparse
import json
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
INPUT_DIR = PROJECT_ROOT / "data" / "imports" / "equipment"

sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models import (
    Edition,
    Equipment,
    EquipmentCategory,
    EquipmentPropertyDefinition,
    EquipmentPropertyLink,
    Source,
)


DOCUMENTS = {
    "srd-2014": {
        "edition_code": "2014",
        "source_name": "System Reference Document 5.1",
        "game_system": "5e-2014",
        "counts": {"items": 237, "weapons": 37, "armor": 12},
    },
    "srd-2024": {
        "edition_code": "2024",
        "source_name": "System Reference Document 5.2",
        "game_system": "5e-2024",
        "counts": {"items": 203, "weapons": 38, "armor": 13},
    },
}


def load_resource(document_key, resource):
    path = (
        INPUT_DIR
        / resource
        / f"open5e_{document_key}.json"
    )

    if not path.exists():
        raise FileNotFoundError(path)

    data = json.loads(path.read_text())

    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: expected JSON object.")

    if data.get("next") is not None:
        raise ValueError(f"{path.name}: pagination is incomplete.")

    records = data.get("results")

    if not isinstance(records, list):
        raise ValueError(f"{path.name}: missing results list.")

    expected = DOCUMENTS[document_key]["counts"][resource]

    if data.get("count") != expected or len(records) != expected:
        raise ValueError(
            f"{path.name}: expected {expected} records; "
            f"found count={data.get('count')}, results={len(records)}."
        )

    seen = set()

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(
                f"{path.name}: record {index} is not an object."
            )

        key = record.get("key")

        if not isinstance(key, str) or not key.strip():
            raise ValueError(
                f"{path.name}: record {index} has no key."
            )

        if key in seen:
            raise ValueError(
                f"{path.name}: duplicate key {key}."
            )

        seen.add(key)

        document = record.get("document")

        if not isinstance(document, dict):
            raise ValueError(
                f"{path.name}: {key} has no document metadata."
            )

        if document.get("key") != document_key:
            raise ValueError(
                f"{path.name}: {key} belongs to "
                f"{document.get('key')}, not {document_key}."
            )

        gamesystem = document.get("gamesystem") or {}

        if gamesystem.get("key") != DOCUMENTS[document_key]["game_system"]:
            raise ValueError(
                f"{path.name}: {key} has unexpected game system."
            )

    return records


def decimal_value(value, field, external_id):
    if value is None:
        return None

    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(
            f"{external_id}: invalid {field}: {value!r}"
        ) from None

    if not result.is_finite():
        raise ValueError(
            f"{external_id}: non-finite {field}: {value!r}"
        )

    return result


def load_all_documents():
    data = {}

    for document_key, metadata in DOCUMENTS.items():
        print(f"\nReading {document_key}...")

        data[document_key] = {
            resource: load_resource(document_key, resource)
            for resource in ("items", "weapons", "armor")
        }

        for resource, records in data[document_key].items():
            print(f"  {resource.capitalize():8} {len(records):4}")

    return data


def normalize_all(data):
    equipment_records = []
    category_names = defaultdict(set)
    property_definitions = {}
    property_links = []
    total_weapons = 0
    total_armor = 0

    for document_key, resources in data.items():
        metadata = DOCUMENTS[document_key]
        edition_code = metadata["edition_code"]
        source_name = metadata["source_name"]

        items = resources["items"]
        weapons = resources["weapons"]
        armor = resources["armor"]

        weapon_by_key = {record["key"]: record for record in weapons}
        armor_by_key = {record["key"]: record for record in armor}

        # Match specialized weapon records to equipment by their item key.
        if set(weapon_by_key) - {item["key"] for item in items}:
            raise ValueError(
                f"{document_key}: weapon records without matching items."
            )

        # Armor uses the embedded armor key, not necessarily the item key.
        armor_item_map = {}

        for item in items:
            embedded = item.get("armor")

            if embedded is None:
                continue

            if not isinstance(embedded, dict):
                raise ValueError(
                    f"{item['key']}: embedded armor must be an object."
                )

            armor_key = embedded.get("key")

            if armor_key not in armor_by_key:
                raise ValueError(
                    f"{item['key']}: embedded armor key "
                    f"{armor_key!r} has no matching armor record."
                )

            if armor_key in armor_item_map:
                raise ValueError(
                    f"{document_key}: armor key {armor_key} "
                    "matches multiple equipment items."
                )

            armor_item_map[armor_key] = item

        if set(armor_item_map) != set(armor_by_key):
            missing = set(armor_by_key) - set(armor_item_map)
            raise ValueError(
                f"{document_key}: unmatched armor records: "
                f"{sorted(missing)}"
            )

        for item in items:
            external_id = item["key"]
            name = item.get("name")

            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    f"{external_id}: missing equipment name."
                )

            if len(name) > 160:
                raise ValueError(
                    f"{external_id}: equipment name exceeds 160 characters."
                )

            category = item.get("category")

            if not isinstance(category, str) or not category.strip():
                category = "Uncategorized"

            if len(category) > 100:
                raise ValueError(
                    f"{external_id}: category exceeds 100 characters."
                )

            description = item.get("desc")

            if description is not None and not isinstance(description, str):
                raise ValueError(
                    f"{external_id}: description must be text."
                )

            cost = decimal_value(item.get("cost"), "cost", external_id)
            weight = decimal_value(item.get("weight"), "weight", external_id)

            if cost is not None and cost < 0:
                raise ValueError(f"{external_id}: negative cost.")

            if weight is not None and weight < 0:
                raise ValueError(f"{external_id}: negative weight.")

            weapon_record = weapon_by_key.get(external_id)

            embedded_armor = item.get("armor")
            armor_record = (
                armor_by_key[embedded_armor["key"]]
                if embedded_armor is not None
                else None
            )

            properties = {
                "source_category": item.get("category"),
                "size": item.get("size"),
                "weight_unit": item.get("weight_unit"),
                "crossreferences": item.get("crossreferences"),
            }

            equipment_records.append({
                "edition_code": edition_code,
                "source_name": source_name,
                "external_id": external_id,
                "name": name,
                "description": description,
                "category_name": category,
                "cost_quantity": cost,
                "cost_unit": "gp" if cost is not None else None,
                "weight": weight,
                "rarity": None,
                "is_magical": False,
                "properties": properties,
                "weapon_data": weapon_record,
                "armor_data": armor_record,
            })

            category_names[edition_code].add(category)

            if weapon_record is not None:
                total_weapons += 1

                weapon_properties = weapon_record.get("properties") or []

                for weapon_property in weapon_properties:
                    definition = weapon_property.get("property") or {}
                    property_name = definition.get("name")

                    if (
                        not isinstance(property_name, str)
                        or not property_name.strip()
                    ):
                        raise ValueError(
                            f"{external_id}: weapon property has no name."
                        )

                    if len(property_name) > 80:
                        raise ValueError(
                            f"{external_id}: property name exceeds 80 characters."
                        )

                    description = definition.get("desc")

                    if description is not None and not isinstance(
                        description, str
                    ):
                        raise ValueError(
                            f"{external_id}: invalid property description."
                        )

                    property_key = (edition_code, property_name)

                    if property_key not in property_definitions:
                        property_definitions[property_key] = {
                            "edition_code": edition_code,
                            "name": property_name,
                            "description": description,
                        }
                    elif (
                        not property_definitions[property_key]["description"]
                        and description
                    ):
                        property_definitions[property_key]["description"] = (
                            description
                        )

                    detail = weapon_property.get("detail")

                    if detail is not None:
                        detail = str(detail)

                    if detail is not None and len(detail) > 160:
                        raise ValueError(
                            f"{external_id}: property detail exceeds "
                            "160 characters."
                        )

                    property_links.append({
                        "edition_code": edition_code,
                        "external_id": external_id,
                        "property_name": property_name,
                        "value": detail,
                    })

            if armor_record is not None:
                total_armor += 1

    identifiers = [
        (record["edition_code"], record["external_id"])
        for record in equipment_records
    ]

    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Duplicate equipment identifiers across documents.")

    names = [
        (record["edition_code"], record["name"])
        for record in equipment_records
    ]

    if len(names) != len(set(names)):
        duplicates = sorted({
            name for edition, name in names
            if names.count((edition, name)) > 1
        })
        raise ValueError(
            f"Duplicate equipment names within an edition: {duplicates}"
        )

    print("\nValidated normalized data:")
    print(f"  Equipment:           {len(equipment_records)}")
    print(f"  Weapon records:      {total_weapons}")
    print(f"  Armor records:       {total_armor}")
    print(f"  Categories:          {sum(map(len, category_names.values()))}")
    print(f"  Property definitions:{len(property_definitions):5}")
    print(f"  Property links:      {len(property_links)}")

    if total_weapons != 75 or total_armor != 25:
        raise ValueError("Specialized equipment record totals are incorrect.")

    return (
        equipment_records,
        category_names,
        list(property_definitions.values()),
        property_links,
    )


def resolve_references(session, records):
    edition_codes = {record["edition_code"] for record in records}
    source_names = {record["source_name"] for record in records}

    editions = {
        row.code: row.id
        for row in session.scalars(
            select(Edition).where(Edition.code.in_(edition_codes))
        )
    }

    sources = {
        row.name: row.id
        for row in session.scalars(
            select(Source).where(Source.name.in_(source_names))
        )
    }

    missing_editions = edition_codes - editions.keys()
    missing_sources = source_names - sources.keys()

    if missing_editions:
        raise ValueError(
            f"Missing editions: {sorted(missing_editions)}"
        )

    if missing_sources:
        raise ValueError(
            f"Missing sources: {sorted(missing_sources)}"
        )

    return editions, sources


def check_existing_name_conflicts(session, records, editions, sources):
    names = {
        (editions[record["edition_code"]], record["name"])
        for record in records
    }

    existing = session.scalars(
        select(Equipment).where(
            Equipment.edition_id.in_({edition for edition, _ in names}),
            Equipment.name.in_({name for _, name in names}),
        )
    )

    incoming = {
        (
            sources[record["source_name"]],
            record["external_id"],
        )
        for record in records
    }

    for row in existing:
        identity = (row.source_id, row.external_id)

        if identity not in incoming:
            raise ValueError(
                f"Equipment name conflict: {row.name!r} already exists "
                f"in edition {row.edition_id} with a different source ID."
            )


def make_equipment_values(records, editions, sources, categories):
    values = []

    for record in records:
        edition_id = editions[record["edition_code"]]
        category_id = categories[(edition_id, record["category_name"])]

        values.append({
            "edition_id": edition_id,
            "category_id": category_id,
            "source_id": sources[record["source_name"]],
            "external_id": record["external_id"],
            "name": record["name"],
            "description": record["description"],
            "cost_quantity": record["cost_quantity"],
            "cost_unit": record["cost_unit"],
            "weight": record["weight"],
            "rarity": record["rarity"],
            "is_magical": record["is_magical"],
            "properties": record["properties"],
            "weapon_data": record["weapon_data"],
            "armor_data": record["armor_data"],
            "container_capacity": None,
        })

    return values


def import_all(
    session,
    records,
    category_names,
    property_definitions,
    property_links,
    dry_run=False,
):
    editions, sources = resolve_references(session, records)

    check_existing_name_conflicts(
        session, records, editions, sources
    )

    # Count existing equipment by its stable source identity.
    identities = {
        (sources[record["source_name"]], record["external_id"])
        for record in records
    }

    existing_equipment = {
        (row.source_id, row.external_id)
        for row in session.scalars(
            select(Equipment).where(
                Equipment.source_id.in_(sources.values()),
                Equipment.external_id.is_not(None),
            )
        )
        if (row.source_id, row.external_id) in identities
    }

    new_equipment = len(identities - existing_equipment)
    existing_count = len(existing_equipment)

    # Resolve existing category and property definitions.
    category_pairs = {
        (editions[edition_code], name)
        for edition_code, names in category_names.items()
        for name in names
    }

    existing_categories = {
        (row.edition_id, row.name): row.id
        for row in session.scalars(
            select(EquipmentCategory).where(
                EquipmentCategory.edition_id.in_(editions.values())
            )
        )
        if (row.edition_id, row.name) in category_pairs
    }

    property_pairs = {
        (
            editions[record["edition_code"]],
            record["name"],
        )
        for record in property_definitions
    }

    existing_properties = {
        (row.edition_id, row.name): row.id
        for row in session.scalars(
            select(EquipmentPropertyDefinition).where(
                EquipmentPropertyDefinition.edition_id.in_(editions.values())
            )
        )
        if (row.edition_id, row.name) in property_pairs
    }

    print("\nImport summary:")
    print(f"  New equipment:              {new_equipment}")
    print(f"  Existing equipment:         {existing_count}")
    print(
        "  New categories:             "
        f"{len(category_pairs) - len(existing_categories)}"
    )
    print(
        "  Existing categories:        "
        f"{len(existing_categories)}"
    )
    print(
        "  New property definitions:   "
        f"{len(property_pairs) - len(existing_properties)}"
    )
    print(
        "  Existing property definitions:"
        f" {len(existing_properties)}"
    )
    print(f"  Property links to sync:     {len(property_links)}")

    if dry_run:
        print("\nDry run completed. No changes committed.")
        return

    # Upsert equipment categories.
    category_values = [
        {"edition_id": edition_id, "name": name}
        for edition_id, name in sorted(category_pairs)
    ]

    if category_values:
        statement = insert(EquipmentCategory).values(category_values)
        statement = statement.on_conflict_do_update(
            index_elements=[
                EquipmentCategory.edition_id,
                EquipmentCategory.name,
            ],
            set_={"name": statement.excluded.name},
        )
        session.execute(statement)

    categories = {
        (row.edition_id, row.name): row.id
        for row in session.scalars(
            select(EquipmentCategory).where(
                EquipmentCategory.edition_id.in_(editions.values())
            )
        )
        if (row.edition_id, row.name) in category_pairs
    }

    # Upsert equipment property definitions.
    definition_values = [
        {
            "edition_id": editions[record["edition_code"]],
            "name": record["name"],
            "description": record["description"],
        }
        for record in property_definitions
    ]

    if definition_values:
        statement = insert(
            EquipmentPropertyDefinition
        ).values(definition_values)

        statement = statement.on_conflict_do_update(
            index_elements=[
                EquipmentPropertyDefinition.edition_id,
                EquipmentPropertyDefinition.name,
            ],
            set_={
                "description": statement.excluded.description,
            },
        )
        session.execute(statement)

    properties = {
        (row.edition_id, row.name): row.id
        for row in session.scalars(
            select(EquipmentPropertyDefinition).where(
                EquipmentPropertyDefinition.edition_id.in_(editions.values())
            )
        )
        if (row.edition_id, row.name) in property_pairs
    }

    # Upsert equipment records by source and external ID.
    equipment_values = make_equipment_values(
        records, editions, sources, categories
    )

    statement = insert(Equipment).values(equipment_values)

    update_columns = [
        "edition_id",
        "category_id",
        "name",
        "description",
        "cost_quantity",
        "cost_unit",
        "weight",
        "rarity",
        "is_magical",
        "properties",
        "weapon_data",
        "armor_data",
        "container_capacity",
    ]

    statement = statement.on_conflict_do_update(
        index_elements=[
            Equipment.source_id,
            Equipment.external_id,
        ],
        set_={
            column: getattr(statement.excluded, column)
            for column in update_columns
        },
    )

    session.execute(statement)

    # Resolve equipment IDs for every imported source record.
    equipment_lookup = {
        (sources[record["source_name"]], record["external_id"]):
        (editions[record["edition_code"]], record["name"])
        for record in records
    }

    equipment_ids = {
        (row.source_id, row.external_id): row.id
        for row in session.scalars(
            select(Equipment).where(
                Equipment.source_id.in_(sources.values()),
                Equipment.external_id.is_not(None),
            )
        )
        if (row.source_id, row.external_id) in equipment_lookup
    }

    if len(equipment_ids) != len(records):
        raise ValueError("Could not resolve every imported equipment ID.")

    # Remove old property links for imported weapons, then rebuild them.
    weapon_ids = {
        equipment_ids[(sources[record["source_name"]], record["external_id"])]
        for record in records
        if record["weapon_data"] is not None
    }

    if weapon_ids:
        session.execute(
            delete(EquipmentPropertyLink).where(
                EquipmentPropertyLink.equipment_id.in_(weapon_ids)
            )
        )

    link_values = []

    for link in property_links:
        source_id = sources[
            next(
                record["source_name"]
                for record in records
                if record["edition_code"] == link["edition_code"]
                and record["external_id"] == link["external_id"]
            )
        ]

        equipment_id = equipment_ids[
            (source_id, link["external_id"])
        ]

        property_id = properties[
            (
                editions[link["edition_code"]],
                link["property_name"],
            )
        ]

        link_values.append({
            "equipment_id": equipment_id,
            "property_id": property_id,
            "value": link["value"],
        })

    if link_values:
        session.execute(
            insert(EquipmentPropertyLink).values(link_values)
        )

    print("\nEquipment import committed successfully.")
    print(f"  Equipment records: {len(equipment_values)}")
    print(f"  Weapon property links: {len(link_values)}")


def main():
    parser = argparse.ArgumentParser(
        description="Import Open5e SRD equipment."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report without committing changes.",
    )
    args = parser.parse_args()

    data = load_all_documents()

    (
        records,
        category_names,
        property_definitions,
        property_links,
    ) = normalize_all(data)

    with SessionLocal() as session:
        with session.begin():
            import_all(
                session,
                records,
                category_names,
                property_definitions,
                property_links,
                dry_run=args.dry_run,
            )

            if args.dry_run:
                session.rollback()


if __name__ == "__main__":
    main()
