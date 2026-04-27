/**
 * API client for ChessAlgos backend.
 */
import type {
    GameState,
    MoveResponse,
    TopMove,
    LegalMove,
    ExplainResponse,
    BranchStateResponse,
    HintMove,
    AiVsAiState,
    EvaluationState,
    EndSessionResponse,
} from '../types/chessTypes';
import type { AILevel } from '../config/demonstrators';

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

export async function getHint(): Promise<HintMove> {
    return request('/analysis/hint');
}

/** Get position evaluation for accuracy meter. */
export async function getEvaluation(): Promise<EvaluationState> {
    return request('/analysis/evaluation');
}

/** End the current game session. */
export async function endSession(): Promise<EndSessionResponse> {
    return request('/game/end-session', { method: 'POST' });
}

export async function explainMove(payload: {
    demonstrator_id: string;
    chosen_move: Record<string, unknown>;
    alternatives: Array<Record<string, unknown>>;
    board_context: Record<string, unknown>;
    branch_mode?: boolean;
}): Promise<ExplainResponse> {
    return request('/reasoning/explain', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

export async function explainBranch(payload: {
    demonstrator_id: string;
    chosen_move: Record<string, unknown>;
    alternatives: Array<Record<string, unknown>>;
    board_context: Record<string, unknown>;
}): Promise<ExplainResponse> {
    return request('/reasoning/explain-branch', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

export async function startBranch(fromSquare: string, toSquare: string, rank: number, level: AILevel): Promise<BranchStateResponse> {
    return request('/simulation/branch/start', {
        method: 'POST',
        body: JSON.stringify({ from_square: fromSquare, to_square: toSquare, rank, level }),
    });
}

export async function advanceBranch(branchId: string): Promise<BranchStateResponse> {
    return request('/simulation/branch/advance', {
        method: 'POST',
        body: JSON.stringify({ branch_id: branchId }),
    });
}

export async function endBranch(branchId: string): Promise<{ message: string }> {
    return request(`/simulation/branch/${branchId}`, { method: 'DELETE' });
}

export async function startAiVsAi(whiteLevel: AILevel, blackLevel: AILevel): Promise<AiVsAiState> {
    return request('/simulation/ai-vs-ai/start', {
        method: 'POST',
        body: JSON.stringify({ white_level: whiteLevel, black_level: blackLevel }),
    });
}

export async function pauseAiVsAi(sessionId: string, paused: boolean): Promise<AiVsAiState> {
    return request('/simulation/ai-vs-ai/pause', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, paused }),
    });
}

export async function stepAiVsAi(sessionId: string): Promise<AiVsAiState> {
    return request('/simulation/ai-vs-ai/step', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId }),
    });
}

export async function resetAiVsAi(sessionId: string): Promise<AiVsAiState> {
    return request('/simulation/ai-vs-ai/reset', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId }),
    });
}
