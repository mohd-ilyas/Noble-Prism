import { create } from "zustand";

interface CommerceState {
  goalDraft: string;
  selectedWorkflowId: string | null;
  setGoalDraft: (goal: string) => void;
  setSelectedWorkflowId: (workflowId: string | null) => void;
}

export const useCommerceStore = create<CommerceState>((set) => ({
  goalDraft: "Find a sustainable GPU provider for a training burst",
  selectedWorkflowId: null,
  setGoalDraft: (goalDraft) => set({ goalDraft }),
  setSelectedWorkflowId: (selectedWorkflowId) => set({ selectedWorkflowId }),
}));
