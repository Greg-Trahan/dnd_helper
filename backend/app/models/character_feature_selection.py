from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CharacterFeatureSelection(Base):
    __tablename__ = "character_feature_selections"

    __table_args__ = (
        Index("ix_character_features_character", "character_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )

    feature_id: Mapped[int] = mapped_column(
        ForeignKey("features.id", ondelete="RESTRICT"),
        nullable=False,
    )

    source_type: Mapped[str | None] = mapped_column(String(40))
    source_id: Mapped[int | None] = mapped_column(Integer)

    selected_at_level: Mapped[int | None] = mapped_column(Integer)

    uses_remaining: Mapped[int | None] = mapped_column(Integer)
    uses_maximum: Mapped[int | None] = mapped_column(Integer)

    state: Mapped[dict | None] = mapped_column(JSON)
