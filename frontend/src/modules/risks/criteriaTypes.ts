export interface RiskProbabilityCriterion {
  id: string
  project_id: string
  level: number
  label: string
  min_probability: string
  max_probability: string
  description: string | null
}

export interface RiskImpactCriterion {
  id: string
  project_id: string
  level: number
  label: string
  min_cost: string | null
  max_cost: string | null
  min_schedule_days: number | null
  max_schedule_days: number | null
  description: string | null
}
