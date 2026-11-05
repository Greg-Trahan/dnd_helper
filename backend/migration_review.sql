BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> b9af956d3d3c

CREATE TABLE campaigns (
    id SERIAL NOT NULL, 
    name VARCHAR(150) NOT NULL, 
    description TEXT, 
    PRIMARY KEY (id)
);

INSERT INTO alembic_version (version_num) VALUES ('b9af956d3d3c') RETURNING alembic_version.version_num;

-- Running upgrade b9af956d3d3c -> cbfc6e0cc6ff

CREATE TABLE items (
    id SERIAL NOT NULL, 
    campaign_id INTEGER, 
    name VARCHAR(150) NOT NULL, 
    item_type VARCHAR(100), 
    rarity VARCHAR(50), 
    weight VARCHAR(30), 
    value VARCHAR(50), 
    requires_attunement BOOLEAN NOT NULL, 
    properties JSON, 
    description TEXT, 
    source VARCHAR(150), 
    PRIMARY KEY (id), 
    FOREIGN KEY(campaign_id) REFERENCES campaigns (id)
);

CREATE TABLE locations (
    id SERIAL NOT NULL, 
    campaign_id INTEGER NOT NULL, 
    name VARCHAR(150) NOT NULL, 
    location_type VARCHAR(100), 
    description TEXT, 
    history TEXT, 
    notable_features JSON, 
    parent_location_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(campaign_id) REFERENCES campaigns (id), 
    FOREIGN KEY(parent_location_id) REFERENCES locations (id)
);

CREATE TABLE monsters (
    id SERIAL NOT NULL, 
    campaign_id INTEGER, 
    name VARCHAR(150) NOT NULL, 
    size VARCHAR(50), 
    creature_type JSON, 
    alignment VARCHAR(50), 
    challenge_rating VARCHAR(20), 
    armor_class INTEGER, 
    hit_points INTEGER, 
    speed VARCHAR(150), 
    ability_scores JSON, 
    abilities JSON, 
    description TEXT, 
    source VARCHAR(150), 
    PRIMARY KEY (id), 
    FOREIGN KEY(campaign_id) REFERENCES campaigns (id)
);

CREATE TABLE npcs (
    id SERIAL NOT NULL, 
    campaign_id INTEGER NOT NULL, 
    name VARCHAR(150) NOT NULL, 
    race VARCHAR(100), 
    class VARCHAR(100), 
    occupation VARCHAR(150), 
    alignment VARCHAR(50), 
    description TEXT, 
    personality TEXT, 
    backstory TEXT, 
    notes TEXT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(campaign_id) REFERENCES campaigns (id)
);

CREATE TABLE players (
    id SERIAL NOT NULL, 
    campaign_id INTEGER NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    email VARCHAR(255), 
    notes TEXT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(campaign_id) REFERENCES campaigns (id)
);

CREATE TABLE encounters (
    id SERIAL NOT NULL, 
    campaign_id INTEGER NOT NULL, 
    location_id INTEGER, 
    name VARCHAR(150) NOT NULL, 
    encounter_type VARCHAR(100), 
    difficulty VARCHAR(50), 
    description TEXT, 
    setup TEXT, 
    notes TEXT, 
    status VARCHAR(30) NOT NULL, 
    scheduled_at TIMESTAMP WITH TIME ZONE, 
    environment JSON, 
    PRIMARY KEY (id), 
    FOREIGN KEY(campaign_id) REFERENCES campaigns (id), 
    FOREIGN KEY(location_id) REFERENCES locations (id)
);

CREATE TABLE inventories (
    id SERIAL NOT NULL, 
    item_id INTEGER NOT NULL, 
    owner_type VARCHAR(30) NOT NULL, 
    owner_id INTEGER NOT NULL, 
    quantity INTEGER NOT NULL, 
    equipped BOOLEAN NOT NULL, 
    notes TEXT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(item_id) REFERENCES items (id), 
    CONSTRAINT uq_inventory_owner_item UNIQUE (item_id, owner_type, owner_id)
);

