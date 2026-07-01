export interface CostElement {
  id: string
  code: string
  project_id: string
  period_id: string
  element_type: 'fixed' | 'percentage'
  rate: string | null
  element_group: string | null
  description: string
  budget: string | null
  forecast: string | null
  actuals: string | null
  variance: string | null
  cpi: string | null
  spi: string | null
  rev_a_baseline: string | null
  cost_per_m2: string | null
  computed_budget: string | null
  computed_forecast: string | null
  computed_actuals: string | null
  created_at: string
  updated_at: string
}

export const ELEMENT_TYPES = ['fixed', 'percentage'] as const
