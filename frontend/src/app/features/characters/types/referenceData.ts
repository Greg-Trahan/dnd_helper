export interface PlayerOption {
  id: number
  name: string
  campaign_id: number
}

export interface EditionOption {
  id: number
  code: string
  name: string
  year: number | null
}

export interface SpeciesOption {
  id: number
  edition_id: number
  name: string
  size: string | null
  creature_type: string
  base_speed: number | null
  is_playable: boolean
}

export interface SpeciesVariantOption {
  id: number
  species_id: number
  name: string
  size_override: string | null
  speed_override: number | null
}

export interface BackgroundOption {
  id: number
  edition_id: number
  name: string
}

export interface ClassOption {
  id: number
  edition_id: number
  name: string
  hit_die: number | null
  primary_ability: string | null
  is_playable: boolean
}
