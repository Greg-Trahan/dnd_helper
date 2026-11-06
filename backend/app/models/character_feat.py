from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    character: Mapped["Character"] = relationship(
        "Character",
        back_populates="feat_selections",
    )

    feat: Mapped["Feat"] = relationship(
        "Feat",
        back_populates="character_selections",
    )

    selected_at_level: Mapped[int | None] = mapped_column(Integer)
