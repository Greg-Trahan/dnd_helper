from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models import (
    Background,
    CharacterClass,
    Edition,
    Player,
    Species,
    SpeciesVariant,
)
from app.schemas.reference_data import (
    BackgroundOption,
    ClassOption,
    EditionOption,
    PlayerOption,
    SpeciesOption,
    SpeciesVariantOption,
)

router = APIRouter(tags=["Reference Data"])


@router.get("/players", response_model=list[PlayerOption])
def read_players(db: Session = Depends(get_db)):
    return db.scalars(
        select(Player).order_by(Player.name)
    ).all()


@router.get("/editions", response_model=list[EditionOption])
def read_editions(db: Session = Depends(get_db)):
    return db.scalars(
        select(Edition).order_by(Edition.year, Edition.name)
    ).all()


@router.get("/species", response_model=list[SpeciesOption])
def read_species(
    edition_id: int | None = Query(default=None, gt=0),
    playable_only: bool = True,
    db: Session = Depends(get_db),
):
    statement = select(Species)

    if edition_id is not None:
        statement = statement.where(Species.edition_id == edition_id)

    if playable_only:
        statement = statement.where(Species.is_playable.is_(True))

    return db.scalars(statement.order_by(Species.name)).all()


@router.get(
    "/species-variants",
    response_model=list[SpeciesVariantOption],
)
def read_species_variants(
    species_id: int = Query(gt=0),
    db: Session = Depends(get_db),
):
    statement = (
        select(SpeciesVariant)
        .where(SpeciesVariant.species_id == species_id)
        .order_by(SpeciesVariant.name)
    )

    return db.scalars(statement).all()


@router.get("/backgrounds", response_model=list[BackgroundOption])
def read_backgrounds(
    edition_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    statement = select(Background)

    if edition_id is not None:
        statement = statement.where(Background.edition_id == edition_id)

    return db.scalars(statement.order_by(Background.name)).all()


@router.get("/classes", response_model=list[ClassOption])
def read_classes(
    edition_id: int | None = Query(default=None, gt=0),
    playable_only: bool = True,
    db: Session = Depends(get_db),
):
    statement = select(CharacterClass)

    if edition_id is not None:
        statement = statement.where(
            CharacterClass.edition_id == edition_id
        )

    if playable_only:
        statement = statement.where(CharacterClass.is_playable.is_(True))

    return db.scalars(statement.order_by(CharacterClass.name)).all()
