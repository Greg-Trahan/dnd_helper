from sqlalchemy import ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ClassFeatureGrant(Base):
    __tablename__ = "class_feature_grants"

    __table_args__ = (
        Index(
            "ix_class_feature_level",
            "class_id",
            "character_level",
        ),
        UniqueConstraint(
            "class_id",
            "feature_id",
            "character_level",
            name="uq_class_feature_level",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
    )
    feature_id: Mapped[int] = mapped_column(
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=False,
    )

    character_class: Mapped["CharacterClass"] = relationship(
        "CharacterClass",
        back_populates="feature_grants",
    )

    feature: Mapped["Feature"] = relationship(
        "Feature",
        back_populates="class_feature_grants",
    )

    character_level: Mapped[int] = mapped_column(Integer, nullable=False)
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    grant_notes: Mapped[str | None] = mapped_column(Text)
