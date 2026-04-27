import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ChessBoard from '../components/ChessBoard';
import MoveHistory from '../components/MoveHistory';
import AlgorithmCard from '../components/AlgorithmCard';
import AccuracyMeter from '../components/AccuracyMeter';
import HintButton from '../components/HintButton';
import type { Board, GameStatus, LegalMove } from '../types/chessTypes';
import * as api from '../services/api';
import { DEMONSTRATORS } from '../config/demonstrators';
import { useGameStore } from '../store/gameStore';
import './HumanVsAiPage.css';

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
const RANKS = ['8', '7', '6', '5', '4', '3', '2', '1'];

function squareFromCoords(row: number, col: number): string {
  return FILES[col] + RANKS[row];
}

function findKingSquare(board: Board, color: string): string | null {
  const kingCode = color + 'K';
  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      if (board[r][c] === kingCode) return squareFromCoords(r, c);
    }
  }
  return null;
}

function statusMessage(status: GameStatus): string {
  switch (status) {
    case 'active': return 'Game in progress';
    case 'checkmate_white': return '♔ White wins by checkmate!';
    case 'checkmate_black': return '♚ Black wins by checkmate!';
    case 'stalemate': return 'Draw — Stalemate';
    case 'draw_50_move': return 'Draw — 50-move rule';
    case 'draw_insufficient': return 'Draw — Insufficient material';
    case 'draw_repetition': return 'Draw — Threefold repetition';
    default: return status;
  }
}

const HumanVsAiPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    sessionActive,
    startSession,
    endSessionStore,
    whiteDemonstrator,
    evaluation,
    updateEvaluation,
    addChatMessage,
    hintMove,
    setHintMove,
  } = useGameStore();

  const [board, setBoard] = useState<Board>([]);
  const [turn, setTurn] = useState<string>('w');
  const [status, setStatus] = useState<GameStatus>('active');
  const [moveHistory, setMoveHistory] = useState<string[]>([]);
  const [isCheck, setIsCheck] = useState(false);
  const [lastMove, setLastMove] = useState<{ from: string; to: string } | null>(null);
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [legalMoves, setLegalMoves] = useState<LegalMove[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);
  const [showPromotion, setShowPromotion] = useState<{ from: string; to: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hintLoading, setHintLoading] = useState(false);
  const savedRef = useRef(false);

  const demonstrator = DEMONSTRATORS[whiteDemonstrator];

  const updateState = useCallback((data: {
    board: Board; turn: string; status: GameStatus;
    move_history?: string[]; is_check: boolean;
    last_move?: { from: string; to: string } | null;
  }) => {
    setBoard(data.board);
    setTurn(data.turn);
    setStatus(data.status);
    if (data.move_history) setMoveHistory(data.move_history);
    setIsCheck(data.is_check);
    setLastMove(data.last_move || null);
    setSelectedSquare(null);
    setLegalMoves([]);
  }, []);

  const fetchEvaluation = useCallback(async () => {
    try {
      const ev = await api.getEvaluation();
      updateEvaluation(ev);
    } catch { /* ignore */ }
  }, [updateEvaluation]);


  // Start game on session start
  const handleStartSession = useCallback(async () => {
    setError(null);
    setIsLoading(true);
    startSession();
    savedRef.current = false;
    try {
      const data = await api.startGame(whiteDemonstrator);
      updateState(data);
      setCanUndo(false);
      setCanRedo(false);
      await fetchEvaluation();
      addChatMessage({
        type: 'system',
        text: `Game started! You're playing against ${demonstrator.name} (${demonstrator.algorithm}).`,
        timestamp: Date.now(),
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to start session');
      endSessionStore();
    } finally {
      setIsLoading(false);
    }
  }, [whiteDemonstrator, startSession, endSessionStore, updateState, fetchEvaluation, addChatMessage, demonstrator]);

  // End session
  const handleEndSession = useCallback(async () => {
    // Only save for manual resignation if auto-save hasn't fired
    if (!savedRef.current) {
      try {
        const result = await api.endSession();
        const { saveToHistory } = useGameStore.getState();
        saveToHistory({
          id: Date.now().toString(),
          date: new Date().toISOString(),
          mode: 'human-vs-ai',
          whiteAlgorithm: 'Human',
          blackAlgorithm: demonstrator.name,
          result: result.status,
          moves: result.move_history,
          totalMoves: result.total_moves,
          finalEvaluation: result.final_evaluation,
        });
        savedRef.current = true;
      } catch { /* game might already be ended */ }
    }
    endSessionStore();
    navigate('/');
  }, [demonstrator.name, endSessionStore, navigate]);

  // Auto-save when game ends
  useEffect(() => {
    if (sessionActive && status !== 'active' && !savedRef.current) {
      addChatMessage({
        type: 'system',
        text: `Game over: ${statusMessage(status)}`,
        timestamp: Date.now(),
      });
      const { saveToHistory } = useGameStore.getState();
      saveToHistory({
        id: Date.now().toString(),
        date: new Date().toISOString(),
        mode: 'human-vs-ai',
        whiteAlgorithm: 'Human',
        blackAlgorithm: demonstrator.name,
        result: status,
        moves: moveHistory,
        totalMoves: moveHistory.length,
        finalEvaluation: evaluation.evaluation,
      });
      savedRef.current = true;
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  // Clear hint after timeout
  useEffect(() => {
    if (!hintMove) return;
    const t = setTimeout(() => setHintMove(null), 4000);
    return () => clearTimeout(t);
  }, [hintMove, setHintMove]);

  const executeMove = async (from: string, to: string, promotion?: string) => {
    setError(null);
    setShowPromotion(null);
    setHintMove(null);

    // Phase 1: Optimistic update — show the player's piece moving immediately
    const FILES_MAP: Record<string, number> = { a: 0, b: 1, c: 2, d: 3, e: 4, f: 5, g: 6, h: 7 };
    const RANKS_MAP: Record<string, number> = { '8': 0, '7': 1, '6': 2, '5': 3, '4': 4, '3': 5, '2': 6, '1': 7 };
    const fR = RANKS_MAP[from[1]], fC = FILES_MAP[from[0]];
    const tR = RANKS_MAP[to[1]], tC = FILES_MAP[to[0]];
    const optimistic = board.map(row => [...row]);
    const movingPiece = optimistic[fR][fC];
    optimistic[tR][tC] = promotion ? (turn + promotion) : movingPiece;
    optimistic[fR][fC] = null;
    setBoard(optimistic);
    setSelectedSquare(null);
    setLegalMoves([]);
    setLastMove({ from, to });

    // Phase 2: Call API, then after a brief pause show the AI response
    setIsLoading(true);
    try {
      const data = await api.makeMove(from, to, promotion);
      setCanUndo(true);
      setCanRedo(false);

      if (data.ai_move) {
        // Brief delay so the player sees their move land before AI responds
        await new Promise(r => setTimeout(r, 450));
        updateState(data);
        await fetchEvaluation();
        const aiLabel = `${data.ai_move.from}→${data.ai_move.to}`;
        addChatMessage({
          type: 'ai',
          text: `${demonstrator.name} played ${aiLabel}`,
          move: aiLabel,
          timestamp: Date.now(),
        });
      } else {
        updateState(data);
        await fetchEvaluation();
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Move failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSquareClick = async (row: number, col: number) => {
    if (isLoading || status !== 'active') return;
    const square = squareFromCoords(row, col);
    const piece = board[row]?.[col];

    if (selectedSquare && legalMoves.some((m) => m.to === square)) {
      const promoMoves = legalMoves.filter((m) => m.to === square && m.promotion !== null);
      if (promoMoves.length > 0) {
        setShowPromotion({ from: selectedSquare, to: square });
        return;
      }
      await executeMove(selectedSquare, square);
      return;
    }

    if (piece && piece[0] === turn) {
      setSelectedSquare(square);
      try {
        const data = await api.getLegalMoves(square);
        setLegalMoves(data.moves);
      } catch { setLegalMoves([]); }
    } else {
      setSelectedSquare(null);
      setLegalMoves([]);
    }
  };

  const handlePromotion = (piece: string) => {
    if (showPromotion) executeMove(showPromotion.from, showPromotion.to, piece);
  };

  const handleUndo = async () => {
    setIsLoading(true);
    try {
      const data = await api.undoMove();
      updateState(data);
      setCanRedo(true);
      await fetchEvaluation();
    } finally { setIsLoading(false); }
  };

  const handleRedo = async () => {
    setIsLoading(true);
    try {
      const data = await api.redoMove();
      updateState(data);
      await fetchEvaluation();
    } finally { setIsLoading(false); }
  };

  const handleAskHint = async () => {
    setHintLoading(true);
    try {
      const hint = await api.getHint();
      setHintMove({ from: hint.from_square, to: hint.to_square });
    } finally { setHintLoading(false); }
  };

  const kingSquare = useMemo(() =>
    isCheck ? findKingSquare(board, turn) : null
  , [board, isCheck, turn]);

  const isGameOver = status !== 'active';

  // ---- Pre-session view ----
  if (!sessionActive) {
    return (
      <div className="hvai-page">
        <div className="hvai-setup">
          <div className="hvai-setup-card">
            <span className="hvai-setup-icon">⚔</span>
            <h2 className="hvai-setup-title">Human vs AI</h2>
            <p className="hvai-setup-sub">
              You play as White against the selected AI algorithm.
              The AI companion will explain every move.
            </p>

            <div className="hvai-setup-algo">
              <span className="hvai-setup-algo-label">Opponent Algorithm</span>
              <span className="hvai-setup-algo-name">
                <span className="hvai-setup-algo-dot" style={{ backgroundColor: demonstrator.accent }} />
                {demonstrator.name} — {demonstrator.algorithm}
              </span>
            </div>

            <p className="hvai-setup-hint">Change algorithm from the sidebar</p>

            <button className="btn-primary" onClick={handleStartSession} disabled={isLoading}>
              {isLoading ? <span className="spinner" /> : null}
              Start Session
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ---- Active session view ----
  return (
    <div className="hvai-page">
      {/* Top bar */}
      <div className="hvai-top-bar">
        <div className={`hvai-status ${isGameOver ? 'game-over' : ''}`}>
          {statusMessage(status)}
        </div>
        <button className="hvai-end-btn" onClick={handleEndSession}>
          ✕ End Session
        </button>
      </div>

      {error && <div className="hvai-error">{error}</div>}
      {isLoading && <div className="hvai-thinking"><span className="spinner" /> AI is thinking...</div>}

      <div className="hvai-game-layout">
        {/* Accuracy Meter */}
        <div className="hvai-meter-col">
          <AccuracyMeter
            evaluation={evaluation.evaluation}
            whiteScore={evaluation.white_score}
            blackScore={evaluation.black_score}
          />
        </div>

        {/* Board */}
        <div className="hvai-board-col">
          <ChessBoard
            board={board}
            selectedSquare={selectedSquare}
            legalMoves={legalMoves}
            lastMove={lastMove}
            isCheck={isCheck}
            kingSquare={kingSquare}
            turn={turn}
            hintMove={hintMove}
            onSquareClick={handleSquareClick}
          />
          <MoveHistory
            moves={moveHistory}
            onUndo={handleUndo}
            onRedo={handleRedo}
            canUndo={canUndo}
            canRedo={canRedo}
          />
        </div>

        {/* Info panel */}
        <div className="hvai-info-col">
          <AlgorithmCard demonstrator={demonstrator} side="black" />
          <div className="hvai-actions">
            <HintButton loading={hintLoading} onAsk={handleAskHint} />
          </div>
        </div>
      </div>

      {/* Promotion dialog */}
      {showPromotion && (
        <div className="promotion-overlay">
          <div className="promotion-dialog">
            <h3>Choose promotion piece</h3>
            <div className="promotion-options">
              {['Q', 'R', 'B', 'N'].map((p) => (
                <button key={p} className="promotion-btn" onClick={() => handlePromotion(p)}>
                  {p}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HumanVsAiPage;
