const API_BASE = import.meta.env.VITE_API_URL || '/api'

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

// Types
export interface Machine {
  id: number
  name: string
  slug: string
  description: string | null
  nozzle_diameter: number
  created_at: string
  updated_at: string
}

export interface Plate {
  id: number
  name: string
  slug: string
  description: string | null
  created_at: string
  updated_at: string
}

export interface Filament {
  id: number
  vendor: string
  material: string
  name: string
  color_name: string | null
  color_hex: string | null
  density: number | null
  diameter: number
  spoolman_filament_id: number | null
  created_at: string
  updated_at: string
}

export interface Profile {
  id: number
  filament_id: number
  machine_id: number
  plate_id: number
  nozzle_temp: number
  nozzle_temp_first_layer: number | null
  bed_temp: number
  bed_temp_first_layer: number | null
  chamber_temp: number | null
  flow_ratio: number
  pressure_advance: number | null
  max_volumetric_speed: number | null
  retraction_length: number | null
  retraction_speed: number | null
  print_speed: number | null
  first_layer_speed: number | null
  outer_wall_speed: number | null
  inner_wall_speed: number | null
  infill_speed: number | null
  travel_speed: number | null
  fan_min_speed: number | null
  fan_max_speed: number | null
  disable_fan_first_layers: number | null
  is_default: boolean
  notes: string | null
  source: string | null
  source_profile: string | null
  created_at: string
  updated_at: string
  filament?: Filament
  machine?: Machine
  plate?: Plate
}

// Machine API
export const machinesApi = {
  list: () => fetchApi<Machine[]>('/machines'),
  get: (id: number) => fetchApi<Machine>(`/machines/${id}`),
  create: (data: Partial<Machine>) => fetchApi<Machine>('/machines', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: Partial<Machine>) => fetchApi<Machine>(`/machines/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) => fetchApi<void>(`/machines/${id}`, { method: 'DELETE' }),
}

// Plate API
export const platesApi = {
  list: () => fetchApi<Plate[]>('/plates'),
  get: (id: number) => fetchApi<Plate>(`/plates/${id}`),
  create: (data: Partial<Plate>) => fetchApi<Plate>('/plates', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: Partial<Plate>) => fetchApi<Plate>(`/plates/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) => fetchApi<void>(`/plates/${id}`, { method: 'DELETE' }),
}

// Filament API
export const filamentsApi = {
  list: (params?: { vendor?: string; material?: string }) => {
    const searchParams = new URLSearchParams()
    if (params?.vendor) searchParams.set('vendor', params.vendor)
    if (params?.material) searchParams.set('material', params.material)
    const query = searchParams.toString()
    return fetchApi<Filament[]>(`/filaments${query ? `?${query}` : ''}`)
  },
  get: (id: number) => fetchApi<Filament>(`/filaments/${id}`),
  create: (data: Partial<Filament>) => fetchApi<Filament>('/filaments', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: Partial<Filament>) => fetchApi<Filament>(`/filaments/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) => fetchApi<void>(`/filaments/${id}`, { method: 'DELETE' }),
}

// Profile API
export const profilesApi = {
  list: (params?: { filament_id?: number; machine_id?: number; plate_id?: number }) => {
    const searchParams = new URLSearchParams()
    if (params?.filament_id) searchParams.set('filament_id', params.filament_id.toString())
    if (params?.machine_id) searchParams.set('machine_id', params.machine_id.toString())
    if (params?.plate_id) searchParams.set('plate_id', params.plate_id.toString())
    const query = searchParams.toString()
    return fetchApi<Profile[]>(`/profiles${query ? `?${query}` : ''}`)
  },
  get: (id: number) => fetchApi<Profile>(`/profiles/${id}`),
  create: (data: Partial<Profile>) => fetchApi<Profile>('/profiles', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: Partial<Profile>) => fetchApi<Profile>(`/profiles/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) => fetchApi<void>(`/profiles/${id}`, { method: 'DELETE' }),
  clone: (id: number, data: { machine_id?: number; plate_id?: number }) =>
    fetchApi<Profile>(`/profiles/${id}/clone`, { method: 'POST', body: JSON.stringify(data) }),
}

// Export API
export const exportApi = {
  profileUrl: (id: number) => `${API_BASE}/export/profile/${id}`,
  machineUrl: (id: number) => `${API_BASE}/export/machine/${id}`,
  previewProfile: (id: number) => fetchApi<Record<string, unknown>>(`/export/profile/${id}/preview`),
}
