import { createLazyApiClient } from 'shell/microFrontendApi'
import type {
  ConceptCreatePayload,
  Diagram,
  DiagramCreatePayload,
  DiagramListResponse,
  DiagramUpdatePayload,
  OntologyConcept,
  OntologyData,
  OntologyProperty,
  PropertyCreatePayload,
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

  async deleteProperty(domainId: string, propertyId: string): Promise<void> {
    const r = await apiClient.delete(`/v1/domains/${domainId}/ontology/properties/${propertyId}`)
    if (r.error) throw new Error(r.error.message)
  }

  async exportOntology(domainId: string): Promise<void> {
    // Trigger file download via direct link
    const url = `/api/v1/domains/${domainId}/ontology/export`
    const a = document.createElement('a')
    a.href = url
    a.download = `ontology_${domainId}.owl`
    a.click()
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
}

export const ontologyApi = new OntologyApiClient()
export default ontologyApi
