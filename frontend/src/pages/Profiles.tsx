import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { profilesApi, machinesApi, platesApi, filamentsApi, exportApi, type Profile } from '../api'

const defaultFormData = {
  filament_id: 0,
  machine_id: 0,
  plate_id: 0,
  nozzle_temp: 200,
  nozzle_temp_first_layer: null as number | null,
  bed_temp: 60,
  bed_temp_first_layer: null as number | null,
  chamber_temp: null as number | null,
  flow_ratio: 1.0,
  pressure_advance: null as number | null,
  max_volumetric_speed: null as number | null,
  retraction_length: null as number | null,
  retraction_speed: null as number | null,
  fan_min_speed: null as number | null,
  fan_max_speed: null as number | null,
  disable_fan_first_layers: null as number | null,
  notes: '',
}

export default function Profiles() {
  const queryClient = useQueryClient()
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState(defaultFormData)
  const [showForm, setShowForm] = useState(false)

  const { data: profiles, isLoading } = useQuery({
    queryKey: ['profiles'],
    queryFn: () => profilesApi.list(),
  })

  const { data: machines } = useQuery({ queryKey: ['machines'], queryFn: machinesApi.list })
  const { data: plates } = useQuery({ queryKey: ['plates'], queryFn: platesApi.list })
  const { data: filaments } = useQuery({ queryKey: ['filaments'], queryFn: () => filamentsApi.list() })

  const createMutation = useMutation({
    mutationFn: profilesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profiles'] })
      resetForm()
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Profile> }) => profilesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profiles'] })
      resetForm()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: profilesApi.delete,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['profiles'] }),
  })

  const resetForm = () => {
    setFormData(defaultFormData)
    setEditingId(null)
    setShowForm(false)
  }

  const handleEdit = (profile: Profile) => {
    setFormData({
      filament_id: profile.filament_id,
      machine_id: profile.machine_id,
      plate_id: profile.plate_id,
      nozzle_temp: profile.nozzle_temp,
      nozzle_temp_first_layer: profile.nozzle_temp_first_layer,
      bed_temp: profile.bed_temp,
      bed_temp_first_layer: profile.bed_temp_first_layer,
      chamber_temp: profile.chamber_temp,
      flow_ratio: profile.flow_ratio,
      pressure_advance: profile.pressure_advance,
      max_volumetric_speed: profile.max_volumetric_speed,
      retraction_length: profile.retraction_length,
      retraction_speed: profile.retraction_speed,
      fan_min_speed: profile.fan_min_speed,
      fan_max_speed: profile.fan_max_speed,
      disable_fan_first_layers: profile.disable_fan_first_layers,
      notes: profile.notes || '',
    })
    setEditingId(profile.id)
    setShowForm(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const data = {
      ...formData,
      nozzle_temp_first_layer: formData.nozzle_temp_first_layer || undefined,
      bed_temp_first_layer: formData.bed_temp_first_layer || undefined,
      chamber_temp: formData.chamber_temp || undefined,
      pressure_advance: formData.pressure_advance || undefined,
      max_volumetric_speed: formData.max_volumetric_speed || undefined,
      retraction_length: formData.retraction_length || undefined,
      retraction_speed: formData.retraction_speed || undefined,
      fan_min_speed: formData.fan_min_speed || undefined,
      fan_max_speed: formData.fan_max_speed || undefined,
      disable_fan_first_layers: formData.disable_fan_first_layers || undefined,
      notes: formData.notes || undefined,
    }
    if (editingId) {
      updateMutation.mutate({ id: editingId, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const handleExport = (profileId: number) => {
    window.open(exportApi.profileUrl(profileId), '_blank')
  }

  if (isLoading) return <div>Loading...</div>

  const canCreate = machines?.length && plates?.length && filaments?.length

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Print Profiles</h1>
        <button
          onClick={() => setShowForm(true)}
          disabled={!canCreate}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          title={!canCreate ? 'Add machines, plates, and filaments first' : ''}
        >
          Add Profile
        </button>
      </div>

      {!canCreate && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-yellow-800">
            To create profiles, you need at least one machine, plate, and filament. Add them first.
          </p>
        </div>
      )}

      {showForm && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">{editingId ? 'Edit Profile' : 'New Profile'}</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Entity Selection */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Filament</label>
                <select
                  value={formData.filament_id}
                  onChange={(e) => setFormData({ ...formData, filament_id: parseInt(e.target.value) })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                  required
                  disabled={!!editingId}
                >
                  <option value={0}>Select filament...</option>
                  {filaments?.map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.vendor} {f.material} {f.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Machine</label>
                <select
                  value={formData.machine_id}
                  onChange={(e) => setFormData({ ...formData, machine_id: parseInt(e.target.value) })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                  required
                  disabled={!!editingId}
                >
                  <option value={0}>Select machine...</option>
                  {machines?.map((m) => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Plate</label>
                <select
                  value={formData.plate_id}
                  onChange={(e) => setFormData({ ...formData, plate_id: parseInt(e.target.value) })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                  required
                  disabled={!!editingId}
                >
                  <option value={0}>Select plate...</option>
                  {plates?.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Temperature Settings */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Temperature</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div>
                  <label className="block text-xs text-gray-500">Nozzle (°C)</label>
                  <input
                    type="number"
                    value={formData.nozzle_temp}
                    onChange={(e) => setFormData({ ...formData, nozzle_temp: parseInt(e.target.value) })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Nozzle 1st Layer</label>
                  <input
                    type="number"
                    value={formData.nozzle_temp_first_layer || ''}
                    onChange={(e) => setFormData({ ...formData, nozzle_temp_first_layer: e.target.value ? parseInt(e.target.value) : null })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    placeholder="Same"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Bed (°C)</label>
                  <input
                    type="number"
                    value={formData.bed_temp}
                    onChange={(e) => setFormData({ ...formData, bed_temp: parseInt(e.target.value) })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Bed 1st Layer</label>
                  <input
                    type="number"
                    value={formData.bed_temp_first_layer || ''}
                    onChange={(e) => setFormData({ ...formData, bed_temp_first_layer: e.target.value ? parseInt(e.target.value) : null })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    placeholder="Same"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Chamber (°C)</label>
                  <input
                    type="number"
                    value={formData.chamber_temp || ''}
                    onChange={(e) => setFormData({ ...formData, chamber_temp: e.target.value ? parseInt(e.target.value) : null })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    placeholder="None"
                  />
                </div>
              </div>
            </div>

            {/* Flow & Extrusion */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Flow & Extrusion</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs text-gray-500">Flow Ratio</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.flow_ratio}
                    onChange={(e) => setFormData({ ...formData, flow_ratio: parseFloat(e.target.value) })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Pressure Advance</label>
                  <input
                    type="number"
                    step="0.001"
                    value={formData.pressure_advance || ''}
                    onChange={(e) => setFormData({ ...formData, pressure_advance: e.target.value ? parseFloat(e.target.value) : null })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    placeholder="e.g., 0.04"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Max Vol Speed (mm³/s)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.max_volumetric_speed || ''}
                    onChange={(e) => setFormData({ ...formData, max_volumetric_speed: e.target.value ? parseFloat(e.target.value) : null })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    placeholder="e.g., 15"
                  />
                </div>
              </div>
            </div>

            {/* Retraction */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Retraction</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-500">Length (mm)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.retraction_length || ''}
                    onChange={(e) => setFormData({ ...formData, retraction_length: e.target.value ? parseFloat(e.target.value) : null })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    placeholder="e.g., 0.8"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Speed (mm/s)</label>
                  <input
                    type="number"
                    step="1"
                    value={formData.retraction_speed || ''}
                    onChange={(e) => setFormData({ ...formData, retraction_speed: e.target.value ? parseFloat(e.target.value) : null })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    placeholder="e.g., 30"
                  />
                </div>
              </div>
            </div>

            {/* Cooling */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Cooling</h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs text-gray-500">Fan Min (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.fan_min_speed || ''}
                    onChange={(e) => setFormData({ ...formData, fan_min_speed: e.target.value ? parseInt(e.target.value) : null })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    placeholder="e.g., 35"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Fan Max (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.fan_max_speed || ''}
                    onChange={(e) => setFormData({ ...formData, fan_max_speed: e.target.value ? parseInt(e.target.value) : null })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    placeholder="e.g., 100"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">No Fan Layers</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.disable_fan_first_layers || ''}
                    onChange={(e) => setFormData({ ...formData, disable_fan_first_layers: e.target.value ? parseInt(e.target.value) : null })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    placeholder="e.g., 1"
                  />
                </div>
              </div>
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                placeholder="Any notes about this profile..."
              />
            </div>

            <div className="flex gap-2">
              <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                {editingId ? 'Update' : 'Create'}
              </button>
              <button type="button" onClick={resetForm} className="bg-gray-200 px-4 py-2 rounded-md hover:bg-gray-300">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Filament</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Machine</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plate</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Temps</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Flow/PA</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {profiles?.map((profile) => (
              <tr key={profile.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    {profile.filament?.color_hex && (
                      <div
                        className="w-4 h-4 rounded-full mr-2 border border-gray-300"
                        style={{ backgroundColor: profile.filament.color_hex }}
                      />
                    )}
                    <span className="text-sm text-gray-900">
                      {profile.filament?.vendor} {profile.filament?.material} {profile.filament?.name}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{profile.machine?.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{profile.plate?.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {profile.nozzle_temp}°C / {profile.bed_temp}°C
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {profile.flow_ratio} / {profile.pressure_advance ?? '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <button onClick={() => handleExport(profile.id)} className="text-green-600 hover:text-green-900">
                    Export
                  </button>
                  <button onClick={() => handleEdit(profile)} className="text-blue-600 hover:text-blue-900">
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Delete this profile?')) deleteMutation.mutate(profile.id)
                    }}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {profiles?.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                  No profiles yet. Add machines, plates, and filaments first, then create profiles.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
