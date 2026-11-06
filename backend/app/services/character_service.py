from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.background import Background
from app.models.character import Character
from app.models.edition import Edition
from app.models.player import Player
from app.models.species import Species
from app.models.species_variant import SpeciesVariant
from app.schemas.character import CharacterCreate, CharacterUpdate


def list_characters(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> list[Character]:
    statement = (
        select(Character)
        .order_by(Character.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_character(
    db: Session,
    character_id: int,
) -> Character | None:
    return db.get(Character, character_id)


def _validate_references(
    db: Session,
    player_id: int,
    edition_id: int,
    species_id: int | None,
    species_variant_id: int | None,
    background_id: int | None,
) -> None:
    if db.get(Player, player_id) is None:
        raise ValueError(f"Player {player_id} does not exist.")

    if db.get(Edition, edition_id) is None:
        raise ValueError(f"Edition {edition_id} does not exist.")

    species = None

    if species_id is not None:
        species = db.get(Species, species_id)

        if species is None:
            raise ValueError(f"Species {species_id} does not exist.")

        if species.edition_id != edition_id:
            raise ValueError(
                "The selected species does not belong to the selected edition."
            )

    if species_variant_id is not None:
        if species is None:
            raise ValueError(
                "A species must be selected when selecting a species variant."
            )

        variant = db.get(SpeciesVariant, species_variant_id)

        if variant is None:
            raise ValueError(
                f"Species variant {species_variant_id} does not exist."
            )

        if variant.species_id != species_id:
            raise ValueError(
                "The selected species variant does not belong to the selected species."
            )

    if background_id is not None:
        background = db.get(Background, background_id)

        if background is None:
            raise ValueError(
                f"Background {background_id} does not exist."
            )

        if background.edition_id != edition_id:
            raise ValueError(
                "The selected background does not belong to the selected edition."
            )


def create_character(
    db: Session,
    character_data: CharacterCreate,
) -> Character:
    values = character_data.model_dump()

    _validate_references(
        db=db,
        player_id=values["player_id"],
        edition_id=values["edition_id"],
        species_id=values["species_id"],
        species_variant_id=values["species_variant_id"],
        background_id=values["background_id"],
    )

    character = Character(**values)

    try:
        db.add(character)
        db.commit()
        db.refresh(character)
        return character
    except Exception:
        db.rollback()
        raise


def update_character(
    db: Session,
    character: Character,
    character_data: CharacterUpdate,
) -> Character:
    updates = character_data.model_dump(exclude_unset=True)

    if not updates:
        raise ValueError("No character fields were provided for update.")

    # Validate the complete resulting state, not just supplied fields.
    resulting_values = {
        "player_id": character.player_id,
        "edition_id": character.edition_id,
        "species_id": character.species_id,
        "species_variant_id": character.species_variant_id,
        "background_id": character.background_id,
    }

    resulting_values.update({
        key: value
        for key, value in updates.items()
        if key in resulting_values
    })

    _validate_references(
        db=db,
        player_id=resulting_values["player_id"],
        edition_id=resulting_values["edition_id"],
        species_id=resulting_values["species_id"],
        species_variant_id=resulting_values["species_variant_id"],
        background_id=resulting_values["background_id"],
    )

    try:
        for field, value in updates.items():
            setattr(character, field, value)

        db.commit()
        db.refresh(character)
        return character
    except Exception:
        db.rollback()
        raise


def delete_character(
    db: Session,
    character: Character,
) -> None:
    try:
        db.delete(character)
        db.commit()
    except Exception:
        db.rollback()
        raise
