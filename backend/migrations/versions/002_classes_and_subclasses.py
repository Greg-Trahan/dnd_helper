"""Classes and subclasses."""
from alembic import op
import sqlalchemy as sa

revision = "dnd_002_classes"
down_revision = "dnd_001_shared_refs"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "classes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL")),
        sa.Column("external_id", sa.String(160)),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("hit_die", sa.Integer()),
        sa.Column("primary_ability", sa.String(120)),
        sa.Column("saving_throw_proficiency_ids", sa.JSON()),
        sa.Column("starting_equipment", sa.JSON()),
        sa.Column("multiclassing", sa.JSON()),
        sa.Column("is_playable", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("edition_id", "name", name="uq_class_edition_name"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_class_source_external"),
    )
    op.create_table(
        "subclasses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("class_id", sa.Integer(), sa.ForeignKey("classes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL")),
        sa.Column("external_id", sa.String(160)),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("subclass_level", sa.Integer()),
        sa.UniqueConstraint("class_id", "name", name="uq_subclass_class_name"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_subclass_source_external"),
    )
    op.create_index("ix_classes_edition", "classes", ["edition_id"])
    op.create_index("ix_subclasses_class", "subclasses", ["class_id"])
    op.create_index("ix_subclasses_edition", "subclasses", ["edition_id"])


def downgrade():
    op.drop_index("ix_subclasses_edition", table_name="subclasses")
    op.drop_index("ix_subclasses_class", table_name="subclasses")
    op.drop_index("ix_classes_edition", table_name="classes")
    op.drop_table("subclasses")
    op.drop_table("classes")
