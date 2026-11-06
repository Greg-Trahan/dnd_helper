from sqlalchemy import ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CharacterClass(Base):
    __tablename__ = "classes"

    __table_args__ = (
        Index("ix_classes_edition", "edition_id"),
        UniqueConstraint(
            "source_id",
            "external_id",
            name="uq_class_source_external",
        ),
        UniqueConstraint(
            "edition_id",
            "name",
            name="uq_class_edition_name",
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

    character_assignments: Mapped[list["CharacterClassAssignment"]] = relationship(
        "CharacterClassAssignment",
        back_populates="character_class",
        passive_deletes=True,
    )

    # Subclasses and granted features
    subclasses: Mapped[list["Subclass"]] = relationship(
        "Subclass",
        back_populates="character_class",
        passive_deletes=True,
    )

    feature_grants: Mapped[list["ClassFeatureGrant"]] = relationship(
        "ClassFeatureGrant",
        back_populates="character_class",
        passive_deletes=True,
    )

    # Level progression and resources
    level_progressions: Mapped[list["ClassLevelProgression"]] = relationship(
        "ClassLevelProgression",
        back_populates="character_class",
        passive_deletes=True,
    )

    resources: Mapped[list["ClassResource"]] = relationship(
        "ClassResource",
        back_populates="character_class",
        passive_deletes=True,
    )

    external_id: Mapped[str | None] = mapped_column(String(160))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    hit_die: Mapped[int | None] = mapped_column(Integer)
    primary_ability: Mapped[str | None] = mapped_column(String(120))
    saving_throw_proficiency_ids: Mapped[dict | list | None] = mapped_column(JSON)
    starting_equipment: Mapped[dict | list | None] = mapped_column(JSON)
    multiclassing: Mapped[dict | list | None] = mapped_column(JSON)

    is_playable: Mapped[bool] = mapped_column(nullable=False, default=True)
