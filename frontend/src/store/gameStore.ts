import { create } from 'zustand';
import type { AILevel } from '../config/demonstrators';
import type { Board, TopMove, ChatMessage, GameHistoryEntry, EvaluationState } from '../types/chessTypes';

export type GameMode = 'human-vs-ai' | 'ai-vs-ai';

type ReasoningState = {
  white: string;
  black: string;
  loadingWhite: boolean;
  loadingBlack: boolean;
};

type BranchState = {
  active: boolean;
  branchId: string | null;
  board: Board;
  progress: number;
  maxHalfMoves: number;
  rank: number;
};

type HintMove = { from: string; to: string } | null;

const HISTORY_KEY = 'chessalgos-history';

function loadHistoryFromStorage(): GameHistoryEntry[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistoryToStorage(history: GameHistoryEntry[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

interface GameStore {
  // Session
  sessionActive: boolean;
  mode: GameMode;

  // Demonstrators
  whiteDemonstrator: AILevel;
  blackDemonstrator: AILevel;

  // Theme
  theme: 'dark' | 'light';

  // Reasoning
  reasoning: ReasoningState;

  // Branch
  branch: BranchState;
  hintMove: HintMove;
  branchSuggestions: TopMove[];

  // AI Companion Chat
  chatMessages: ChatMessage[];

  // Evaluation (accuracy meter)
  evaluation: EvaluationState;

  // Game History
  gameHistory: GameHistoryEntry[];

  // Actions — session
  startSession: () => void;
  endSessionStore: () => void;

  // Actions — mode & demonstrators
  setMode: (mode: GameMode) => void;
  setWhiteDemonstrator: (level: AILevel) => void;
  setBlackDemonstrator: (level: AILevel) => void;
  setTheme: (theme: 'dark' | 'light') => void;

  // Actions — reasoning
  setReasoning: (side: 'white' | 'black', text: string) => void;
  setReasoningLoading: (side: 'white' | 'black', loading: boolean) => void;

  // Actions — branch
  setBranch: (partial: Partial<BranchState>) => void;
  resetBranch: () => void;
  setHintMove: (move: HintMove) => void;
  setBranchSuggestions: (suggestions: TopMove[]) => void;

  // Actions — chat
  addChatMessage: (msg: ChatMessage) => void;
  clearChat: () => void;

  // Actions — evaluation
  updateEvaluation: (eval_: EvaluationState) => void;

  // Actions — history
  saveToHistory: (entry: GameHistoryEntry) => void;
  clearHistory: () => void;
  loadHistory: () => void;
}

const initialBranch: BranchState = {
  active: false,
  branchId: null,
  board: [],
  progress: 0,
  maxHalfMoves: 5,
  rank: 1,
};

const initialEvaluation: EvaluationState = {
  evaluation: 0,
  white_score: 50,
  black_score: 50,
};

export const useGameStore = create<GameStore>((set, get) => ({
  sessionActive: false,
  mode: 'human-vs-ai',
  whiteDemonstrator: 5,
  blackDemonstrator: 4,
  theme: 'dark',
  reasoning: {
    white: '',
    black: '',
    loadingWhite: false,
    loadingBlack: false,
  },
  branch: initialBranch,
  hintMove: null,
  branchSuggestions: [],
  chatMessages: [],
  evaluation: initialEvaluation,
  gameHistory: loadHistoryFromStorage(),

  // Session
  startSession: () => set({ sessionActive: true, chatMessages: [], evaluation: initialEvaluation }),
  endSessionStore: () => set({
    sessionActive: false,
    chatMessages: [],
    evaluation: initialEvaluation,
    branch: initialBranch,
    hintMove: null,
    reasoning: { white: '', black: '', loadingWhite: false, loadingBlack: false },
  }),

  // Mode & Demonstrators
  setMode: (mode) => set({ mode }),
  setWhiteDemonstrator: (level) => set({ whiteDemonstrator: level }),
  setBlackDemonstrator: (level) => set({ blackDemonstrator: level }),
  setTheme: (theme) => set({ theme }),

  // Reasoning
  setReasoning: (side, text) =>
    set((state) => ({
      reasoning: { ...state.reasoning, [side]: text },
    })),
  setReasoningLoading: (side, loading) =>
    set((state) => ({
      reasoning: {
        ...state.reasoning,
        ...(side === 'white' ? { loadingWhite: loading } : { loadingBlack: loading }),
      },
    })),

  // Branch
  setBranch: (partial) => set((state) => ({ branch: { ...state.branch, ...partial } })),
  resetBranch: () => set({ branch: initialBranch }),
  setHintMove: (hintMove) => set({ hintMove }),
  setBranchSuggestions: (branchSuggestions) => set({ branchSuggestions }),

  // Chat
  addChatMessage: (msg) => set((state) => ({ chatMessages: [...state.chatMessages, msg] })),
  clearChat: () => set({ chatMessages: [] }),

  // Evaluation
  updateEvaluation: (eval_) => set({ evaluation: eval_ }),

  // History
  saveToHistory: (entry) => {
    const updated = [entry, ...get().gameHistory].slice(0, 50); // keep last 50
    saveHistoryToStorage(updated);
    set({ gameHistory: updated });
  },
  clearHistory: () => {
    localStorage.removeItem(HISTORY_KEY);
    set({ gameHistory: [] });
  },
  loadHistory: () => set({ gameHistory: loadHistoryFromStorage() }),
}));
