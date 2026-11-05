--
-- PostgreSQL database dump
--

\restrict 46fZ5LbfBRQKqf770JWW5lsXvaY6GRxtGfuV2dcL2MrmQ2UgVmYnxuFBzFf9C7A

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: backgrounds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backgrounds (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    source_id integer,
    external_id character varying(160),
    name character varying(140) NOT NULL,
    description text,
    skill_proficiencies json,
    tool_proficiencies json,
    languages json,
    starting_equipment json,
    ability_score_rules json,
    feature_id integer
);


--
-- Name: backgrounds_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backgrounds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backgrounds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backgrounds_id_seq OWNED BY public.backgrounds.id;


--
-- Name: campaigns; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.campaigns (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    description text
);


--
-- Name: campaigns_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.campaigns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: campaigns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.campaigns_id_seq OWNED BY public.campaigns.id;


--
-- Name: character_choice_selections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_choice_selections (
    id integer NOT NULL,
    character_id integer NOT NULL,
    choice_group_id integer NOT NULL,
    option_id integer NOT NULL,
    selected_at_level integer
);


--
-- Name: character_choice_selections_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.character_choice_selections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: character_choice_selections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.character_choice_selections_id_seq OWNED BY public.character_choice_selections.id;


--
-- Name: character_classes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_classes (
    id integer NOT NULL,
    character_id integer NOT NULL,
    class_id integer NOT NULL,
    subclass_id integer,
    class_level integer NOT NULL,
    is_primary boolean DEFAULT false NOT NULL
);


--
-- Name: character_classes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.character_classes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: character_classes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.character_classes_id_seq OWNED BY public.character_classes.id;


--
-- Name: character_feats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_feats (
    id integer NOT NULL,
    character_id integer NOT NULL,
    feat_id integer NOT NULL,
    selected_at_level integer
);


--
-- Name: character_feats_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.character_feats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: character_feats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.character_feats_id_seq OWNED BY public.character_feats.id;


--
-- Name: character_feature_selections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_feature_selections (
    id integer NOT NULL,
    character_id integer NOT NULL,
    feature_id integer NOT NULL,
    source_type character varying(40),
    source_id integer,
    selected_at_level integer,
    uses_remaining integer,
    uses_maximum integer,
    state json
);


--
-- Name: character_feature_selections_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.character_feature_selections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: character_feature_selections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.character_feature_selections_id_seq OWNED BY public.character_feature_selections.id;


--
-- Name: character_inventory; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_inventory (
    id integer NOT NULL,
    character_id integer NOT NULL,
    equipment_id integer NOT NULL,
    quantity integer DEFAULT 1 NOT NULL,
    is_equipped boolean DEFAULT false NOT NULL,
    is_attuned boolean DEFAULT false NOT NULL,
    notes text
);


--
-- Name: character_inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.character_inventory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: character_inventory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.character_inventory_id_seq OWNED BY public.character_inventory.id;


--
-- Name: character_languages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_languages (
    character_id integer NOT NULL,
    language_id integer NOT NULL,
    source_type character varying(40),
    source_id integer
);


--
-- Name: character_proficiencies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.character_proficiencies (
    character_id integer NOT NULL,
    proficiency_id integer NOT NULL,
    source_type character varying(40),
    source_id integer,
    expertise boolean DEFAULT false NOT NULL
);


