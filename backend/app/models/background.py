from sqlalchemy import ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Background(Base):
    __tablename__ = "backgrounds"

    __table_args__ = (
        Index("ix_backgrounds_edition", "edition_id"),
        UniqueConstraint(
            "edition_id",
            "name",
            name="uq_background_edition_name",
        ),
        UniqueConstraint(
            "source_id",
            "external_id",
            name="uq_background_source_external",
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
        back_populates="background",
        passive_deletes=True,
    )

    external_id: Mapped[str | None] = mapped_column(String(160))
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    skill_proficiencies: Mapped[dict | list | None] = mapped_column(JSON)
    tool_proficiencies: Mapped[dict | list | None] = mapped_column(JSON)
    languages: Mapped[dict | list | None] = mapped_column(JSON)
    starting_equipment: Mapped[dict | list | None] = mapped_column(JSON)
    ability_score_rules: Mapped[dict | list | None] = mapped_column(JSON)

    feature_id: Mapped[int | None] = mapped_column(
        ForeignKey("features.id", ondelete="SET NULL"),
        nullable=True,
    )
