import { create } from 'zustand';

interface DateRange {
  from: string;
  to: string;
}

interface WorkspaceState {
  currentWorkspaceId: string | null;
  currentProjectId: string | null;
  dateRange: DateRange;
  selectedModels: string[];
  setWorkspace: (id: string) => void;
  setProject: (id: string) => void;
  setDateRange: (range: DateRange) => void;
  toggleModel: (model: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  currentWorkspaceId: null,
  currentProjectId: null,
  dateRange: { from: '7d', to: 'now' },
  selectedModels: [],
  setWorkspace: (id) => set({ currentWorkspaceId: id, currentProjectId: null }),
  setProject: (id) => set({ currentProjectId: id }),
  setDateRange: (range) => set({ dateRange: range }),
  toggleModel: (model) => set((state) => ({
    selectedModels: state.selectedModels.includes(model)
      ? state.selectedModels.filter(m => m !== model)
      : [...state.selectedModels, model]
  })),
}));