--
-- Name: characters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.characters (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    edition_id integer NOT NULL,
    species_id integer,
    species_variant_id integer,
    background_id integer,
    level integer DEFAULT 1 NOT NULL,
    experience_points integer DEFAULT 0 NOT NULL,
    alignment character varying(80),
    size character varying(80),
    speed integer,
    ability_scores json,
    hit_point_maximum integer,
    current_hit_points integer,
    temporary_hit_points integer DEFAULT 0 NOT NULL,
    armor_class integer,
    initiative_bonus integer,
    proficiency_bonus integer,
    death_saves json,
    personality_traits text,
    ideals text,
    bonds text,
    flaws text,
    backstory text,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: characters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.characters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: characters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.characters_id_seq OWNED BY public.characters.id;


--
-- Name: class_feature_grants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.class_feature_grants (
    id integer NOT NULL,
    class_id integer NOT NULL,
    feature_id integer NOT NULL,
    character_level integer NOT NULL,
    display_order integer DEFAULT 0 NOT NULL,
    grant_notes text
);


--
-- Name: class_feature_grants_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.class_feature_grants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: class_feature_grants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.class_feature_grants_id_seq OWNED BY public.class_feature_grants.id;


--
-- Name: class_level_progressions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.class_level_progressions (
    id integer NOT NULL,
    class_id integer NOT NULL,
    level integer NOT NULL,
    proficiency_bonus integer NOT NULL,
    features_summary text,
    progression_data json
);


--
-- Name: class_level_progressions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.class_level_progressions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: class_level_progressions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.class_level_progressions_id_seq OWNED BY public.class_level_progressions.id;


--
-- Name: class_resource_progressions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.class_resource_progressions (
    id integer NOT NULL,
    resource_id integer NOT NULL,
    level integer NOT NULL,
    maximum_uses integer,
    formula character varying(200),
    notes text
);


--
-- Name: class_resource_progressions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.class_resource_progressions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: class_resource_progressions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.class_resource_progressions_id_seq OWNED BY public.class_resource_progressions.id;


--
-- Name: class_resources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.class_resources (
    id integer NOT NULL,
    class_id integer NOT NULL,
    name character varying(120) NOT NULL,
    description text,
    recovery character varying(80),
    uses_formula character varying(200),
    resource_key character varying(80)
);


--
-- Name: class_resources_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.class_resources_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: class_resources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.class_resources_id_seq OWNED BY public.class_resources.id;


--
-- Name: classes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.classes (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    source_id integer,
    external_id character varying(160),
    name character varying(100) NOT NULL,
    description text,
    hit_die integer,
    primary_ability character varying(120),
    saving_throw_proficiency_ids json,
    starting_equipment json,
    multiclassing json,
    is_playable boolean DEFAULT true NOT NULL
);


--
-- Name: classes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.classes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: classes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.classes_id_seq OWNED BY public.classes.id;


--
-- Name: conditions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conditions (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text NOT NULL,
    source_id integer,
    external_id character varying(160)
);


--
-- Name: conditions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.conditions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: conditions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.conditions_id_seq OWNED BY public.conditions.id;


--
-- Name: damage_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.damage_types (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    name character varying(60) NOT NULL,
    description text
);


--
-- Name: damage_types_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.damage_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: damage_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.damage_types_id_seq OWNED BY public.damage_types.id;


--
-- Name: editions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.editions (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(80) NOT NULL,
    year integer,
    description text
);


--
-- Name: editions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.editions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: editions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.editions_id_seq OWNED BY public.editions.id;


--
-- Name: encounter_monsters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.encounter_monsters (
    id integer NOT NULL,
    encounter_id integer NOT NULL,
    monster_id integer NOT NULL,
    quantity integer NOT NULL,
    notes text
);


--
-- Name: encounter_monsters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.encounter_monsters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: encounter_monsters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.encounter_monsters_id_seq OWNED BY public.encounter_monsters.id;


--
-- Name: encounters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.encounters (
    id integer NOT NULL,
    campaign_id integer NOT NULL,
    location_id integer,
    name character varying(150) NOT NULL,
    encounter_type character varying(100),
    difficulty character varying(50),
    description text,
    setup text,
    notes text,
    status character varying(30) NOT NULL,
    scheduled_at timestamp with time zone,
    environment json
);


--
-- Name: encounters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.encounters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: encounters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.encounters_id_seq OWNED BY public.encounters.id;


--
-- Name: equipment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.equipment (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    category_id integer,
    source_id integer,
    external_id character varying(160),
    name character varying(160) NOT NULL,
    description text,
    cost_quantity numeric(10,2),
    cost_unit character varying(20),
    weight numeric(10,2),
    rarity character varying(40),
    is_magical boolean DEFAULT false NOT NULL,
    properties json,
    weapon_data json,
    armor_data json,
    container_capacity character varying(120)
);


--
-- Name: equipment_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.equipment_categories (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text
);


--
-- Name: equipment_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.equipment_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: equipment_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.equipment_categories_id_seq OWNED BY public.equipment_categories.id;


--
-- Name: equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.equipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.equipment_id_seq OWNED BY public.equipment.id;


--
-- Name: equipment_property_definitions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.equipment_property_definitions (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    name character varying(80) NOT NULL,
    description text
);


--
-- Name: equipment_property_definitions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.equipment_property_definitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: equipment_property_definitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.equipment_property_definitions_id_seq OWNED BY public.equipment_property_definitions.id;


--
-- Name: equipment_property_links; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.equipment_property_links (
    equipment_id integer NOT NULL,
    property_id integer NOT NULL,
    value character varying(160)
);


--
-- Name: feat_feature_links; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feat_feature_links (
    id integer NOT NULL,
    feat_id integer NOT NULL,
    feature_id integer NOT NULL,
    display_order integer DEFAULT 0 NOT NULL
);


--
-- Name: feat_feature_links_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feat_feature_links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feat_feature_links_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feat_feature_links_id_seq OWNED BY public.feat_feature_links.id;


--
-- Name: feat_prerequisites; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feat_prerequisites (
    id integer NOT NULL,
    feat_id integer NOT NULL,
    prerequisite_type character varying(50) NOT NULL,
    operator character varying(20) DEFAULT 'eq'::character varying NOT NULL,
    value character varying(200) NOT NULL,
    description text,
    is_hard_requirement boolean DEFAULT true NOT NULL
);


--
-- Name: feat_prerequisites_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feat_prerequisites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feat_prerequisites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feat_prerequisites_id_seq OWNED BY public.feat_prerequisites.id;


--
-- Name: feats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feats (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    source_id integer,
    external_id character varying(160),
    name character varying(160) NOT NULL,
    description text NOT NULL,
    feat_type character varying(60),
    repeatable boolean DEFAULT false NOT NULL,
    mechanics json
);


--
-- Name: feats_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feats_id_seq OWNED BY public.feats.id;


--
-- Name: feature_choice_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feature_choice_groups (
    id integer NOT NULL,
    feature_id integer NOT NULL,
    name character varying(140) NOT NULL,
    description text,
    min_choices integer DEFAULT 1 NOT NULL,
    max_choices integer DEFAULT 1 NOT NULL,
    selection_mode character varying(30) DEFAULT 'select'::character varying NOT NULL,
    is_required boolean DEFAULT true NOT NULL,
    display_order integer DEFAULT 0 NOT NULL
);


--
-- Name: feature_choice_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feature_choice_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feature_choice_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feature_choice_groups_id_seq OWNED BY public.feature_choice_groups.id;


--
-- Name: feature_options; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feature_options (
    id integer NOT NULL,
    choice_group_id integer NOT NULL,
    name character varying(160) NOT NULL,
    description text,
    mechanics json,
    display_order integer DEFAULT 0 NOT NULL,
    is_default boolean DEFAULT false NOT NULL
);


--
-- Name: feature_options_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feature_options_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feature_options_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feature_options_id_seq OWNED BY public.feature_options.id;


--
-- Name: feature_prerequisites; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feature_prerequisites (
    id integer NOT NULL,
    feature_id integer NOT NULL,
    prerequisite_type character varying(50) NOT NULL,
    operator character varying(20) DEFAULT 'eq'::character varying NOT NULL,
    value character varying(200) NOT NULL,
    description text,
    is_hard_requirement boolean DEFAULT true NOT NULL,
    group_key character varying(60)
);


--
-- Name: feature_prerequisites_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feature_prerequisites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feature_prerequisites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feature_prerequisites_id_seq OWNED BY public.feature_prerequisites.id;


--
-- Name: features; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.features (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    source_id integer,
    external_id character varying(160),
    name character varying(160) NOT NULL,
    feature_type character varying(50) NOT NULL,
    description text NOT NULL,
    rules_text text,
    mechanics json,
    uses_formula character varying(200),
    recharge character varying(80),
    activation character varying(80),
    duration character varying(120),
    is_repeatable boolean DEFAULT false NOT NULL
);


--
-- Name: features_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.features_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: features_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.features_id_seq OWNED BY public.features.id;


--
-- Name: inventories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventories (
    id integer NOT NULL,
    item_id integer NOT NULL,
    owner_type character varying(30) NOT NULL,
    owner_id integer NOT NULL,
    quantity integer NOT NULL,
    equipped boolean NOT NULL,
    notes text
);


--
-- Name: inventories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.inventories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: inventories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.inventories_id_seq OWNED BY public.inventories.id;


--
-- Name: items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.items (
    id integer NOT NULL,
    campaign_id integer,
    name character varying(150) NOT NULL,
    item_type character varying(100),
    rarity character varying(50),
    weight character varying(30),
    value character varying(50),
    requires_attunement boolean NOT NULL,
    properties json,
    description text,
    source character varying(150)
);


--
-- Name: items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.items_id_seq OWNED BY public.items.id;


--
-- Name: languages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.languages (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    name character varying(100) NOT NULL,
    typical_speakers text,
    script character varying(100),
    description text,
    source_id integer,
    external_id character varying(160)
);


--
-- Name: languages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.languages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: languages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.languages_id_seq OWNED BY public.languages.id;


--
-- Name: location_npcs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.location_npcs (
    id integer NOT NULL,
    location_id integer NOT NULL,
    npc_id integer NOT NULL,
    quantity integer NOT NULL,
    notes text
);


--
-- Name: location_npcs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.location_npcs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: location_npcs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.location_npcs_id_seq OWNED BY public.location_npcs.id;


--
-- Name: locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.locations (
    id integer NOT NULL,
    campaign_id integer NOT NULL,
    name character varying(150) NOT NULL,
    location_type character varying(100),
    description text,
    history text,
    notable_features json,
    parent_location_id integer
);


--
-- Name: locations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;


--
-- Name: monsters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.monsters (
    id integer NOT NULL,
    campaign_id integer,
    name character varying(150) NOT NULL,
    size character varying(50),
    creature_type json,
    alignment character varying(50),
    challenge_rating double precision,
    armor_class integer,
    hit_points integer,
    speed json,
    ability_scores json,
    abilities json,
    description text,
    source character varying(150),
    edition character varying(10),
    source_key character varying(100),
    source_id character varying(150),
    raw_data json
);


--
-- Name: monsters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.monsters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: monsters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.monsters_id_seq OWNED BY public.monsters.id;


--
-- Name: npcs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.npcs (
    id integer NOT NULL,
    campaign_id integer NOT NULL,
    name character varying(150) NOT NULL,
    race character varying(100),
    occupation character varying(150),
    alignment character varying(50),
    description text,
    personality text,
    backstory text,
    notes text,
    character_class character varying(100)
);


--
-- Name: npcs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.npcs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: npcs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.npcs_id_seq OWNED BY public.npcs.id;


--
-- Name: players; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.players (
    id integer NOT NULL,
    campaign_id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(255),
    notes text
);


--
-- Name: players_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.players_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: players_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.players_id_seq OWNED BY public.players.id;


--
-- Name: proficiencies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.proficiencies (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    name character varying(120) NOT NULL,
    category character varying(40) NOT NULL,
    description text,
    source_id integer,
    external_id character varying(160)
);


--
-- Name: proficiencies_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.proficiencies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: proficiencies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.proficiencies_id_seq OWNED BY public.proficiencies.id;


--
-- Name: sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sources (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    url character varying(500),
    description text
);


--
-- Name: sources_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sources_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sources_id_seq OWNED BY public.sources.id;


--
-- Name: species; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.species (
    id integer NOT NULL,
    edition_id integer NOT NULL,
    source_id integer,
    external_id character varying(160),
    name character varying(120) NOT NULL,
    description text,
    size character varying(80),
    creature_type character varying(80) DEFAULT 'Humanoid'::character varying NOT NULL,
    base_speed integer,
    ability_score_rules json,
    age text,
    alignment text,
    languages_summary text,
    is_playable boolean DEFAULT true NOT NULL
);


--
-- Name: species_feature_grants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.species_feature_grants (
    id integer NOT NULL,
    species_id integer NOT NULL,
    variant_id integer,
    feature_id integer NOT NULL,
    display_order integer DEFAULT 0 NOT NULL,
    grant_notes text
);


--
-- Name: species_feature_grants_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.species_feature_grants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: species_feature_grants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.species_feature_grants_id_seq OWNED BY public.species_feature_grants.id;


--
-- Name: species_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.species_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: species_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.species_id_seq OWNED BY public.species.id;


--
-- Name: species_variants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.species_variants (
    id integer NOT NULL,
    species_id integer NOT NULL,
    name character varying(140) NOT NULL,
    description text,
    size_override character varying(80),
    speed_override integer,
    ability_score_rules json,
    mechanics json
);


--
-- Name: species_variants_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.species_variants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: species_variants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.species_variants_id_seq OWNED BY public.species_variants.id;


--
-- Name: spells; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spells (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    edition character varying(10),
    source_key character varying(100),
    source_id character varying(150),
    source character varying(150),
    school character varying(50),
    school_key character varying(50),
    classes json,
    casting_options json,
    level integer,
    description text,
    higher_level text,
    target_type character varying(100),
    target_count integer,
    range integer,
    range_text character varying(100),
    range_unit character varying(30),
    shape_type character varying(50),
    shape_size double precision,
    shape_size_unit character varying(30),
    casting_time character varying(100),
    reaction_condition text,
    duration character varying(100),
    ritual boolean,
    concentration boolean,
    verbal boolean,
    somatic boolean,
    material boolean,
    material_specified text,
    material_cost json,
    material_consumed boolean,
    saving_throw_ability character varying(30),
    attack_roll boolean,
    damage_roll character varying(100),
    damage_types json,
    crossreferences json,
    raw_data json
);


--
-- Name: spells_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.spells_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: spells_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.spells_id_seq OWNED BY public.spells.id;


--
-- Name: subclass_feature_grants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subclass_feature_grants (
    id integer NOT NULL,
    subclass_id integer NOT NULL,
    feature_id integer NOT NULL,
    character_level integer NOT NULL,
    display_order integer DEFAULT 0 NOT NULL,
    grant_notes text
);


--
-- Name: subclass_feature_grants_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.subclass_feature_grants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: subclass_feature_grants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.subclass_feature_grants_id_seq OWNED BY public.subclass_feature_grants.id;


--
-- Name: subclasses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subclasses (
    id integer NOT NULL,
    class_id integer NOT NULL,
    edition_id integer NOT NULL,
    source_id integer,
    external_id character varying(160),
    name character varying(120) NOT NULL,
    description text,
    subclass_level integer
);


--
-- Name: subclasses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.subclasses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: subclasses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.subclasses_id_seq OWNED BY public.subclasses.id;


--
-- Name: backgrounds id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backgrounds ALTER COLUMN id SET DEFAULT nextval('public.backgrounds_id_seq'::regclass);


--
-- Name: campaigns id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.campaigns ALTER COLUMN id SET DEFAULT nextval('public.campaigns_id_seq'::regclass);


--
-- Name: character_choice_selections id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_choice_selections ALTER COLUMN id SET DEFAULT nextval('public.character_choice_selections_id_seq'::regclass);


--
-- Name: character_classes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_classes ALTER COLUMN id SET DEFAULT nextval('public.character_classes_id_seq'::regclass);


--
-- Name: character_feats id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_feats ALTER COLUMN id SET DEFAULT nextval('public.character_feats_id_seq'::regclass);


--
-- Name: character_feature_selections id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_feature_selections ALTER COLUMN id SET DEFAULT nextval('public.character_feature_selections_id_seq'::regclass);


--
-- Name: character_inventory id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_inventory ALTER COLUMN id SET DEFAULT nextval('public.character_inventory_id_seq'::regclass);


--
-- Name: characters id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters ALTER COLUMN id SET DEFAULT nextval('public.characters_id_seq'::regclass);


--
-- Name: class_feature_grants id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_feature_grants ALTER COLUMN id SET DEFAULT nextval('public.class_feature_grants_id_seq'::regclass);


--
-- Name: class_level_progressions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_level_progressions ALTER COLUMN id SET DEFAULT nextval('public.class_level_progressions_id_seq'::regclass);


--
-- Name: class_resource_progressions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_resource_progressions ALTER COLUMN id SET DEFAULT nextval('public.class_resource_progressions_id_seq'::regclass);


--
-- Name: class_resources id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_resources ALTER COLUMN id SET DEFAULT nextval('public.class_resources_id_seq'::regclass);


--
-- Name: classes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.classes ALTER COLUMN id SET DEFAULT nextval('public.classes_id_seq'::regclass);


--
-- Name: conditions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conditions ALTER COLUMN id SET DEFAULT nextval('public.conditions_id_seq'::regclass);


--
-- Name: damage_types id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.damage_types ALTER COLUMN id SET DEFAULT nextval('public.damage_types_id_seq'::regclass);


--
-- Name: editions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.editions ALTER COLUMN id SET DEFAULT nextval('public.editions_id_seq'::regclass);


--
-- Name: encounter_monsters id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounter_monsters ALTER COLUMN id SET DEFAULT nextval('public.encounter_monsters_id_seq'::regclass);


--
-- Name: encounters id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounters ALTER COLUMN id SET DEFAULT nextval('public.encounters_id_seq'::regclass);


--
-- Name: equipment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment ALTER COLUMN id SET DEFAULT nextval('public.equipment_id_seq'::regclass);


--
-- Name: equipment_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_categories ALTER COLUMN id SET DEFAULT nextval('public.equipment_categories_id_seq'::regclass);


--
-- Name: equipment_property_definitions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_property_definitions ALTER COLUMN id SET DEFAULT nextval('public.equipment_property_definitions_id_seq'::regclass);


--
-- Name: feat_feature_links id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feat_feature_links ALTER COLUMN id SET DEFAULT nextval('public.feat_feature_links_id_seq'::regclass);


--
-- Name: feat_prerequisites id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feat_prerequisites ALTER COLUMN id SET DEFAULT nextval('public.feat_prerequisites_id_seq'::regclass);


--
-- Name: feats id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feats ALTER COLUMN id SET DEFAULT nextval('public.feats_id_seq'::regclass);


--
-- Name: feature_choice_groups id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feature_choice_groups ALTER COLUMN id SET DEFAULT nextval('public.feature_choice_groups_id_seq'::regclass);


--
-- Name: feature_options id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feature_options ALTER COLUMN id SET DEFAULT nextval('public.feature_options_id_seq'::regclass);


--
-- Name: feature_prerequisites id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feature_prerequisites ALTER COLUMN id SET DEFAULT nextval('public.feature_prerequisites_id_seq'::regclass);


--
-- Name: features id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.features ALTER COLUMN id SET DEFAULT nextval('public.features_id_seq'::regclass);


--
-- Name: inventories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventories ALTER COLUMN id SET DEFAULT nextval('public.inventories_id_seq'::regclass);


--
-- Name: items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items ALTER COLUMN id SET DEFAULT nextval('public.items_id_seq'::regclass);


--
-- Name: languages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.languages ALTER COLUMN id SET DEFAULT nextval('public.languages_id_seq'::regclass);


--
-- Name: location_npcs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_npcs ALTER COLUMN id SET DEFAULT nextval('public.location_npcs_id_seq'::regclass);


--
-- Name: locations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.locations_id_seq'::regclass);


--
-- Name: monsters id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monsters ALTER COLUMN id SET DEFAULT nextval('public.monsters_id_seq'::regclass);


--
-- Name: npcs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.npcs ALTER COLUMN id SET DEFAULT nextval('public.npcs_id_seq'::regclass);


--
-- Name: players id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players ALTER COLUMN id SET DEFAULT nextval('public.players_id_seq'::regclass);


--
-- Name: proficiencies id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proficiencies ALTER COLUMN id SET DEFAULT nextval('public.proficiencies_id_seq'::regclass);


--
-- Name: sources id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sources ALTER COLUMN id SET DEFAULT nextval('public.sources_id_seq'::regclass);


--
-- Name: species id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species ALTER COLUMN id SET DEFAULT nextval('public.species_id_seq'::regclass);


--
-- Name: species_feature_grants id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species_feature_grants ALTER COLUMN id SET DEFAULT nextval('public.species_feature_grants_id_seq'::regclass);


--
-- Name: species_variants id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species_variants ALTER COLUMN id SET DEFAULT nextval('public.species_variants_id_seq'::regclass);


--
-- Name: spells id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spells ALTER COLUMN id SET DEFAULT nextval('public.spells_id_seq'::regclass);


--
-- Name: subclass_feature_grants id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclass_feature_grants ALTER COLUMN id SET DEFAULT nextval('public.subclass_feature_grants_id_seq'::regclass);


--
-- Name: subclasses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclasses ALTER COLUMN id SET DEFAULT nextval('public.subclasses_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: backgrounds backgrounds_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backgrounds
    ADD CONSTRAINT backgrounds_pkey PRIMARY KEY (id);


--
-- Name: campaigns campaigns_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.campaigns
    ADD CONSTRAINT campaigns_pkey PRIMARY KEY (id);


--
-- Name: character_choice_selections character_choice_selections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_choice_selections
    ADD CONSTRAINT character_choice_selections_pkey PRIMARY KEY (id);


--
-- Name: character_classes character_classes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_classes
    ADD CONSTRAINT character_classes_pkey PRIMARY KEY (id);


--
-- Name: character_feats character_feats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_feats
    ADD CONSTRAINT character_feats_pkey PRIMARY KEY (id);


--
-- Name: character_feature_selections character_feature_selections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_feature_selections
    ADD CONSTRAINT character_feature_selections_pkey PRIMARY KEY (id);


--
-- Name: character_inventory character_inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_inventory
    ADD CONSTRAINT character_inventory_pkey PRIMARY KEY (id);


--
-- Name: character_languages character_languages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_languages
    ADD CONSTRAINT character_languages_pkey PRIMARY KEY (character_id, language_id);


--
-- Name: character_proficiencies character_proficiencies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_proficiencies
    ADD CONSTRAINT character_proficiencies_pkey PRIMARY KEY (character_id, proficiency_id);


--
-- Name: characters characters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_pkey PRIMARY KEY (id);


--
-- Name: class_feature_grants class_feature_grants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_feature_grants
    ADD CONSTRAINT class_feature_grants_pkey PRIMARY KEY (id);


--
-- Name: class_level_progressions class_level_progressions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_level_progressions
    ADD CONSTRAINT class_level_progressions_pkey PRIMARY KEY (id);


--
-- Name: class_resource_progressions class_resource_progressions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_resource_progressions
    ADD CONSTRAINT class_resource_progressions_pkey PRIMARY KEY (id);


--
-- Name: class_resources class_resources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_resources
    ADD CONSTRAINT class_resources_pkey PRIMARY KEY (id);


--
-- Name: classes classes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (id);


--
-- Name: conditions conditions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conditions
    ADD CONSTRAINT conditions_pkey PRIMARY KEY (id);


--
-- Name: damage_types damage_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.damage_types
    ADD CONSTRAINT damage_types_pkey PRIMARY KEY (id);


--
-- Name: editions editions_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.editions
    ADD CONSTRAINT editions_code_key UNIQUE (code);


--
-- Name: editions editions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.editions
    ADD CONSTRAINT editions_pkey PRIMARY KEY (id);


--
-- Name: encounter_monsters encounter_monsters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounter_monsters
    ADD CONSTRAINT encounter_monsters_pkey PRIMARY KEY (id);


--
-- Name: encounters encounters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounters
    ADD CONSTRAINT encounters_pkey PRIMARY KEY (id);


--
-- Name: equipment_categories equipment_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_categories
    ADD CONSTRAINT equipment_categories_pkey PRIMARY KEY (id);


--
-- Name: equipment equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_pkey PRIMARY KEY (id);


--
-- Name: equipment_property_definitions equipment_property_definitions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_property_definitions
    ADD CONSTRAINT equipment_property_definitions_pkey PRIMARY KEY (id);


--
-- Name: equipment_property_links equipment_property_links_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_property_links
    ADD CONSTRAINT equipment_property_links_pkey PRIMARY KEY (equipment_id, property_id);


--
-- Name: feat_feature_links feat_feature_links_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feat_feature_links
    ADD CONSTRAINT feat_feature_links_pkey PRIMARY KEY (id);


--
-- Name: feat_prerequisites feat_prerequisites_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feat_prerequisites
    ADD CONSTRAINT feat_prerequisites_pkey PRIMARY KEY (id);


--
-- Name: feats feats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feats
    ADD CONSTRAINT feats_pkey PRIMARY KEY (id);


--
-- Name: feature_choice_groups feature_choice_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feature_choice_groups
    ADD CONSTRAINT feature_choice_groups_pkey PRIMARY KEY (id);


--
-- Name: feature_options feature_options_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feature_options
    ADD CONSTRAINT feature_options_pkey PRIMARY KEY (id);


--
-- Name: feature_prerequisites feature_prerequisites_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feature_prerequisites
    ADD CONSTRAINT feature_prerequisites_pkey PRIMARY KEY (id);


--
-- Name: features features_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.features
    ADD CONSTRAINT features_pkey PRIMARY KEY (id);


--
-- Name: inventories inventories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT inventories_pkey PRIMARY KEY (id);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);


--
-- Name: languages languages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.languages
    ADD CONSTRAINT languages_pkey PRIMARY KEY (id);


--
-- Name: location_npcs location_npcs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_npcs
    ADD CONSTRAINT location_npcs_pkey PRIMARY KEY (id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: monsters monsters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monsters
    ADD CONSTRAINT monsters_pkey PRIMARY KEY (id);


--
-- Name: npcs npcs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.npcs
    ADD CONSTRAINT npcs_pkey PRIMARY KEY (id);


--
-- Name: players players_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players
    ADD CONSTRAINT players_pkey PRIMARY KEY (id);


--
-- Name: proficiencies proficiencies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proficiencies
    ADD CONSTRAINT proficiencies_pkey PRIMARY KEY (id);


--
-- Name: sources sources_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sources
    ADD CONSTRAINT sources_name_key UNIQUE (name);


--
-- Name: sources sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sources
    ADD CONSTRAINT sources_pkey PRIMARY KEY (id);


--
-- Name: species_feature_grants species_feature_grants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species_feature_grants
    ADD CONSTRAINT species_feature_grants_pkey PRIMARY KEY (id);


--
-- Name: species species_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species
    ADD CONSTRAINT species_pkey PRIMARY KEY (id);


--
-- Name: species_variants species_variants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species_variants
    ADD CONSTRAINT species_variants_pkey PRIMARY KEY (id);


--
-- Name: spells spells_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spells
    ADD CONSTRAINT spells_pkey PRIMARY KEY (id);


--
-- Name: subclass_feature_grants subclass_feature_grants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclass_feature_grants
    ADD CONSTRAINT subclass_feature_grants_pkey PRIMARY KEY (id);


--
-- Name: subclasses subclasses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclasses
    ADD CONSTRAINT subclasses_pkey PRIMARY KEY (id);


--
-- Name: backgrounds uq_background_edition_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backgrounds
    ADD CONSTRAINT uq_background_edition_name UNIQUE (edition_id, name);


--
-- Name: backgrounds uq_background_source_external; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backgrounds
    ADD CONSTRAINT uq_background_source_external UNIQUE (source_id, external_id);


--
-- Name: character_choice_selections uq_character_choice_option; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_choice_selections
    ADD CONSTRAINT uq_character_choice_option UNIQUE (character_id, choice_group_id, option_id);


--
-- Name: character_classes uq_character_class; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_classes
    ADD CONSTRAINT uq_character_class UNIQUE (character_id, class_id);


--
-- Name: character_feats uq_character_feat; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_feats
    ADD CONSTRAINT uq_character_feat UNIQUE (character_id, feat_id);


--
-- Name: classes uq_class_edition_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT uq_class_edition_name UNIQUE (edition_id, name);


--
-- Name: class_feature_grants uq_class_feature_level; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_feature_grants
    ADD CONSTRAINT uq_class_feature_level UNIQUE (class_id, feature_id, character_level);


--
-- Name: class_level_progressions uq_class_progression_level; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_level_progressions
    ADD CONSTRAINT uq_class_progression_level UNIQUE (class_id, level);


--
-- Name: class_resources uq_class_resource_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_resources
    ADD CONSTRAINT uq_class_resource_key UNIQUE (class_id, resource_key);


--
-- Name: classes uq_class_source_external; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT uq_class_source_external UNIQUE (source_id, external_id);


--
-- Name: conditions uq_condition_edition_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conditions
    ADD CONSTRAINT uq_condition_edition_name UNIQUE (edition_id, name);


--
-- Name: conditions uq_condition_source_external; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conditions
    ADD CONSTRAINT uq_condition_source_external UNIQUE (source_id, external_id);


--
-- Name: damage_types uq_damage_type_edition_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.damage_types
    ADD CONSTRAINT uq_damage_type_edition_name UNIQUE (edition_id, name);


--
-- Name: equipment_categories uq_equipment_category_edition_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_categories
    ADD CONSTRAINT uq_equipment_category_edition_name UNIQUE (edition_id, name);


--
-- Name: equipment uq_equipment_edition_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT uq_equipment_edition_name UNIQUE (edition_id, name);


--
-- Name: equipment_property_definitions uq_equipment_property_edition_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_property_definitions
    ADD CONSTRAINT uq_equipment_property_edition_name UNIQUE (edition_id, name);


--
-- Name: equipment uq_equipment_source_external; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT uq_equipment_source_external UNIQUE (source_id, external_id);


--
-- Name: feats uq_feat_edition_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feats
    ADD CONSTRAINT uq_feat_edition_name UNIQUE (edition_id, name);


--
-- Name: feat_feature_links uq_feat_feature_link; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feat_feature_links
    ADD CONSTRAINT uq_feat_feature_link UNIQUE (feat_id, feature_id);


--
-- Name: feats uq_feat_source_external; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feats
    ADD CONSTRAINT uq_feat_source_external UNIQUE (source_id, external_id);


--
-- Name: feature_choice_groups uq_feature_choice_group_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feature_choice_groups
    ADD CONSTRAINT uq_feature_choice_group_name UNIQUE (feature_id, name);


--
-- Name: features uq_feature_edition_name_type; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.features
    ADD CONSTRAINT uq_feature_edition_name_type UNIQUE (edition_id, name, feature_type);


--
-- Name: feature_options uq_feature_option_group_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feature_options
    ADD CONSTRAINT uq_feature_option_group_name UNIQUE (choice_group_id, name);


--
-- Name: features uq_feature_source_external; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.features
    ADD CONSTRAINT uq_feature_source_external UNIQUE (source_id, external_id);


--
-- Name: inventories uq_inventory_owner_item; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT uq_inventory_owner_item UNIQUE (item_id, owner_type, owner_id);


--
-- Name: languages uq_language_edition_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.languages
    ADD CONSTRAINT uq_language_edition_name UNIQUE (edition_id, name);


--
-- Name: languages uq_language_source_external; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.languages
    ADD CONSTRAINT uq_language_source_external UNIQUE (source_id, external_id);


--
-- Name: monsters uq_monster_source; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monsters
    ADD CONSTRAINT uq_monster_source UNIQUE (source_key, source_id);


--
-- Name: proficiencies uq_proficiency_edition_name_category; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proficiencies
    ADD CONSTRAINT uq_proficiency_edition_name_category UNIQUE (edition_id, name, category);


--
-- Name: proficiencies uq_proficiency_source_external; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proficiencies
    ADD CONSTRAINT uq_proficiency_source_external UNIQUE (source_id, external_id);


--
-- Name: class_resource_progressions uq_resource_progression_level; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_resource_progressions
    ADD CONSTRAINT uq_resource_progression_level UNIQUE (resource_id, level);


--
-- Name: species uq_species_edition_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species
    ADD CONSTRAINT uq_species_edition_name UNIQUE (edition_id, name);


--
-- Name: species uq_species_source_external; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species
    ADD CONSTRAINT uq_species_source_external UNIQUE (source_id, external_id);


--
-- Name: species_feature_grants uq_species_variant_feature; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species_feature_grants
    ADD CONSTRAINT uq_species_variant_feature UNIQUE (species_id, variant_id, feature_id);


--
-- Name: species_variants uq_species_variant_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species_variants
    ADD CONSTRAINT uq_species_variant_name UNIQUE (species_id, name);


--
-- Name: spells uq_spell_source; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spells
    ADD CONSTRAINT uq_spell_source UNIQUE (source_key, source_id);


--
-- Name: subclasses uq_subclass_class_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclasses
    ADD CONSTRAINT uq_subclass_class_name UNIQUE (class_id, name);


--
-- Name: subclass_feature_grants uq_subclass_feature_level; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclass_feature_grants
    ADD CONSTRAINT uq_subclass_feature_level UNIQUE (subclass_id, feature_id, character_level);


--
-- Name: subclasses uq_subclass_source_external; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclasses
    ADD CONSTRAINT uq_subclass_source_external UNIQUE (source_id, external_id);


--
-- Name: ix_backgrounds_edition; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_backgrounds_edition ON public.backgrounds USING btree (edition_id);


--
-- Name: ix_character_classes_character; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_character_classes_character ON public.character_classes USING btree (character_id);


--
-- Name: ix_character_features_character; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_character_features_character ON public.character_feature_selections USING btree (character_id);


--
-- Name: ix_character_inventory_character; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_character_inventory_character ON public.character_inventory USING btree (character_id);


--
-- Name: ix_characters_edition; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_characters_edition ON public.characters USING btree (edition_id);


--
-- Name: ix_class_feature_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_class_feature_level ON public.class_feature_grants USING btree (class_id, character_level);


--
-- Name: ix_class_progression_class_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_class_progression_class_level ON public.class_level_progressions USING btree (class_id, level);


--
-- Name: ix_classes_edition; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_classes_edition ON public.classes USING btree (edition_id);


--
-- Name: ix_conditions_edition; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_conditions_edition ON public.conditions USING btree (edition_id);


--
-- Name: ix_equipment_edition_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_equipment_edition_category ON public.equipment USING btree (edition_id, category_id);


--
-- Name: ix_equipment_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_equipment_name ON public.equipment USING btree (name);


--
-- Name: ix_feats_edition; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_feats_edition ON public.feats USING btree (edition_id);


--
-- Name: ix_feature_options_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_feature_options_group ON public.feature_options USING btree (choice_group_id);


--
-- Name: ix_feature_prerequisites_feature; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_feature_prerequisites_feature ON public.feature_prerequisites USING btree (feature_id);


--
-- Name: ix_features_edition_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_features_edition_type ON public.features USING btree (edition_id, feature_type);


--
-- Name: ix_languages_edition; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_languages_edition ON public.languages USING btree (edition_id);


--
-- Name: ix_proficiencies_edition_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_proficiencies_edition_category ON public.proficiencies USING btree (edition_id, category);


--
-- Name: ix_species_edition; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_species_edition ON public.species USING btree (edition_id);


--
-- Name: ix_species_variants_species; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_species_variants_species ON public.species_variants USING btree (species_id);


--
-- Name: ix_subclass_feature_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_subclass_feature_level ON public.subclass_feature_grants USING btree (subclass_id, character_level);


--
-- Name: ix_subclasses_class; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_subclasses_class ON public.subclasses USING btree (class_id);


--
-- Name: ix_subclasses_edition; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_subclasses_edition ON public.subclasses USING btree (edition_id);


--
-- Name: backgrounds backgrounds_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backgrounds
    ADD CONSTRAINT backgrounds_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: backgrounds backgrounds_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backgrounds
    ADD CONSTRAINT backgrounds_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id) ON DELETE SET NULL;


--
-- Name: backgrounds backgrounds_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backgrounds
    ADD CONSTRAINT backgrounds_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE SET NULL;


--
-- Name: character_choice_selections character_choice_selections_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_choice_selections
    ADD CONSTRAINT character_choice_selections_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id) ON DELETE CASCADE;


