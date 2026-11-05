"""Level-by-level class progression and resource progression."""
from alembic import op
import sqlalchemy as sa

revision = "dnd_005_class_progression"
down_revision = "dnd_004_choices"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "class_level_progressions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("class_id", sa.Integer(), sa.ForeignKey("classes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("proficiency_bonus", sa.Integer(), nullable=False),
        sa.Column("features_summary", sa.Text()),
        sa.Column("progression_data", sa.JSON()),
        sa.UniqueConstraint("class_id", "level", name="uq_class_progression_level"),
    )
    op.create_table(
        "class_resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("class_id", sa.Integer(), sa.ForeignKey("classes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("recovery", sa.String(80)),
        sa.Column("uses_formula", sa.String(200)),
        sa.Column("resource_key", sa.String(80)),
        sa.UniqueConstraint("class_id", "resource_key", name="uq_class_resource_key"),
    )
    op.create_table(
        "class_resource_progressions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("resource_id", sa.Integer(), sa.ForeignKey("class_resources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("maximum_uses", sa.Integer()),
        sa.Column("formula", sa.String(200)),
        sa.Column("notes", sa.Text()),
        sa.UniqueConstraint("resource_id", "level", name="uq_resource_progression_level"),
    )
    op.create_index("ix_class_progression_class_level", "class_level_progressions", ["class_id", "level"])


def downgrade():
    op.drop_index("ix_class_progression_class_level", table_name="class_level_progressions")
    op.drop_table("class_resource_progressions")
    op.drop_table("class_resources")
    op.drop_table("class_level_progressions")
