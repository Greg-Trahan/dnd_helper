"""Shared source, edition, and rules reference tables."""
from alembic import op
import sqlalchemy as sa

revision = "dnd_001_shared_refs"
down_revision = "7c1f5e17c533"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("url", sa.String(500)),
        sa.Column("description", sa.Text()),
    )
    op.create_table(
        "editions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("year", sa.Integer()),
        sa.Column("description", sa.Text()),
    )
    op.create_table(
        "proficiencies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL")),
        sa.Column("external_id", sa.String(160)),
        sa.UniqueConstraint("edition_id", "name", "category", name="uq_proficiency_edition_name_category"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_proficiency_source_external"),
    )
    op.create_table(
        "languages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("typical_speakers", sa.Text()),
        sa.Column("script", sa.String(100)),
        sa.Column("description", sa.Text()),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL")),
        sa.Column("external_id", sa.String(160)),
        sa.UniqueConstraint("edition_id", "name", name="uq_language_edition_name"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_language_source_external"),
    )
    op.create_table(
        "damage_types",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(60), nullable=False),
        sa.Column("description", sa.Text()),
        sa.UniqueConstraint("edition_id", "name", name="uq_damage_type_edition_name"),
    )
    op.create_table(
        "conditions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL")),
        sa.Column("external_id", sa.String(160)),
        sa.UniqueConstraint("edition_id", "name", name="uq_condition_edition_name"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_condition_source_external"),
    )
    op.create_index("ix_proficiencies_edition_category", "proficiencies", ["edition_id", "category"])
    op.create_index("ix_languages_edition", "languages", ["edition_id"])
    op.create_index("ix_conditions_edition", "conditions", ["edition_id"])


def downgrade():
    op.drop_index("ix_conditions_edition", table_name="conditions")
    op.drop_index("ix_languages_edition", table_name="languages")
    op.drop_index("ix_proficiencies_edition_category", table_name="proficiencies")
    for table in ("conditions", "damage_types", "languages", "proficiencies", "editions", "sources"):
        op.drop_table(table)
