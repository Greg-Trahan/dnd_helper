from sqlalchemy import Column, ForeignKey, Index, Integer, Table

from app.database.base import Base


character_campaigns = Table(
    "character_campaigns",
    Base.metadata,
    Column(
        "character_id",
        Integer,
        ForeignKey("characters.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "campaign_id",
        Integer,
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_character_campaigns_campaign_id", "campaign_id"),
)
