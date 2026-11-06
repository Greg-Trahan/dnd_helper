from sqlalchemy import Boolean, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Species(Base):
    __tablename__ = "species"

    __table_args__ = (
        Index("ix_species_edition", "edition_id"),
        UniqueConstraint(
            "edition_id",
            "name",
            name="uq_species_edition_name",
        ),
        UniqueConstraint(
            "source_id",
            "external_id",
            name="uq_species_source_external",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    edition_id: Mapped[int] = mapped_column(
        ForeignKey("editions.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
    )

    characters: Mapped[list["Character"]] = relationship(
        "Character",
        back_populates="species",
        passive_deletes=True,
    )

    variants: Mapped[list["SpeciesVariant"]] = relationship(
        "SpeciesVariant",
        back_populates="species",
        passive_deletes=True,
    )

    feature_grants: Mapped[list["SpeciesFeatureGrant"]] = relationship(
        "SpeciesFeatureGrant",
        back_populates="species",
        passive_deletes=True,
    )

    external_id: Mapped[str | None] = mapped_column(String(160))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    size: Mapped[str | None] = mapped_column(String(80))
    creature_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        default="Humanoid",
    )
    base_speed: Mapped[int | None] = mapped_column(Integer)

    ability_score_rules: Mapped[dict | list | None] = mapped_column(JSON)
    age: Mapped[str | None] = mapped_column(Text)
    alignment: Mapped[str | None] = mapped_column(Text)
    languages_summary: Mapped[str | None] = mapped_column(Text)

    is_playable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
