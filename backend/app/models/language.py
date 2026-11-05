from sqlalchemy import (
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Language(Base):
    __tablename__ = "languages"

    __table_args__ = (
        Index("ix_languages_edition", "edition_id"),
        UniqueConstraint(
            "edition_id",
            "name",
            name="uq_language_edition_name",
        ),
        UniqueConstraint(
            "source_id",
            "external_id",
            name="uq_language_source_external",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    edition_id: Mapped[int] = mapped_column(
        ForeignKey("editions.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    typical_speakers: Mapped[str | None] = mapped_column(Text)

    script: Mapped[str | None] = mapped_column(String(100))

    description: Mapped[str | None] = mapped_column(Text)

    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
    )

    external_id: Mapped[str | None] = mapped_column(String(160))
