
import argparse
import json
import re
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models import (
    Edition,
    Feature,
    Source,
    Species,
    SpeciesFeatureGrant,
    SpeciesVariant,
)


INPUT_DIR = PROJECT_ROOT / "data" / "imports" / "species"

DOCUMENTS = {
    "open5e": {
        "edition_code": "2014",
        "source_name": "Open5e Originals",
        "game_system_key": "5e-2014",
        "expected_count": 1,
    },
    "srd-2014": {
        "edition_code": "2014",
        "source_name": "System Reference Document 5.1",
        "game_system_key": "5e-2014",
        "expected_count": 13,
    },
    "srd-2024": {
        "edition_code": "2024",
        "source_name": "System Reference Document 5.2",
        "game_system_key": "5e-2024",
        "expected_count": 9,
    },
    "toh": {
        "edition_code": "2014",
        "source_name": "Tome of Heroes",
        "game_system_key": "5e-2014",
        "expected_count": 40,
    },
}

BATCH_SIZE = 500
FEATURE_TYPE = "species_trait"

SIZE_PATTERN = re.compile(
    r"\b(Tiny|Small|Medium|Large|Huge|Gargantuan)\b",
    re.IGNORECASE,
)

SPEED_PATTERN = re.compile(
    r"\b(\d+)\s*(?:feet|ft\.?)\b",
    re.IGNORECASE,
)


def load_file(file_path, document_key):
    """Load and validate one Open5e species response."""

    if not file_path.exists():
        raise FileNotFoundError(f"Could not find {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        response = json.load(file)

    if not isinstance(response, dict):
        raise ValueError(f"Invalid response in {file_path}")

    records = response.get("results")

    if not isinstance(records, list):
        raise ValueError(f"Invalid results in {file_path}")

    if response.get("next") is not None:
        raise ValueError(
            f"{file_path.name} contains additional API pages."
        )

    if response.get("count") != len(records):
        raise ValueError(
            f"{file_path.name}: record count does not match API count."
        )

    config = DOCUMENTS[document_key]

    if len(records) != config["expected_count"]:
        raise ValueError(
            f"{file_path.name}: expected {config['expected_count']} "
            f"records, received {len(records)}."
        )

    seen_keys = set()

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(
                f"Invalid record {index} in {file_path.name}."
            )

        key = record.get("key")
        name = record.get("name")

        if not isinstance(key, str) or not key:
            raise ValueError(
                f"{file_path.name}: record {index} has no valid key."
            )

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"{file_path.name}: record {key} has no valid name."
            )

        if key in seen_keys:
            raise ValueError(
                f"{file_path.name}: duplicate species key {key}."
            )

        seen_keys.add(key)

        document = record.get("document") or {}

        if document.get("key") != document_key:
            raise ValueError(
                f"{key}: unexpected document key "
                f"{document.get('key')}."
            )

        if document.get("name") != config["source_name"]:
            raise ValueError(
                f"{key}: unexpected source name "
                f"{document.get('name')}."
            )

        game_system = document.get("gamesystem") or {}

        if game_system.get("key") != config["game_system_key"]:
            raise ValueError(
                f"{key}: unexpected game system."
            )

        if not isinstance(record.get("is_subspecies"), bool):
            raise ValueError(
                f"{key}: invalid is_subspecies value."
            )

        traits = record.get("traits")

        if not isinstance(traits, list):
            raise ValueError(f"{key}: traits must be a list.")

        for trait_index, trait in enumerate(traits):
            if not isinstance(trait, dict):
                raise ValueError(
                    f"{key}: invalid trait at index {trait_index}."
                )

            if not isinstance(trait.get("name"), str):
                raise ValueError(
                    f"{key}: trait {trait_index} has no valid name."
                )

            if not isinstance(trait.get("desc"), str):
                raise ValueError(
                    f"{key}: trait {trait_index} has no valid description."
                )

    return records


def load_all_data(document_keys):
    """Load all selected documents independently."""

    data = {}

    for document_key in document_keys:
        file_path = INPUT_DIR / f"open5e_{document_key}.json"

        print(f"\nReading {file_path.name}...")

        records = load_file(file_path, document_key)
        data[document_key] = records

        base_count = sum(
            not record["is_subspecies"]
            for record in records
        )
        variant_count = sum(
            record["is_subspecies"]
            for record in records
        )

        print(f"Validated: {len(records)} records.")
        print(f"  Base species: {base_count}")
        print(f"  Variants:     {variant_count}")

    return data


