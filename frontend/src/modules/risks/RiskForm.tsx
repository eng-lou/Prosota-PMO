import { useState } from 'react'
import { RISK_STATUSES, type Risk } from './types'

export interface RiskFormValues {
  title: string
  category: string
  status: string
  probability: string
  impact: string
  rating: string
  emv_cost: string
  emv_schedule_days: string
  mitigation_status: string
}

function toFormValues(risk: Risk | null): RiskFormValues {
  return {
    title: risk?.title ?? '',
    category: risk?.category ?? '',
    status: risk?.status ?? 'open',
    probability: risk?.probability ?? '',
    impact: risk?.impact ?? '',
    rating: risk?.rating ?? '',
    emv_cost: risk?.emv_cost ?? '',
    emv_schedule_days: risk?.emv_schedule_days?.toString() ?? '',
    mitigation_status: risk?.mitigation_status ?? '',
  }
}

// Backend stores probability/impact/rating as a 0–1 fraction (e.g. 0.3 = 30%).
export function toRiskPayload(values: RiskFormValues) {
  return {
    title: values.title.trim(),
    category: values.category.trim() || null,
    status: values.status,
    probability: values.probability === '' ? null : values.probability,
    impact: values.impact === '' ? null : values.impact,
    rating: values.rating === '' ? null : values.rating,
    emv_cost: values.emv_cost === '' ? null : values.emv_cost,
    emv_schedule_days: values.emv_schedule_days === '' ? null : Number(values.emv_schedule_days),
    mitigation_status: values.mitigation_status.trim() || null,
  }
}

interface RiskFormProps {
  risk: Risk | null
  onCancel: () => void
  onSubmit: (values: RiskFormValues) => Promise<void>
}

const inputClass =
  'w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'
const labelClass = 'block text-xs font-medium text-gray-600 mb-1'

export function RiskForm({ risk, onCancel, onSubmit }: RiskFormProps) {
  const [values, setValues] = useState<RiskFormValues>(() => toFormValues(risk))
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const set = <K extends keyof RiskFormValues>(key: K, value: RiskFormValues[K]) =>
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
      setError('Failed to save risk')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white border border-gray-200 rounded-lg p-5 space-y-4 mb-6"
    >
      <h2 className="font-medium text-gray-900 text-sm">{risk ? 'Edit risk' : 'New risk'}</h2>

      {error && (
        <div className="p-2 bg-red-50 border border-red-200 rounded-md text-red-700 text-xs">
          {error}
        </div>
      )}

      <div>
        <label className={labelClass}>Title *</label>
        <input
          autoFocus
          type="text"
          value={values.title}
          onChange={e => set('title', e.target.value)}
          className={inputClass}
          placeholder="e.g. Unforeseen ground conditions"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Category</label>
          <input
            type="text"
            value={values.category}
            onChange={e => set('category', e.target.value)}
            className={inputClass}
            placeholder="e.g. Technical, Commercial, Site"
          />
        </div>
        <div>
          <label className={labelClass}>Status</label>
          <select value={values.status} onChange={e => set('status', e.target.value)} className={inputClass}>
            {RISK_STATUSES.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className={labelClass}>Probability (0–1)</label>
          <input
            type="number" min={0} max={1} step={0.01}
            value={values.probability}
            onChange={e => set('probability', e.target.value)}
            className={inputClass}
            placeholder="0.30"
          />
        </div>
        <div>
          <label className={labelClass}>Impact (0–1)</label>
          <input
            type="number" min={0} max={1} step={0.01}
            value={values.impact}
            onChange={e => set('impact', e.target.value)}
            className={inputClass}
            placeholder="0.80"
          />
        </div>
        <div>
          <label className={labelClass}>Rating (0–1)</label>
          <input
            type="number" min={0} max={1} step={0.01}
            value={values.rating}
            onChange={e => set('rating', e.target.value)}
            className={inputClass}
            placeholder="0.24"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>EMV Cost (£)</label>
          <input
            type="number" step="0.01"
            value={values.emv_cost}
            onChange={e => set('emv_cost', e.target.value)}
            className={inputClass}
            placeholder="175000"
          />
        </div>
        <div>
          <label className={labelClass}>EMV Schedule (days)</label>
          <input
            type="number" step="1"
            value={values.emv_schedule_days}
            onChange={e => set('emv_schedule_days', e.target.value)}
            className={inputClass}
            placeholder="15"
          />
        </div>
      </div>

      <div>
        <label className={labelClass}>Mitigation status</label>
        <input
          type="text"
          value={values.mitigation_status}
          onChange={e => set('mitigation_status', e.target.value)}
          className={inputClass}
          placeholder="e.g. Mitigation plan agreed with subcontractor"
        />
      </div>

      <div className="flex gap-2 pt-1">
        <button
          type="submit"
          disabled={submitting}
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? 'Saving…' : risk ? 'Save changes' : 'Create risk'}
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
