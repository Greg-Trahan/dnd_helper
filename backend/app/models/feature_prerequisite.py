from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FeaturePrerequisite(Base):
    __tablename__ = "feature_prerequisites"

    __table_args__ = (
        Index(
            "ix_feature_prerequisites_feature",
            "feature_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    feature_id: Mapped[int] = mapped_column(
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=False,
    )

    feature: Mapped["Feature"] = relationship(
        "Feature",
        back_populates="prerequisites",
    )

    prerequisite_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    operator: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="eq",
    )
    value: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(Text)

    is_hard_requirement: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    group_key: Mapped[str | None] = mapped_column(String(60))
