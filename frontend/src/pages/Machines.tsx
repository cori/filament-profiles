import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { machinesApi, type Machine } from '../api'

export default function Machines() {
  const queryClient = useQueryClient()
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({ name: '', description: '', nozzle_diameter: 0.4 })
  const [showForm, setShowForm] = useState(false)

  const { data: machines, isLoading } = useQuery({
    queryKey: ['machines'],
    queryFn: machinesApi.list,
  })

  const createMutation = useMutation({
    mutationFn: machinesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] })
      resetForm()
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Machine> }) => machinesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] })
      resetForm()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: machinesApi.delete,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['machines'] }),
  })

  const resetForm = () => {
    setFormData({ name: '', description: '', nozzle_diameter: 0.4 })
    setEditingId(null)
    setShowForm(false)
  }

  const handleEdit = (machine: Machine) => {
    setFormData({
      name: machine.name,
      description: machine.description || '',
      nozzle_diameter: machine.nozzle_diameter,
    })
    setEditingId(machine.id)
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
        <h1 className="text-2xl font-bold">Machines</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Add Machine
        </button>
      </div>

      {showForm && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">{editingId ? 'Edit Machine' : 'New Machine'}</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Description</label>
              <input
                type="text"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Nozzle Diameter (mm)</label>
              <input
                type="number"
                step="0.1"
                value={formData.nozzle_diameter}
                onChange={(e) => setFormData({ ...formData, nozzle_diameter: parseFloat(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border px-3 py-2"
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nozzle</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {machines?.map((machine) => (
              <tr key={machine.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{machine.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{machine.nozzle_diameter}mm</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{machine.description || '-'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button onClick={() => handleEdit(machine)} className="text-blue-600 hover:text-blue-900 mr-4">
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Delete this machine?')) deleteMutation.mutate(machine.id)
                    }}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {machines?.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-4 text-center text-gray-500">
                  No machines yet. Add one to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
