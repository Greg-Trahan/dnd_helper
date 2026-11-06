from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

class ClassResourceProgression(Base):
    __tablename__ = "class_resource_progressions"

    __table_args__ = (
        UniqueConstraint(
            "resource_id",
            "level",
            name="uq_resource_progression_level",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    resource_id: Mapped[int] = mapped_column(
        ForeignKey("class_resources.id", ondelete="CASCADE"),
        nullable=False,
    )

    resource: Mapped["ClassResource"] = relationship(
        "ClassResource",
        back_populates="resource_progressions",
    )

    level: Mapped[int] = mapped_column(Integer, nullable=False)
    maximum_uses: Mapped[int | None] = mapped_column(Integer)
    formula: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
