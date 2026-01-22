import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { filamentsApi, type Filament } from '../api'

const defaultFormData = {
  vendor: '',
  material: 'PLA',
  name: '',
  color_name: '',
  color_hex: '#000000',
  density: 1.24,
  diameter: 1.75,
}

export default function Filaments() {
  const queryClient = useQueryClient()
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState(defaultFormData)
  const [showForm, setShowForm] = useState(false)

  const { data: filaments, isLoading } = useQuery({
    queryKey: ['filaments'],
    queryFn: () => filamentsApi.list(),
  })

  const createMutation = useMutation({
    mutationFn: filamentsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['filaments'] })
      resetForm()
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Filament> }) => filamentsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['filaments'] })
      resetForm()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: filamentsApi.delete,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['filaments'] }),
  })

  const resetForm = () => {
    setFormData(defaultFormData)
    setEditingId(null)
    setShowForm(false)
  }

  const handleEdit = (filament: Filament) => {
    setFormData({
      vendor: filament.vendor,
      material: filament.material,
      name: filament.name,
      color_name: filament.color_name || '',
      color_hex: filament.color_hex || '#000000',
      density: filament.density || 1.24,
      diameter: filament.diameter,
    })
    setEditingId(filament.id)
    setShowForm(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editingId) {
      updateMutation.mutate({ id: editingId, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Filaments</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Add Filament
        </button>
      </div>

      {showForm && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">{editingId ? 'Edit Filament' : 'New Filament'}</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Vendor</label>
                <input
                  type="text"
                  value={formData.vendor}
                  onChange={(e) => setFormData({ ...formData, vendor: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                  placeholder="e.g., Bambu Lab"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Material</label>
                <select
                  value={formData.material}
                  onChange={(e) => setFormData({ ...formData, material: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                >
                  <option value="PLA">PLA</option>
                  <option value="PETG">PETG</option>
                  <option value="ABS">ABS</option>
                  <option value="ASA">ASA</option>
                  <option value="TPU">TPU</option>
                  <option value="PA">PA (Nylon)</option>
                  <option value="PC">PC</option>
                  <option value="PVA">PVA</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                  placeholder="e.g., Matte, Basic, Silk"
                  required
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Color Name</label>
                <input
                  type="text"
                  value={formData.color_name}
                  onChange={(e) => setFormData({ ...formData, color_name: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                  placeholder="e.g., Bone White"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Color</label>
                <div className="mt-1 flex gap-2">
                  <input
                    type="color"
                    value={formData.color_hex}
                    onChange={(e) => setFormData({ ...formData, color_hex: e.target.value })}
                    className="h-10 w-14 rounded border border-gray-300"
                  />
                  <input
                    type="text"
                    value={formData.color_hex}
                    onChange={(e) => setFormData({ ...formData, color_hex: e.target.value })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                    placeholder="#E8E0D5"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Density (g/cm³)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.density}
                  onChange={(e) => setFormData({ ...formData, density: parseFloat(e.target.value) })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Diameter (mm)</label>
                <select
                  value={formData.diameter}
                  onChange={(e) => setFormData({ ...formData, diameter: parseFloat(e.target.value) })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                >
                  <option value={1.75}>1.75mm</option>
                  <option value={2.85}>2.85mm</option>
                </select>
              </div>
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Color</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Material</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filaments?.map((filament) => (
              <tr key={filament.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-6 h-6 rounded-full border border-gray-300"
                      style={{ backgroundColor: filament.color_hex || '#ccc' }}
                    />
                    <span className="text-sm text-gray-500">{filament.color_name || '-'}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{filament.vendor}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{filament.material}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{filament.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button onClick={() => handleEdit(filament)} className="text-blue-600 hover:text-blue-900 mr-4">
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Delete this filament?')) deleteMutation.mutate(filament.id)
                    }}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {filaments?.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                  No filaments yet. Add one to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