CREATE TABLE encounter_monsters (
    id SERIAL NOT NULL, 
    encounter_id INTEGER NOT NULL, 
    monster_id INTEGER NOT NULL, 
    quantity INTEGER NOT NULL, 
    notes TEXT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(encounter_id) REFERENCES encounters (id), 
    FOREIGN KEY(monster_id) REFERENCES monsters (id)
);

UPDATE alembic_version SET version_num='cbfc6e0cc6ff' WHERE alembic_version.version_num = 'b9af956d3d3c';

-- Running upgrade cbfc6e0cc6ff -> 026948cc0771

CREATE TABLE location_npcs (
    id SERIAL NOT NULL, 
    location_id INTEGER NOT NULL, 
    npc_id INTEGER NOT NULL, 
    quantity INTEGER NOT NULL, 
    notes TEXT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(location_id) REFERENCES locations (id), 
    FOREIGN KEY(npc_id) REFERENCES npcs (id)
);

ALTER TABLE npcs ADD COLUMN character_class VARCHAR(100);

ALTER TABLE npcs DROP COLUMN class;

UPDATE alembic_version SET version_num='026948cc0771' WHERE alembic_version.version_num = 'cbfc6e0cc6ff';

-- Running upgrade 026948cc0771 -> d55abb67fdf6

ALTER TABLE monsters ADD COLUMN edition VARCHAR(10);

ALTER TABLE monsters ADD COLUMN source_key VARCHAR(100);

ALTER TABLE monsters ADD COLUMN source_id VARCHAR(150);

ALTER TABLE monsters ADD COLUMN raw_data JSON;

ALTER TABLE monsters ADD CONSTRAINT uq_monster_source UNIQUE (source_key, source_id);

UPDATE alembic_version SET version_num='d55abb67fdf6' WHERE alembic_version.version_num = '026948cc0771';

-- Running upgrade d55abb67fdf6 -> 1e1e8c430c2b

ALTER TABLE monsters ALTER COLUMN challenge_rating TYPE FLOAT USING challenge_rating::double precision;

ALTER TABLE monsters ALTER COLUMN speed TYPE JSON USING speed::json;

UPDATE alembic_version SET version_num='1e1e8c430c2b' WHERE alembic_version.version_num = 'd55abb67fdf6';

-- Running upgrade 1e1e8c430c2b -> 808e9000ae37

CREATE TABLE feats (
    id SERIAL NOT NULL, 
    name VARCHAR(150) NOT NULL, 
    edition VARCHAR(10), 
    source_key VARCHAR(100), 
    source_id VARCHAR(150), 
    source VARCHAR(150), 
    feat_type VARCHAR(50), 
    has_prerequisite BOOLEAN, 
    prerequisite TEXT, 
    description TEXT, 
    benefits JSON, 
    crossreferences JSON, 
    raw_data JSON, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_feat_source UNIQUE (source_key, source_id)
);

CREATE TABLE spells (
    id SERIAL NOT NULL, 
    name VARCHAR(150) NOT NULL, 
    edition VARCHAR(10), 
    source_key VARCHAR(100), 
    source_id VARCHAR(150), 
    source VARCHAR(150), 
    school VARCHAR(50), 
    school_key VARCHAR(50), 
    classes JSON, 
    casting_options JSON, 
    level INTEGER, 
    description TEXT, 
    higher_level TEXT, 
    target_type VARCHAR(100), 
    target_count INTEGER, 
    range INTEGER, 
    range_text VARCHAR(100), 
    range_unit VARCHAR(30), 
    shape_type VARCHAR(50), 
    shape_size FLOAT, 
    shape_size_unit VARCHAR(30), 
    casting_time VARCHAR(100), 
    reaction_condition TEXT, 
    duration VARCHAR(100), 
    ritual BOOLEAN, 
    concentration BOOLEAN, 
    verbal BOOLEAN, 
    somatic BOOLEAN, 
    material BOOLEAN, 
    material_specified TEXT, 
    material_cost JSON, 
    material_consumed BOOLEAN, 
    saving_throw_ability VARCHAR(30), 
    attack_roll BOOLEAN, 
    damage_roll VARCHAR(100), 
    damage_types JSON, 
    crossreferences JSON, 
    raw_data JSON, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_spell_source UNIQUE (source_key, source_id)
);

