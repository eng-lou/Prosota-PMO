export type RiskType = 'threat' | 'opportunity'

export interface Risk {
  id: string
  code: string
  project_id: string
  period_id: string
  title: string
  category: string | null
  area: string | null
  status: string
  risk_owner: string | null
  cause: string | null
  effect: string | null
  rationale: string | null
  risk_type: RiskType
  response_strategy: string | null
  probability: string | null
  impact: string | null
  probability_residual: string | null
  impact_residual: string | null
  rating_narrative: string | null
  cost_min: string | null
  cost_most_likely: string | null
  cost_max: string | null
  schedule_min_days: number | null
  schedule_most_likely_days: number | null
  schedule_max_days: number | null
  rating: string | null
  rating_residual: string | null
  emv_cost: string | null
  emv_schedule_days: string | null
  mitigation_status: string | null
  contingency_plan: string | null
  fallback_plan: string | null
  created_at: string
  updated_at: string
}

export interface RiskMitigationAction {
  id: string
  code: string
  risk_id: string
  description: string
  owner: string | null
  due_date: string | null
  status: string
  pct_complete: number
  created_at: string
  updated_at: string
}

export const ACTION_STATUSES = ['not_started', 'in_progress', 'complete', 'overdue'] as const

export const RISK_STATUSES = ['open', 'mitigated', 'closed'] as const

// Per Rita Mulcahy Ch. 12: threats and opportunities have distinct response
// strategies, sharing only Escalate and Accept.
export const RESPONSE_STRATEGIES_BY_TYPE: Record<RiskType, string[]> = {
  threat: ['avoid', 'mitigate', 'transfer', 'escalate', 'accept'],
  opportunity: ['exploit', 'enhance', 'share', 'escalate', 'accept'],
}
