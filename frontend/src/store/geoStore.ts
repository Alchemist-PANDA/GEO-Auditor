import { create } from 'zustand';
import {
  fetchVisibility,
  fetchCitations,
  fetchExplorerData,
  fetchRecommendations,
  type VisibilityOverview,
  type Citation,
  type VolumeOverview,
  type Recommendation,
} from '@/lib/api';

interface GeoState {
  visibility: VisibilityOverview | null;
  citations: Citation[];
  explorerData: VolumeOverview | null;
  recommendations: Recommendation[];
  isLoading: boolean;
  error: string | null;

  loadVisibility: (projectId: string) => Promise<void>;
  loadCitations: (projectId: string) => Promise<void>;
  loadExplorer: (keyword: string) => Promise<void>;
  loadRecommendations: (projectId: string) => Promise<void>;
  clearError: () => void;
}

export const useGeoStore = create<GeoState>((set) => ({
  visibility: null,
  citations: [],
  explorerData: null,
  recommendations: [],
  isLoading: false,
  error: null,

  loadVisibility: async (projectId: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await fetchVisibility(projectId);
      set({ visibility: data, isLoading: false });
    } catch (err: unknown) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  loadCitations: async (projectId: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await fetchCitations(projectId);
      set({ citations: data, isLoading: false });
    } catch (err: unknown) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  loadExplorer: async (keyword: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await fetchExplorerData(keyword);
      set({ explorerData: data, isLoading: false });
    } catch (err: unknown) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  loadRecommendations: async (projectId: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await fetchRecommendations(projectId);
      set({ recommendations: data, isLoading: false });
    } catch (err: unknown) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
