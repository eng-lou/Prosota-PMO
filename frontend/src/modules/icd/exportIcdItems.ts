import type { IcdItem } from './types'

const COLUMNS: { key: keyof IcdItem; label: string }[] = [
  { key: 'code', label: 'Code' },
  { key: 'item_type', label: 'Type' },
  { key: 'title', label: 'Title' },
  { key: 'description', label: 'Description' },
  { key: 'status', label: 'Status' },
  { key: 'priority', label: 'Priority' },
  { key: 'raised_by', label: 'Raised By' },
  { key: 'owner', label: 'Owner' },
  { key: 'raised_date', label: 'Raised Date' },
  { key: 'due_date', label: 'Due Date' },
  { key: 'closed_date', label: 'Closed Date' },
  { key: 'last_reviewed_date', label: 'Last Reviewed' },
  { key: 'severity', label: 'Severity (Issue)' },
  { key: 'change_type', label: 'Change Type' },
  { key: 'ccb_decision', label: 'CCB Decision' },
  { key: 'rejection_reason', label: 'Rejection Reason' },
  { key: 'contract_reference', label: 'Contract Reference' },
  { key: 'cost_impact', label: 'Cost Impact (£)' },
  { key: 'schedule_impact_days', label: 'Schedule Impact (days)' },
  { key: 'cost_claim', label: 'Cost Claim (£)' },
  { key: 'eot_claim_days', label: 'EOT Claim (days)' },
  { key: 'quality_impact', label: 'Quality Impact' },
  { key: 'decision_maker', label: 'Decision Maker' },
  { key: 'required_by', label: 'Required By (Decision)' },
  { key: 'if_late_consequence', label: 'Consequence If Late (Decision)' },
  { key: 'resolution', label: 'Resolution' },
]

function csvEscape(value: unknown): string {
  if (value === null || value === undefined) return ''
  const str = String(value)
  if (/[",\n]/.test(str)) return `"${str.replace(/"/g, '""')}"`
  return str
}

export function icdItemsToCsv(items: IcdItem[]): string {
  const header = COLUMNS.map(c => csvEscape(c.label)).join(',')
  const rows = items.map(item => COLUMNS.map(c => csvEscape(item[c.key])).join(','))
  return [header, ...rows].join('\r\n')
}

export function downloadIcdItemsCsv(items: IcdItem[], projectName: string) {
  const csv = icdItemsToCsv(items)
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const date = new Date().toISOString().slice(0, 10)
  link.href = url
  link.download = `${projectName.replace(/[^\w-]+/g, '_')}_icd_tracker_${date}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
