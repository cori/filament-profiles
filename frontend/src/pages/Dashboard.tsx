import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { machinesApi, platesApi, filamentsApi, profilesApi } from '../api'

export default function Dashboard() {
  const machines = useQuery({ queryKey: ['machines'], queryFn: machinesApi.list })
  const plates = useQuery({ queryKey: ['plates'], queryFn: platesApi.list })
  const filaments = useQuery({ queryKey: ['filaments'], queryFn: filamentsApi.list })
  const profiles = useQuery({ queryKey: ['profiles'], queryFn: profilesApi.list })

  const stats = [
    { name: 'Machines', count: machines.data?.length ?? 0, href: '/machines' },
    { name: 'Plates', count: plates.data?.length ?? 0, href: '/plates' },
    { name: 'Filaments', count: filaments.data?.length ?? 0, href: '/filaments' },
    { name: 'Profiles', count: profiles.data?.length ?? 0, href: '/profiles' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Link
            key={stat.name}
            to={stat.href}
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
              <dd className="mt-1 text-3xl font-semibold text-gray-900">{stat.count}</dd>
            </div>
          </Link>
        ))}
      </div>

      {profiles.data && profiles.data.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-4">Recent Profiles</h2>
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Filament
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Machine
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Plate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Temps
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {profiles.data.slice(0, 5).map((profile) => (
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {profile.machine?.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {profile.plate?.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {profile.nozzle_temp}°C / {profile.bed_temp}°C
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
