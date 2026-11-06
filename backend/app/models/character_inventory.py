from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CharacterInventory(Base):
    __tablename__ = "character_inventory"

    __table_args__ = (
        Index("ix_character_inventory_character", "character_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )

    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id", ondelete="RESTRICT"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    is_equipped: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    is_attuned: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    character: Mapped["Character"] = relationship(
        "Character",
        back_populates="inventory_entries",
    )

    equipment: Mapped["Equipment"] = relationship(
        "Equipment",
        back_populates="character_inventory_entries",
    )

    notes: Mapped[str | None] = mapped_column(Text)
