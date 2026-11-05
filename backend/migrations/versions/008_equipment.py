"""Equipment catalogue and normalized equipment properties."""
from alembic import op
import sqlalchemy as sa

revision = "dnd_008_equipment"
down_revision = "dnd_007_backgrounds_feats"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "equipment_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.UniqueConstraint("edition_id", "name", name="uq_equipment_category_edition_name"),
    )
    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("equipment_categories.id", ondelete="SET NULL")),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL")),
        sa.Column("external_id", sa.String(160)),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("cost_quantity", sa.Numeric(10, 2)),
        sa.Column("cost_unit", sa.String(20)),
        sa.Column("weight", sa.Numeric(10, 2)),
        sa.Column("rarity", sa.String(40)),
        sa.Column("is_magical", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("properties", sa.JSON()),
        sa.Column("weapon_data", sa.JSON()),
        sa.Column("armor_data", sa.JSON()),
        sa.Column("container_capacity", sa.String(120)),
        sa.UniqueConstraint("edition_id", "name", name="uq_equipment_edition_name"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_equipment_source_external"),
    )
    op.create_table(
        "equipment_property_definitions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("description", sa.Text()),
        sa.UniqueConstraint("edition_id", "name", name="uq_equipment_property_edition_name"),
    )
    op.create_table(
        "equipment_property_links",
        sa.Column("equipment_id", sa.Integer(), sa.ForeignKey("equipment.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("equipment_property_definitions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("value", sa.String(160)),
    )
    op.create_index("ix_equipment_edition_category", "equipment", ["edition_id", "category_id"])
    op.create_index("ix_equipment_name", "equipment", ["name"])


def downgrade():
    op.drop_index("ix_equipment_name", table_name="equipment")
    op.drop_index("ix_equipment_edition_category", table_name="equipment")
    op.drop_table("equipment_property_links")
    op.drop_table("equipment_property_definitions")
    op.drop_table("equipment")
    op.drop_table("equipment_categories")
