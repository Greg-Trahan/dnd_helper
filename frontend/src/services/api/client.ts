const API_BASE_URL = '/api/v1'

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    let message = `API request failed: ${response.status} ${response.statusText}`

    try {
      const errorData = await response.json()
      if (typeof errorData.detail === 'string') {
        message = errorData.detail
      }
    } catch {
      // Keep the default HTTP error message.
    }

    throw new ApiError(message, response.status)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export const api = {
  get<T>(endpoint: string): Promise<T> {
    return request<T>(endpoint)
  },

  post<T>(endpoint: string, body: unknown): Promise<T> {
    return request<T>(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
  },

  put<T>(endpoint: string, body: unknown): Promise<T> {
    return request<T>(endpoint, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
  },

  patch<T>(endpoint: string, body: unknown): Promise<T> {
    return request<T>(endpoint, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
  },

  delete<T>(endpoint: string): Promise<T> {
    return request<T>(endpoint, {
      method: 'DELETE',
    })
  },
}
