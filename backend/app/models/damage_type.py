from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DamageType(Base):
    __tablename__ = "damage_types"

    __table_args__ = (
        UniqueConstraint(
            "edition_id",
            "name",
            name="uq_damage_type_edition_name",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    edition_id: Mapped[int] = mapped_column(
        ForeignKey("editions.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(60), nullable=False)

    description: Mapped[str | None] = mapped_column(Text)
