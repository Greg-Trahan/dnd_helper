from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ClassResource(Base):
    __tablename__ = "class_resources"

    __table_args__ = (
        UniqueConstraint(
            "class_id",
            "resource_key",
            name="uq_class_resource_key",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    recovery: Mapped[str | None] = mapped_column(String(80))
    uses_formula: Mapped[str | None] = mapped_column(String(200))
    resource_key: Mapped[str | None] = mapped_column(String(80))
