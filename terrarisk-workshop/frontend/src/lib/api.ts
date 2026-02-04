// TerraRisk Workshop - API Client
import type { Group, Layer, Municipality, MunicipalityBasic, AdminStats } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Groups
  async createGroup(name: string): Promise<Group> {
    return this.request<Group>('/groups', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }

  async getGroup(id: string): Promise<Group> {
    return this.request<Group>(`/groups/${id}`);
  }

  async listGroups(): Promise<Group[]> {
    return this.request<Group[]>('/groups');
  }

  async joinGroup(id: string): Promise<Group> {
    return this.request<Group>(`/groups/${id}`);
  }

  async purchaseLayer(groupId: string, layerId: string): Promise<Group> {
    return this.request<Group>(`/groups/${groupId}/purchase`, {
      method: 'POST',
      body: JSON.stringify({ layerId }),
    });
  }

  // Layers
  async getLayers(): Promise<Layer[]> {
    return this.request<Layer[]>('/layers');
  }

  async getLayer(id: string): Promise<Layer> {
    return this.request<Layer>(`/layers/${id}`);
  }

  // Municipalities
  async getMunicipalities(): Promise<MunicipalityBasic[]> {
    return this.request<MunicipalityBasic[]>('/municipalities');
  }

  async getMunicipality(code: string): Promise<Municipality> {
    return this.request<Municipality>(`/municipalities/${code}`);
  }

  async searchMunicipalities(query: string): Promise<MunicipalityBasic[]> {
    return this.request<MunicipalityBasic[]>(`/municipalities/search?q=${encodeURIComponent(query)}`);
  }

  // Bivariate
  async generateBivariate(layer1Id: string, layer2Id: string): Promise<{ imageUrl: string }> {
    return this.request<{ imageUrl: string }>('/bivariate', {
      method: 'POST',
      body: JSON.stringify({ layer1Id, layer2Id }),
    });
  }

  // Admin
  async getAdminStats(): Promise<AdminStats> {
    return this.request<AdminStats>('/admin/stats');
  }

  async resetGroupCredits(groupId: string): Promise<Group> {
    return this.request<Group>(`/admin/reset/${groupId}`, {
      method: 'POST',
    });
  }

  async deleteGroup(groupId: string): Promise<void> {
    return this.request<void>(`/admin/groups/${groupId}`, {
      method: 'DELETE',
    });
  }
}

export const api = new ApiClient();
export default api;
