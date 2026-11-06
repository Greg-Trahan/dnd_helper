from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CharacterChoiceSelection(Base):
    __tablename__ = "character_choice_selections"

    __table_args__ = (
        UniqueConstraint(
            "character_id",
            "choice_group_id",
            "option_id",
            name="uq_character_choice_option",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )

    choice_group_id: Mapped[int] = mapped_column(
        ForeignKey("feature_choice_groups.id", ondelete="RESTRICT"),
        nullable=False,
    )

    option_id: Mapped[int] = mapped_column(
        ForeignKey("feature_options.id", ondelete="RESTRICT"),
        nullable=False,
    )

    character: Mapped["Character"] = relationship(
        "Character",
        back_populates="choice_selections",
    )

    choice_group: Mapped["FeatureChoiceGroup"] = relationship(
        "FeatureChoiceGroup",
        back_populates="character_selections",
    )

    option: Mapped["FeatureOption"] = relationship(
        "FeatureOption",
        back_populates="character_selections",
    )

    selected_at_level: Mapped[int | None] = mapped_column(Integer)