def find_core_trait(traits, names=(), trait_type=None):
    """Find a core species trait by name or Open5e trait type."""

    normalized_names = {name.lower() for name in names}

    for trait in traits:
        name = trait["name"].strip().lower()
        current_type = (trait.get("type") or "").upper()

        if name in normalized_names:
            return trait

        if trait_type and current_type == trait_type.upper():
            return trait

    return None


def extract_size(traits, fallback=None):
    trait = find_core_trait(
        traits,
        names=("size",),
        trait_type="SIZE",
    )

    if trait:
        match = SIZE_PATTERN.search(trait["desc"])

        if match:
            return match.group(1).title()

    return fallback


def extract_speed(traits):
    trait = find_core_trait(
        traits,
        names=("speed",),
        trait_type="SPEED",
    )

    if not trait:
        return None

    match = SPEED_PATTERN.search(trait["desc"])

    if match:
        return int(match.group(1))

    return None


def extract_ability_rules(traits):
    trait = find_core_trait(
        traits,
        names=(
            "ability score increase",
            "ability score improvement",
        ),
    )

    if trait:
        return {"text": trait["desc"]}

    return None


def extract_text_trait(traits, name):
    trait = find_core_trait(traits, names=(name,))

    if trait:
        return trait["desc"]

    return None


def normalize_species(record):
    traits = record["traits"]

    return {
        "external_id": record["key"],
        "name": record["name"],
        "description": record.get("desc") or "",
        "size": extract_size(traits, record.get("size")),
        "creature_type": record.get("creature_type") or "Humanoid",
        "base_speed": extract_speed(traits),
        "ability_score_rules": extract_ability_rules(traits),
        "age": extract_text_trait(traits, "age"),
        "alignment": extract_text_trait(traits, "alignment"),
        "languages_summary": extract_text_trait(traits, "languages"),
        "is_playable": True,
        "traits": traits,
    }


def normalize_variant(record):
    traits = record["traits"]

    return {
        "external_id": record["key"],
        "name": record["name"],
        "description": record.get("desc") or "",
        "size_override": extract_size(traits),
        "speed_override": extract_speed(traits),
        "ability_score_rules": extract_ability_rules(traits),
        "traits": traits,
        "parent_external_id": record.get("subspecies_of"),
    }


def normalize_document(records, document_key):
    """Separate base species and variants within one source document."""

    base_records = []
    variant_records = []

    for record in records:
        if record["is_subspecies"]:
            variant_records.append(normalize_variant(record))
        else:
            base_records.append(normalize_species(record))

    return {
        "species": base_records,
        "variants": variant_records,
    }

def normalize_all(data):
    normalized = {
        document_key: normalize_document(records, document_key)
        for document_key, records in data.items()
    }

    # Index all base species by edition and external ID.
    base_species_by_edition = {}

    for document_key, item in normalized.items():
        edition_code = DOCUMENTS[document_key]["edition_code"]

        edition_species = base_species_by_edition.setdefault(
            edition_code,
            set(),
        )

        edition_species.update(
            record["external_id"]
            for record in item["species"]
        )

    # Validate variant parents against all base species in that edition.
    for document_key, item in normalized.items():
        edition_code = DOCUMENTS[document_key]["edition_code"]
        available_parents = base_species_by_edition[edition_code]

        for variant in item["variants"]:
            parent_id = variant["parent_external_id"]

            if not parent_id or parent_id not in available_parents:
                raise ValueError(
                    f"{document_key}: variant {variant['name']} has "
                    f"an unresolved parent species: {parent_id}."
                )

    return normalized