--
-- Name: character_choice_selections character_choice_selections_choice_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_choice_selections
    ADD CONSTRAINT character_choice_selections_choice_group_id_fkey FOREIGN KEY (choice_group_id) REFERENCES public.feature_choice_groups(id) ON DELETE RESTRICT;


--
-- Name: character_choice_selections character_choice_selections_option_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_choice_selections
    ADD CONSTRAINT character_choice_selections_option_id_fkey FOREIGN KEY (option_id) REFERENCES public.feature_options(id) ON DELETE RESTRICT;


--
-- Name: character_classes character_classes_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_classes
    ADD CONSTRAINT character_classes_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id) ON DELETE CASCADE;


--
-- Name: character_classes character_classes_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_classes
    ADD CONSTRAINT character_classes_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE RESTRICT;


--
-- Name: character_classes character_classes_subclass_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_classes
    ADD CONSTRAINT character_classes_subclass_id_fkey FOREIGN KEY (subclass_id) REFERENCES public.subclasses(id) ON DELETE SET NULL;


--
-- Name: character_feats character_feats_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_feats
    ADD CONSTRAINT character_feats_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id) ON DELETE CASCADE;


--
-- Name: character_feats character_feats_feat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_feats
    ADD CONSTRAINT character_feats_feat_id_fkey FOREIGN KEY (feat_id) REFERENCES public.feats(id) ON DELETE RESTRICT;


