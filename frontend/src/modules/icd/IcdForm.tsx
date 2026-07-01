import { useState } from 'react'
import { ITEM_TYPE_LABELS, ITEM_TYPES, SEVERITIES, STATUSES_BY_TYPE, type IcdItem, type ItemType, type Severity } from './types'

export interface IcdFormValues {
  item_type: ItemType
  title: string
  status: string
  priority: string
  owner: string
  raised_date: string
  closed_date: string
  cost_impact: string
  schedule_impact_days: string
  decision_maker: string
  required_by: string
  severity: Severity | ''
}

function toFormValues(item: IcdItem | null): IcdFormValues {
  return {
    item_type: item?.item_type ?? 'issue',
    title: item?.title ?? '',
    status: item?.status ?? 'open',
    priority: item?.priority ?? '',
    owner: item?.owner ?? '',
    raised_date: item?.raised_date ?? '',
    closed_date: item?.closed_date ?? '',
    cost_impact: item?.cost_impact ?? '',
    schedule_impact_days: item?.schedule_impact_days?.toString() ?? '',
    decision_maker: item?.decision_maker ?? '',
    required_by: item?.required_by ?? '',
    severity: item?.severity ?? '',
  }
}

// item_type is a discriminator — the backend rejects type-specific fields (cost_impact,
// decision_maker, severity, ...) that don't match it, and doesn't allow changing it after creation.
export function toIcdPayload(values: IcdFormValues) {
  return {
    title: values.title.trim(),
    status: values.status,
    priority: values.priority.trim() || null,
    owner: values.owner.trim() || null,
    raised_date: values.raised_date || null,
    closed_date: values.closed_date || null,
    cost_impact: values.item_type === 'change' && values.cost_impact !== '' ? values.cost_impact : null,
    schedule_impact_days: values.item_type === 'change' && values.schedule_impact_days !== '' ? Number(values.schedule_impact_days) : null,
    decision_maker: values.item_type === 'decision' ? (values.decision_maker.trim() || null) : null,
    required_by: values.item_type === 'decision' ? (values.required_by || null) : null,
    severity: values.item_type === 'issue' ? (values.severity || null) : null,
  }
}

interface IcdFormProps {
  item: IcdItem | null
  onCancel: () => void
  onSubmit: (values: IcdFormValues) => Promise<void>
}

const inputClass =
  'w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'
const labelClass = 'block text-xs font-medium text-gray-600 mb-1'

export function IcdForm({ item, onCancel, onSubmit }: IcdFormProps) {
  const [values, setValues] = useState<IcdFormValues>(() => toFormValues(item))
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const set = <K extends keyof IcdFormValues>(key: K, value: IcdFormValues[K]) =>
    setValues(prev => ({ ...prev, [key]: value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!values.title.trim()) {
      setError('Title is required')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await onSubmit(values)
    } catch {
      setError('Failed to save item')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white border border-gray-200 rounded-lg p-5 space-y-4 mb-6"
    >
      <h2 className="font-medium text-gray-900 text-sm">{item ? 'Edit item' : 'New issue / change / decision'}</h2>

      {error && (
        <div className="p-2 bg-red-50 border border-red-200 rounded-md text-red-700 text-xs">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Type</label>
          <select
            value={values.item_type}
            onChange={e => {
              const newType = e.target.value as ItemType
              setValues(prev => ({
                ...prev,
                item_type: newType,
                status: STATUSES_BY_TYPE[newType].includes(prev.status) ? prev.status : STATUSES_BY_TYPE[newType][0],
              }))
            }}
            className={inputClass}
            disabled={!!item}
          >
            {ITEM_TYPES.map(t => <option key={t} value={t}>{ITEM_TYPE_LABELS[t]}</option>)}
          </select>
          {item && <p className="text-xs text-gray-400 mt-1">Type can't be changed after creation.</p>}
        </div>
        <div>
          <label className={labelClass}>Status</label>
          <select
            value={values.status}
            onChange={e => set('status', e.target.value)}
            className={inputClass}
          >
            {!STATUSES_BY_TYPE[values.item_type].includes(values.status) && (
              <option value={values.status}>{values.status}</option>
            )}
            {STATUSES_BY_TYPE[values.item_type].map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className={labelClass}>Title *</label>
        <input
          autoFocus
          type="text"
          value={values.title}
          onChange={e => set('title', e.target.value)}
          className={inputClass}
          placeholder="e.g. Underground service clash — 450mm water main"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Priority</label>
          <input
            type="text"
            value={values.priority}
            onChange={e => set('priority', e.target.value)}
            className={inputClass}
            placeholder="Critical, High, Medium, Low"
          />
        </div>
        <div>
          <label className={labelClass}>Owner</label>
          <input
            type="text"
            value={values.owner}
            onChange={e => set('owner', e.target.value)}
            className={inputClass}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Raised date</label>
          <input
            type="date"
            value={values.raised_date}
            onChange={e => set('raised_date', e.target.value)}
            className={inputClass}
          />
        </div>
        <div>
          <label className={labelClass}>Closed date</label>
          <input
            type="date"
            value={values.closed_date}
            onChange={e => set('closed_date', e.target.value)}
            className={inputClass}
          />
        </div>
      </div>

      {values.item_type === 'issue' && (
        <div>
          <label className={labelClass}>Severity</label>
          <select
            value={values.severity}
            onChange={e => set('severity', e.target.value as Severity)}
            className={inputClass}
          >
            <option value="">—</option>
            {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      )}

      {values.item_type === 'change' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Cost impact (£)</label>
            <input
              type="number" step="0.01"
              value={values.cost_impact}
              onChange={e => set('cost_impact', e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Schedule impact (days)</label>
            <input
              type="number" step="1"
              value={values.schedule_impact_days}
              onChange={e => set('schedule_impact_days', e.target.value)}
              className={inputClass}
            />
          </div>
        </div>
      )}

      {values.item_type === 'decision' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Decision maker</label>
            <input
              type="text"
              value={values.decision_maker}
              onChange={e => set('decision_maker', e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Required by</label>
            <input
              type="date"
              value={values.required_by}
              onChange={e => set('required_by', e.target.value)}
              className={inputClass}
            />
          </div>
        </div>
      )}

      <div className="flex gap-2 pt-1">
        <button
          type="submit"
          disabled={submitting}
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? 'Saving…' : item ? 'Save changes' : 'Create item'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="text-gray-500 px-4 py-2 rounded-md text-sm hover:bg-gray-100"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
