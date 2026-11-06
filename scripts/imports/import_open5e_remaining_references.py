import argparse
import sys
from pathlib import Path

import httpx
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database.session import SessionLocal
from app.models.edition import Edition
from app.models.source import Source
from app.models.language import Language
from app.models.proficiency import Proficiency


BASE_URL = "https://api.open5e.com/v2/"

EXPECTED = {
    "languages": {"void-speech"},
    "skills": {"a5e-ag_culture", "a5e-ag_engineering"},
}


def fetch_all(endpoint):
    records = []
    url = f"{BASE_URL}{endpoint}/"
    params = {"limit": 100}

    with httpx.Client(timeout=30) as client:
        while url:
            response = client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

            if not isinstance(payload, dict):
                raise ValueError(f"Invalid {endpoint} response")

            results = payload.get("results")
            if not isinstance(results, list):
                raise ValueError(f"Invalid results from {endpoint}")

            records.extend(results)
            url = payload.get("next")
            params = None

    return records


def get_source(session, name):
    source = session.scalar(
        select(Source).where(Source.name == name)
    )
    if source is None:
        raise ValueError(f"Required source not found: {name}")
    return source


def upsert_tome_of_beasts_source(session, document):
    publisher = document.get("publisher") or {}
    gamesystem = document.get("gamesystem") or {}

    record = {
        "name": document["name"],
        "url": document.get("permalink"),
        "description": (
            f"Publisher: {publisher['name']}. "
            f"Game system: {gamesystem['name']}."
            if publisher.get("name") and gamesystem.get("name")
            else None
        ),
    }

    statement = insert(Source).values(**record)
    statement = statement.on_conflict_do_update(
        index_elements=["name"],
        set_={
            "url": statement.excluded.url,
            "description": statement.excluded.description,
        },
    ).returning(Source.id)

    return session.execute(statement).scalar_one()


def validate_records(languages, skills):
    language_records = [
        record for record in languages
        if record.get("key") in EXPECTED["languages"]
    ]
    skill_records = [
        record for record in skills
        if record.get("key") in EXPECTED["skills"]
    ]

    actual_languages = {r["key"] for r in language_records}
    actual_skills = {r["key"] for r in skill_records}

    if actual_languages != EXPECTED["languages"]:
        raise ValueError(
            f"Unexpected language records: {actual_languages}"
        )

    if actual_skills != EXPECTED["skills"]:
        raise ValueError(
            f"Unexpected skill records: {actual_skills}"
        )

    for record in language_records:
        document = record.get("document") or {}
        if document.get("key") != "tob":
            raise ValueError("Void Speech has unexpected source")

    for record in skill_records:
        if record.get("document") != "a5e-ag":
            raise ValueError(
                f"Unexpected source for skill {record['name']}"
            )

    return language_records, skill_records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and roll back without committing.",
    )
    args = parser.parse_args()

    print("Fetching Open5e reference records...")
    languages = fetch_all("languages")
    skills = fetch_all("skills")

    language_records, skill_records = validate_records(
        languages, skills
    )

    print(f"Void Speech: {len(language_records)}")
    print(f"A5E skills: {len(skill_records)}")

    with SessionLocal() as session:
        try:
            edition_2014 = session.scalar(
                select(Edition).where(Edition.code == "2014")
            )
            edition_a5e = session.scalar(
                select(Edition).where(Edition.code == "a5e")
            )

            if edition_2014 is None or edition_a5e is None:
                raise ValueError("Required editions are missing")

            adventurers_guide = get_source(
                session, "Adventurer's Guide"
            )

            tob_document = language_records[0]["document"]
            tob_source_id = upsert_tome_of_beasts_source(
                session, tob_document
            )

            language_data = []
            for record in language_records:
                language_data.append({
                    "edition_id": edition_2014.id,
                    "name": record["name"],
                    "typical_speakers": record.get("desc"),
                    "script": record.get("script_language"),
                    "description": None,
                    "source_id": tob_source_id,
                    "external_id": record["key"],
                })

            proficiency_data = []
            for record in skill_records:
                descriptions = record.get("descriptions") or []
                description = next(
                    (
                        item.get("desc")
                        for item in descriptions
                        if item.get("document") == "a5e-ag"
                    ),
                    None,
                )

                if not description:
                    raise ValueError(
                        f"Missing A5E description: {record['name']}"
                    )

                proficiency_data.append({
                    "edition_id": edition_a5e.id,
                    "name": record["name"],
                    "category": "skill",
                    "description": description,
                    "source_id": adventurers_guide.id,
                    "external_id": record["key"],
                })

            # Guard against edition/name conflicts belonging to
            # a different source or external ID.
            for model, records in (
                (Language, language_data),
                (Proficiency, proficiency_data),
            ):
                for record in records:
                    existing = session.scalar(
                        select(model).where(
                            model.edition_id == record["edition_id"],
                            model.name == record["name"],
                        )
                    )
                    if existing is not None and (
                        existing.source_id != record["source_id"]
                        or existing.external_id != record["external_id"]
                    ):
                        raise ValueError(
                            f"Conflicting existing {model.__name__}: "
                            f"{record['name']}"
                        )

            for model, records in (
                (Language, language_data),
                (Proficiency, proficiency_data),
            ):
                statement = insert(model).values(records)
                statement = statement.on_conflict_do_update(
                    index_elements=["source_id", "external_id"],
                    set_={
                        key: getattr(statement.excluded, key)
                        for key in records[0]
                        if key not in ("source_id", "external_id")
                    },
                )
                session.execute(statement)

            print("\nValidated import:")
            print(f"  Languages: {len(language_data)}")
            print(f"  Proficiencies: {len(proficiency_data)}")
            print("  New source: Tome of Beasts")

            if args.dry_run:
                session.rollback()
                print("\nDry run completed. No changes committed.")
            else:
                session.commit()
                print("\nReference import committed successfully.")

        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    main()
