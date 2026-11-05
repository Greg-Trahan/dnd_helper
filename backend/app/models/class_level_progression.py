from sqlalchemy import ForeignKey, Index, Integer, JSON, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ClassLevelProgression(Base):
    __tablename__ = "class_level_progressions"

    __table_args__ = (
        Index(
            "ix_class_progression_class_level",
            "class_id",
            "level",
        ),
        UniqueConstraint(
            "class_id",
            "level",
            name="uq_class_progression_level",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
    )

    level: Mapped[int] = mapped_column(Integer, nullable=False)
    proficiency_bonus: Mapped[int] = mapped_column(Integer, nullable=False)

    features_summary: Mapped[str | None] = mapped_column(Text)
    progression_data: Mapped[dict | list | None] = mapped_column(JSON)
