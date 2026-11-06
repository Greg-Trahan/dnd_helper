import { api } from '../../../../services/api/client'
import { API_ENDPOINTS } from '../../../../services/api/endpoints'
import type {
  BackgroundOption,
  ClassOption,
  EditionOption,
  PlayerOption,
  SpeciesOption,
  SpeciesVariantOption,
} from '../types/referenceData'

export async function getPlayers(): Promise<PlayerOption[]> {
  return api.get<PlayerOption[]>(API_ENDPOINTS.players)
}

export async function getEditions(): Promise<EditionOption[]> {
  return api.get<EditionOption[]>(API_ENDPOINTS.editions)
}

export async function getSpecies(
  editionId?: number,
): Promise<SpeciesOption[]> {
  const params = new URLSearchParams({
    playable_only: 'false',
  })

  if (editionId) {
    params.set('edition_id', String(editionId))
  }

  return api.get<SpeciesOption[]>(
    `${API_ENDPOINTS.species}?${params.toString()}`,
  )
}

export async function getSpeciesVariants(
  speciesId: number,
): Promise<SpeciesVariantOption[]> {
  return api.get<SpeciesVariantOption[]>(
    `${API_ENDPOINTS.speciesVariants}?species_id=${speciesId}`,
  )
}

export async function getBackgrounds(
  editionId?: number,
): Promise<BackgroundOption[]> {
  const query = editionId ? `?edition_id=${editionId}` : ''
  return api.get<BackgroundOption[]>(`${API_ENDPOINTS.backgrounds}${query}`)
}

export async function getClasses(
  editionId?: number,
): Promise<ClassOption[]> {
  const query = editionId ? `?edition_id=${editionId}` : ''
  return api.get<ClassOption[]>(`${API_ENDPOINTS.classes}${query}`)
}
