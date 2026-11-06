from pydantic import BaseModel, ConfigDict


class ReferenceBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PlayerOption(ReferenceBase):
    id: int
    name: str
    campaign_id: int


class EditionOption(ReferenceBase):
    id: int
    code: str
    name: str
    year: int | None


class SpeciesOption(ReferenceBase):
    id: int
    edition_id: int
    name: str
    size: str | None
    creature_type: str
    base_speed: int | None
    is_playable: bool


class SpeciesVariantOption(ReferenceBase):
    id: int
    species_id: int
    name: str
    size_override: str | None
    speed_override: int | None


class BackgroundOption(ReferenceBase):
    id: int
    edition_id: int
    name: str


class ClassOption(ReferenceBase):
    id: int
    edition_id: int
    name: str
    hit_die: int | None
    primary_ability: str | None
    is_playable: bool
