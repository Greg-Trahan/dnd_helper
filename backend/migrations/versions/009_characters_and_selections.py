"""Characters and their normalized class, choice, proficiency, and inventory selections."""
from alembic import op
import sqlalchemy as sa

revision = "dnd_009_characters"
down_revision = "dnd_008_equipment"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "characters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("edition_id", sa.Integer(), sa.ForeignKey("editions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("species_id", sa.Integer(), sa.ForeignKey("species.id", ondelete="RESTRICT")),
        sa.Column("species_variant_id", sa.Integer(), sa.ForeignKey("species_variants.id", ondelete="SET NULL")),
        sa.Column("background_id", sa.Integer(), sa.ForeignKey("backgrounds.id", ondelete="SET NULL")),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("experience_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("alignment", sa.String(80)),
        sa.Column("size", sa.String(80)),
        sa.Column("speed", sa.Integer()),
        sa.Column("ability_scores", sa.JSON()),
        sa.Column("hit_point_maximum", sa.Integer()),
        sa.Column("current_hit_points", sa.Integer()),
        sa.Column("temporary_hit_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("armor_class", sa.Integer()),
        sa.Column("initiative_bonus", sa.Integer()),
        sa.Column("proficiency_bonus", sa.Integer()),
        sa.Column("death_saves", sa.JSON()),
        sa.Column("personality_traits", sa.Text()),
        sa.Column("ideals", sa.Text()),
        sa.Column("bonds", sa.Text()),
        sa.Column("flaws", sa.Text()),
        sa.Column("backstory", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "character_classes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("character_id", sa.Integer(), sa.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("class_id", sa.Integer(), sa.ForeignKey("classes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("subclass_id", sa.Integer(), sa.ForeignKey("subclasses.id", ondelete="SET NULL")),
        sa.Column("class_level", sa.Integer(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("character_id", "class_id", name="uq_character_class"),
    )
    op.create_table(
        "character_feature_selections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("character_id", sa.Integer(), sa.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_id", sa.Integer(), sa.ForeignKey("features.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("source_type", sa.String(40)),
        sa.Column("source_id", sa.Integer()),
        sa.Column("selected_at_level", sa.Integer()),
        sa.Column("uses_remaining", sa.Integer()),
        sa.Column("uses_maximum", sa.Integer()),
        sa.Column("state", sa.JSON()),
    )
    op.create_table(
        "character_choice_selections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("character_id", sa.Integer(), sa.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("choice_group_id", sa.Integer(), sa.ForeignKey("feature_choice_groups.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("option_id", sa.Integer(), sa.ForeignKey("feature_options.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("selected_at_level", sa.Integer()),
        sa.UniqueConstraint("character_id", "choice_group_id", "option_id", name="uq_character_choice_option"),
    )
    op.create_table(
        "character_proficiencies",
        sa.Column("character_id", sa.Integer(), sa.ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("proficiency_id", sa.Integer(), sa.ForeignKey("proficiencies.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("source_type", sa.String(40)),
        sa.Column("source_id", sa.Integer()),
        sa.Column("expertise", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "character_languages",
        sa.Column("character_id", sa.Integer(), sa.ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("language_id", sa.Integer(), sa.ForeignKey("languages.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("source_type", sa.String(40)),
        sa.Column("source_id", sa.Integer()),
    )
    op.create_table(
        "character_feats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("character_id", sa.Integer(), sa.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feat_id", sa.Integer(), sa.ForeignKey("feats.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("selected_at_level", sa.Integer()),
        sa.UniqueConstraint("character_id", "feat_id", name="uq_character_feat"),
    )
    op.create_table(
        "character_inventory",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("character_id", sa.Integer(), sa.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("equipment_id", sa.Integer(), sa.ForeignKey("equipment.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_equipped", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_attuned", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("notes", sa.Text()),
    )
    op.create_index("ix_characters_edition", "characters", ["edition_id"])
    op.create_index("ix_character_classes_character", "character_classes", ["character_id"])
    op.create_index("ix_character_features_character", "character_feature_selections", ["character_id"])
    op.create_index("ix_character_inventory_character", "character_inventory", ["character_id"])


def downgrade():
    op.drop_index("ix_character_inventory_character", table_name="character_inventory")
    op.drop_index("ix_character_features_character", table_name="character_feature_selections")
    op.drop_index("ix_character_classes_character", table_name="character_classes")
    op.drop_index("ix_characters_edition", table_name="characters")
    for table in (
        "character_inventory", "character_feats", "character_languages",
        "character_proficiencies", "character_choice_selections",
        "character_feature_selections", "character_classes", "characters",
    ):
        op.drop_table(table)
