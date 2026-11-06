from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.character import (
    CharacterCreate,
    CharacterRead,
    CharacterUpdate,
)
from app.services import character_service

router = APIRouter(
    prefix="/characters",
    tags=["Characters"],
)


@router.get(
    "",
    response_model=list[CharacterRead],
)
def read_characters(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return character_service.list_characters(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{character_id}",
    response_model=CharacterRead,
)
def read_character(
    character_id: int,
    db: Session = Depends(get_db),
):
    character = character_service.get_character(
        db=db,
        character_id=character_id,
    )

    if character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found.",
        )

    return character


@router.post(
    "",
    response_model=CharacterRead,
    status_code=status.HTTP_201_CREATED,
)
def create_character(
    character_data: CharacterCreate,
    db: Session = Depends(get_db),
):
    try:
        return character_service.create_character(
            db=db,
            character_data=character_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{character_id}",
    response_model=CharacterRead,
)
def update_character(
    character_id: int,
    character_data: CharacterUpdate,
    db: Session = Depends(get_db),
):
    character = character_service.get_character(
        db=db,
        character_id=character_id,
    )

    if character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found.",
        )

    try:
        return character_service.update_character(
            db=db,
            character=character,
            character_data=character_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{character_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_character(
    character_id: int,
    db: Session = Depends(get_db),
):
    character = character_service.get_character(
        db=db,
        character_id=character_id,
    )

    if character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found.",
        )

    character_service.delete_character(
        db=db,
        character=character,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