--
-- Name: character_feature_selections character_feature_selections_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_feature_selections
    ADD CONSTRAINT character_feature_selections_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id) ON DELETE CASCADE;


--
-- Name: character_feature_selections character_feature_selections_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_feature_selections
    ADD CONSTRAINT character_feature_selections_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id) ON DELETE RESTRICT;


--
-- Name: character_inventory character_inventory_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_inventory
    ADD CONSTRAINT character_inventory_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id) ON DELETE CASCADE;


--
-- Name: character_inventory character_inventory_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_inventory
    ADD CONSTRAINT character_inventory_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id) ON DELETE RESTRICT;


--
-- Name: character_languages character_languages_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_languages
    ADD CONSTRAINT character_languages_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id) ON DELETE CASCADE;


--
-- Name: character_languages character_languages_language_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_languages
    ADD CONSTRAINT character_languages_language_id_fkey FOREIGN KEY (language_id) REFERENCES public.languages(id) ON DELETE RESTRICT;


--
-- Name: character_proficiencies character_proficiencies_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_proficiencies
    ADD CONSTRAINT character_proficiencies_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id) ON DELETE CASCADE;


--
-- Name: character_proficiencies character_proficiencies_proficiency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.character_proficiencies
    ADD CONSTRAINT character_proficiencies_proficiency_id_fkey FOREIGN KEY (proficiency_id) REFERENCES public.proficiencies(id) ON DELETE RESTRICT;


