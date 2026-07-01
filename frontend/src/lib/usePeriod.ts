import { useEffect, useState } from 'react'
import { api } from './api'
import type { Period } from './types'

// Every module (Risks, Cost Plan, ...) is period-scoped, but Period Manager
// doesn't exist yet. This is a stopgap: use the project's live period, or
// auto-create "Period 1" if none exists yet — not the real Period Manager.
export function useActivePeriod(projectId: string | undefined) {
  const [period, setPeriod] = useState<Period | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) return
    let cancelled = false

    async function bootstrap() {
      try {
        setLoading(true)
        const { data: periods } = await api.get<Period[]>('/api/v1/periods/', {
          params: { project_id: projectId },
        })
        let active = periods.find(p => p.freeze_status === 'live') ?? periods[0] ?? null

        if (!active) {
          const { data: created } = await api.post<Period>('/api/v1/periods/', {
            project_id: projectId,
            period_label: 'Period 1',
            freeze_status: 'live',
          })
          active = created
        }
        if (!cancelled) setPeriod(active)
      } catch {
        if (!cancelled) setError('Failed to load period')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    bootstrap()
    return () => { cancelled = true }
  }, [projectId])

  return { period, loading, error }
}
