/**
 * Chess type definitions for the ChessAlgos frontend.
 */
import type { AILevel } from '../config/demonstrators';

/** A piece code like 'wK', 'bP', etc. or null for empty. */
export type PieceCode = string | null;

/** 8x8 board represented as a 2D array. */
export type Board = PieceCode[][];

/** Game status strings from the backend. */
export type GameStatus =
  | 'active'
  | 'checkmate_white'
  | 'checkmate_black'
  | 'stalemate'
  | 'draw_50_move'
  | 'draw_insufficient'
  | 'draw_repetition';

/** A top move suggestion from the analysis engine. */
export interface TopMove {
  move: string;
  score: number;
  from_square: string;
  to_square: string;
}

/** The full game state from the backend. */
export interface GameState {
  board: Board;
  turn: string;
  status: GameStatus;
  move_history: string[];
  is_check: boolean;
  last_move: { from: string; to: string } | null;
}

/** Response from POST /game/move */
export interface MoveResponse {
  board: Board;
  turn: string;
  status: GameStatus;
  move_history: string[];
  is_check: boolean;
  player_move: { from: string; to: string; promotion: string | null } | null;
  ai_move: { from: string; to: string; promotion: string | null } | null;
  last_move: { from: string; to: string } | null;
  message: string;
}

/** Legal move for a square. */
export interface LegalMove {
  to: string;
  promotion: string | null;
}

export type { AILevel };

export interface HintMove {
  from_square: string;
  to_square: string;
  score: number;
}

export interface BranchStateResponse {
  branch_id: string;
  board: Board;
  turn: string;
  status: string;
  steps: Array<{ from: string; to: string; score: number | null; move: string }>;
  progress: number;
  max_half_moves: number;
  base_rank: number;
  suggestions: TopMove[];
}

export interface ExplainResponse {
  explanation: string;
}

export interface AiVsAiState {
  session_id: string;
  board: Board;
  turn: string;
  status: string;
  move_history: string[];
  is_check: boolean;
  paused: boolean;
  white_level: AILevel;
  black_level: AILevel;
  last_move: { from: string; to: string } | null;
  evaluation: number;
  white_score: number;
  black_score: number;
}

/** Evaluation response for accuracy meter */
export interface EvaluationState {
  evaluation: number;
  white_score: number;
  black_score: number;
}

/** Chat message for AI companion */
export interface ChatMessage {
  type: 'ai' | 'system' | 'user';
  text: string;
  move?: string;
  timestamp: number;
}

/** Game history entry for localStorage persistence */
export interface GameHistoryEntry {
  id: string;
  date: string;
  mode: 'human-vs-ai' | 'ai-vs-ai';
  whiteAlgorithm: string;
  blackAlgorithm: string;
  result: string;
  moves: string[];
  totalMoves: number;
  finalEvaluation: number;
}

/** End session response */
export interface EndSessionResponse {
  status: string;
  move_history: string[];
  total_moves: number;
  final_evaluation: number;
}

/** Unicode chess piece symbols. */
export const PIECE_SYMBOLS: Record<string, string> = {
  wK: '♔',
  wQ: '♕',
  wR: '♖',
  wB: '♗',
  wN: '♘',
  wP: '♙',
  bK: '♚',
  bQ: '♛',
  bR: '♜',
  bB: '♝',
  bN: '♞',
  bP: '♟',
};
