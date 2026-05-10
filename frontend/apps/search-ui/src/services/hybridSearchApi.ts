import { createLazyApiClient } from 'shell/microFrontendApi'
import type { HybridSearchResult } from '../types/semantic'

const apiClient = createLazyApiClient()

export interface HybridSearchParams {
  q: string
  domain_id: string
  limit?: number
}

class HybridSearchApiClient {
  async search(params: HybridSearchParams): Promise<HybridSearchResult[]> {
    const qs = new URLSearchParams({ q: params.q, domain_id: params.domain_id })
    if (params.limit) qs.set('limit', String(params.limit))

    const r = await apiClient.get<HybridSearchResult[]>(`/v1/search/hybrid?${qs}`)
    if (r.error) throw new Error(r.error.message)
    return r.data ?? []
  }
}

export const hybridSearchApi = new HybridSearchApiClient()
export default hybridSearchApi
