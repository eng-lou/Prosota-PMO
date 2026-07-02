export interface CostVarianceCriterion {
  id: string
  project_id: string
  level: number
  label: string
  min_pct: string | null
  max_pct: string | null
  description: string | null
}
