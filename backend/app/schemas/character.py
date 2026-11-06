from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


JsonValue = dict[str, Any] | list[Any] | None


class CharacterCreate(BaseModel):
    """Fields required or accepted when creating a character."""

    name: str = Field(min_length=1, max_length=120)
    player_id: int = Field(gt=0)
    edition_id: int = Field(gt=0)

    species_id: int | None = Field(default=None, gt=0)
    species_variant_id: int | None = Field(default=None, gt=0)
    background_id: int | None = Field(default=None, gt=0)

    level: int = Field(default=1, ge=1, le=20)
    experience_points: int = Field(default=0, ge=0)

    alignment: str | None = Field(default=None, max_length=80)
    size: str | None = Field(default=None, max_length=80)
    speed: int | None = Field(default=None, ge=0)

    ability_scores: JsonValue = None

    hit_point_maximum: int | None = Field(default=None, ge=0)
    current_hit_points: int | None = Field(default=None, ge=0)
    temporary_hit_points: int = Field(default=0, ge=0)

    armor_class: int | None = Field(default=None, ge=0)
    initiative_bonus: int | None = None
    proficiency_bonus: int | None = Field(default=None, ge=0)

    death_saves: JsonValue = None

    personality_traits: str | None = None
    ideals: str | None = None
    bonds: str | None = None
    flaws: str | None = None
    backstory: str | None = None
    notes: str | None = None


class CharacterUpdate(BaseModel):
    """Fields that may be changed on an existing character."""

    name: str | None = Field(default=None, min_length=1, max_length=120)
    player_id: int | None = Field(default=None, gt=0)
    edition_id: int | None = Field(default=None, gt=0)

    species_id: int | None = Field(default=None, gt=0)
    species_variant_id: int | None = Field(default=None, gt=0)
    background_id: int | None = Field(default=None, gt=0)

    level: int | None = Field(default=None, ge=1, le=20)
    experience_points: int | None = Field(default=None, ge=0)

    alignment: str | None = Field(default=None, max_length=80)
    size: str | None = Field(default=None, max_length=80)
    speed: int | None = Field(default=None, ge=0)

    ability_scores: JsonValue = None

    hit_point_maximum: int | None = Field(default=None, ge=0)
    current_hit_points: int | None = Field(default=None, ge=0)
    temporary_hit_points: int | None = Field(default=None, ge=0)

    armor_class: int | None = Field(default=None, ge=0)
    initiative_bonus: int | None = None
    proficiency_bonus: int | None = Field(default=None, ge=0)

    death_saves: JsonValue = None

    personality_traits: str | None = None
    ideals: str | None = None
    bonds: str | None = None
    flaws: str | None = None
    backstory: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def reject_null_for_required_fields(self):
        required_fields = {
            "name",
            "player_id",
            "edition_id",
            "level",
            "experience_points",
            "temporary_hit_points",
        }

        for field_name in required_fields:
            if field_name in self.model_fields_set:
                if getattr(self, field_name) is None:
                    raise ValueError(f"{field_name} cannot be null.")

        return self


class CharacterRead(BaseModel):
    """Character representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    player_id: int
    edition_id: int

    species_id: int | None
    species_variant_id: int | None
    background_id: int | None

    level: int
    experience_points: int

    alignment: str | None
    size: str | None
    speed: int | None

    ability_scores: JsonValue

    hit_point_maximum: int | None
    current_hit_points: int | None
    temporary_hit_points: int

    armor_class: int | None
    initiative_bonus: int | None
    proficiency_bonus: int | None

    death_saves: JsonValue

    personality_traits: str | None
    ideals: str | None
    bonds: str | None
    flaws: str | None
    backstory: str | None
    notes: str | None

    created_at: datetime
    updated_at: datetime
