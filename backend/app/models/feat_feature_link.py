from sqlalchemy import (
    ForeignKey,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FeatFeatureLink(Base):
    __tablename__ = "feat_feature_links"

    __table_args__ = (
        UniqueConstraint(
            "feat_id",
            "feature_id",
            name="uq_feat_feature_link",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    feat_id: Mapped[int] = mapped_column(
        ForeignKey("feats.id", ondelete="CASCADE"),
        nullable=False,
    )

    feature_id: Mapped[int] = mapped_column(
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=False,
    )

    feat: Mapped["Feat"] = relationship(
        "Feat",
        back_populates="feature_links",
    )

    feature: Mapped["Feature"] = relationship(
        "Feature",
        back_populates="feat_feature_links",
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
