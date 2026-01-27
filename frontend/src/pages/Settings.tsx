import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { settingsApi, filamentsApi, type SpoolmanFilament } from '../api'

export default function Settings() {
  const queryClient = useQueryClient()
  const [importingFilaments, setImportingFilaments] = useState(false)
  const [importResult, setImportResult] = useState<{ success: number; failed: number } | null>(null)

  const { data: settings, isLoading: settingsLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsApi.get,
  })

  const { data: spoolmanStatus, isLoading: statusLoading, refetch: refetchStatus } = useQuery({
    queryKey: ['spoolman-status'],
    queryFn: settingsApi.getSpoolmanStatus,
    enabled: !!settings?.spoolman_url,
    refetchInterval: false,
  })

  const { data: spoolmanFilaments, isLoading: filamentsLoading, refetch: refetchFilaments } = useQuery({
    queryKey: ['spoolman-filaments'],
    queryFn: settingsApi.getSpoolmanFilaments,
    enabled: !!spoolmanStatus?.connected,
  })

  const createFilamentMutation = useMutation({
    mutationFn: filamentsApi.create,
  })

  const handleTestConnection = () => {
    refetchStatus()
  }

  const handleRefreshFilaments = () => {
    refetchFilaments()
  }

  const handleImportFilament = async (spoolmanFilament: SpoolmanFilament) => {
    try {
      await createFilamentMutation.mutateAsync({
        vendor: spoolmanFilament.vendor_name || 'Unknown',
        material: spoolmanFilament.material || 'PLA',
        name: spoolmanFilament.name || 'Unknown',
        color_hex: spoolmanFilament.color_hex,
        density: spoolmanFilament.density,
        diameter: spoolmanFilament.diameter || 1.75,
        spoolman_filament_id: spoolmanFilament.id,
      })
      queryClient.invalidateQueries({ queryKey: ['filaments'] })
      return true
    } catch {
      return false
    }
  }

  const handleImportAll = async () => {
    if (!spoolmanFilaments) return

    setImportingFilaments(true)
    setImportResult(null)

    let success = 0
    let failed = 0

    for (const filament of spoolmanFilaments) {
      const result = await handleImportFilament(filament)
      if (result) {
        success++
      } else {
        failed++
      }
    }

    setImportResult({ success, failed })
    setImportingFilaments(false)
    queryClient.invalidateQueries({ queryKey: ['filaments'] })
  }

  if (settingsLoading) return <div>Loading...</div>

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-6">Settings</h1>
      </div>

      {/* Spoolman Integration */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Spoolman Integration</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Spoolman URL
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={settings?.spoolman_url || ''}
                readOnly
                className="flex-1 rounded-md border-gray-300 shadow-sm border px-3 py-2 bg-gray-50"
                placeholder="Not configured - set SPOOLMAN_URL environment variable"
              />
              <button
                onClick={handleTestConnection}
                disabled={!settings?.spoolman_url || statusLoading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
              >
                {statusLoading ? 'Testing...' : 'Test Connection'}
              </button>
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Configure via environment variable: <code className="bg-gray-100 px-1 rounded">SPOOLMAN_URL=http://your-spoolman:7912</code>
            </p>
          </div>

          {/* Connection Status */}
          {spoolmanStatus && (
            <div className={`p-4 rounded-lg ${spoolmanStatus.connected ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${spoolmanStatus.connected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className={spoolmanStatus.connected ? 'text-green-800' : 'text-red-800'}>
                  {spoolmanStatus.connected
                    ? `Connected to Spoolman v${spoolmanStatus.version}`
                    : `Not connected: ${spoolmanStatus.error}`
                  }
                </span>
              </div>
            </div>
          )}

          {/* Filaments from Spoolman */}
          {spoolmanStatus?.connected && (
            <div className="mt-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-md font-medium">Filaments in Spoolman</h3>
                <div className="flex gap-2">
                  <button
                    onClick={handleRefreshFilaments}
                    disabled={filamentsLoading}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    {filamentsLoading ? 'Loading...' : 'Refresh'}
                  </button>
                  {spoolmanFilaments && spoolmanFilaments.length > 0 && (
                    <button
                      onClick={handleImportAll}
                      disabled={importingFilaments}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 disabled:bg-gray-400"
                    >
                      {importingFilaments ? 'Importing...' : `Import All (${spoolmanFilaments.length})`}
                    </button>
                  )}
                </div>
              </div>

              {importResult && (
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-blue-800">
                    Import complete: {importResult.success} succeeded, {importResult.failed} failed
                  </p>
                </div>
              )}

              {filamentsLoading ? (
                <div className="text-gray-500">Loading filaments...</div>
              ) : spoolmanFilaments && spoolmanFilaments.length > 0 ? (
                <div className="border rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Color</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Vendor</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Material</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {spoolmanFilaments.map((filament) => (
                        <tr key={filament.id}>
                          <td className="px-4 py-2">
                            <div
                              className="w-6 h-6 rounded-full border border-gray-300"
                              style={{ backgroundColor: filament.color_hex || '#ccc' }}
                            />
                          </td>
                          <td className="px-4 py-2 text-sm">{filament.vendor_name || '-'}</td>
                          <td className="px-4 py-2 text-sm">{filament.material || '-'}</td>
                          <td className="px-4 py-2 text-sm">{filament.name || '-'}</td>
                          <td className="px-4 py-2 text-right">
                            <button
                              onClick={() => handleImportFilament(filament)}
                              disabled={createFilamentMutation.isPending}
                              className="text-blue-600 hover:text-blue-800 text-sm"
                            >
                              Import
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-gray-500 text-center py-4">
                  No filaments found in Spoolman
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* About */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">About FilamentProfiles</h2>
        <p className="text-gray-600">
          FilamentProfiles helps you manage print settings for different filament, machine, and build plate combinations.
          Connect it to your Spoolman instance to sync filament data and track your spool inventory.
        </p>
        <div className="mt-4 space-y-2 text-sm text-gray-500">
          <p><strong>Workflow:</strong></p>
          <ol className="list-decimal list-inside space-y-1 ml-2">
            <li>Add your machines (printers) and build plates</li>
            <li>Import filaments from Spoolman or add them manually</li>
            <li>Create print profiles for each filament/machine/plate combination</li>
            <li>Export profiles to OrcaSlicer/QIDI Studio format</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