def resolve_references(session, document_keys):
    """Resolve existing edition and source database records."""

    edition_codes = {
        DOCUMENTS[key]["edition_code"]
        for key in document_keys
    }

    source_names = {
        DOCUMENTS[key]["source_name"]
        for key in document_keys
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

    return editions, {
        key: sources[DOCUMENTS[key]["source_name"]]
        for key in document_keys
    }


def make_species_values(records, edition_id, source_id):
    return [
        {
            "edition_id": edition_id,
            "source_id": source_id,
            "external_id": record["external_id"],
            "name": record["name"],
            "description": record["description"],
            "size": record["size"],
            "creature_type": record["creature_type"],
            "base_speed": record["base_speed"],
            "ability_score_rules": record["ability_score_rules"],
            "age": record["age"],
            "alignment": record["alignment"],
            "languages_summary": record["languages_summary"],
            "is_playable": record["is_playable"],
        }
        for record in records
    ]


def make_variant_values(records, species_ids):
    values = []

    for record in records:
        parent_id = record["parent_external_id"]

        if parent_id not in species_ids:
            raise ValueError(
                f"Could not resolve parent for {record['name']}."
            )

        values.append({
            "species_id": species_ids[parent_id],
            "name": record["name"],
            "description": record["description"],
            "size_override": record["size_override"],
            "speed_override": record["speed_override"],
            "ability_score_rules": record["ability_score_rules"],
        })

    return values


def make_feature_values(
    species_records,
    variant_records,
    edition_id,
    source_id,
):
    """Create one feature per species/variant trait occurrence."""

    values = []
    occurrences = []
    owners = []

    for record in species_records:
        owners.append((
            record["external_id"],
            record["name"],
            None,
            record["traits"],
        ))

    for record in variant_records:
        owners.append((
            record["external_id"],
            record["name"],
            record["parent_external_id"],
            record["traits"],
        ))

    for owner_key, owner_name, parent_key, traits in owners:
        for index, trait in enumerate(traits):
            trait_name = trait["name"].strip()
            feature_name = f"{owner_name}: {trait_name}"

            if len(feature_name) > 160:
                raise ValueError(
                    f"Feature name exceeds 160 characters: {feature_name}"
                )

            external_id = f"species:{owner_key}:trait:{index}"

            if len(external_id) > 160:
                raise ValueError(
                    f"Feature external ID exceeds 160 characters: "
                    f"{external_id}"
                )

            description = trait["desc"]

            values.append({
                "edition_id": edition_id,
                "source_id": source_id,
                "external_id": external_id,
                "name": feature_name,
                "feature_type": FEATURE_TYPE,
                "description": description,
                "rules_text": description,
                "mechanics": {
                    "open5e_trait_name": trait_name,
                    "open5e_trait_type": trait.get("type"),
                    "open5e_order": trait.get("order"),
                },
            })

            occurrences.append({
                "external_id": external_id,
                "owner_key": owner_key,
                "parent_key": parent_key,
                "display_order": (
                    trait["order"]
                    if isinstance(trait.get("order"), int)
                    else index + 1
                ),
            })

    return values, occurrences


def upsert_records(session, model, records, conflict_columns):
    """Insert or update records in batches."""

    if not records:
        return

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


def fetch_species_ids(session, records):
    identifiers = [
        record["external_id"]
        for record in records
    ]

    if not identifiers:
        return {}

    rows = session.execute(
        select(Species.external_id, Species.id).where(
            Species.external_id.in_(identifiers),
        )
    ).all()

    return {
        external_id: species_id
        for external_id, species_id in rows
    }

def fetch_variant_ids(session, records, species_ids):
    resolved = {}

    for record in records:
        species_id = species_ids[record["parent_external_id"]]

        variant = session.scalar(
            select(SpeciesVariant).where(
                SpeciesVariant.species_id == species_id,
                SpeciesVariant.name == record["name"],
            )
        )

        if variant is None:
            raise ValueError(
                f"Could not resolve variant {record['name']}."
            )

        resolved[record["external_id"]] = variant.id

    return resolved


def fetch_feature_ids(session, feature_values, source_id):
    identifiers = [
        record["external_id"]
        for record in feature_values
    ]

    if not identifiers:
        return {}

    rows = session.execute(
        select(Feature.external_id, Feature.id).where(
            Feature.source_id == source_id,
            Feature.external_id.in_(identifiers),
        )
    ).all()

    return {
        external_id: feature_id
        for external_id, feature_id in rows
    }


def upsert_grants(
    session,
    occurrences,
    species_ids,
    variant_ids,
    feature_ids,
):
    """Create or update grants, including grants with NULL variant IDs."""

    created = 0
    updated = 0

    for occurrence in occurrences:
        owner_key = occurrence["owner_key"]
        parent_key = occurrence["parent_key"]

        if parent_key is None:
            species_id = species_ids[owner_key]
            variant_id = None
        else:
            species_id = species_ids[parent_key]
            variant_id = variant_ids[owner_key]

        feature_id = feature_ids[occurrence["external_id"]]

        conditions = [
            SpeciesFeatureGrant.species_id == species_id,
            SpeciesFeatureGrant.feature_id == feature_id,
        ]

        if variant_id is None:
            conditions.append(
                SpeciesFeatureGrant.variant_id.is_(None)
            )
        else:
            conditions.append(
                SpeciesFeatureGrant.variant_id == variant_id
            )

        grant = session.scalar(
            select(SpeciesFeatureGrant).where(*conditions)
        )

        if grant is None:
            session.add(
                SpeciesFeatureGrant(
                    species_id=species_id,
                    variant_id=variant_id,
                    feature_id=feature_id,
                    display_order=occurrence["display_order"],
                )
            )
            created += 1
        else:
            grant.display_order = occurrence["display_order"]
            updated += 1

    session.flush()

    return created, updated


def import_all(data, dry_run=False):
    normalized = normalize_all(data)

    total_species = sum(
        len(item["species"])
        for item in normalized.values()
    )

    total_variants = sum(
        len(item["variants"])
        for item in normalized.values()
    )

    print("\n" + "=" * 55)
    print("VALIDATED SPECIES IMPORT PLAN")
    print("=" * 55)
    print(f"Documents:    {len(normalized)}")
    print(f"Base species: {total_species}")
    print(f"Variants:     {total_variants}")

    with SessionLocal() as session:
        transaction = session.begin()

        try:
            editions, sources = resolve_references(
                session,
                list(normalized),
            )

            # First pass: insert every base species before resolving
            # any variant parent references.
            all_species_ids = {}

            for document_key, item in normalized.items():
                config = DOCUMENTS[document_key]
                edition_code = config["edition_code"]
                edition_id = editions[edition_code]
                source_id = sources[document_key]

                species_values = make_species_values(
                    item["species"],
                    edition_id,
                    source_id,
                )

                upsert_records(
                    session,
                    Species,
                    species_values,
                    ("source_id", "external_id"),
                )

            # Resolve all base species by edition, allowing variants
            # to reference parents published by another document.
            edition_codes = {
                DOCUMENTS[key]["edition_code"]
                for key in normalized
            }

            for edition_code in edition_codes:
                edition_species_records = [
                    record
                    for document_key, item in normalized.items()
                    if DOCUMENTS[document_key]["edition_code"]
                    == edition_code
                    for record in item["species"]
                ]

                species_ids = fetch_species_ids(
                    session,
                    edition_species_records,
                )

                if len(species_ids) != len(edition_species_records):
                    raise ValueError(
                        f"Could not resolve every {edition_code} "
                        f"base species."
                    )

                all_species_ids[edition_code] = species_ids

            total_features = 0
            total_grants = 0
            total_updated_grants = 0

            # Second pass: variants, traits, and grants.
            for document_key, item in normalized.items():
                config = DOCUMENTS[document_key]
                edition_code = config["edition_code"]
                edition_id = editions[edition_code]
                source_id = sources[document_key]

                species_records = item["species"]
                variant_records = item["variants"]
                species_ids = all_species_ids[edition_code]

                print(f"\nProcessing {document_key}...")

                variant_values = make_variant_values(
                    variant_records,
                    species_ids,
                )

                upsert_records(
                    session,
                    SpeciesVariant,
                    variant_values,
                    ("species_id", "name"),
                )

                variant_ids = fetch_variant_ids(
                    session,
                    variant_records,
                    species_ids,
                )

                feature_values, occurrences = make_feature_values(
                    species_records,
                    variant_records,
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
                        f"Could not resolve every {document_key} trait."
                    )

                created, updated = upsert_grants(
                    session,
                    occurrences,
                    species_ids,
                    variant_ids,
                    feature_ids,
                )

                total_features += len(feature_values)
                total_grants += created
                total_updated_grants += updated

                print(f"  Species:          {len(species_records)}")
                print(f"  Variants:         {len(variant_values)}")
                print(f"  Traits:           {len(feature_values)}")
                print(f"  Grants created:   {created}")
                print(f"  Grants updated:   {updated}")

            print("\n" + "=" * 55)
            print("SPECIES IMPORT SUMMARY")
            print("=" * 55)
            print(f"Base species:       {total_species}")
            print(f"Variants:           {total_variants}")
            print(f"Features:           {total_features}")
            print(f"Grants created:     {total_grants}")
            print(f"Grants updated:     {total_updated_grants}")

            if dry_run:
                transaction.rollback()
                print("\nDry run completed. No changes committed.")
            else:
                transaction.commit()
                print("\nSpecies import committed successfully.")

        except Exception:
            if transaction.is_active:
                transaction.rollback()
            raise

def main():
    parser = argparse.ArgumentParser(
        description="Import Open5e species and species traits."
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
        help="Validate and execute the import, then roll back.",
    )

    args = parser.parse_args()

    data = load_all_data(args.document)
    import_all(data, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
