export interface Period {
  id: string
  project_id: string
  period_label: string
  freeze_status: string
}

export type RecordType = 'activity' | 'risk' | 'cost_element' | 'issue' | 'change' | 'decision'

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
