from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[int] = mapped_column(primary_key=True)

    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id"), nullable=False
    )

    owner_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )

    owner_id: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )

    equipped: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "item_id",
            "owner_type",
            "owner_id",
            name="uq_inventory_owner_item",
        ),
    )
