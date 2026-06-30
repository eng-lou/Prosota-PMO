import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { useProject, type Project } from '@/lib/ProjectContext'

export function ProjectSelector() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)
  const [newName, setNewName] = useState('')
  const [newClient, setNewClient] = useState('')
  const { selectProject } = useProject()
  const navigate = useNavigate()

  useEffect(() => {
    api.get<Project[]>('/api/v1/projects/')
      .then(r => setProjects(r.data))
      .catch(() => setError('Failed to load projects'))
      .finally(() => setLoading(false))
  }, [])

  const handleSelect = (project: Project) => {
    selectProject(project)
    navigate('/dashboard')
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newName.trim()) return
    try {
      const { data } = await api.post<Project>('/api/v1/projects/', {
        name: newName.trim(),
        client_name: newClient.trim() || null,
      })
      setProjects(prev => [...prev, data])
      setCreating(false)
      setNewName('')
      setNewClient('')
    } catch {
      setError('Failed to create project')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <span className="text-gray-400 text-sm">Loading projects…</span>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-2xl">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Select a project</h1>
          <p className="text-gray-500 text-sm mt-1">Choose a project to continue into ProsotaPMO</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-3 mb-6">
          {projects.map(project => (
            <button
              key={project.id}
              onClick={() => handleSelect(project)}
              className="w-full text-left bg-white border border-gray-200 rounded-lg px-5 py-4 hover:border-blue-400 hover:shadow-sm transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900 group-hover:text-blue-600">{project.name}</p>
                  {project.client_name && (
                    <p className="text-sm text-gray-500 mt-0.5">{project.client_name}</p>
                  )}
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                  project.status === 'active'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-500'
                }`}>
                  {project.status}
                </span>
              </div>
            </button>
          ))}

          {projects.length === 0 && !creating && (
            <p className="text-gray-400 text-sm text-center py-8">
              No projects yet. Create your first one below.
            </p>
          )}
        </div>

        {creating ? (
          <form onSubmit={handleCreate} className="bg-white border border-gray-200 rounded-lg p-5 space-y-3">
            <h2 className="font-medium text-gray-900 text-sm">New project</h2>
            <input
              autoFocus
              type="text"
              placeholder="Project name"
              value={newName}
              onChange={e => setNewName(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Client name (optional)"
              value={newClient}
              onChange={e => setNewClient(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="flex gap-2">
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
              >
                Create
              </button>
              <button
                type="button"
                onClick={() => setCreating(false)}
                className="text-gray-500 px-4 py-2 rounded-md text-sm hover:bg-gray-100"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <button
            onClick={() => setCreating(true)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            + New project
          </button>
        )}
      </div>
    </div>
  )
}
