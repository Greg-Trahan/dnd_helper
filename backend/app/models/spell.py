from sqlalchemy import (
    Boolean,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION

from app.database.base import Base


class Spell(Base):
    __tablename__ = "spells"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    edition: Mapped[str | None] = mapped_column(String(10), nullable=True)

    source_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(150), nullable=True)
    source: Mapped[str | None] = mapped_column(String(150), nullable=True)

    school: Mapped[str | None] = mapped_column(String(50), nullable=True)
    school_key: Mapped[str | None] = mapped_column(String(50), nullable=True)
    classes: Mapped[list | None] = mapped_column(JSON, nullable=True)
    casting_options: Mapped[list | None] = mapped_column(JSON, nullable=True)

    level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    higher_level: Mapped[str | None] = mapped_column(Text, nullable=True)

    target_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    range_value: Mapped[int | None] = mapped_column("range", Integer, nullable=True)
    range_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    range_unit: Mapped[str | None] = mapped_column(String(30), nullable=True)

    shape_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    shape_size: Mapped[float | None] = mapped_column(
        DOUBLE_PRECISION,
        nullable=True,
    )
    shape_size_unit: Mapped[str | None] = mapped_column(String(30), nullable=True)

    casting_time: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reaction_condition: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration: Mapped[str | None] = mapped_column(String(100), nullable=True)

    ritual: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    concentration: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    verbal: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    somatic: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    material: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    material_specified: Mapped[str | None] = mapped_column(Text, nullable=True)
    material_cost: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    material_consumed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    saving_throw_ability: Mapped[str | None] = mapped_column(String(30), nullable=True)
    attack_roll: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    damage_roll: Mapped[str | None] = mapped_column(String(100), nullable=True)
    damage_types: Mapped[list | None] = mapped_column(JSON, nullable=True)

    crossreferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        UniqueConstraint("source_key", "source_id", name="uq_spell_source"),
    )