--
-- Name: characters characters_background_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_background_id_fkey FOREIGN KEY (background_id) REFERENCES public.backgrounds(id) ON DELETE SET NULL;


--
-- Name: characters characters_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE RESTRICT;


--
-- Name: characters characters_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.species(id) ON DELETE RESTRICT;


--
-- Name: characters characters_species_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_species_variant_id_fkey FOREIGN KEY (species_variant_id) REFERENCES public.species_variants(id) ON DELETE SET NULL;


--
-- Name: class_feature_grants class_feature_grants_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_feature_grants
    ADD CONSTRAINT class_feature_grants_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: class_feature_grants class_feature_grants_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_feature_grants
    ADD CONSTRAINT class_feature_grants_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id) ON DELETE CASCADE;


--
-- Name: class_level_progressions class_level_progressions_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_level_progressions
    ADD CONSTRAINT class_level_progressions_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: class_resource_progressions class_resource_progressions_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_resource_progressions
    ADD CONSTRAINT class_resource_progressions_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.class_resources(id) ON DELETE CASCADE;


--
-- Name: class_resources class_resources_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.class_resources
    ADD CONSTRAINT class_resources_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: classes classes_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: classes classes_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE SET NULL;


--
-- Name: conditions conditions_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conditions
    ADD CONSTRAINT conditions_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: conditions conditions_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conditions
    ADD CONSTRAINT conditions_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE SET NULL;


