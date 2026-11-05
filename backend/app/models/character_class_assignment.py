from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CharacterClassAssignment(Base):
    __tablename__ = "character_classes"

    __table_args__ = (
        Index("ix_character_classes_character", "character_id"),
        UniqueConstraint(
            "character_id",
            "class_id",
            name="uq_character_class",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )

    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    subclass_id: Mapped[int | None] = mapped_column(
        ForeignKey("subclasses.id", ondelete="SET NULL"),
        nullable=True,
    )

    class_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    character = relationship(
        "Character",
        back_populates="class_assignments",
    )
