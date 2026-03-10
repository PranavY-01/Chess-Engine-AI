/**
 * API client for communicating with the Chess Engine backend.
 */
import type { GameState, MoveResponse, TopMove, LegalMove } from '../types/chessTypes';

const API_BASE = 'http://localhost:8000';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${url}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

/** Start a new game. */
export async function startGame(aiLevel: number = 3): Promise<GameState & { message: string }> {
    return request('/game/start', {
        method: 'POST',
        body: JSON.stringify({ ai_level: aiLevel }),
    });
}

/** Get current game state. */
export async function getGameState(): Promise<GameState> {
    return request('/game/state');
}

/** Make a player move. */
export async function makeMove(
    fromSquare: string,
    toSquare: string,
    promotion?: string
): Promise<MoveResponse> {
    return request('/game/move', {
        method: 'POST',
        body: JSON.stringify({
            from_square: fromSquare,
            to_square: toSquare,
            promotion: promotion || null,
        }),
    });
}

/** Get AI to make a move. */
export async function getAIMove(level?: number): Promise<MoveResponse> {
    return request('/ai/move', {
        method: 'POST',
        body: JSON.stringify({ level: level || null }),
    });
}

/** Get top move suggestions. */
export async function getTopMoves(): Promise<{ suggestions: TopMove[]; turn: string }> {
    return request('/analysis/top-moves');
}

/** Get legal moves for a square. */
export async function getLegalMoves(square: string): Promise<{ moves: LegalMove[] }> {
    return request(`/game/legal-moves/${square}`);
}

/** Undo last move. */
export async function undoMove(): Promise<GameState & { message: string }> {
    return request('/game/undo', { method: 'POST' });
}

/** Redo last undone move. */
export async function redoMove(): Promise<GameState & { message: string }> {
    return request('/game/redo', { method: 'POST' });
}

/** Set AI difficulty level. */
export async function setDifficulty(level: number): Promise<{ message: string; level: number }> {
    return request(`/game/set-difficulty?level=${level}`, { method: 'POST' });
}
