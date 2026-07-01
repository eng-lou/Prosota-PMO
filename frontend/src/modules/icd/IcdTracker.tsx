import { Fragment, useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { useProject } from '@/lib/ProjectContext'
import { useActivePeriod } from '@/lib/usePeriod'
import { RecordLinks, type LinkCandidate } from '@/components/RecordLinks'
import { IcdForm, toIcdPayload, type IcdFormValues } from './IcdForm'
import { ITEM_TYPE_LABELS, ITEM_TYPES, type IcdItem, type ItemType } from './types'

interface RiskSummary { id: string; code: string; title: string }
interface CostElementSummary { id: string; code: string; description: string }

const TYPE_STYLES: Record<ItemType, string> = {
  issue: 'bg-red-100 text-red-700',
  change: 'bg-amber-100 text-amber-700',
  decision: 'bg-blue-100 text-blue-700',
}

function formatCurrency(value: string | null) {
  if (value === null) return '—'
  return `£${Number(value).toLocaleString()}`
}

export function IcdTracker() {
  const { selectedProject } = useProject()
  const { period, loading: periodLoading, error: periodError } = useActivePeriod(selectedProject?.id)
  const [items, setItems] = useState<IcdItem[]>([])
  const [risks, setRisks] = useState<RiskSummary[]>([])
  const [costElements, setCostElements] = useState<CostElementSummary[]>([])
  const [typeFilter, setTypeFilter] = useState<ItemType | 'all'>('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<IcdItem | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  useEffect(() => {
    if (!selectedProject || !period) return
    let cancelled = false

    async function load() {
      try {
        setLoading(true)
        const [itemRes, riskRes, costRes] = await Promise.all([
          api.get<IcdItem[]>('/api/v1/icd-items/', { params: { project_id: selectedProject!.id, period_id: period!.id } }),
          api.get<RiskSummary[]>('/api/v1/risks/', { params: { project_id: selectedProject!.id, period_id: period!.id } }),
          api.get<CostElementSummary[]>('/api/v1/cost-elements/', { params: { project_id: selectedProject!.id, period_id: period!.id } }),
        ])
        if (cancelled) return
        setItems(itemRes.data)
        setRisks(riskRes.data)
        setCostElements(costRes.data)
      } catch {
        if (!cancelled) setError('Failed to load ICD tracker')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => { cancelled = true }
  }, [selectedProject, period])

  if (!selectedProject) return null

  const refreshItems = async () => {
    if (!period) return
    const { data } = await api.get<IcdItem[]>('/api/v1/icd-items/', {
      params: { project_id: selectedProject.id, period_id: period.id },
    })
    setItems(data)
  }

  const handleCreate = async (values: IcdFormValues) => {
    if (!period) return
    await api.post('/api/v1/icd-items/', {
      ...toIcdPayload(values),
      item_type: values.item_type,
      project_id: selectedProject.id,
      period_id: period.id,
    })
    setFormOpen(false)
    await refreshItems()
  }

  const handleUpdate = async (values: IcdFormValues) => {
    if (!editingItem) return
    await api.patch(`/api/v1/icd-items/${editingItem.id}`, toIcdPayload(values))
    setEditingItem(null)
    await refreshItems()
  }

  const handleDelete = async (item: IcdItem) => {
    if (!window.confirm(`Delete "${item.title}"? This cannot be undone.`)) return
    await api.delete(`/api/v1/icd-items/${item.id}`)
    await refreshItems()
  }

  const candidatesFor = (item: IcdItem): LinkCandidate[] => [
    ...items.filter(i => i.id !== item.id).map(i => ({ id: i.id, type: i.item_type, label: `${i.code}: ${i.title}` })),
    ...risks.map(r => ({ id: r.id, type: 'risk' as const, label: `${r.code}: ${r.title}` })),
    ...costElements.map(c => ({ id: c.id, type: 'cost_element' as const, label: `${c.code}: ${c.description}` })),
  ]

  const visibleItems = typeFilter === 'all' ? items : items.filter(i => i.item_type === typeFilter)

  if (loading || periodLoading) {
    return <div className="p-8 text-sm text-gray-400">Loading ICD tracker…</div>
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-2xl font-bold text-gray-900">ICD Tracker</h1>
        {period && (
          <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600 font-medium">
            {period.period_label} · {period.freeze_status}
          </span>
        )}
      </div>
      <p className="text-gray-500 text-sm mb-6">Issues, changes, and decisions for {selectedProject.name}.</p>

      {(error || periodError) && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">{error ?? periodError}</div>
      )}

      <div className="flex gap-2 mb-4">
        {(['all', ...ITEM_TYPES] as const).map(t => (
          <button
            key={t}
            onClick={() => setTypeFilter(t)}
            className={`text-xs px-3 py-1.5 rounded-full font-medium ${
              typeFilter === t ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {t === 'all' ? 'All' : ITEM_TYPE_LABELS[t]}
          </button>
        ))}
      </div>

      {formOpen && (
        <IcdForm item={null} onCancel={() => setFormOpen(false)} onSubmit={handleCreate} />
      )}
      {editingItem && (
        <IcdForm item={editingItem} onCancel={() => setEditingItem(null)} onSubmit={handleUpdate} />
      )}

      {!formOpen && !editingItem && (
        <button
          onClick={() => setFormOpen(true)}
          className="mb-4 text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          + New issue / change / decision
        </button>
      )}

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200 text-left text-xs text-gray-500 font-medium uppercase tracking-wide">
              <th className="px-4 py-2.5">Code</th>
              <th className="px-4 py-2.5">Title</th>
              <th className="px-4 py-2.5">Type</th>
              <th className="px-4 py-2.5">Status</th>
              <th className="px-4 py-2.5">Priority</th>
              <th className="px-4 py-2.5">Owner</th>
              <th className="px-4 py-2.5">Impact</th>
              <th className="px-4 py-2.5"></th>
            </tr>
          </thead>
          <tbody>
            {visibleItems.map(item => (
              <Fragment key={item.id}>
                <tr className="border-b border-gray-100 last:border-0 hover:bg-gray-50">
                  <td className="px-4 py-2.5 text-gray-500 font-mono text-xs">{item.code}</td>
                  <td className="px-4 py-2.5">
                    <button
                      onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}
                      className="text-left font-medium text-gray-900 hover:text-blue-600"
                    >
                      {item.title}
                    </button>
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TYPE_STYLES[item.item_type]}`}>
                      {ITEM_TYPE_LABELS[item.item_type]}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-gray-600">{item.status}</td>
                  <td className="px-4 py-2.5 text-gray-600">{item.priority ?? '—'}</td>
                  <td className="px-4 py-2.5 text-gray-600">{item.owner ?? '—'}</td>
                  <td className="px-4 py-2.5 text-gray-600">
                    {item.item_type === 'change' && (
                      <>{formatCurrency(item.cost_impact)}{item.schedule_impact_days ? ` · +${item.schedule_impact_days}d` : ''}</>
                    )}
                    {item.item_type === 'issue' && (item.severity ?? '—')}
                    {item.item_type === 'decision' && (item.required_by ? `by ${item.required_by}` : '—')}
                  </td>
                  <td className="px-4 py-2.5 text-right whitespace-nowrap">
                    <button onClick={() => setEditingItem(item)} className="text-xs text-blue-600 hover:text-blue-700 mr-3">
                      Edit
                    </button>
                    <button onClick={() => handleDelete(item)} className="text-xs text-gray-400 hover:text-red-600">
                      Delete
                    </button>
                  </td>
                </tr>
                {expandedId === item.id && (
                  <tr>
                    <td colSpan={8} className="p-0">
                      <RecordLinks recordType={item.item_type} recordId={item.id} candidates={candidatesFor(item)} />
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}

            {visibleItems.length === 0 && (
              <tr>
                <td colSpan={8} className="px-4 py-10 text-center text-gray-400 text-sm">
                  No items yet{typeFilter !== 'all' ? ` of type "${ITEM_TYPE_LABELS[typeFilter]}"` : ''}. Add the first one above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
