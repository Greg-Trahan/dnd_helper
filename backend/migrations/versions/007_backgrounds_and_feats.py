"""Backgrounds and feats."""
from alembic import op
import sqlalchemy as sa

revision = "dnd_007_backgrounds_feats"
down_revision = "dnd_006_species"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "backgrounds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL")),
        sa.Column("external_id", sa.String(160)),
        sa.Column("name", sa.String(140), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("skill_proficiencies", sa.JSON()),
        sa.Column("tool_proficiencies", sa.JSON()),
        sa.Column("languages", sa.JSON()),
        sa.Column("starting_equipment", sa.JSON()),
        sa.Column("ability_score_rules", sa.JSON()),
        sa.Column("feature_id", sa.Integer(), sa.ForeignKey("features.id", ondelete="SET NULL")),
        sa.UniqueConstraint("edition_id", "name", name="uq_background_edition_name"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_background_source_external"),
    )
    op.create_table(
        "feats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL")),
        sa.Column("external_id", sa.String(160)),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("feat_type", sa.String(60)),
        sa.Column("repeatable", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("mechanics", sa.JSON()),
        sa.UniqueConstraint("edition_id", "name", name="uq_feat_edition_name"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_feat_source_external"),
    )
    op.create_table(
        "feat_prerequisites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feat_id", sa.Integer(), sa.ForeignKey("feats.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prerequisite_type", sa.String(50), nullable=False),
        sa.Column("operator", sa.String(20), nullable=False, server_default="eq"),
        sa.Column("value", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_hard_requirement", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "feat_feature_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feat_id", sa.Integer(), sa.ForeignKey("feats.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_id", sa.Integer(), sa.ForeignKey("features.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("feat_id", "feature_id", name="uq_feat_feature_link"),
    )
    op.create_index("ix_backgrounds_edition", "backgrounds", ["edition_id"])
    op.create_index("ix_feats_edition", "feats", ["edition_id"])


def downgrade():
    op.drop_index("ix_feats_edition", table_name="feats")
    op.drop_index("ix_backgrounds_edition", table_name="backgrounds")
    op.drop_table("feat_feature_links")
    op.drop_table("feat_prerequisites")
    op.drop_table("feats")
    op.drop_table("backgrounds")