--
-- Name: damage_types damage_types_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.damage_types
    ADD CONSTRAINT damage_types_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: encounter_monsters encounter_monsters_encounter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounter_monsters
    ADD CONSTRAINT encounter_monsters_encounter_id_fkey FOREIGN KEY (encounter_id) REFERENCES public.encounters(id);


--
-- Name: encounter_monsters encounter_monsters_monster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounter_monsters
    ADD CONSTRAINT encounter_monsters_monster_id_fkey FOREIGN KEY (monster_id) REFERENCES public.monsters(id);


--
-- Name: encounters encounters_campaign_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounters
    ADD CONSTRAINT encounters_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES public.campaigns(id);


--
-- Name: encounters encounters_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounters
    ADD CONSTRAINT encounters_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: equipment_categories equipment_categories_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_categories
    ADD CONSTRAINT equipment_categories_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: equipment equipment_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.equipment_categories(id) ON DELETE SET NULL;


--
-- Name: equipment equipment_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: equipment_property_definitions equipment_property_definitions_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_property_definitions
    ADD CONSTRAINT equipment_property_definitions_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: equipment_property_links equipment_property_links_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_property_links
    ADD CONSTRAINT equipment_property_links_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id) ON DELETE CASCADE;


--
-- Name: equipment_property_links equipment_property_links_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_property_links
    ADD CONSTRAINT equipment_property_links_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.equipment_property_definitions(id) ON DELETE CASCADE;


