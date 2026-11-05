from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class EquipmentPropertyLink(Base):
    __tablename__ = "equipment_property_links"

    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id", ondelete="CASCADE"),
        primary_key=True,
    )

    property_id: Mapped[int] = mapped_column(
        ForeignKey(
            "equipment_property_definitions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    value: Mapped[str | None] = mapped_column(String(160))
