// GEO Platform API Client
// Typed HTTP client for all backend endpoints

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

function getAuthHeaders(): HeadersInit {
  if (typeof window === 'undefined') return { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: getAuthHeaders(),
    ...options,
  });
  if (!res.ok) {
    const errorText = await res.text().catch(() => 'Unknown error');
    throw new Error(`API Error ${res.status}: ${errorText}`);
  }
  return res.json();
}

// ─── Types ──────────────────────────────────────────────

export interface VisibilityHistoryPoint {
  date: string;
  score: number;
}

export interface RankingEntry {
  rank: number;
  brand: string;
  score: number;
  change: number;
}

export interface VisibilityOverview {
  visibility_score: number;
  weekly_change: number;
  history: VisibilityHistoryPoint[];
  rankings: RankingEntry[];
  share_of_voice: number;
  share_of_voice_breakdown: { name: string; share: number }[];
}

export interface Citation {
  url: string;
  mentions_count: number;
  visibility_gain: number;
  last_observed: string;
  status: string;
}

export interface TopicVariation {
  text: string;
  weight: number;
}

export interface GraphNode {
  id: string;
  parent: string;
}

export interface VolumeOverview {
  total_volume: string;
  frequency_rank: string;
  platforms: Record<string, string>;
  geos: Record<string, string>;
  variations: TopicVariation[];
  graph_nodes: GraphNode[];
}

export interface RecommendationAction {
  id: string;
  action_text: string;
  is_completed: boolean;
  completed_at: string | null;
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  priority: string;
  status: string;
  estimated_visibility_gain: number;
  created_at: string;
  actions: RecommendationAction[];
}

export interface PromptRun {
  id: string;
  model_id: string;
  status: string;
  executed_at: string | null;
  error_message: string | null;
}

export interface PromptWithRuns {
  id: string;
  project_id: string;
  text: string;
  locale: string;
  tags: string[];
  created_at: string;
  prompt_runs: PromptRun[];
}

export interface PromptInput {
  text: string;
  locale?: string;
  tags?: string[];
}

// ─── API Functions ──────────────────────────────────────

export async function fetchVisibility(projectId: string): Promise<VisibilityOverview> {
  return apiFetch<VisibilityOverview>(`/analytics/visibility?project_id=${projectId}`);
}

export async function fetchCitations(projectId: string): Promise<Citation[]> {
  return apiFetch<Citation[]>(`/analytics/citations?project_id=${projectId}`);
}

export async function fetchExplorerData(keyword: string): Promise<VolumeOverview> {
  return apiFetch<VolumeOverview>(`/analytics/explorer?keyword=${encodeURIComponent(keyword)}`);
}

export async function fetchRecommendations(projectId: string): Promise<Recommendation[]> {
  return apiFetch<Recommendation[]>(`/recommendations?project_id=${projectId}`);
}

export async function createPrompts(projectId: string, prompts: PromptInput[]): Promise<any> {
  return apiFetch<any>('/prompts', {
    method: 'POST',
    body: JSON.stringify({ project_id: projectId, prompts }),
  });
}

export async function triggerRun(projectId: string, models: string[]): Promise<{ message: string }> {
  return apiFetch<{ message: string }>('/prompts/run', {
    method: 'POST',
    body: JSON.stringify({ project_id: projectId, models }),
  });
}

export async function fetchPrompts(projectId: string): Promise<PromptWithRuns[]> {
  return apiFetch<PromptWithRuns[]>(`/prompts?project_id=${projectId}`);
}

export async function generateRecommendations(projectId: string): Promise<any> {
  return apiFetch<any>(`/recommendations/generate?project_id=${projectId}`, {
    method: 'POST',
  });
}

export async function generateAdvancedRecommendations(projectId: string): Promise<any> {
  return apiFetch<any>(`/recommendations/advanced?project_id=${projectId}`, {
    method: 'POST',
  });
}

export async function updateRecommendationStatus(recId: string, status: string): Promise<any> {
  return apiFetch<any>(`/recommendations/${recId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

export async function checkHealth(): Promise<{ status: string; service: string }> {
  return apiFetch('/health');
}

export async function requestAudit(url: string, email: string): Promise<{ audit_id: string; status: string; message: string }> {
  return apiFetch('/audit/request', {
    method: 'POST',
    body: JSON.stringify({ url, email })
  });
}

export async function getAudit(auditId: string): Promise<any> {
  return apiFetch(`/audit/${auditId}`);
}

export async function getAudits(): Promise<any[]> {
  return apiFetch('/audit');
}

export async function login(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
  return apiFetch('/workspaces/token', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export interface Workspace {
  id: string;
  organization_id: string;
  name: string;
  tier: string;
  prompt_limit: number;
  prompts_used: number;
}

export interface Project {
  id: string;
  workspace_id: string;
  name: string;
}

export interface Brand {
  id: string;
  project_id: string;
  name: string;
  domain: string;
}

export interface Competitor {
  id: string;
  brand_id: string;
  name: string;
  domain: string;
}

export async function fetchWorkspaces(): Promise<Workspace[]> {
  return apiFetch<Workspace[]>('/workspaces');
}

export async function fetchProjects(workspaceId: string): Promise<Project[]> {
  return apiFetch<Project[]>(`/workspaces/projects?workspace_id=${workspaceId}`);
}

export async function fetchBrands(projectId: string): Promise<Brand[]> {
  return apiFetch<Brand[]>(`/workspaces/projects/${projectId}/brands`);
}

export async function fetchCompetitors(brandId: string): Promise<Competitor[]> {
  return apiFetch<Competitor[]>(`/workspaces/brands/${brandId}/competitors`);
}

export async function createWorkspace(name: string, tier = 'pitch'): Promise<Workspace> {
  return apiFetch<Workspace>('/workspaces', {
    method: 'POST',
    body: JSON.stringify({ name, tier }),
  });
}

export async function createProject(name: string, workspaceId: string): Promise<Project> {
  return apiFetch<Project>('/workspaces/projects', {
    method: 'POST',
    body: JSON.stringify({ name, workspace_id: workspaceId }),
  });
}

export async function createBrand(name: string, domain: string, projectId: string): Promise<Brand> {
  return apiFetch<Brand>('/workspaces/brands', {
    method: 'POST',
    body: JSON.stringify({ name, domain, project_id: projectId }),
  });
}

export async function createCompetitor(name: string, domain: string, brandId: string): Promise<Competitor> {
  return apiFetch<Competitor>('/workspaces/competitors', {
    method: 'POST',
    body: JSON.stringify({ name, domain, brand_id: brandId }),
  });
}

export async function register(email: string, password: string, fullName: string, organizationName: string): Promise<{ message: string }> {
  return apiFetch<{ message: string }>('/workspaces/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name: fullName, organization_name: organizationName }),
  });
}