--
-- Name: equipment equipment_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE SET NULL;


--
-- Name: feat_feature_links feat_feature_links_feat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feat_feature_links
    ADD CONSTRAINT feat_feature_links_feat_id_fkey FOREIGN KEY (feat_id) REFERENCES public.feats(id) ON DELETE CASCADE;


--
-- Name: feat_feature_links feat_feature_links_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feat_feature_links
    ADD CONSTRAINT feat_feature_links_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id) ON DELETE CASCADE;


--
-- Name: feat_prerequisites feat_prerequisites_feat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feat_prerequisites
    ADD CONSTRAINT feat_prerequisites_feat_id_fkey FOREIGN KEY (feat_id) REFERENCES public.feats(id) ON DELETE CASCADE;


--
-- Name: feats feats_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feats
    ADD CONSTRAINT feats_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: feats feats_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feats
    ADD CONSTRAINT feats_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE SET NULL;


--
-- Name: feature_choice_groups feature_choice_groups_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feature_choice_groups
    ADD CONSTRAINT feature_choice_groups_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id) ON DELETE CASCADE;


--
-- Name: feature_options feature_options_choice_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feature_options
    ADD CONSTRAINT feature_options_choice_group_id_fkey FOREIGN KEY (choice_group_id) REFERENCES public.feature_choice_groups(id) ON DELETE CASCADE;


