from sqlalchemy import (
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Proficiency(Base):
    __tablename__ = "proficiencies"

    __table_args__ = (
        Index(
            "ix_proficiencies_edition_category",
            "edition_id",
            "category",
        ),
        UniqueConstraint(
            "edition_id",
            "name",
            "category",
            name="uq_proficiency_edition_name_category",
        ),
        UniqueConstraint(
            "source_id",
            "external_id",
            name="uq_proficiency_source_external",
        ),
    )

    character_assignments: Mapped[list["CharacterProficiency"]] = relationship(
        "CharacterProficiency",
        back_populates="proficiency",
        passive_deletes=True,
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    edition_id: Mapped[int] = mapped_column(
        ForeignKey("editions.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)

    category: Mapped[str] = mapped_column(String(40), nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
    )

    external_id: Mapped[str | None] = mapped_column(String(160))
