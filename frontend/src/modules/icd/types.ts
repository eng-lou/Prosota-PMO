export type ItemType = 'issue' | 'change' | 'decision'
export type Severity = 'low' | 'medium' | 'high' | 'critical'
export type ChangeType = 'variation' | 'client_instruction' | 'omission'
export type CcbDecision = 'approved' | 'rejected' | 'deferred'
export type QualityImpact = 'high' | 'medium' | 'low' | 'none'

export interface IcdItem {
  id: string
  code: string
  project_id: string
  period_id: string
  item_type: ItemType
  title: string
  description: string | null
  status: string
  priority: string | null
  raised_by: string | null
  owner: string | null
  raised_date: string | null
  due_date: string | null
  closed_date: string | null
  resolution: string | null
  last_reviewed_date: string | null
  cost_impact: string | null
  schedule_impact_days: number | null
  change_type: ChangeType | null
  ccb_decision: CcbDecision | null
  rejection_reason: string | null
  contract_reference: string | null
  cost_claim: string | null
  eot_claim_days: number | null
  quality_impact: QualityImpact | null
  decision_maker: string | null
  required_by: string | null
  if_late_consequence: string | null
  severity: Severity | null
  created_at: string
  updated_at: string
}

export const ITEM_TYPES: ItemType[] = ['issue', 'change', 'decision']
export const SEVERITIES: Severity[] = ['low', 'medium', 'high', 'critical']
export const CHANGE_TYPES: ChangeType[] = ['variation', 'client_instruction', 'omission']
export const CHANGE_TYPE_LABELS: Record<ChangeType, string> = {
  variation: 'Variation',
  client_instruction: 'Client Instruction',
  omission: 'Omission',
}
export const CCB_DECISIONS: CcbDecision[] = ['approved', 'rejected', 'deferred']
export const QUALITY_IMPACTS: QualityImpact[] = ['high', 'medium', 'low', 'none']
export const ITEM_TYPE_LABELS: Record<ItemType, string> = {
  issue: 'Issue',
  change: 'Change',
  decision: 'Decision',
}

// Status is a free-text string on the backend (no fixed enum), but each item
// type has its own conventional set of values — mirrors the prototype. Values
// are lowercase snake_case to match what's actually stored (the backend default
// is "open"); labels below are for display only.
export const STATUSES_BY_TYPE: Record<ItemType, string[]> = {
  issue: ['open', 'in_progress', 'overdue', 'closed'],
  change: ['pending_approval', 'approved', 'rejected', 'implemented'],
  decision: ['pending', 'decided'],
}

export const STATUS_LABELS: Record<string, string> = {
  open: 'Open',
  in_progress: 'In Progress',
  overdue: 'Overdue',
  closed: 'Closed',
  pending_approval: 'Pending Approval',
  approved: 'Approved',
  rejected: 'Rejected',
  implemented: 'Implemented',
  pending: 'Pending',
  decided: 'Decided',
}

export type Priority = 'critical' | 'high' | 'medium' | 'low'
export const PRIORITIES: Priority[] = ['critical', 'high', 'medium', 'low']
export const PRIORITY_LABELS: Record<Priority, string> = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
}

export interface IcdReassessment {
  id: string
  icd_item_id: string
  note: string
  reviewed_at: string
}

export interface IcdActionItem {
  id: string
  code: string
  icd_item_id: string
  description: string
  owner: string | null
  due_date: string | null
  status: string
  pct_complete: number
  created_at: string
  updated_at: string
}

export const ACTION_STATUSES = ['not_started', 'in_progress', 'complete', 'overdue'] as const

export interface IcdComment {
  id: string
  icd_item_id: string
  author_id: string
  author_name: string
  body: string
  created_at: string
  updated_at: string
}

// Fields that, if changed, should prompt for a reassessment note — an item's
// assessment shifting (priority/severity/quality) or a CCB decision being made
// are review events worth logging, mirroring the Risk module's trigger fields.
// Limited to string-typed fields (matching both IcdItem and IcdFormValues as
// strings) so the equality check below doesn't false-positive on number vs
// string comparisons; schedule_impact_days/eot_claim_days are numbers and are
// deliberately excluded.
export const REASSESSMENT_TRIGGER_FIELDS = [
  'status', 'priority', 'severity', 'ccb_decision', 'cost_impact', 'quality_impact',
] as const
