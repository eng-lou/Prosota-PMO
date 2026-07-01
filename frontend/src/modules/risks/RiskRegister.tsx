import { Fragment, useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { useProject } from '@/lib/ProjectContext'
import { useActivePeriod } from '@/lib/usePeriod'
import { RecordLinks, type LinkCandidate } from '@/components/RecordLinks'
import { HeatMatrix } from '@/components/HeatMatrix'
import { RiskForm, toRiskPayload, type RiskFormValues } from './RiskForm'
import { MitigationActions } from './MitigationActions'
import { CriteriaThresholds } from './CriteriaThresholds'
import type { Risk } from './types'

interface CostElementSummary {
  id: string
  code: string
  description: string
}

const STATUS_STYLES: Record<string, string> = {
  open: 'bg-amber-100 text-amber-700',
  mitigated: 'bg-blue-100 text-blue-700',
  closed: 'bg-green-100 text-green-700',
}

const RISK_TYPE_STYLES: Record<string, string> = {
  threat: 'bg-red-100 text-red-700',
  opportunity: 'bg-green-100 text-green-700',
}

function formatPercent(value: string | null) {
  if (value === null) return '—'
  return `${Math.round(Number(value) * 100)}%`
}

// EMV is signed (threats negative, opportunities positive — see RISK_MODULE_PLAN.md).
function formatCurrency(value: string | null) {
  if (value === null) return '—'
  const n = Number(value)
  return n < 0 ? `-£${Math.abs(n).toLocaleString()}` : `£${n.toLocaleString()}`
}

function formatDays(value: string | null) {
  if (value === null) return '—'
  return Number(value).toFixed(1)
}

export function RiskRegister() {
  const { selectedProject } = useProject()
  const { period, loading: periodLoading, error: periodError } = useActivePeriod(selectedProject?.id)
  const [risks, setRisks] = useState<Risk[]>([])
  const [costElements, setCostElements] = useState<CostElementSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [editingRisk, setEditingRisk] = useState<Risk | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  useEffect(() => {
    if (!selectedProject || !period) return
    let cancelled = false

    async function load() {
      try {
        setLoading(true)
        const [riskRes, costRes] = await Promise.all([
          api.get<Risk[]>('/api/v1/risks/', { params: { project_id: selectedProject!.id, period_id: period!.id } }),
          api.get<CostElementSummary[]>('/api/v1/cost-elements/', { params: { project_id: selectedProject!.id, period_id: period!.id } }),
        ])
        if (cancelled) return
        setRisks(riskRes.data)
        setCostElements(costRes.data)
      } catch {
        if (!cancelled) setError('Failed to load risk register')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => { cancelled = true }
  }, [selectedProject, period])

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

  const candidatesFor = (risk: Risk): LinkCandidate[] => [
    ...risks.filter(r => r.id !== risk.id).map(r => ({ id: r.id, type: 'risk' as const, label: `${r.code}: ${r.title}` })),
    ...costElements.map(c => ({ id: c.id, type: 'cost_element' as const, label: `${c.code}: ${c.description}` })),
  ]

  if (loading || periodLoading) {
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

      {(error || periodError) && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">{error ?? periodError}</div>
      )}

      <CriteriaThresholds projectId={selectedProject.id} />

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
              <th className="px-4 py-2.5">Code</th>
              <th className="px-4 py-2.5">Title</th>
              <th className="px-4 py-2.5">Type</th>
              <th className="px-4 py-2.5">Theme</th>
              <th className="px-4 py-2.5">Area</th>
              <th className="px-4 py-2.5">Status</th>
              <th className="px-4 py-2.5">Prob.</th>
              <th className="px-4 py-2.5">Impact</th>
              <th className="px-4 py-2.5">Rating</th>
              <th className="px-4 py-2.5">EMV Cost</th>
              <th className="px-4 py-2.5">EMV Days</th>
              <th className="px-4 py-2.5"></th>
            </tr>
          </thead>
          <tbody>
            {risks.map(risk => (
              <Fragment key={risk.id}>
                <tr className="border-b border-gray-100 last:border-0 hover:bg-gray-50">
                  <td className="px-4 py-2.5 text-gray-500 font-mono text-xs">{risk.code}</td>
                  <td className="px-4 py-2.5">
                    <button
                      onClick={() => setExpandedId(expandedId === risk.id ? null : risk.id)}
                      className="text-left font-medium text-gray-900 hover:text-blue-600"
                    >
                      {risk.title}
                    </button>
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${RISK_TYPE_STYLES[risk.risk_type]}`}>
                      {risk.risk_type}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-gray-600">{risk.category ?? '—'}</td>
                  <td className="px-4 py-2.5 text-gray-600">{risk.area ?? '—'}</td>
                  <td className="px-4 py-2.5">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_STYLES[risk.status] ?? 'bg-gray-100 text-gray-600'}`}>
                      {risk.status}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-gray-600">{formatPercent(risk.probability)}</td>
                  <td className="px-4 py-2.5 text-gray-600">{formatPercent(risk.impact)}</td>
                  <td className="px-4 py-2.5 text-gray-600">{risk.rating ?? '—'}</td>
                  <td className="px-4 py-2.5 text-gray-600">{formatCurrency(risk.emv_cost)}</td>
                  <td className="px-4 py-2.5 text-gray-600">{formatDays(risk.emv_schedule_days)}</td>
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
                    <td colSpan={12} className="p-0">
                      <div className="px-4 py-4 bg-gray-50 border-t border-gray-100 flex gap-10 flex-wrap">
                        <HeatMatrix
                          label="Inherent (pre-mitigation)"
                          probability={risk.probability !== null ? Number(risk.probability) : null}
                          impact={risk.impact !== null ? Number(risk.impact) : null}
                        />
                        <HeatMatrix
                          label="Residual (post-mitigation target)"
                          probability={risk.probability_residual !== null ? Number(risk.probability_residual) : null}
                          impact={risk.impact_residual !== null ? Number(risk.impact_residual) : null}
                        />
                      </div>
                      {risk.rating_narrative && (
                        <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 text-xs text-gray-600">
                          {risk.rating_narrative}
                        </div>
                      )}
                      <MitigationActions riskId={risk.id} />
                      {(risk.contingency_plan || risk.fallback_plan) && (
                        <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 space-y-2 text-xs">
                          {risk.contingency_plan && (
                            <div>
                              <span className="font-semibold text-gray-600">Contingency plan: </span>
                              <span className="text-gray-600">{risk.contingency_plan}</span>
                            </div>
                          )}
                          {risk.fallback_plan && (
                            <div>
                              <span className="font-semibold text-gray-600">Fallback plan: </span>
                              <span className="text-gray-600">{risk.fallback_plan}</span>
                            </div>
                          )}
                        </div>
                      )}
                      <RecordLinks recordType="risk" recordId={risk.id} candidates={candidatesFor(risk)} />
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}

            {risks.length === 0 && (
              <tr>
                <td colSpan={12} className="px-4 py-10 text-center text-gray-400 text-sm">
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
