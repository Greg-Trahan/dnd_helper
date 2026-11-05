from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int | None] = mapped_column(
        ForeignKey("campaigns.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    item_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rarity: Mapped[str | None] = mapped_column(String(50), nullable=True)

    weight: Mapped[str | None] = mapped_column(String(30), nullable=True)
    value: Mapped[str | None] = mapped_column(String(50), nullable=True)

    requires_attunement: Mapped[bool] = mapped_column(default=False)
    properties: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(150), nullable=True)
