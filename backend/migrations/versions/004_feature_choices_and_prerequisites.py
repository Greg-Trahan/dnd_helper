"""Feature choice groups, options, and prerequisites."""
from alembic import op
import sqlalchemy as sa

revision = "dnd_004_choices"
down_revision = "dnd_003_features"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "feature_choice_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feature_id", sa.Integer(), sa.ForeignKey("features.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(140), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("min_choices", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("max_choices", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("selection_mode", sa.String(30), nullable=False, server_default="select"),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("feature_id", "name", name="uq_feature_choice_group_name"),
    )
    op.create_table(
        "feature_options",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("choice_group_id", sa.Integer(), sa.ForeignKey("feature_choice_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("mechanics", sa.JSON()),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("choice_group_id", "name", name="uq_feature_option_group_name"),
    )
    op.create_table(
        "feature_prerequisites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feature_id", sa.Integer(), sa.ForeignKey("features.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prerequisite_type", sa.String(50), nullable=False),
        sa.Column("operator", sa.String(20), nullable=False, server_default="eq"),
        sa.Column("value", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_hard_requirement", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("group_key", sa.String(60)),
    )
    op.create_index("ix_feature_options_group", "feature_options", ["choice_group_id"])
    op.create_index("ix_feature_prerequisites_feature", "feature_prerequisites", ["feature_id"])


def downgrade():
    op.drop_index("ix_feature_prerequisites_feature", table_name="feature_prerequisites")
    op.drop_index("ix_feature_options_group", table_name="feature_options")
    op.drop_table("feature_prerequisites")
    op.drop_table("feature_options")
    op.drop_table("feature_choice_groups")
