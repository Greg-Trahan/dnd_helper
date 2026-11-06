import { api } from '../../../../services/api/client'
import { API_ENDPOINTS } from '../../../../services/api/endpoints'
import type {
  Character,
  CharacterCreate,
  CharacterUpdate,
} from '../types/character'

export async function getCharacters(): Promise<Character[]> {
  return api.get<Character[]>(API_ENDPOINTS.characters)
}

export async function getCharacter(id: number): Promise<Character> {
  return api.get<Character>(`${API_ENDPOINTS.characters}/${id}`)
}

export async function createCharacter(
  data: CharacterCreate,
): Promise<Character> {
  return api.post<Character>(API_ENDPOINTS.characters, data)
}

export async function updateCharacter(
  id: number,
  data: CharacterUpdate,
): Promise<Character> {
  return api.patch<Character>(`${API_ENDPOINTS.characters}/${id}`, data)
}

export async function deleteCharacter(id: number): Promise<void> {
  return api.delete<void>(`${API_ENDPOINTS.characters}/${id}`)
}
