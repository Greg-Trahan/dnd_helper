from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.character_campaign import character_campaigns


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    characters: Mapped[list["Character"]] = relationship(
        "Character",
        secondary=character_campaigns,
        back_populates="campaigns",
        passive_deletes=True,
    )
