import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ChessBoard from '../components/ChessBoard';
import MoveHistory from '../components/MoveHistory';
import AlgorithmCard from '../components/AlgorithmCard';
import AccuracyMeter from '../components/AccuracyMeter';
import type { Board, GameStatus } from '../types/chessTypes';
import * as api from '../services/api';
import { DEMONSTRATORS } from '../config/demonstrators';
import { useGameStore } from '../store/gameStore';
import './AiVsAiPage.css';

function statusMessage(status: GameStatus): string {
  switch (status) {
    case 'active': return 'Simulation running';
    case 'checkmate_white': return '♔ White wins by checkmate!';
    case 'checkmate_black': return '♚ Black wins by checkmate!';
    case 'stalemate': return 'Draw — Stalemate';
    case 'draw_50_move': return 'Draw — 50-move rule';
    case 'draw_insufficient': return 'Draw — Insufficient material';
    case 'draw_repetition': return 'Draw — Threefold repetition';
    default: return status;
  }
}

const AiVsAiPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    sessionActive,
    startSession,
    endSessionStore,
    whiteDemonstrator,
    blackDemonstrator,
    evaluation,
    updateEvaluation,
    addChatMessage,
  } = useGameStore();

  const [board, setBoard] = useState<Board>([]);
  const [turn, setTurn] = useState<string>('w');
  const [status, setStatus] = useState<GameStatus>('active');
  const [moveHistory, setMoveHistory] = useState<string[]>([]);
  const [isCheck, setIsCheck] = useState(false);
  const [lastMove, setLastMove] = useState<{ from: string; to: string } | null>(null);
  const [aiSessionId, setAiSessionId] = useState<string | null>(null);
  const [simPaused, setSimPaused] = useState(false);
  const [simSpeed, setSimSpeed] = useState(2);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Guard against concurrent step calls & track move count across renders
  const steppingRef = useRef(false);
  const prevMoveCountRef = useRef(0);
  const savedRef = useRef(false);

  const whiteDem = DEMONSTRATORS[whiteDemonstrator];
  const blackDem = DEMONSTRATORS[blackDemonstrator];

  const handleStartSession = useCallback(async () => {
    setError(null);
    setIsLoading(true);
    startSession();
    savedRef.current = false;
    prevMoveCountRef.current = 0;
    try {
      const session = await api.startAiVsAi(whiteDemonstrator, blackDemonstrator);
      setAiSessionId(session.session_id);
      setBoard(session.board);
      setTurn(session.turn);
      setStatus(session.status as GameStatus);
      setMoveHistory(session.move_history);
      setIsCheck(session.is_check);
      setLastMove(session.last_move || null);
      setSimPaused(false);
      addChatMessage({
        type: 'system',
        text: `AI vs AI: ${whiteDem.name} (${whiteDem.algorithm}) vs ${blackDem.name} (${blackDem.algorithm})`,
        timestamp: Date.now(),
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to start');
      endSessionStore();
    } finally {
      setIsLoading(false);
    }
  }, [whiteDemonstrator, blackDemonstrator, startSession, endSessionStore, addChatMessage, whiteDem, blackDem]);

  const handleEndSession = useCallback(() => {
    // Only save if game ended naturally and wasn't already saved
    if (!savedRef.current && status !== 'active') {
      const { saveToHistory } = useGameStore.getState();
      saveToHistory({
        id: Date.now().toString(),
        date: new Date().toISOString(),
        mode: 'ai-vs-ai',
        whiteAlgorithm: whiteDem.name,
        blackAlgorithm: blackDem.name,
        result: status,
        moves: moveHistory,
        totalMoves: moveHistory.length,
        finalEvaluation: evaluation.evaluation,
      });
      savedRef.current = true;
    }
    endSessionStore();
    navigate('/');
  }, [whiteDem.name, blackDem.name, status, moveHistory, evaluation.evaluation, endSessionStore, navigate]);

  // Auto-step simulation — uses setTimeout chain to prevent concurrent calls
  useEffect(() => {
    if (!sessionActive || !aiSessionId || simPaused || status !== 'active') return;
    const delay = simSpeed === 1 ? 2200 : simSpeed === 2 ? 1200 : 600;

    const timer = setInterval(async () => {
      // Skip if a previous step is still in-flight
      if (steppingRef.current) return;
      steppingRef.current = true;

      try {
        const session = await api.stepAiVsAi(aiSessionId);

        setBoard(session.board);
        setTurn(session.turn);
        setStatus(session.status as GameStatus);
        setMoveHistory(session.move_history);
        setIsCheck(session.is_check);
        setLastMove(session.last_move || null);

        updateEvaluation({
          evaluation: session.evaluation,
          white_score: session.white_score,
          black_score: session.black_score,
        });

        if (session.move_history.length > prevMoveCountRef.current) {
          const lastMoveStr = session.move_history[session.move_history.length - 1];
          const side = session.turn === 'w' ? blackDem : whiteDem;
          addChatMessage({
            type: 'ai',
            text: `${side.name} played ${lastMoveStr}`,
            move: lastMoveStr,
            timestamp: Date.now(),
          });
          prevMoveCountRef.current = session.move_history.length;
        }
      } catch {
        setSimPaused(true);
      } finally {
        steppingRef.current = false;
      }
    }, delay);

    return () => clearInterval(timer);
  }, [sessionActive, aiSessionId, simPaused, simSpeed, status, updateEvaluation, addChatMessage, whiteDem, blackDem]);

  // Auto-save on game end (single save, tracked by ref)
  useEffect(() => {
    if (sessionActive && status !== 'active' && aiSessionId && !savedRef.current) {
      addChatMessage({
        type: 'system',
        text: `Simulation ended: ${statusMessage(status)}`,
        timestamp: Date.now(),
      });
      const { saveToHistory } = useGameStore.getState();
      saveToHistory({
        id: Date.now().toString(),
        date: new Date().toISOString(),
        mode: 'ai-vs-ai',
        whiteAlgorithm: whiteDem.name,
        blackAlgorithm: blackDem.name,
        result: status,
        moves: moveHistory,
        totalMoves: moveHistory.length,
        finalEvaluation: evaluation.evaluation,
      });
      savedRef.current = true;
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  const handlePauseToggle = async () => {
    if (!aiSessionId) return;
    const next = !simPaused;
    setSimPaused(next);
    await api.pauseAiVsAi(aiSessionId, next);
  };

  const isGameOver = status !== 'active';

  // Pre-session
  if (!sessionActive) {
    return (
      <div className="avai-page">
        <div className="avai-setup">
          <div className="avai-setup-card">
            <span className="avai-setup-icon">⚡</span>
            <h2 className="avai-setup-title">AI vs AI</h2>
            <p className="avai-setup-sub">
              Watch two algorithms battle. Select algorithms from the sidebar.
            </p>

            <div className="avai-setup-algos">
              <div className="avai-setup-algo-card">
                <div className="avai-setup-algo-side">White</div>
                <div className="avai-setup-algo-name">
                  <span className="hvai-setup-algo-dot" style={{ backgroundColor: whiteDem.accent }} />
                  {whiteDem.name}
                </div>
                <div className="avai-setup-algo-type">{whiteDem.algorithm}</div>
              </div>
              <span className="avai-setup-vs">VS</span>
              <div className="avai-setup-algo-card">
                <div className="avai-setup-algo-side">Black</div>
                <div className="avai-setup-algo-name">
                  <span className="hvai-setup-algo-dot" style={{ backgroundColor: blackDem.accent }} />
                  {blackDem.name}
                </div>
                <div className="avai-setup-algo-type">{blackDem.algorithm}</div>
              </div>
            </div>

            <button className="btn-primary" onClick={handleStartSession} disabled={isLoading}>
              {isLoading ? <span className="spinner" /> : null}
              Start Simulation
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="avai-page">
      <div className="avai-top-bar">
        <div className={`avai-status ${isGameOver ? 'game-over' : ''}`}>
          {statusMessage(status)}
        </div>
        <button className="avai-end-btn" onClick={handleEndSession}>✕ End Session</button>
      </div>

      {error && <div className="avai-error">{error}</div>}

      <div className="avai-game-layout">
        <div className="avai-side-col">
          <AlgorithmCard demonstrator={whiteDem} side="white" />
        </div>

        <div className="avai-center-col">
          <ChessBoard
            board={board}
            selectedSquare={null}
            legalMoves={[]}
            lastMove={lastMove}
            isCheck={isCheck}
            turn={turn}
            kingSquare={null}
            readOnly
            onSquareClick={() => undefined}
          />
          <div className="avai-controls">
            <span className="avai-controls-label">Speed</span>
            {[1, 2, 3].map((s) => (
              <button
                key={s}
                className={`avai-speed-btn ${simSpeed === s ? 'active' : ''}`}
                onClick={() => setSimSpeed(s)}
              >
                {s === 1 ? 'Slow' : s === 2 ? 'Normal' : 'Fast'}
              </button>
            ))}
            <button
              className={`avai-pause-btn ${simPaused ? 'paused' : 'playing'}`}
              onClick={handlePauseToggle}
            >
              {simPaused ? '▶ Resume' : '⏸ Pause'}
            </button>
          </div>
          <MoveHistory moves={moveHistory} onUndo={() => undefined} onRedo={() => undefined} canUndo={false} canRedo={false} />
        </div>

        <div className="avai-side-col">
          <AlgorithmCard demonstrator={blackDem} side="black" />
          <div className="avai-meter-col">
            <AccuracyMeter
              evaluation={evaluation.evaluation}
              whiteScore={evaluation.white_score}
              blackScore={evaluation.black_score}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AiVsAiPage;
