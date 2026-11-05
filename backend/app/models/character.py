from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Character(Base):
    __tablename__ = "characters"

    __table_args__ = (
        Index("ix_characters_edition", "edition_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    edition_id: Mapped[int] = mapped_column(
        ForeignKey("editions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    species_id: Mapped[int | None] = mapped_column(
        ForeignKey("species.id", ondelete="RESTRICT"),
        nullable=True,
    )
    species_variant_id: Mapped[int | None] = mapped_column(
        ForeignKey("species_variants.id", ondelete="SET NULL"),
        nullable=True,
    )
    background_id: Mapped[int | None] = mapped_column(
        ForeignKey("backgrounds.id", ondelete="SET NULL"),
        nullable=True,
    )

    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    experience_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    alignment: Mapped[str | None] = mapped_column(String(80))
    size: Mapped[str | None] = mapped_column(String(80))
    speed: Mapped[int | None] = mapped_column(Integer)

    ability_scores: Mapped[dict | list | None] = mapped_column(JSON)

    hit_point_maximum: Mapped[int | None] = mapped_column(Integer)
    current_hit_points: Mapped[int | None] = mapped_column(Integer)
    temporary_hit_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    armor_class: Mapped[int | None] = mapped_column(Integer)
    initiative_bonus: Mapped[int | None] = mapped_column(Integer)
    proficiency_bonus: Mapped[int | None] = mapped_column(Integer)

    death_saves: Mapped[dict | list | None] = mapped_column(JSON)

    personality_traits: Mapped[str | None] = mapped_column(Text)
    ideals: Mapped[str | None] = mapped_column(Text)
    bonds: Mapped[str | None] = mapped_column(Text)
    flaws: Mapped[str | None] = mapped_column(Text)
    backstory: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    class_assignments: Mapped[list["CharacterClassAssignment"]] = relationship(
        "CharacterClassAssignment",
        back_populates="character",
        cascade="all, delete-orphan",
    )
