/**
 * SuggestionsPanel — shows top 3 AI move suggestions with evaluation scores.
 */
import React from 'react';
import type { TopMove } from '../types/chessTypes';
import './SuggestionsPanel.css';

interface SuggestionsPanelProps {
    suggestions: TopMove[];
    loading: boolean;
}

const SuggestionsPanel: React.FC<SuggestionsPanelProps> = ({ suggestions, loading }) => {
    const maxAbsScore = Math.max(
        ...suggestions.map((s) => Math.abs(s.score)),
        1
    );

    return (
        <div className="suggestions-panel">
            <h3 className="panel-title">
                <span className="panel-icon">🧠</span>
                Best Moves
            </h3>

            {loading ? (
                <div className="suggestions-loading">
                    <div className="loading-spinner" />
                    Analyzing...
                </div>
            ) : suggestions.length === 0 ? (
                <div className="no-suggestions">No suggestions available</div>
            ) : (
                <div className="suggestions-list">
                    {suggestions.map((s, idx) => {
                        const barWidth = Math.min(Math.abs(s.score) / maxAbsScore * 100, 100);
                        const isPositive = s.score >= 0;

                        return (
                            <div key={idx} className={`suggestion-item rank-${idx + 1}`}>
                                <div className="suggestion-rank">#{idx + 1}</div>
                                <div className="suggestion-details">
                                    <div className="suggestion-move">{s.move}</div>
                                    <div className="eval-bar-container">
                                        <div
                                            className={`eval-bar ${isPositive ? 'eval-positive' : 'eval-negative'}`}
                                            style={{ width: `${barWidth}%` }}
                                        />
                                    </div>
                                </div>
                                <div className={`suggestion-score ${isPositive ? 'score-positive' : 'score-negative'}`}>
                                    {isPositive ? '+' : ''}{s.score.toFixed(2)}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default SuggestionsPanel;
