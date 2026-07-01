import { useState } from 'react'
import { ELEMENT_TYPES, type CostElement } from './types'

export interface CostFormValues {
  description: string
  element_group: string
  element_type: 'fixed' | 'percentage'
  rate: string
  budget: string
  forecast: string
  actuals: string
  rev_a_baseline: string
  cost_per_m2: string
}

function toFormValues(el: CostElement | null): CostFormValues {
  return {
    description: el?.description ?? '',
    element_group: el?.element_group ?? '',
    element_type: el?.element_type ?? 'fixed',
    rate: el?.rate ?? '',
    budget: el?.budget ?? '',
    forecast: el?.forecast ?? '',
    actuals: el?.actuals ?? '',
    rev_a_baseline: el?.rev_a_baseline ?? '',
    cost_per_m2: el?.cost_per_m2 ?? '',
  }
}

export function toCostElementPayload(values: CostFormValues) {
  const isPercentage = values.element_type === 'percentage'
  return {
    description: values.description.trim(),
    element_group: values.element_group.trim() || null,
    element_type: values.element_type,
    rate: isPercentage ? values.rate : null,
    budget: !isPercentage && values.budget !== '' ? values.budget : null,
    forecast: !isPercentage && values.forecast !== '' ? values.forecast : null,
    actuals: !isPercentage && values.actuals !== '' ? values.actuals : null,
    rev_a_baseline: values.rev_a_baseline === '' ? null : values.rev_a_baseline,
    cost_per_m2: values.cost_per_m2 === '' ? null : values.cost_per_m2,
  }
}

interface CostFormProps {
  costElement: CostElement | null
  onCancel: () => void
  onSubmit: (values: CostFormValues) => Promise<void>
}

const inputClass =
  'w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'
const labelClass = 'block text-xs font-medium text-gray-600 mb-1'

export function CostForm({ costElement, onCancel, onSubmit }: CostFormProps) {
  const [values, setValues] = useState<CostFormValues>(() => toFormValues(costElement))
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const set = <K extends keyof CostFormValues>(key: K, value: CostFormValues[K]) =>
    setValues(prev => ({ ...prev, [key]: value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!values.description.trim()) {
      setError('Description is required')
      return
    }
    if (values.element_type === 'percentage' && values.rate === '') {
      setError('Rate is required for percentage elements')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await onSubmit(values)
    } catch {
      setError('Failed to save cost element')
    } finally {
      setSubmitting(false)
    }
  }

  const isPercentage = values.element_type === 'percentage'

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white border border-gray-200 rounded-lg p-5 space-y-4 mb-6"
    >
      <h2 className="font-medium text-gray-900 text-sm">{costElement ? 'Edit cost element' : 'New cost element'}</h2>

      {error && (
        <div className="p-2 bg-red-50 border border-red-200 rounded-md text-red-700 text-xs">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Description *</label>
          <input
            autoFocus
            type="text"
            value={values.description}
            onChange={e => set('description', e.target.value)}
            className={inputClass}
            placeholder="e.g. Substructure, Prelims"
          />
        </div>
        <div>
          <label className={labelClass}>Group</label>
          <input
            type="text"
            value={values.element_group}
            onChange={e => set('element_group', e.target.value)}
            className={inputClass}
            placeholder="e.g. Structure, On Costs"
          />
        </div>
      </div>

      <div>
        <label className={labelClass}>Type</label>
        <select
          value={values.element_type}
          onChange={e => set('element_type', e.target.value as 'fixed' | 'percentage')}
          className={inputClass}
        >
          {ELEMENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <p className="text-xs text-gray-400 mt-1">
          Percentage elements (e.g. Prelims, Contingency) compute their value from the sum of all fixed elements — they don't get their own budget figure.
        </p>
      </div>

      {isPercentage ? (
        <div>
          <label className={labelClass}>Rate (e.g. 0.15 = 15%)</label>
          <input
            type="number" min={0} max={10} step={0.001}
            value={values.rate}
            onChange={e => set('rate', e.target.value)}
            className={inputClass}
            placeholder="0.15"
          />
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className={labelClass}>Budget (£)</label>
            <input
              type="number" step="0.01"
              value={values.budget}
              onChange={e => set('budget', e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Forecast (£)</label>
            <input
              type="number" step="0.01"
              value={values.forecast}
              onChange={e => set('forecast', e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Actuals (£)</label>
            <input
              type="number" step="0.01"
              value={values.actuals}
              onChange={e => set('actuals', e.target.value)}
              className={inputClass}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Rev A Baseline (£)</label>
          <input
            type="number" step="0.01"
            value={values.rev_a_baseline}
            onChange={e => set('rev_a_baseline', e.target.value)}
            className={inputClass}
          />
        </div>
        <div>
          <label className={labelClass}>Cost / m²</label>
          <input
            type="number" step="0.01"
            value={values.cost_per_m2}
            onChange={e => set('cost_per_m2', e.target.value)}
            className={inputClass}
          />
        </div>
      </div>

      <div className="flex gap-2 pt-1">
        <button
          type="submit"
          disabled={submitting}
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? 'Saving…' : costElement ? 'Save changes' : 'Create cost element'}
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
