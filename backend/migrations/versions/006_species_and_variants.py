"""Species, species variants, and species feature grants."""
from alembic import op
import sqlalchemy as sa

revision = "dnd_006_species"
down_revision = "dnd_005_class_progression"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "species",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL")),
        sa.Column("external_id", sa.String(160)),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("size", sa.String(80)),
        sa.Column("creature_type", sa.String(80), nullable=False, server_default="Humanoid"),
        sa.Column("base_speed", sa.Integer()),
        sa.Column("ability_score_rules", sa.JSON()),
        sa.Column("age", sa.Text()),
        sa.Column("alignment", sa.Text()),
        sa.Column("languages_summary", sa.Text()),
        sa.Column("is_playable", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("edition_id", "name", name="uq_species_edition_name"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_species_source_external"),
    )
    op.create_table(
        "species_variants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("species_id", sa.Integer(), sa.ForeignKey("species.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(140), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("size_override", sa.String(80)),
        sa.Column("speed_override", sa.Integer()),
        sa.Column("ability_score_rules", sa.JSON()),
        sa.Column("mechanics", sa.JSON()),
        sa.UniqueConstraint("species_id", "name", name="uq_species_variant_name"),
    )
    op.create_table(
        "species_feature_grants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("species_id", sa.Integer(), sa.ForeignKey("species.id", ondelete="CASCADE"), nullable=False),
        sa.Column("variant_id", sa.Integer(), sa.ForeignKey("species_variants.id", ondelete="CASCADE")),
        sa.Column("feature_id", sa.Integer(), sa.ForeignKey("features.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("grant_notes", sa.Text()),
        sa.UniqueConstraint("species_id", "variant_id", "feature_id", name="uq_species_variant_feature"),
    )
    op.create_index("ix_species_edition", "species", ["edition_id"])
    op.create_index("ix_species_variants_species", "species_variants", ["species_id"])


def downgrade():
    op.drop_index("ix_species_variants_species", table_name="species_variants")
    op.drop_index("ix_species_edition", table_name="species")
    op.drop_table("species_feature_grants")
    op.drop_table("species_variants")
    op.drop_table("species")
