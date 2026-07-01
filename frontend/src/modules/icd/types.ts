export type ItemType = 'issue' | 'change' | 'decision'
export type Severity = 'low' | 'medium' | 'high' | 'critical'

export interface IcdItem {
  id: string
  code: string
  project_id: string
  period_id: string
  item_type: ItemType
  title: string
  status: string
  priority: string | null
  owner: string | null
  raised_date: string | null
  closed_date: string | null
  cost_impact: string | null
  schedule_impact_days: number | null
  decision_maker: string | null
  required_by: string | null
  severity: Severity | null
  created_at: string
  updated_at: string
}

export const ITEM_TYPES: ItemType[] = ['issue', 'change', 'decision']
export const SEVERITIES: Severity[] = ['low', 'medium', 'high', 'critical']
export const ITEM_TYPE_LABELS: Record<ItemType, string> = {
  issue: 'Issue',
  change: 'Change',
  decision: 'Decision',
}

// Status is a free-text string on the backend (no fixed enum), but each item
// type has its own conventional set of values — mirrors the prototype.
export const STATUSES_BY_TYPE: Record<ItemType, string[]> = {
  issue: ['Open', 'In Progress', 'Overdue', 'Closed'],
  change: ['Pending Approval', 'Approved', 'Rejected', 'Implemented'],
  decision: ['Pending', 'Decided'],
}
