/**
 * GamePage — main chess game page composing all components.
 * Manages all game state via backend API calls.
 */
import React, { useState, useEffect, useCallback } from 'react';
import ChessBoard from '../components/ChessBoard';
import MoveHistory from '../components/MoveHistory';
import SuggestionsPanel from '../components/SuggestionsPanel';
import Controls from '../components/Controls';
import type { Board, GameStatus, TopMove, LegalMove, AILevel } from '../types/chessTypes';
import * as api from '../services/api';
import './GamePage.css';

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
const RANKS = ['8', '7', '6', '5', '4', '3', '2', '1'];

function squareFromCoords(row: number, col: number): string {
    return FILES[col] + RANKS[row];
}

function findKingSquare(board: Board, color: string): string | null {
    const kingCode = color + 'K';
    for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
            if (board[r][c] === kingCode) {
                return squareFromCoords(r, c);
            }
        }
    }
    return null;
}

const GamePage: React.FC = () => {
    const [board, setBoard] = useState<Board>([]);
    const [turn, setTurn] = useState<string>('w');
    const [status, setStatus] = useState<GameStatus>('active');
    const [moveHistory, setMoveHistory] = useState<string[]>([]);
    const [isCheck, setIsCheck] = useState(false);
    const [lastMove, setLastMove] = useState<{ from: string; to: string } | null>(null);
    const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
    const [legalMoves, setLegalMoves] = useState<LegalMove[]>([]);
    const [suggestions, setSuggestions] = useState<TopMove[]>([]);
    const [aiLevel, setAiLevel] = useState<AILevel>(3);
    const [isLoading, setIsLoading] = useState(false);
    const [suggestionsLoading, setSuggestionsLoading] = useState(false);
    const [canUndo, setCanUndo] = useState(false);
    const [canRedo, setCanRedo] = useState(false);
    const [showPromotion, setShowPromotion] = useState<{
        from: string;
        to: string;
    } | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Initialize game on mount
    useEffect(() => {
        handleNewGame();
    }, []);

    const updateState = useCallback((data: {
        board: Board;
        turn: string;
        status: GameStatus;
        move_history?: string[];
        is_check: boolean;
        last_move?: { from: string; to: string } | null;
    }) => {
        setBoard(data.board);
        setTurn(data.turn);
        setStatus(data.status as GameStatus);
        if (data.move_history) setMoveHistory(data.move_history);
        setIsCheck(data.is_check);
        setLastMove(data.last_move || null);
        setSelectedSquare(null);
        setLegalMoves([]);
        setCanUndo(
            data.move_history !== undefined && data.move_history.length > 0
        );
    }, []);

    const fetchSuggestions = useCallback(async () => {
        if (status !== 'active') return;
        setSuggestionsLoading(true);
        try {
            const data = await api.getTopMoves();
            setSuggestions(data.suggestions);
        } catch {
            setSuggestions([]);
        } finally {
            setSuggestionsLoading(false);
        }
    }, [status]);

    const handleNewGame = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await api.startGame(aiLevel);
            updateState(data);
            setCanUndo(false);
            setCanRedo(false);
            setSuggestions([]);
            // Fetch suggestions after game starts
            setTimeout(async () => {
                setSuggestionsLoading(true);
                try {
                    const sData = await api.getTopMoves();
                    setSuggestions(sData.suggestions);
                } catch { /* ignore */ }
                setSuggestionsLoading(false);
            }, 100);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to start game');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSquareClick = async (row: number, col: number) => {
        if (isLoading || status !== 'active') return;

        const square = squareFromCoords(row, col);
        const piece = board[row]?.[col];

        // If we have a selected piece and clicked a legal move target
        if (selectedSquare && legalMoves.some((m) => m.to === square)) {
            // Check if this is a promotion move
            const promoMoves = legalMoves.filter(
                (m) => m.to === square && m.promotion !== null
            );
            if (promoMoves.length > 0) {
                setShowPromotion({ from: selectedSquare, to: square });
                return;
            }

            await executeMove(selectedSquare, square);
            return;
        }

        // Select a piece
        if (piece && piece[0] === turn) {
            setSelectedSquare(square);
            try {
                const data = await api.getLegalMoves(square);
                setLegalMoves(data.moves);
            } catch {
                setLegalMoves([]);
            }
        } else {
            setSelectedSquare(null);
            setLegalMoves([]);
        }
    };

    const executeMove = async (from: string, to: string, promotion?: string) => {
        setIsLoading(true);
        setError(null);
        setShowPromotion(null);
        try {
            const data = await api.makeMove(from, to, promotion);
            updateState(data);
            setCanUndo(true);
            setCanRedo(false);

            // Fetch suggestions after move
            if (data.status === 'active') {
                fetchSuggestions();
            } else {
                setSuggestions([]);
            }
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Move failed');
        } finally {
            setIsLoading(false);
        }
    };

    const handlePromotion = (piece: string) => {
        if (showPromotion) {
            executeMove(showPromotion.from, showPromotion.to, piece);
        }
    };

    const handleUndo = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await api.undoMove();
            updateState(data);
            setCanRedo(true);
            fetchSuggestions();
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Undo failed');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRedo = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await api.redoMove();
            updateState(data);
            fetchSuggestions();
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Redo failed');
        } finally {
            setIsLoading(false);
        }
    };

    const handleAILevelChange = async (level: AILevel) => {
        setAiLevel(level);
        try {
            await api.setDifficulty(level);
        } catch { /* ignore */ }
    };

    const kingSquare = isCheck ? findKingSquare(board, turn) : null;

    return (
        <div className="game-page">
            <header className="game-header">
                <h1 className="game-title">
                    <span className="title-icon">♛</span>
                    Chess AI Engine
                </h1>
                <p className="game-subtitle">AI-Powered Chess with Game Tree Analysis</p>
            </header>

            {error && (
                <div className="error-banner" onClick={() => setError(null)}>
                    ⚠️ {error}
                </div>
            )}

            <div className="game-layout">
                {/* Left Panel: Controls */}
                <div className="left-panel">
                    <Controls
                        aiLevel={aiLevel}
                        onAILevelChange={handleAILevelChange}
                        onNewGame={handleNewGame}
                        gameStatus={status}
                        isLoading={isLoading}
                    />
                </div>

                {/* Center: Chess Board */}
                <div className="center-panel">
                    <ChessBoard
                        board={board}
                        selectedSquare={selectedSquare}
                        legalMoves={legalMoves}
                        lastMove={lastMove}
                        isCheck={isCheck}
                        kingSquare={kingSquare}
                        turn={turn}
                        onSquareClick={handleSquareClick}
                    />
                </div>

                {/* Right Panel: Suggestions + Move History */}
                <div className="right-panel">
                    <SuggestionsPanel
                        suggestions={suggestions}
                        loading={suggestionsLoading}
                    />
                    <MoveHistory
                        moves={moveHistory}
                        onUndo={handleUndo}
                        onRedo={handleRedo}
                        canUndo={canUndo}
                        canRedo={canRedo}
                    />
                </div>
            </div>

            {/* Promotion Dialog */}
            {showPromotion && (
                <div className="promotion-overlay">
                    <div className="promotion-dialog">
                        <h3>Choose promotion piece</h3>
                        <div className="promotion-options">
                            {['Q', 'R', 'B', 'N'].map((p) => (
                                <button
                                    key={p}
                                    className="promotion-btn"
                                    onClick={() => handlePromotion(p)}
                                >
                                    {p === 'Q' ? '♛' : p === 'R' ? '♜' : p === 'B' ? '♝' : '♞'}
                                    <span>{p === 'Q' ? 'Queen' : p === 'R' ? 'Rook' : p === 'B' ? 'Bishop' : 'Knight'}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GamePage;
