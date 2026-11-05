from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Feat(Base):
    __tablename__ = "feats"

    __table_args__ = (
        Index("ix_feats_edition", "edition_id"),
        UniqueConstraint(
            "edition_id",
            "name",
            name="uq_feat_edition_name",
        ),
        UniqueConstraint(
            "source_id",
            "external_id",
            name="uq_feat_source_external",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    edition_id: Mapped[int] = mapped_column(
        ForeignKey("editions.id", ondelete="CASCADE"),
        nullable=False,
    )

    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
    )

    external_id: Mapped[str | None] = mapped_column(String(160))

    name: Mapped[str] = mapped_column(String(160), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    feat_type: Mapped[str | None] = mapped_column(String(60))

    repeatable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    mechanics: Mapped[dict | None] = mapped_column(JSON)
