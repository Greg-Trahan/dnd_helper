import { api } from '../api/client'
import { API_ENDPOINTS } from '../api/endpoints'
import type { HealthResponse } from '../api/types'

export function getHealth(): Promise<HealthResponse> {
  return api.get<HealthResponse>(API_ENDPOINTS.health)
}