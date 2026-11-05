from decimal import Decimal

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Equipment(Base):
    __tablename__ = "equipment"

    __table_args__ = (
        Index("ix_equipment_edition_category", "edition_id", "category_id"),
        Index("ix_equipment_name", "name"),
        UniqueConstraint(
            "edition_id",
            "name",
            name="uq_equipment_edition_name",
        ),
        UniqueConstraint(
            "source_id",
            "external_id",
            name="uq_equipment_source_external",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    edition_id: Mapped[int] = mapped_column(
        ForeignKey("editions.id", ondelete="CASCADE"),
        nullable=False,
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("equipment_categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
    )

    external_id: Mapped[str | None] = mapped_column(String(160))

    name: Mapped[str] = mapped_column(String(160), nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    cost_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2)
    )

    cost_unit: Mapped[str | None] = mapped_column(String(20))

    weight: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2)
    )

    rarity: Mapped[str | None] = mapped_column(String(40))

    is_magical: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    properties: Mapped[dict | None] = mapped_column(JSON)

    weapon_data: Mapped[dict | None] = mapped_column(JSON)

    armor_data: Mapped[dict | None] = mapped_column(JSON)

    container_capacity: Mapped[str | None] = mapped_column(String(120))
