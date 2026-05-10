import bffClient from './bffClient'

// ── Types ──────────────────────────────────────────────────────
export interface KbSummary {
  activeOntologies: number
  knowledgeDomains: number
  ingestedDocuments: number
  monthlyQueries: number
}

export type IntelStatus = 'HEALTHY' | 'WARNING' | 'CRITICAL'

export interface IntelStatusResponse {
  overall: IntelStatus
  components: Array<{
    name: string
    status: string
    lastUpdate: string
  }>
}

export type NewsCategory = 'PLATFORM' | 'INFRA' | 'COMPLIANCE' | 'COMMUNITY' | 'CONTENT'

export interface NewsItem {
  id: string
  category: NewsCategory
  date: string
  title: string
  summary: string
  url?: string
}

// ── Mock data (used while endpoints are not ready) ────────────
const MOCK_KB_SUMMARY: KbSummary = {
  activeOntologies: 12,
  knowledgeDomains: 24,
  ingestedDocuments: 15400,
  monthlyQueries: 8200,
}

const MOCK_INTEL_STATUS: IntelStatusResponse = {
  overall: 'HEALTHY',
  components: [
    { name: 'LLM Connector',   status: 'healthy', lastUpdate: new Date().toISOString() },
    { name: 'Vector Database', status: 'healthy', lastUpdate: new Date().toISOString() },
    { name: 'Knowledge Graph', status: 'healthy', lastUpdate: new Date().toISOString() },
    { name: 'Event Bus',       status: 'healthy', lastUpdate: new Date().toISOString() },
    { name: 'BFF',             status: 'healthy', lastUpdate: new Date().toISOString() },
  ],
}

const now = Date.now()
const MOCK_NEWS: NewsItem[] = [
  {
    id: '1',
    category: 'PLATFORM',
    date: new Date(now - 2 * 3_600_000).toISOString(),
    title: 'Neural Semantic Indexing v2 Live',
    summary: 'Enhanced document retrieval accuracy by 34% using multi-modal search.',
    url: 'https://example.com',
  },
  {
    id: '2',
    category: 'INFRA',
    date: new Date(now - 86_400_000).toISOString(),
    title: 'Scheduled Cluster Expansion',
    summary: 'Maintenance and scaling scheduled for Friday, 22:00 UTC.',
  },
  {
    id: '3',
    category: 'COMPLIANCE',
    date: new Date(now - 3 * 86_400_000).toISOString(),
    title: 'SOC-2 Type II Audit Finalized',
    summary: 'Successful security validation completed with zero findings.',
  },
  {
    id: '4',
    category: 'COMMUNITY',
    date: new Date(now + 9 * 86_400_000).toISOString(),
    title: 'Global Research Sync',
    summary: 'Bi-weekly meeting to align European and Asian hubs.',
  },
  {
    id: '5',
    category: 'CONTENT',
    date: new Date(now - 5 * 86_400_000).toISOString(),
    title: 'New Content Available',
    summary: 'Fresh insights and updates added to the knowledge base.',
  },
]

// ── API calls with mock fallback ──────────────────────────────
export async function fetchKbSummary(): Promise<KbSummary> {
  const res = await bffClient.get<KbSummary>('/v1/kb-summary')
  return res.data ?? MOCK_KB_SUMMARY
}

export async function fetchIntelStatus(): Promise<IntelStatusResponse> {
  const res = await bffClient.get<IntelStatusResponse>('/v1/intel-status')
  return res.data ?? MOCK_INTEL_STATUS
}

export async function fetchNews(): Promise<NewsItem[]> {
  const res = await bffClient.get<NewsItem[]>('/v1/news')
  return res.data ?? MOCK_NEWS
}
