from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CharacterFeat(Base):
    __tablename__ = "character_feats"

    __table_args__ = (
        UniqueConstraint(
            "character_id",
            "feat_id",
            name="uq_character_feat",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )

    feat_id: Mapped[int] = mapped_column(
        ForeignKey("feats.id", ondelete="RESTRICT"),
        nullable=False,
    )

    selected_at_level: Mapped[int | None] = mapped_column(Integer)
