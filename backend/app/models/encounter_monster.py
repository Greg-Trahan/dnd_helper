from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class EncounterMonster(Base):
    __tablename__ = "encounter_monsters"

    id: Mapped[int] = mapped_column(primary_key=True)

    encounter_id: Mapped[int] = mapped_column(
        ForeignKey("encounters.id"), nullable=False
    )
    monster_id: Mapped[int] = mapped_column(
        ForeignKey("monsters.id"), nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
