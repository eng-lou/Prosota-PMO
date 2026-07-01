import { Fragment, useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { useProject } from '@/lib/ProjectContext'
import { RiskForm, toRiskPayload, type RiskFormValues } from './RiskForm'
import { RiskLinks } from './RiskLinks'
import type { Period, Risk } from './types'

const STATUS_STYLES: Record<string, string> = {
  open: 'bg-amber-100 text-amber-700',
  mitigated: 'bg-blue-100 text-blue-700',
  closed: 'bg-green-100 text-green-700',
}

function formatPercent(value: string | null) {
  if (value === null) return '—'
  return `${Math.round(Number(value) * 100)}%`
}

function formatCurrency(value: string | null) {
  if (value === null) return '—'
  return `£${Number(value).toLocaleString()}`
}

export function RiskRegister() {
  const { selectedProject } = useProject()
  const [period, setPeriod] = useState<Period | null>(null)
  const [risks, setRisks] = useState<Risk[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [editingRisk, setEditingRisk] = useState<Risk | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  useEffect(() => {
    if (!selectedProject) return
    let cancelled = false

    async function bootstrap() {
      try {
        setLoading(true)
        const { data: periods } = await api.get<Period[]>('/api/v1/periods/', {
          params: { project_id: selectedProject!.id },
        })
        let activePeriod = periods.find(p => p.freeze_status === 'live') ?? periods[0] ?? null

        if (!activePeriod) {
          const { data: created } = await api.post<Period>('/api/v1/periods/', {
            project_id: selectedProject!.id,
            period_label: 'Period 1',
            freeze_status: 'live',
          })
          activePeriod = created
        }
        if (cancelled) return
        setPeriod(activePeriod)

        const { data: riskData } = await api.get<Risk[]>('/api/v1/risks/', {
          params: { project_id: selectedProject!.id, period_id: activePeriod.id },
        })
        if (!cancelled) setRisks(riskData)
      } catch {
        if (!cancelled) setError('Failed to load risk register')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    bootstrap()
    return () => { cancelled = true }
  }, [selectedProject])

  if (!selectedProject) return null

  const refreshRisks = async () => {
    if (!period) return
    const { data } = await api.get<Risk[]>('/api/v1/risks/', {
      params: { project_id: selectedProject.id, period_id: period.id },
    })
    setRisks(data)
  }

  const handleCreate = async (values: RiskFormValues) => {
    if (!period) return
    await api.post('/api/v1/risks/', {
      ...toRiskPayload(values),
      project_id: selectedProject.id,
      period_id: period.id,
    })
    setFormOpen(false)
    await refreshRisks()
  }

  const handleUpdate = async (values: RiskFormValues) => {
    if (!editingRisk) return
    await api.patch(`/api/v1/risks/${editingRisk.id}`, toRiskPayload(values))
    setEditingRisk(null)
    await refreshRisks()
  }

  const handleDelete = async (risk: Risk) => {
    if (!window.confirm(`Delete risk "${risk.title}"? This cannot be undone.`)) return
    await api.delete(`/api/v1/risks/${risk.id}`)
    await refreshRisks()
  }

  if (loading) {
    return <div className="p-8 text-sm text-gray-400">Loading risk register…</div>
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-2xl font-bold text-gray-900">Risk Register</h1>
        {period && (
          <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600 font-medium">
            {period.period_label} · {period.freeze_status}
          </span>
        )}
      </div>
      <p className="text-gray-500 text-sm mb-6">
        Risks for {selectedProject.name}. Frozen periods will become read-only once Period Manager is built.
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">{error}</div>
      )}

      {formOpen && (
        <RiskForm risk={null} onCancel={() => setFormOpen(false)} onSubmit={handleCreate} />
      )}
      {editingRisk && (
        <RiskForm risk={editingRisk} onCancel={() => setEditingRisk(null)} onSubmit={handleUpdate} />
      )}

      {!formOpen && !editingRisk && (
        <button
          onClick={() => setFormOpen(true)}
          className="mb-4 text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          + New risk
        </button>
      )}

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200 text-left text-xs text-gray-500 font-medium uppercase tracking-wide">
              <th className="px-4 py-2.5">Title</th>
              <th className="px-4 py-2.5">Category</th>
              <th className="px-4 py-2.5">Status</th>
              <th className="px-4 py-2.5">Prob.</th>
              <th className="px-4 py-2.5">Impact</th>
              <th className="px-4 py-2.5">EMV Cost</th>
              <th className="px-4 py-2.5">EMV Days</th>
              <th className="px-4 py-2.5"></th>
            </tr>
          </thead>
          <tbody>
            {risks.map(risk => (
              <Fragment key={risk.id}>
                <tr className="border-b border-gray-100 last:border-0 hover:bg-gray-50">
                  <td className="px-4 py-2.5">
                    <button
                      onClick={() => setExpandedId(expandedId === risk.id ? null : risk.id)}
                      className="text-left font-medium text-gray-900 hover:text-blue-600"
                    >
                      {risk.title}
                    </button>
                  </td>
                  <td className="px-4 py-2.5 text-gray-600">{risk.category ?? '—'}</td>
                  <td className="px-4 py-2.5">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_STYLES[risk.status] ?? 'bg-gray-100 text-gray-600'}`}>
                      {risk.status}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-gray-600">{formatPercent(risk.probability)}</td>
                  <td className="px-4 py-2.5 text-gray-600">{formatPercent(risk.impact)}</td>
                  <td className="px-4 py-2.5 text-gray-600">{formatCurrency(risk.emv_cost)}</td>
                  <td className="px-4 py-2.5 text-gray-600">{risk.emv_schedule_days ?? '—'}</td>
                  <td className="px-4 py-2.5 text-right whitespace-nowrap">
                    <button onClick={() => setEditingRisk(risk)} className="text-xs text-blue-600 hover:text-blue-700 mr-3">
                      Edit
                    </button>
                    <button onClick={() => handleDelete(risk)} className="text-xs text-gray-400 hover:text-red-600">
                      Delete
                    </button>
                  </td>
                </tr>
                {expandedId === risk.id && (
                  <tr>
                    <td colSpan={8} className="p-0">
                      <RiskLinks risk={risk} allRisks={risks} />
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}

            {risks.length === 0 && (
              <tr>
                <td colSpan={8} className="px-4 py-10 text-center text-gray-400 text-sm">
                  No risks yet for this period. Add the first one above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
