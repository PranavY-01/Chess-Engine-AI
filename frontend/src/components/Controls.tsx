/**
 * Controls component — New Game, difficulty selector, game status display.
 */
import React from 'react';
import type { AILevel, GameStatus } from '../types/chessTypes';
import { AI_LEVEL_NAMES } from '../types/chessTypes';
import './Controls.css';

interface ControlsProps {
    aiLevel: AILevel;
    onAILevelChange: (level: AILevel) => void;
    onNewGame: () => void;
    gameStatus: GameStatus;
    isLoading: boolean;
}

function statusMessage(status: GameStatus): string {
    switch (status) {
        case 'active':
            return 'Game in progress';
        case 'checkmate_white':
            return '♔ White wins by checkmate!';
        case 'checkmate_black':
            return '♚ Black wins by checkmate!';
        case 'stalemate':
            return 'Draw — Stalemate';
        case 'draw_50_move':
            return 'Draw — 50-move rule';
        case 'draw_insufficient':
            return 'Draw — Insufficient material';
        case 'draw_repetition':
            return 'Draw — Threefold repetition';
        default:
            return status;
    }
}

const Controls: React.FC<ControlsProps> = ({
    aiLevel,
    onAILevelChange,
    onNewGame,
    gameStatus,
    isLoading,
}) => {
    const isGameOver = gameStatus !== 'active';

    return (
        <div className="controls-panel">
            <h3 className="panel-title">
                <span className="panel-icon">⚙️</span>
                Controls
            </h3>

            {/* Game Status */}
            <div className={`game-status ${isGameOver ? 'game-over' : ''}`}>
                {statusMessage(gameStatus)}
            </div>

            {/* Loading indicator */}
            {isLoading && (
                <div className="ai-thinking">
                    <div className="thinking-dots">
                        <span></span><span></span><span></span>
                    </div>
                    AI is thinking...
                </div>
            )}

            {/* Difficulty Selector */}
            <div className="difficulty-section">
                <label className="difficulty-label">AI Difficulty</label>
                <div className="difficulty-buttons">
                    {([1, 2, 3, 4, 5] as AILevel[]).map((level) => (
                        <button
                            key={level}
                            className={`difficulty-btn ${aiLevel === level ? 'active' : ''}`}
                            onClick={() => onAILevelChange(level)}
                            title={AI_LEVEL_NAMES[level]}
                        >
                            <span className="difficulty-num">{level}</span>
                            <span className="difficulty-name">{AI_LEVEL_NAMES[level]}</span>
                        </button>
                    ))}
                </div>
            </div>

            {/* New Game Button */}
            <button
                className="new-game-btn"
                onClick={onNewGame}
                disabled={isLoading}
            >
                🎮 New Game
            </button>
        </div>
    );
};

export default Controls;
