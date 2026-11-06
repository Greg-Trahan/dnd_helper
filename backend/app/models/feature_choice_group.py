from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FeatureChoiceGroup(Base):
    __tablename__ = "feature_choice_groups"

    __table_args__ = (
        UniqueConstraint(
            "feature_id",
            "name",
            name="uq_feature_choice_group_name",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    feature_id: Mapped[int] = mapped_column(
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=False,
    )

    feature: Mapped["Feature"] = relationship(
        "Feature",
        back_populates="choice_groups",
    )

    options: Mapped[list["FeatureOption"]] = relationship(
        "FeatureOption",
        back_populates="choice_group",
        passive_deletes=True,
    )

    character_selections: Mapped[list["CharacterChoiceSelection"]] = relationship(
        "CharacterChoiceSelection",
        back_populates="choice_group",
        passive_deletes=True,
    )

    name: Mapped[str] = mapped_column(String(140), nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    min_choices: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    max_choices: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    selection_mode: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'select'"),
    )

    is_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
