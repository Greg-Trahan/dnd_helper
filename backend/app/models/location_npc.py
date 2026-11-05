from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class LocationNpc(Base):
    __tablename__ = "location_npcs"

    id: Mapped[int] = mapped_column(primary_key=True)

    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False
    )
    npc_id: Mapped[int] = mapped_column(
        ForeignKey("npcs.id"), nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
