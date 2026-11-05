"""Reusable features and grants to classes/subclasses."""
from alembic import op
import sqlalchemy as sa

revision = "dnd_003_features"
down_revision = "dnd_002_classes"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "features",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL")),
        sa.Column("external_id", sa.String(160)),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("feature_type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("rules_text", sa.Text()),
        sa.Column("mechanics", sa.JSON()),
        sa.Column("uses_formula", sa.String(200)),
        sa.Column("recharge", sa.String(80)),
        sa.Column("activation", sa.String(80)),
        sa.Column("duration", sa.String(120)),
        sa.Column("is_repeatable", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("edition_id", "name", "feature_type", name="uq_feature_edition_name_type"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_feature_source_external"),
    )
    op.create_table(
        "class_feature_grants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("class_id", sa.Integer(), sa.ForeignKey("classes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_id", sa.Integer(), sa.ForeignKey("features.id", ondelete="CASCADE"), nullable=False),
        sa.Column("character_level", sa.Integer(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("grant_notes", sa.Text()),
        sa.UniqueConstraint("class_id", "feature_id", "character_level", name="uq_class_feature_level"),
    )
    op.create_table(
        "subclass_feature_grants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subclass_id", sa.Integer(), sa.ForeignKey("subclasses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_id", sa.Integer(), sa.ForeignKey("features.id", ondelete="CASCADE"), nullable=False),
        sa.Column("character_level", sa.Integer(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("grant_notes", sa.Text()),
        sa.UniqueConstraint("subclass_id", "feature_id", "character_level", name="uq_subclass_feature_level"),
    )
    op.create_index("ix_features_edition_type", "features", ["edition_id", "feature_type"])
    op.create_index("ix_class_feature_level", "class_feature_grants", ["class_id", "character_level"])
    op.create_index("ix_subclass_feature_level", "subclass_feature_grants", ["subclass_id", "character_level"])


def downgrade():
    op.drop_index("ix_subclass_feature_level", table_name="subclass_feature_grants")
    op.drop_index("ix_class_feature_level", table_name="class_feature_grants")
    op.drop_index("ix_features_edition_type", table_name="features")
    op.drop_table("subclass_feature_grants")
    op.drop_table("class_feature_grants")
    op.drop_table("features")
