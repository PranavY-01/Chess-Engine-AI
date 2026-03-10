/**
 * Chess type definitions for the frontend.
 */

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

/** AI difficulty levels. */
export type AILevel = 1 | 2 | 3 | 4 | 5;

/** Difficulty level descriptions. */
export const AI_LEVEL_NAMES: Record<AILevel, string> = {
  1: 'Random',
  2: 'Greedy',
  3: 'Minimax',
  4: 'Alpha-Beta',
  5: 'Advanced',
};

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
