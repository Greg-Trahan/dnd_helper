export interface AbilityScores {
  strength: number
  dexterity: number
  constitution: number
  intelligence: number
  wisdom: number
  charisma: number
}

export type JsonValue =
  | Record<string, unknown>
  | unknown[]
  | null

export interface Character {
  id: number
  name: string
  player_id: number
  edition_id: number

  species_id: number | null
  species_variant_id: number | null
  background_id: number | null

  level: number
  experience_points: number

  alignment: string | null
  size: string | null
  speed: number | null

  ability_scores: JsonValue

  hit_point_maximum: number | null
  current_hit_points: number | null
  temporary_hit_points: number

  armor_class: number | null
  initiative_bonus: number | null
  proficiency_bonus: number | null

  death_saves: JsonValue

  personality_traits: string | null
  ideals: string | null
  bonds: string | null
  flaws: string | null
  backstory: string | null
  notes: string | null

  created_at: string
  updated_at: string
}

export interface CharacterCreate {
  name: string
  player_id: number
  edition_id: number

  species_id?: number | null
  species_variant_id?: number | null
  background_id?: number | null

  level?: number
  experience_points?: number

  alignment?: string | null
  size?: string | null
  speed?: number | null

  ability_scores?: JsonValue

  hit_point_maximum?: number | null
  current_hit_points?: number | null
  temporary_hit_points?: number

  armor_class?: number | null
  initiative_bonus?: number | null
  proficiency_bonus?: number | null

  death_saves?: JsonValue

  personality_traits?: string | null
  ideals?: string | null
  bonds?: string | null
  flaws?: string | null
  backstory?: string | null
  notes?: string | null
}

export type CharacterUpdate = Partial<CharacterCreate>