UPDATE alembic_version SET version_num='808e9000ae37' WHERE alembic_version.version_num = '1e1e8c430c2b';

-- Running upgrade 808e9000ae37 -> 7c1f5e17c533

DROP TABLE feats;

UPDATE alembic_version SET version_num='7c1f5e17c533' WHERE alembic_version.version_num = '808e9000ae37';

-- Running upgrade 7c1f5e17c533 -> dnd_001_shared_refs

CREATE TABLE sources (
    id SERIAL NOT NULL, 
    name VARCHAR(120) NOT NULL, 
    url VARCHAR(500), 
    description TEXT, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE editions (
    id SERIAL NOT NULL, 
    code VARCHAR(20) NOT NULL, 
    name VARCHAR(80) NOT NULL, 
    year INTEGER, 
    description TEXT, 
    PRIMARY KEY (id), 
    UNIQUE (code)
);

CREATE TABLE proficiencies (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    name VARCHAR(120) NOT NULL, 
    category VARCHAR(40) NOT NULL, 
    description TEXT, 
    source_id INTEGER, 
    external_id VARCHAR(160), 
    PRIMARY KEY (id), 
    CONSTRAINT uq_proficiency_edition_name_category UNIQUE (edition_id, name, category), 
    CONSTRAINT uq_proficiency_source_external UNIQUE (source_id, external_id), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE, 
    FOREIGN KEY(source_id) REFERENCES sources (id) ON DELETE SET NULL
);

CREATE TABLE languages (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    typical_speakers TEXT, 
    script VARCHAR(100), 
    description TEXT, 
    source_id INTEGER, 
    external_id VARCHAR(160), 
    PRIMARY KEY (id), 
    CONSTRAINT uq_language_edition_name UNIQUE (edition_id, name), 
    CONSTRAINT uq_language_source_external UNIQUE (source_id, external_id), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE, 
    FOREIGN KEY(source_id) REFERENCES sources (id) ON DELETE SET NULL
);

CREATE TABLE damage_types (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    name VARCHAR(60) NOT NULL, 
    description TEXT, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_damage_type_edition_name UNIQUE (edition_id, name), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE
);

CREATE TABLE conditions (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    description TEXT NOT NULL, 
    source_id INTEGER, 
    external_id VARCHAR(160), 
    PRIMARY KEY (id), 
    CONSTRAINT uq_condition_edition_name UNIQUE (edition_id, name), 
    CONSTRAINT uq_condition_source_external UNIQUE (source_id, external_id), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE, 
    FOREIGN KEY(source_id) REFERENCES sources (id) ON DELETE SET NULL
);

CREATE INDEX ix_proficiencies_edition_category ON proficiencies (edition_id, category);

CREATE INDEX ix_languages_edition ON languages (edition_id);

CREATE INDEX ix_conditions_edition ON conditions (edition_id);

UPDATE alembic_version SET version_num='dnd_001_shared_refs' WHERE alembic_version.version_num = '7c1f5e17c533';

-- Running upgrade dnd_001_shared_refs -> dnd_002_classes

CREATE TABLE classes (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    source_id INTEGER, 
    external_id VARCHAR(160), 
    name VARCHAR(100) NOT NULL, 
    description TEXT, 
    hit_die INTEGER, 
    primary_ability VARCHAR(120), 
    saving_throw_proficiency_ids JSON, 
    starting_equipment JSON, 
    multiclassing JSON, 
    is_playable BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_class_edition_name UNIQUE (edition_id, name), 
    CONSTRAINT uq_class_source_external UNIQUE (source_id, external_id), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE, 
    FOREIGN KEY(source_id) REFERENCES sources (id) ON DELETE SET NULL
);

CREATE TABLE subclasses (
    id SERIAL NOT NULL, 
    class_id INTEGER NOT NULL, 
    edition_id INTEGER NOT NULL, 
    source_id INTEGER, 
    external_id VARCHAR(160), 
    name VARCHAR(120) NOT NULL, 
    description TEXT, 
    subclass_level INTEGER, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_subclass_class_name UNIQUE (class_id, name), 
    CONSTRAINT uq_subclass_source_external UNIQUE (source_id, external_id), 
    FOREIGN KEY(class_id) REFERENCES classes (id) ON DELETE CASCADE, 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE, 
    FOREIGN KEY(source_id) REFERENCES sources (id) ON DELETE SET NULL
);

CREATE INDEX ix_classes_edition ON classes (edition_id);

CREATE INDEX ix_subclasses_class ON subclasses (class_id);

CREATE INDEX ix_subclasses_edition ON subclasses (edition_id);

UPDATE alembic_version SET version_num='dnd_002_classes' WHERE alembic_version.version_num = 'dnd_001_shared_refs';

-- Running upgrade dnd_002_classes -> dnd_003_features

CREATE TABLE features (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    source_id INTEGER, 
    external_id VARCHAR(160), 
    name VARCHAR(160) NOT NULL, 
    feature_type VARCHAR(50) NOT NULL, 
    description TEXT NOT NULL, 
    rules_text TEXT, 
    mechanics JSON, 
    uses_formula VARCHAR(200), 
    recharge VARCHAR(80), 
    activation VARCHAR(80), 
    duration VARCHAR(120), 
    is_repeatable BOOLEAN DEFAULT false NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_feature_edition_name_type UNIQUE (edition_id, name, feature_type), 
    CONSTRAINT uq_feature_source_external UNIQUE (source_id, external_id), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE, 
    FOREIGN KEY(source_id) REFERENCES sources (id) ON DELETE SET NULL
);

CREATE TABLE class_feature_grants (
    id SERIAL NOT NULL, 
    class_id INTEGER NOT NULL, 
    feature_id INTEGER NOT NULL, 
    character_level INTEGER NOT NULL, 
    display_order INTEGER DEFAULT '0' NOT NULL, 
    grant_notes TEXT, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_class_feature_level UNIQUE (class_id, feature_id, character_level), 
    FOREIGN KEY(class_id) REFERENCES classes (id) ON DELETE CASCADE, 
    FOREIGN KEY(feature_id) REFERENCES features (id) ON DELETE CASCADE
);

CREATE TABLE subclass_feature_grants (
    id SERIAL NOT NULL, 
    subclass_id INTEGER NOT NULL, 
    feature_id INTEGER NOT NULL, 
    character_level INTEGER NOT NULL, 
    display_order INTEGER DEFAULT '0' NOT NULL, 
    grant_notes TEXT, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_subclass_feature_level UNIQUE (subclass_id, feature_id, character_level), 
    FOREIGN KEY(subclass_id) REFERENCES subclasses (id) ON DELETE CASCADE, 
    FOREIGN KEY(feature_id) REFERENCES features (id) ON DELETE CASCADE
);

CREATE INDEX ix_features_edition_type ON features (edition_id, feature_type);

CREATE INDEX ix_class_feature_level ON class_feature_grants (class_id, character_level);

CREATE INDEX ix_subclass_feature_level ON subclass_feature_grants (subclass_id, character_level);

UPDATE alembic_version SET version_num='dnd_003_features' WHERE alembic_version.version_num = 'dnd_002_classes';

-- Running upgrade dnd_003_features -> dnd_004_choices

CREATE TABLE feature_choice_groups (
    id SERIAL NOT NULL, 
    feature_id INTEGER NOT NULL, 
    name VARCHAR(140) NOT NULL, 
    description TEXT, 
    min_choices INTEGER DEFAULT '1' NOT NULL, 
    max_choices INTEGER DEFAULT '1' NOT NULL, 
    selection_mode VARCHAR(30) DEFAULT 'select' NOT NULL, 
    is_required BOOLEAN DEFAULT true NOT NULL, 
    display_order INTEGER DEFAULT '0' NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_feature_choice_group_name UNIQUE (feature_id, name), 
    FOREIGN KEY(feature_id) REFERENCES features (id) ON DELETE CASCADE
);

CREATE TABLE feature_options (
    id SERIAL NOT NULL, 
    choice_group_id INTEGER NOT NULL, 
    name VARCHAR(160) NOT NULL, 
    description TEXT, 
    mechanics JSON, 
    display_order INTEGER DEFAULT '0' NOT NULL, 
    is_default BOOLEAN DEFAULT false NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_feature_option_group_name UNIQUE (choice_group_id, name), 
    FOREIGN KEY(choice_group_id) REFERENCES feature_choice_groups (id) ON DELETE CASCADE
);

CREATE TABLE feature_prerequisites (
    id SERIAL NOT NULL, 
    feature_id INTEGER NOT NULL, 
    prerequisite_type VARCHAR(50) NOT NULL, 
    operator VARCHAR(20) DEFAULT 'eq' NOT NULL, 
    value VARCHAR(200) NOT NULL, 
    description TEXT, 
    is_hard_requirement BOOLEAN DEFAULT true NOT NULL, 
    group_key VARCHAR(60), 
    PRIMARY KEY (id), 
    FOREIGN KEY(feature_id) REFERENCES features (id) ON DELETE CASCADE
);

CREATE INDEX ix_feature_options_group ON feature_options (choice_group_id);

CREATE INDEX ix_feature_prerequisites_feature ON feature_prerequisites (feature_id);

UPDATE alembic_version SET version_num='dnd_004_choices' WHERE alembic_version.version_num = 'dnd_003_features';

-- Running upgrade dnd_004_choices -> dnd_005_class_progression

CREATE TABLE class_level_progressions (
    id SERIAL NOT NULL, 
    class_id INTEGER NOT NULL, 
    level INTEGER NOT NULL, 
    proficiency_bonus INTEGER NOT NULL, 
    features_summary TEXT, 
    progression_data JSON, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_class_progression_level UNIQUE (class_id, level), 
    FOREIGN KEY(class_id) REFERENCES classes (id) ON DELETE CASCADE
);

CREATE TABLE class_resources (
    id SERIAL NOT NULL, 
    class_id INTEGER NOT NULL, 
    name VARCHAR(120) NOT NULL, 
    description TEXT, 
    recovery VARCHAR(80), 
    uses_formula VARCHAR(200), 
    resource_key VARCHAR(80), 
    PRIMARY KEY (id), 
    CONSTRAINT uq_class_resource_key UNIQUE (class_id, resource_key), 
    FOREIGN KEY(class_id) REFERENCES classes (id) ON DELETE CASCADE
);

CREATE TABLE class_resource_progressions (
    id SERIAL NOT NULL, 
    resource_id INTEGER NOT NULL, 
    level INTEGER NOT NULL, 
    maximum_uses INTEGER, 
    formula VARCHAR(200), 
    notes TEXT, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_resource_progression_level UNIQUE (resource_id, level), 
    FOREIGN KEY(resource_id) REFERENCES class_resources (id) ON DELETE CASCADE
);

CREATE INDEX ix_class_progression_class_level ON class_level_progressions (class_id, level);

UPDATE alembic_version SET version_num='dnd_005_class_progression' WHERE alembic_version.version_num = 'dnd_004_choices';

-- Running upgrade dnd_005_class_progression -> dnd_006_species

CREATE TABLE species (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    source_id INTEGER, 
    external_id VARCHAR(160), 
    name VARCHAR(120) NOT NULL, 
    description TEXT, 
    size VARCHAR(80), 
    creature_type VARCHAR(80) DEFAULT 'Humanoid' NOT NULL, 
    base_speed INTEGER, 
    ability_score_rules JSON, 
    age TEXT, 
    alignment TEXT, 
    languages_summary TEXT, 
    is_playable BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_species_edition_name UNIQUE (edition_id, name), 
    CONSTRAINT uq_species_source_external UNIQUE (source_id, external_id), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE, 
    FOREIGN KEY(source_id) REFERENCES sources (id) ON DELETE SET NULL
);

CREATE TABLE species_variants (
    id SERIAL NOT NULL, 
    species_id INTEGER NOT NULL, 
    name VARCHAR(140) NOT NULL, 
    description TEXT, 
    size_override VARCHAR(80), 
    speed_override INTEGER, 
    ability_score_rules JSON, 
    mechanics JSON, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_species_variant_name UNIQUE (species_id, name), 
    FOREIGN KEY(species_id) REFERENCES species (id) ON DELETE CASCADE
);

CREATE TABLE species_feature_grants (
    id SERIAL NOT NULL, 
    species_id INTEGER NOT NULL, 
    variant_id INTEGER, 
    feature_id INTEGER NOT NULL, 
    display_order INTEGER DEFAULT '0' NOT NULL, 
    grant_notes TEXT, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_species_variant_feature UNIQUE (species_id, variant_id, feature_id), 
    FOREIGN KEY(species_id) REFERENCES species (id) ON DELETE CASCADE, 
    FOREIGN KEY(variant_id) REFERENCES species_variants (id) ON DELETE CASCADE, 
    FOREIGN KEY(feature_id) REFERENCES features (id) ON DELETE CASCADE
);

CREATE INDEX ix_species_edition ON species (edition_id);

CREATE INDEX ix_species_variants_species ON species_variants (species_id);

UPDATE alembic_version SET version_num='dnd_006_species' WHERE alembic_version.version_num = 'dnd_005_class_progression';

-- Running upgrade dnd_006_species -> dnd_007_backgrounds_feats

CREATE TABLE backgrounds (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    source_id INTEGER, 
    external_id VARCHAR(160), 
    name VARCHAR(140) NOT NULL, 
    description TEXT, 
    skill_proficiencies JSON, 
    tool_proficiencies JSON, 
    languages JSON, 
    starting_equipment JSON, 
    ability_score_rules JSON, 
    feature_id INTEGER, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_background_edition_name UNIQUE (edition_id, name), 
    CONSTRAINT uq_background_source_external UNIQUE (source_id, external_id), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE, 
    FOREIGN KEY(source_id) REFERENCES sources (id) ON DELETE SET NULL, 
    FOREIGN KEY(feature_id) REFERENCES features (id) ON DELETE SET NULL
);

CREATE TABLE feats (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    source_id INTEGER, 
    external_id VARCHAR(160), 
    name VARCHAR(160) NOT NULL, 
    description TEXT NOT NULL, 
    feat_type VARCHAR(60), 
    repeatable BOOLEAN DEFAULT false NOT NULL, 
    mechanics JSON, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_feat_edition_name UNIQUE (edition_id, name), 
    CONSTRAINT uq_feat_source_external UNIQUE (source_id, external_id), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE, 
    FOREIGN KEY(source_id) REFERENCES sources (id) ON DELETE SET NULL
);

CREATE TABLE feat_prerequisites (
    id SERIAL NOT NULL, 
    feat_id INTEGER NOT NULL, 
    prerequisite_type VARCHAR(50) NOT NULL, 
    operator VARCHAR(20) DEFAULT 'eq' NOT NULL, 
    value VARCHAR(200) NOT NULL, 
    description TEXT, 
    is_hard_requirement BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(feat_id) REFERENCES feats (id) ON DELETE CASCADE
);

CREATE TABLE feat_feature_links (
    id SERIAL NOT NULL, 
    feat_id INTEGER NOT NULL, 
    feature_id INTEGER NOT NULL, 
    display_order INTEGER DEFAULT '0' NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_feat_feature_link UNIQUE (feat_id, feature_id), 
    FOREIGN KEY(feat_id) REFERENCES feats (id) ON DELETE CASCADE, 
    FOREIGN KEY(feature_id) REFERENCES features (id) ON DELETE CASCADE
);

CREATE INDEX ix_backgrounds_edition ON backgrounds (edition_id);

CREATE INDEX ix_feats_edition ON feats (edition_id);

UPDATE alembic_version SET version_num='dnd_007_backgrounds_feats' WHERE alembic_version.version_num = 'dnd_006_species';

-- Running upgrade dnd_007_backgrounds_feats -> dnd_008_equipment

CREATE TABLE equipment_categories (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    description TEXT, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_equipment_category_edition_name UNIQUE (edition_id, name), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE
);

CREATE TABLE equipment (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    category_id INTEGER, 
    source_id INTEGER, 
    external_id VARCHAR(160), 
    name VARCHAR(160) NOT NULL, 
    description TEXT, 
    cost_quantity NUMERIC(10, 2), 
    cost_unit VARCHAR(20), 
    weight NUMERIC(10, 2), 
    rarity VARCHAR(40), 
    is_magical BOOLEAN DEFAULT false NOT NULL, 
    properties JSON, 
    weapon_data JSON, 
    armor_data JSON, 
    container_capacity VARCHAR(120), 
    PRIMARY KEY (id), 
    CONSTRAINT uq_equipment_edition_name UNIQUE (edition_id, name), 
    CONSTRAINT uq_equipment_source_external UNIQUE (source_id, external_id), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE, 
    FOREIGN KEY(category_id) REFERENCES equipment_categories (id) ON DELETE SET NULL, 
    FOREIGN KEY(source_id) REFERENCES sources (id) ON DELETE SET NULL
);

CREATE TABLE equipment_property_definitions (
    id SERIAL NOT NULL, 
    edition_id INTEGER NOT NULL, 
    name VARCHAR(80) NOT NULL, 
    description TEXT, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_equipment_property_edition_name UNIQUE (edition_id, name), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE CASCADE
);

CREATE TABLE equipment_property_links (
    equipment_id INTEGER NOT NULL, 
    property_id INTEGER NOT NULL, 
    value VARCHAR(160), 
    PRIMARY KEY (equipment_id, property_id), 
    FOREIGN KEY(equipment_id) REFERENCES equipment (id) ON DELETE CASCADE, 
    FOREIGN KEY(property_id) REFERENCES equipment_property_definitions (id) ON DELETE CASCADE
);

CREATE INDEX ix_equipment_edition_category ON equipment (edition_id, category_id);

CREATE INDEX ix_equipment_name ON equipment (name);

UPDATE alembic_version SET version_num='dnd_008_equipment' WHERE alembic_version.version_num = 'dnd_007_backgrounds_feats';

-- Running upgrade dnd_008_equipment -> dnd_009_characters

CREATE TABLE characters (
    id SERIAL NOT NULL, 
    name VARCHAR(120) NOT NULL, 
    edition_id INTEGER NOT NULL, 
    species_id INTEGER, 
    species_variant_id INTEGER, 
    background_id INTEGER, 
    level INTEGER DEFAULT '1' NOT NULL, 
    experience_points INTEGER DEFAULT '0' NOT NULL, 
    alignment VARCHAR(80), 
    size VARCHAR(80), 
    speed INTEGER, 
    ability_scores JSON, 
    hit_point_maximum INTEGER, 
    current_hit_points INTEGER, 
    temporary_hit_points INTEGER DEFAULT '0' NOT NULL, 
    armor_class INTEGER, 
    initiative_bonus INTEGER, 
    proficiency_bonus INTEGER, 
    death_saves JSON, 
    personality_traits TEXT, 
    ideals TEXT, 
    bonds TEXT, 
    flaws TEXT, 
    backstory TEXT, 
    notes TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(edition_id) REFERENCES editions (id) ON DELETE RESTRICT, 
    FOREIGN KEY(species_id) REFERENCES species (id) ON DELETE RESTRICT, 
    FOREIGN KEY(species_variant_id) REFERENCES species_variants (id) ON DELETE SET NULL, 
    FOREIGN KEY(background_id) REFERENCES backgrounds (id) ON DELETE SET NULL
);

CREATE TABLE character_classes (
    id SERIAL NOT NULL, 
    character_id INTEGER NOT NULL, 
    class_id INTEGER NOT NULL, 
    subclass_id INTEGER, 
    class_level INTEGER NOT NULL, 
    is_primary BOOLEAN DEFAULT false NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_character_class UNIQUE (character_id, class_id), 
    FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE, 
    FOREIGN KEY(class_id) REFERENCES classes (id) ON DELETE RESTRICT, 
    FOREIGN KEY(subclass_id) REFERENCES subclasses (id) ON DELETE SET NULL
);

CREATE TABLE character_feature_selections (
    id SERIAL NOT NULL, 
    character_id INTEGER NOT NULL, 
    feature_id INTEGER NOT NULL, 
    source_type VARCHAR(40), 
    source_id INTEGER, 
    selected_at_level INTEGER, 
    uses_remaining INTEGER, 
    uses_maximum INTEGER, 
    state JSON, 
    PRIMARY KEY (id), 
    FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE, 
    FOREIGN KEY(feature_id) REFERENCES features (id) ON DELETE RESTRICT
);

CREATE TABLE character_choice_selections (
    id SERIAL NOT NULL, 
    character_id INTEGER NOT NULL, 
    choice_group_id INTEGER NOT NULL, 
    option_id INTEGER NOT NULL, 
    selected_at_level INTEGER, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_character_choice_option UNIQUE (character_id, choice_group_id, option_id), 
    FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE, 
    FOREIGN KEY(choice_group_id) REFERENCES feature_choice_groups (id) ON DELETE RESTRICT, 
    FOREIGN KEY(option_id) REFERENCES feature_options (id) ON DELETE RESTRICT
);

CREATE TABLE character_proficiencies (
    character_id INTEGER NOT NULL, 
    proficiency_id INTEGER NOT NULL, 
    source_type VARCHAR(40), 
    source_id INTEGER, 
    expertise BOOLEAN DEFAULT false NOT NULL, 
    PRIMARY KEY (character_id, proficiency_id), 
    FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE, 
    FOREIGN KEY(proficiency_id) REFERENCES proficiencies (id) ON DELETE RESTRICT
);

CREATE TABLE character_languages (
    character_id INTEGER NOT NULL, 
    language_id INTEGER NOT NULL, 
    source_type VARCHAR(40), 
    source_id INTEGER, 
    PRIMARY KEY (character_id, language_id), 
    FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE, 
    FOREIGN KEY(language_id) REFERENCES languages (id) ON DELETE RESTRICT
);

CREATE TABLE character_feats (
    id SERIAL NOT NULL, 
    character_id INTEGER NOT NULL, 
    feat_id INTEGER NOT NULL, 
    selected_at_level INTEGER, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_character_feat UNIQUE (character_id, feat_id), 
    FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE, 
    FOREIGN KEY(feat_id) REFERENCES feats (id) ON DELETE RESTRICT
);

CREATE TABLE character_inventory (
    id SERIAL NOT NULL, 
    character_id INTEGER NOT NULL, 
    equipment_id INTEGER NOT NULL, 
    quantity INTEGER DEFAULT '1' NOT NULL, 
    is_equipped BOOLEAN DEFAULT false NOT NULL, 
    is_attuned BOOLEAN DEFAULT false NOT NULL, 
    notes TEXT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE, 
    FOREIGN KEY(equipment_id) REFERENCES equipment (id) ON DELETE RESTRICT
);

CREATE INDEX ix_characters_edition ON characters (edition_id);

CREATE INDEX ix_character_classes_character ON character_classes (character_id);

CREATE INDEX ix_character_features_character ON character_feature_selections (character_id);

CREATE INDEX ix_character_inventory_character ON character_inventory (character_id);

UPDATE alembic_version SET version_num='dnd_009_characters' WHERE alembic_version.version_num = 'dnd_008_equipment';

COMMIT;

