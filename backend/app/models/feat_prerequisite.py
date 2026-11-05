from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class FeatPrerequisite(Base):
    __tablename__ = "feat_prerequisites"

    id: Mapped[int] = mapped_column(primary_key=True)

    feat_id: Mapped[int] = mapped_column(
        ForeignKey("feats.id", ondelete="CASCADE"),
        nullable=False,
    )

    prerequisite_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    operator: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'eq'"),
    )

    value: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(Text)

    is_hard_requirement: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
