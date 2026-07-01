export interface Risk {
  id: string
  project_id: string
  period_id: string
  title: string
  category: string | null
  status: string
  probability: string | null
  impact: string | null
  rating: string | null
  emv_cost: string | null
  emv_schedule_days: number | null
  mitigation_status: string | null
  created_at: string
  updated_at: string
}

export interface Period {
  id: string
  project_id: string
  period_label: string
  freeze_status: string
}

export interface RecordLink {
  id: string
  source_type: string
  source_id: string
  target_type: string
  target_id: string
  link_type: string
  note: string | null
  created_at: string
}

export const LINK_TYPES = ['causes', 'impacts', 'mitigates', 'relates_to'] as const

export const RISK_STATUSES = ['open', 'mitigated', 'closed'] as const
