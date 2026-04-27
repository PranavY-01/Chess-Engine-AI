import React, { useState } from 'react';
import { useGameStore } from '../store/gameStore';
import type { GameHistoryEntry } from '../types/chessTypes';
import './GameHistoryPage.css';

function getResultLabel(result: string): { text: string; cls: string } {
  if (result.includes('checkmate_white')) return { text: 'White Win', cls: 'win' };
  if (result.includes('checkmate_black')) return { text: 'Black Win', cls: 'loss' };
  if (result.includes('draw') || result.includes('stalemate')) return { text: 'Draw', cls: 'draw' };
  if (result === 'active') return { text: 'Incomplete', cls: 'draw' };
  return { text: result, cls: 'draw' };
}

const GameHistoryPage: React.FC = () => {
  const { gameHistory, clearHistory } = useGameStore();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="history-page">
      <div className="history-header">
        <h1 className="history-title">Game History</h1>
        {gameHistory.length > 0 && (
          <button className="history-clear-btn" onClick={clearHistory}>
            Clear All
          </button>
        )}
      </div>

      {gameHistory.length === 0 ? (
        <div className="history-empty">
          <span className="history-empty-icon">☰</span>
          <div className="history-empty-title">No games yet</div>
          <div className="history-empty-sub">
            Play a game and it will appear here when the session ends.
          </div>
        </div>
      ) : (
        <div className="history-list">
          {gameHistory.map((game: GameHistoryEntry) => {
            const result = getResultLabel(game.result);
            const isExpanded = expandedId === game.id;

            return (
              <div key={game.id} className="history-card">
                <button
                  className="history-card-main"
                  onClick={() => toggleExpand(game.id)}
                >
                  <span className="history-card-mode">
                    {game.mode === 'human-vs-ai' ? 'H vs AI' : 'AI vs AI'}
                  </span>
                  <div className="history-card-info">
                    <div className="history-card-matchup">
                      {game.whiteAlgorithm} vs {game.blackAlgorithm}
                    </div>
                    <div className="history-card-meta">
                      <span>{game.totalMoves} moves</span>
                      <span>{new Date(game.date).toLocaleDateString()}</span>
                      <span>{new Date(game.date).toLocaleTimeString()}</span>
                    </div>
                  </div>
                  <span className={`history-card-result ${result.cls}`}>
                    {result.text}
                  </span>
                  <span className={`history-card-arrow ${isExpanded ? 'open' : ''}`}>
                    ▾
                  </span>
                </button>

                {isExpanded && (
                  <div className="history-card-detail">
                    <div className="history-detail-label">Move History</div>
                    <div className="history-detail-moves">
                      {game.moves.length === 0 ? (
                        <span className="history-detail-move" style={{ color: 'var(--text-muted)' }}>
                          No moves recorded
                        </span>
                      ) : (
                        game.moves.map((move, i) => (
                          <span key={i} className="history-detail-move">{move}</span>
                        ))
                      )}
                    </div>
                    <div className="history-detail-eval">
                      Final evaluation: <strong>{game.finalEvaluation > 0 ? '+' : ''}{game.finalEvaluation.toFixed(2)}</strong>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default GameHistoryPage;
