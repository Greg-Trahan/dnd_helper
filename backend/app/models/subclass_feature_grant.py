from sqlalchemy import ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SubclassFeatureGrant(Base):
    __tablename__ = "subclass_feature_grants"

    __table_args__ = (
        Index(
            "ix_subclass_feature_level",
            "subclass_id",
            "character_level",
        ),
        UniqueConstraint(
            "subclass_id",
            "feature_id",
            "character_level",
            name="uq_subclass_feature_level",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    subclass_id: Mapped[int] = mapped_column(
        ForeignKey("subclasses.id", ondelete="CASCADE"),
        nullable=False,
    )
    feature_id: Mapped[int] = mapped_column(
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=False,
    )

    subclass: Mapped["Subclass"] = relationship(
        "Subclass",
        back_populates="feature_grants",
    )

    feature: Mapped["Feature"] = relationship(
        "Feature",
        back_populates="subclass_feature_grants",
    )

    character_level: Mapped[int] = mapped_column(Integer, nullable=False)
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    grant_notes: Mapped[str | None] = mapped_column(Text)
