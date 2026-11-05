from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    JSON,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class FeatureOption(Base):
    __tablename__ = "feature_options"

    __table_args__ = (
        Index("ix_feature_options_group", "choice_group_id"),
        UniqueConstraint(
            "choice_group_id",
            "name",
            name="uq_feature_option_group_name",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    choice_group_id: Mapped[int] = mapped_column(
        ForeignKey("feature_choice_groups.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(160), nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    mechanics: Mapped[dict | None] = mapped_column(JSON)

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
