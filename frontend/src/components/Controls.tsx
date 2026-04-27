/**
 * Controls component with mode and demonstrator selectors.
 */
import React from 'react';
import type { GameStatus } from '../types/chessTypes';
import type { AILevel } from '../config/demonstrators';
import { DEMONSTRATOR_LIST } from '../config/demonstrators';
import './Controls.css';

interface ControlsProps {
    mode: 'human-vs-ai' | 'ai-vs-ai';
    onModeChange: (mode: 'human-vs-ai' | 'ai-vs-ai') => void;
    whiteLevel: AILevel;
    blackLevel: AILevel;
    onWhiteLevelChange: (level: AILevel) => void;
    onBlackLevelChange: (level: AILevel) => void;
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
    mode,
    onModeChange,
    whiteLevel,
    blackLevel,
    onWhiteLevelChange,
    onBlackLevelChange,
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
                <label className="difficulty-label">Simulation Mode</label>
                <div className="mode-buttons">
                    <button className={mode === 'human-vs-ai' ? 'active' : ''} onClick={() => onModeChange('human-vs-ai')}>Human vs AI</button>
                    <button className={mode === 'ai-vs-ai' ? 'active' : ''} onClick={() => onModeChange('ai-vs-ai')}>AI vs AI</button>
                </div>
            </div>

            <div className="difficulty-section">
                <label className="difficulty-label">White Demonstrator</label>
                <div className="difficulty-buttons">
                    {DEMONSTRATOR_LIST.map((cfg) => (
                        <button
                            key={`w-${cfg.id}`}
                            className={`difficulty-btn ${whiteLevel === cfg.level ? 'active' : ''}`}
                            style={{ borderColor: whiteLevel === cfg.level ? cfg.accent : undefined }}
                            onClick={() => onWhiteLevelChange(cfg.level)}
                        >
                            <span className="difficulty-num">{cfg.avatar}</span>
                            <span className="difficulty-name">{cfg.name}</span>
                        </button>
                    ))}
                </div>
            </div>

            {mode === 'ai-vs-ai' && (
                <div className="difficulty-section">
                    <label className="difficulty-label">Black Demonstrator</label>
                    <div className="difficulty-buttons">
                        {DEMONSTRATOR_LIST.map((cfg) => (
                            <button
                                key={`b-${cfg.id}`}
                                className={`difficulty-btn ${blackLevel === cfg.level ? 'active' : ''}`}
                                style={{ borderColor: blackLevel === cfg.level ? cfg.accent : undefined }}
                                onClick={() => onBlackLevelChange(cfg.level)}
                            >
                                <span className="difficulty-num">{cfg.avatar}</span>
                                <span className="difficulty-name">{cfg.name}</span>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* New Game Button */}
            <button
                className="new-game-btn"
                onClick={onNewGame}
                disabled={isLoading}
            >
                Start Session
            </button>
        </div>
    );
};

export default Controls;
