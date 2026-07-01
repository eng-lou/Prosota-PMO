import type { Risk } from './types'

const COLUMNS: { key: keyof Risk; label: string }[] = [
  { key: 'code', label: 'Code' },
  { key: 'title', label: 'Title' },
  { key: 'risk_type', label: 'Type' },
  { key: 'category', label: 'Theme' },
  { key: 'area', label: 'Area' },
  { key: 'status', label: 'Status' },
  { key: 'risk_owner', label: 'Owner' },
  { key: 'probability', label: 'Probability' },
  { key: 'impact', label: 'Impact (qualitative)' },
  { key: 'rating', label: 'Rating (inherent)' },
  { key: 'probability_residual', label: 'Probability (residual)' },
  { key: 'impact_residual', label: 'Impact (residual)' },
  { key: 'rating_residual', label: 'Rating (residual)' },
  { key: 'cost_min', label: 'Cost Min (£)' },
  { key: 'cost_most_likely', label: 'Cost Most Likely (£)' },
  { key: 'cost_max', label: 'Cost Max (£)' },
  { key: 'schedule_min_days', label: 'Schedule Min (days)' },
  { key: 'schedule_most_likely_days', label: 'Schedule Most Likely (days)' },
  { key: 'schedule_max_days', label: 'Schedule Max (days)' },
  { key: 'emv_cost', label: 'EMV Cost (£)' },
  { key: 'emv_schedule_days', label: 'EMV Schedule (days)' },
  { key: 'response_strategy', label: 'Response Strategy' },
  { key: 'date_raised', label: 'Date Raised' },
  { key: 'expected_impact_date', label: 'Expected Impact Date' },
  { key: 'last_reviewed_date', label: 'Last Reviewed' },
  { key: 'date_closed', label: 'Date Closed' },
  { key: 'cause', label: 'Cause' },
  { key: 'effect', label: 'Effect' },
  { key: 'rationale', label: 'Rationale' },
  { key: 'mitigation_status', label: 'Mitigation Status' },
  { key: 'contingency_plan', label: 'Contingency Plan' },
  { key: 'fallback_plan', label: 'Fallback Plan' },
]

function csvEscape(value: unknown): string {
  if (value === null || value === undefined) return ''
  const str = String(value)
  if (/[",\n]/.test(str)) return `"${str.replace(/"/g, '""')}"`
  return str
}

export function risksToCsv(risks: Risk[]): string {
  const header = COLUMNS.map(c => csvEscape(c.label)).join(',')
  const rows = risks.map(risk => COLUMNS.map(c => csvEscape(risk[c.key])).join(','))
  return [header, ...rows].join('\r\n')
}

export function downloadRisksCsv(risks: Risk[], projectName: string) {
  const csv = risksToCsv(risks)
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const date = new Date().toISOString().slice(0, 10)
  link.href = url
  link.download = `${projectName.replace(/[^\w-]+/g, '_')}_risk_register_${date}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
