export type CriterionDimension = 'priority' | 'severity' | 'quality_impact'

export interface IcdCriterion {
  id: string
  project_id: string
  dimension: CriterionDimension
  level: number
  label: string
  description: string | null
}
