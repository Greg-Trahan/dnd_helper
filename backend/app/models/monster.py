from sqlalchemy import Float, String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, ForeignKey, JSON, UniqueConstraint

from app.database.base import Base


class Monster(Base):
    __tablename__ = "monsters"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int | None] = mapped_column(
        ForeignKey("campaigns.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    creature_type: Mapped[str | None] = mapped_column(JSON, nullable=True)
    alignment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    challenge_rating: Mapped[str | None] = mapped_column(Float, nullable=True)

    armor_class: Mapped[int | None] = mapped_column(nullable=True)
    hit_points: Mapped[int | None] = mapped_column(nullable=True)
    speed: Mapped[str | None] = mapped_column(JSON, nullable=True)

    ability_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    abilities: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(150), nullable=True)

    edition: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )

    source_key: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    source_id: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )

    raw_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )

    __table_args__ = (
        UniqueConstraint(
            "source_key",
            "source_id",
            name="uq_monster_source",
        ),
    )
