from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Subclass(Base):
    __tablename__ = "subclasses"

    __table_args__ = (
        Index("ix_subclasses_class", "class_id"),
        Index("ix_subclasses_edition", "edition_id"),
        UniqueConstraint(
            "class_id",
            "name",
            name="uq_subclass_class_name",
        ),
        UniqueConstraint(
            "source_id",
            "external_id",
            name="uq_subclass_source_external",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
    )
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
        back_populates="subclass",
        passive_deletes=True,
    )

    character_class: Mapped["CharacterClass"] = relationship(
        "CharacterClass",
        back_populates="subclasses",
    )

    feature_grants: Mapped[list["SubclassFeatureGrant"]] = relationship(
        "SubclassFeatureGrant",
        back_populates="subclass",
        passive_deletes=True,
    )

    external_id: Mapped[str | None] = mapped_column(String(160))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    subclass_level: Mapped[int | None] = mapped_column(Integer)
