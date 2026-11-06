from sqlalchemy import ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SpeciesVariant(Base):
    __tablename__ = "species_variants"

    __table_args__ = (
        Index("ix_species_variants_species", "species_id"),
        UniqueConstraint(
            "species_id",
            "name",
            name="uq_species_variant_name",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"),
        nullable=False,
    )

    characters: Mapped[list["Character"]] = relationship(
        "Character",
        back_populates="species_variant",
        passive_deletes=True,
    )

    species: Mapped["Species"] = relationship(
        "Species",
        back_populates="variants",
    )

    feature_grants: Mapped[list["SpeciesFeatureGrant"]] = relationship(
        "SpeciesFeatureGrant",
        back_populates="variant",
        passive_deletes=True,
    )

    name: Mapped[str] = mapped_column(String(140), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    size_override: Mapped[str | None] = mapped_column(String(80))
    speed_override: Mapped[int | None] = mapped_column(Integer)

    ability_score_rules: Mapped[dict | list | None] = mapped_column(JSON)
    mechanics: Mapped[dict | list | None] = mapped_column(JSON)
