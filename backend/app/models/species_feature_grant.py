from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SpeciesFeatureGrant(Base):
    __tablename__ = "species_feature_grants"

    __table_args__ = (
        UniqueConstraint(
            "species_id",
            "variant_id",
            "feature_id",
            name="uq_species_variant_feature",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"),
        nullable=False,
    )
    variant_id: Mapped[int | None] = mapped_column(
        ForeignKey("species_variants.id", ondelete="CASCADE"),
        nullable=True,
    )
    feature_id: Mapped[int] = mapped_column(
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=False,
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    grant_notes: Mapped[str | None] = mapped_column(Text)
