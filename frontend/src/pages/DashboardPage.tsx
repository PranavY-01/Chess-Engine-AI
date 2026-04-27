import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../store/gameStore';
import './DashboardPage.css';

function getResultLabel(result: string): { text: string; cls: string } {
  if (result.includes('checkmate_white')) return { text: 'White Win', cls: 'win' };
  if (result.includes('checkmate_black')) return { text: 'Black Win', cls: 'loss' };
  if (result.includes('draw') || result.includes('stalemate')) return { text: 'Draw', cls: 'draw' };
  if (result === 'active') return { text: 'Ongoing', cls: 'draw' };
  return { text: result, cls: 'draw' };
}

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { gameHistory } = useGameStore();

  const totalGames = gameHistory.length;
  const wins = gameHistory.filter((g) => g.result === 'checkmate_white').length;
  const winRate = totalGames > 0 ? Math.round((wins / totalGames) * 100) : 0;
  const recentGames = gameHistory.slice(0, 3);

  return (
    <div className="dashboard-page">
      {/* Hero */}
      <div className="dashboard-hero">
        <h1 className="dashboard-hero-title">ChessAlgos</h1>
        <p className="dashboard-hero-sub">
          Explore AI algorithm behavior through interactive chess simulations.
          Watch algorithms think, compare strategies, and learn how each one decides.
        </p>
      </div>

      {/* Mode Cards */}
      <div className="dashboard-modes">
        <button
          className="dashboard-mode-card"
          onClick={() => navigate('/human-vs-ai')}
        >
          <div className="dashboard-mode-icon">⚔</div>
          <div className="dashboard-mode-title">Human vs AI</div>
          <div className="dashboard-mode-desc">
            Play against an AI algorithm and watch the companion explain every decision in real time.
          </div>
          <div className="dashboard-mode-action">
            Start Session →
          </div>
        </button>

        <button
          className="dashboard-mode-card"
          onClick={() => navigate('/ai-vs-ai')}
        >
          <div className="dashboard-mode-icon">⚡</div>
          <div className="dashboard-mode-title">AI vs AI</div>
          <div className="dashboard-mode-desc">
            Pit two different algorithms against each other and observe their contrasting strategies.
          </div>
          <div className="dashboard-mode-action">
            Start Simulation →
          </div>
        </button>
      </div>

      {/* Stats */}
      <div className="dashboard-stats">
        <div className="dashboard-stat-card">
          <div className="dashboard-stat-value">{totalGames}</div>
          <div className="dashboard-stat-label">Total Games</div>
        </div>
        <div className="dashboard-stat-card">
          <div className="dashboard-stat-value">{winRate}%</div>
          <div className="dashboard-stat-label">Win Rate</div>
        </div>
        <div className="dashboard-stat-card">
          <div className="dashboard-stat-value">{wins}</div>
          <div className="dashboard-stat-label">Victories</div>
        </div>
      </div>

      {/* Recent Games */}
      <div className="dashboard-recent">
        <div className="dashboard-section-title">☰ Recent Games</div>
        {recentGames.length === 0 ? (
          <div className="dashboard-empty-history">
            No games played yet. Start a session to begin!
          </div>
        ) : (
          <div className="dashboard-recent-list">
            {recentGames.map((game) => {
              const result = getResultLabel(game.result);
              return (
                <div key={game.id} className="dashboard-recent-item">
                  <span className="dashboard-recent-mode">
                    {game.mode === 'human-vs-ai' ? 'H vs AI' : 'AI vs AI'}
                  </span>
                  <div className="dashboard-recent-info">
                    <strong>{game.whiteAlgorithm} vs {game.blackAlgorithm}</strong>
                    <span>{game.totalMoves} moves · {new Date(game.date).toLocaleDateString()}</span>
                  </div>
                  <span className={`dashboard-recent-result ${result.cls}`}>
                    {result.text}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
