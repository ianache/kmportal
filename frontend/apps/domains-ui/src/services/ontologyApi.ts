import { createLazyApiClient } from 'shell/microFrontendApi'
import type {
  ConceptCreatePayload,
  Diagram,
  DiagramCreatePayload,
  DiagramListResponse,
  DiagramUpdatePayload,
  OntologyConcept,
  OntologyData,
  OntologyImportResult,
  OntologyProperty,
  PropertyCreatePayload,
  PropertyUpdatePayload,
  OntologyBatchPayload,
  OntologyBatchResponse,
} from '../types/ontology'

const apiClient = createLazyApiClient()

class OntologyApiClient {
  async getOntology(domainId: string): Promise<OntologyData> {
    const r = await apiClient.get<OntologyData>(`/v1/domains/${domainId}/ontology`)
    if (r.error) throw new Error(r.error.message)
    return r.data!
  }

  async createConcept(domainId: string, payload: ConceptCreatePayload): Promise<OntologyConcept> {
    const r = await apiClient.post<OntologyConcept>(`/v1/domains/${domainId}/ontology/concepts`, payload)
    if (r.error) throw new Error(r.error.message)
    return r.data!
  }

  async updateConcept(domainId: string, conceptId: string, payload: Partial<ConceptCreatePayload>): Promise<OntologyConcept> {
    const r = await apiClient.put<OntologyConcept>(`/v1/domains/${domainId}/ontology/concepts/${conceptId}`, payload)
    if (r.error) throw new Error(r.error.message)
    return r.data!
  }

  async deleteConcept(domainId: string, conceptId: string): Promise<void> {
    const r = await apiClient.delete(`/v1/domains/${domainId}/ontology/concepts/${conceptId}`)
    if (r.error) throw new Error(r.error.message)
  }

  async createProperty(domainId: string, payload: PropertyCreatePayload): Promise<OntologyProperty> {
    const r = await apiClient.post<OntologyProperty>(`/v1/domains/${domainId}/ontology/properties`, payload)
    if (r.error) throw new Error(r.error.message)
    return r.data!
  }

  async updateProperty(domainId: string, propertyId: string, payload: PropertyUpdatePayload): Promise<OntologyProperty> {
    const r = await apiClient.put<OntologyProperty>(`/v1/domains/${domainId}/ontology/properties/${propertyId}`, payload)
    if (r.error) throw new Error(r.error.message)
    return r.data!
  }

  async deleteProperty(domainId: string, propertyId: string): Promise<void> {
    const r = await apiClient.delete(`/v1/domains/${domainId}/ontology/properties/${propertyId}`)
    if (r.error) throw new Error(r.error.message)
  }

  exportOntology(domainId: string, format: 'owl' | 'ttl' = 'owl'): void {
    const ext = format === 'ttl' ? 'ttl' : 'owl'
    const url = `/api/v1/domains/${domainId}/ontology/export?format=${format}`
    const a = document.createElement('a')
    a.href = url
    a.download = `ontology_${domainId}.${ext}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  async importOntology(domainId: string, file: File, mode: 'merge' | 'replace' = 'merge'): Promise<OntologyImportResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('mode', mode)
    const res = await fetch(`/api/v1/domains/${domainId}/ontology/import`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    })
    if (!res.ok) {
      const detail = await res.text().catch(() => res.statusText)
      throw new Error(detail)
    }
    return res.json() as Promise<OntologyImportResult>
  }

  async listDiagrams(domainId: string): Promise<DiagramListResponse> {
    const r = await apiClient.get<DiagramListResponse>(`/v1/domains/${domainId}/diagrams`)
    if (r.error) throw new Error(r.error.message)
    return r.data!
  }

  async createDiagram(domainId: string, payload: DiagramCreatePayload): Promise<Diagram> {
    const r = await apiClient.post<Diagram>(`/v1/domains/${domainId}/diagrams`, payload)
    if (r.error) throw new Error(r.error.message)
    return r.data!
  }

  async getDiagram(domainId: string, diagramId: string): Promise<Diagram> {
    const r = await apiClient.get<Diagram>(`/v1/domains/${domainId}/diagrams/${diagramId}`)
    if (r.error) throw new Error(r.error.message)
    return r.data!
  }

  async saveDiagram(domainId: string, diagramId: string, payload: DiagramUpdatePayload): Promise<Diagram> {
    const r = await apiClient.put<Diagram>(`/v1/domains/${domainId}/diagrams/${diagramId}`, payload)
    if (r.error) throw new Error(r.error.message)
    return r.data!
  }

  async deleteDiagram(domainId: string, diagramId: string): Promise<void> {
    const r = await apiClient.delete(`/v1/domains/${domainId}/diagrams/${diagramId}`)
    if (r.error) throw new Error(r.error.message)
  }

  async saveOntologyBatch(domainId: string, payload: OntologyBatchPayload): Promise<OntologyBatchResponse> {
    const r = await apiClient.post<OntologyBatchResponse>(`/v1/domains/${domainId}/ontology/batch`, payload)
    if (r.error) throw new Error(r.error.message)
    return r.data!
  }
}

export const ontologyApi = new OntologyApiClient()
export default ontologyApi
