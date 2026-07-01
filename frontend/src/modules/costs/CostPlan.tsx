import { Fragment, useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { useProject } from '@/lib/ProjectContext'
import { useActivePeriod } from '@/lib/usePeriod'
import { RecordLinks, type LinkCandidate } from '@/components/RecordLinks'
import { CostForm, toCostElementPayload, type CostFormValues } from './CostForm'
import type { CostElement } from './types'

interface RiskSummary {
  id: string
  code: string
  title: string
}

function formatCurrency(value: string | null) {
  if (value === null) return '—'
  return `£${Number(value).toLocaleString()}`
}

export function CostPlan() {
  const { selectedProject } = useProject()
  const { period, loading: periodLoading, error: periodError } = useActivePeriod(selectedProject?.id)
  const [elements, setElements] = useState<CostElement[]>([])
  const [risks, setRisks] = useState<RiskSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [editingElement, setEditingElement] = useState<CostElement | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  useEffect(() => {
    if (!selectedProject || !period) return
    let cancelled = false

    async function load() {
      try {
        setLoading(true)
        const [costRes, riskRes] = await Promise.all([
          api.get<CostElement[]>('/api/v1/cost-elements/', { params: { project_id: selectedProject!.id, period_id: period!.id } }),
          api.get<RiskSummary[]>('/api/v1/risks/', { params: { project_id: selectedProject!.id, period_id: period!.id } }),
        ])
        if (cancelled) return
        setElements(costRes.data)
        setRisks(riskRes.data)
      } catch {
        if (!cancelled) setError('Failed to load cost plan')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => { cancelled = true }
  }, [selectedProject, period])

  if (!selectedProject) return null

  const refreshElements = async () => {
    if (!period) return
    const { data } = await api.get<CostElement[]>('/api/v1/cost-elements/', {
      params: { project_id: selectedProject.id, period_id: period.id },
    })
    setElements(data)
  }

  const handleCreate = async (values: CostFormValues) => {
    if (!period) return
    await api.post('/api/v1/cost-elements/', {
      ...toCostElementPayload(values),
      project_id: selectedProject.id,
      period_id: period.id,
    })
    setFormOpen(false)
    await refreshElements()
  }

  const handleUpdate = async (values: CostFormValues) => {
    if (!editingElement) return
    await api.patch(`/api/v1/cost-elements/${editingElement.id}`, toCostElementPayload(values))
    setEditingElement(null)
    await refreshElements()
  }

  const handleDelete = async (el: CostElement) => {
    if (!window.confirm(`Delete cost element "${el.description}"? This cannot be undone.`)) return
    await api.delete(`/api/v1/cost-elements/${el.id}`)
    await refreshElements()
  }

  const candidatesFor = (el: CostElement): LinkCandidate[] => [
    ...elements.filter(e => e.id !== el.id).map(e => ({ id: e.id, type: 'cost_element' as const, label: `${e.code}: ${e.description}` })),
    ...risks.map(r => ({ id: r.id, type: 'risk' as const, label: `${r.code}: ${r.title}` })),
  ]

  if (loading || periodLoading) {
    return <div className="p-8 text-sm text-gray-400">Loading cost plan…</div>
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-2xl font-bold text-gray-900">Cost Plan</h1>
        {period && (
          <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600 font-medium">
            {period.period_label} · {period.freeze_status}
          </span>
        )}
      </div>
      <p className="text-gray-500 text-sm mb-6">
        Cost elements for {selectedProject.name}. Percentage elements (Prelims, Contingency, etc.) compute automatically from the fixed subtotal.
      </p>

      {(error || periodError) && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">{error ?? periodError}</div>
      )}

      {formOpen && (
        <CostForm costElement={null} onCancel={() => setFormOpen(false)} onSubmit={handleCreate} />
      )}
      {editingElement && (
        <CostForm costElement={editingElement} onCancel={() => setEditingElement(null)} onSubmit={handleUpdate} />
      )}

      {!formOpen && !editingElement && (
        <button
          onClick={() => setFormOpen(true)}
          className="mb-4 text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          + New cost element
        </button>
      )}

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200 text-left text-xs text-gray-500 font-medium uppercase tracking-wide">
              <th className="px-4 py-2.5">Code</th>
              <th className="px-4 py-2.5">Description</th>
              <th className="px-4 py-2.5">Group</th>
              <th className="px-4 py-2.5">Type</th>
              <th className="px-4 py-2.5">Budget</th>
              <th className="px-4 py-2.5">Forecast</th>
              <th className="px-4 py-2.5">Actuals</th>
              <th className="px-4 py-2.5">CPI</th>
              <th className="px-4 py-2.5">SPI</th>
              <th className="px-4 py-2.5"></th>
            </tr>
          </thead>
          <tbody>
            {elements.map(el => {
              const isPct = el.element_type === 'percentage'
              const budget = isPct ? el.computed_budget : el.budget
              const forecast = isPct ? el.computed_forecast : el.forecast
              const actuals = isPct ? el.computed_actuals : el.actuals
              return (
                <Fragment key={el.id}>
                  <tr className="border-b border-gray-100 last:border-0 hover:bg-gray-50">
                    <td className="px-4 py-2.5 text-gray-500 font-mono text-xs">{el.code}</td>
                    <td className="px-4 py-2.5">
                      <button
                        onClick={() => setExpandedId(expandedId === el.id ? null : el.id)}
                        className="text-left font-medium text-gray-900 hover:text-blue-600"
                      >
                        {el.description}
                      </button>
                    </td>
                    <td className="px-4 py-2.5 text-gray-600">{el.element_group ?? '—'}</td>
                    <td className="px-4 py-2.5">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${isPct ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'}`}>
                        {isPct ? `${el.rate ? Math.round(Number(el.rate) * 100) : 0}%` : 'fixed'}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-gray-600">{formatCurrency(budget)}</td>
                    <td className="px-4 py-2.5 text-gray-600">{formatCurrency(forecast)}</td>
                    <td className="px-4 py-2.5 text-gray-600">{formatCurrency(actuals)}</td>
                    <td className="px-4 py-2.5 text-gray-600">{el.cpi ?? '—'}</td>
                    <td className="px-4 py-2.5 text-gray-600">{el.spi ?? '—'}</td>
                    <td className="px-4 py-2.5 text-right whitespace-nowrap">
                      <button onClick={() => setEditingElement(el)} className="text-xs text-blue-600 hover:text-blue-700 mr-3">
                        Edit
                      </button>
                      <button onClick={() => handleDelete(el)} className="text-xs text-gray-400 hover:text-red-600">
                        Delete
                      </button>
                    </td>
                  </tr>
                  {expandedId === el.id && (
                    <tr>
                      <td colSpan={10} className="p-0">
                        <RecordLinks recordType="cost_element" recordId={el.id} candidates={candidatesFor(el)} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              )
            })}

            {elements.length === 0 && (
              <tr>
                <td colSpan={10} className="px-4 py-10 text-center text-gray-400 text-sm">
                  No cost elements yet for this period. Add the first one above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