--
-- Name: feature_prerequisites feature_prerequisites_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feature_prerequisites
    ADD CONSTRAINT feature_prerequisites_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id) ON DELETE CASCADE;


--
-- Name: features features_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.features
    ADD CONSTRAINT features_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: features features_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.features
    ADD CONSTRAINT features_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE SET NULL;


--
-- Name: inventories inventories_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT inventories_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: items items_campaign_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES public.campaigns(id);


--
-- Name: languages languages_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.languages
    ADD CONSTRAINT languages_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: languages languages_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.languages
    ADD CONSTRAINT languages_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE SET NULL;


--
-- Name: location_npcs location_npcs_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_npcs
    ADD CONSTRAINT location_npcs_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: location_npcs location_npcs_npc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_npcs
    ADD CONSTRAINT location_npcs_npc_id_fkey FOREIGN KEY (npc_id) REFERENCES public.npcs(id);


--
-- Name: locations locations_campaign_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES public.campaigns(id);


--
-- Name: locations locations_parent_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_parent_location_id_fkey FOREIGN KEY (parent_location_id) REFERENCES public.locations(id);


--
-- Name: monsters monsters_campaign_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monsters
    ADD CONSTRAINT monsters_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES public.campaigns(id);


--
-- Name: npcs npcs_campaign_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.npcs
    ADD CONSTRAINT npcs_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES public.campaigns(id);


--
-- Name: players players_campaign_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players
    ADD CONSTRAINT players_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES public.campaigns(id);


--
-- Name: proficiencies proficiencies_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proficiencies
    ADD CONSTRAINT proficiencies_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: proficiencies proficiencies_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proficiencies
    ADD CONSTRAINT proficiencies_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE SET NULL;


--
-- Name: species species_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species
    ADD CONSTRAINT species_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: species_feature_grants species_feature_grants_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species_feature_grants
    ADD CONSTRAINT species_feature_grants_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id) ON DELETE CASCADE;


--
-- Name: species_feature_grants species_feature_grants_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species_feature_grants
    ADD CONSTRAINT species_feature_grants_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.species(id) ON DELETE CASCADE;


--
-- Name: species_feature_grants species_feature_grants_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species_feature_grants
    ADD CONSTRAINT species_feature_grants_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES public.species_variants(id) ON DELETE CASCADE;


--
-- Name: species species_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species
    ADD CONSTRAINT species_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE SET NULL;


--
-- Name: species_variants species_variants_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.species_variants
    ADD CONSTRAINT species_variants_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.species(id) ON DELETE CASCADE;


--
-- Name: subclass_feature_grants subclass_feature_grants_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclass_feature_grants
    ADD CONSTRAINT subclass_feature_grants_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id) ON DELETE CASCADE;


--
-- Name: subclass_feature_grants subclass_feature_grants_subclass_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclass_feature_grants
    ADD CONSTRAINT subclass_feature_grants_subclass_id_fkey FOREIGN KEY (subclass_id) REFERENCES public.subclasses(id) ON DELETE CASCADE;


--
-- Name: subclasses subclasses_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclasses
    ADD CONSTRAINT subclasses_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- Name: subclasses subclasses_edition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclasses
    ADD CONSTRAINT subclasses_edition_id_fkey FOREIGN KEY (edition_id) REFERENCES public.editions(id) ON DELETE CASCADE;


--
-- Name: subclasses subclasses_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subclasses
    ADD CONSTRAINT subclasses_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict 46fZ5LbfBRQKqf770JWW5lsXvaY6GRxtGfuV2dcL2MrmQ2UgVmYnxuFBzFf9C7A

