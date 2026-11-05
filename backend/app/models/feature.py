from sqlalchemy import Boolean, ForeignKey, Index, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Feature(Base):
    __tablename__ = "features"

    __table_args__ = (
        Index(
            "ix_features_edition_type",
            "edition_id",
            "feature_type",
        ),
        UniqueConstraint(
            "edition_id",
            "name",
            "feature_type",
            name="uq_feature_edition_name_type",
        ),
        UniqueConstraint(
            "source_id",
            "external_id",
            name="uq_feature_source_external",
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
    feature_type: Mapped[str] = mapped_column(String(50), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    rules_text: Mapped[str | None] = mapped_column(Text)
    mechanics: Mapped[dict | list | None] = mapped_column(JSON)

    uses_formula: Mapped[str | None] = mapped_column(String(200))
    recharge: Mapped[str | None] = mapped_column(String(80))
    activation: Mapped[str | None] = mapped_column(String(80))
    duration: Mapped[str | None] = mapped_column(String(120))

    is_repeatable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
