import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { LINK_TYPES, type RecordLink, type Risk } from './types'

interface RiskLinksProps {
  risk: Risk
  allRisks: Risk[]
}

// Shows and manages entries in the shared `record_links` graph (see ARCHITECTURE.md
// Section 4.3) for this risk. Only risk-to-risk links are offered here for now,
// since Activities/Cost Elements/ICD items don't have frontend screens yet to pick from.
export function RiskLinks({ risk, allRisks }: RiskLinksProps) {
  const [links, setLinks] = useState<RecordLink[]>([])
  const [loading, setLoading] = useState(true)
  const [targetId, setTargetId] = useState('')
  const [linkType, setLinkType] = useState<string>(LINK_TYPES[0])
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    setLoading(true)
    api.get<RecordLink[]>('/api/v1/record-links/', {
      params: { record_type: 'risk', record_id: risk.id },
    })
      .then(r => setLinks(r.data))
      .catch(() => setError('Failed to load links'))
      .finally(() => setLoading(false))
  }

  useEffect(load, [risk.id])

  const otherRisks = allRisks.filter(r => r.id !== risk.id)

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!targetId) return
    try {
      await api.post('/api/v1/record-links/', {
        source_type: 'risk',
        source_id: risk.id,
        target_type: 'risk',
        target_id: targetId,
        link_type: linkType,
      })
      setTargetId('')
      load()
    } catch {
      setError('Failed to create link')
    }
  }

  const handleDelete = async (linkId: string) => {
    await api.delete(`/api/v1/record-links/${linkId}`)
    load()
  }

  const titleFor = (id: string) => allRisks.find(r => r.id === id)?.title ?? id

  if (loading) return <p className="text-xs text-gray-400 px-4 py-3">Loading links…</p>

  return (
    <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
      {error && <p className="text-xs text-red-600 mb-2">{error}</p>}

      {links.length === 0 ? (
        <p className="text-xs text-gray-400 mb-3">No linked records yet.</p>
      ) : (
        <ul className="text-xs text-gray-700 space-y-1 mb-3">
          {links.map(link => {
            const isSource = link.source_id === risk.id
            const otherId = isSource ? link.target_id : link.source_id
            return (
              <li key={link.id} className="flex items-center justify-between">
                <span>
                  {isSource ? 'This risk' : titleFor(otherId)}{' '}
                  <span className="font-medium">{link.link_type}</span>{' '}
                  {isSource ? titleFor(otherId) : 'this risk'}
                </span>
                <button onClick={() => handleDelete(link.id)} className="text-gray-400 hover:text-red-600">
                  remove
                </button>
              </li>
            )
          })}
        </ul>
      )}

      <form onSubmit={handleAdd} className="flex items-center gap-2">
        <select
          value={linkType}
          onChange={e => setLinkType(e.target.value)}
          className="border border-gray-300 rounded-md px-2 py-1.5 text-xs"
        >
          {LINK_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <select
          value={targetId}
          onChange={e => setTargetId(e.target.value)}
          className="flex-1 border border-gray-300 rounded-md px-2 py-1.5 text-xs"
        >
          <option value="">Link to another risk…</option>
          {otherRisks.map(r => <option key={r.id} value={r.id}>{r.title}</option>)}
        </select>
        <button
          type="submit"
          disabled={!targetId}
          className="text-xs bg-gray-800 text-white px-3 py-1.5 rounded-md hover:bg-gray-900 disabled:opacity-40"
        >
          Add link
        </button>
      </form>
    </div>
  )
}
