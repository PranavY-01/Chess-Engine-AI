import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { useGameStore } from '../store/gameStore';
import { DEMONSTRATOR_LIST } from '../config/demonstrators';
import type { AILevel } from '../config/demonstrators';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { whiteDemonstrator, setWhiteDemonstrator } = useGameStore();

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-header">
        <div className="sidebar-logo">♟</div>
        <div className="sidebar-brand">
          <span className="sidebar-brand-name">ChessAlgos</span>
          <span className="sidebar-brand-sub">Algorithm Simulator</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Menu</div>
        <NavLink to="/" end className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <span className="sidebar-link-icon">◉</span>
          <span className="sidebar-link-text">Dashboard</span>
        </NavLink>
        <NavLink to="/human-vs-ai" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <span className="sidebar-link-icon">⚔</span>
          <span className="sidebar-link-text">Human vs AI</span>
        </NavLink>
        <NavLink to="/ai-vs-ai" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <span className="sidebar-link-icon">⚡</span>
          <span className="sidebar-link-text">AI vs AI</span>
        </NavLink>
        <NavLink to="/history" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <span className="sidebar-link-icon">☰</span>
          <span className="sidebar-link-text">Game History</span>
        </NavLink>
      </nav>

      {/* Algorithm Selector */}
      <div className="sidebar-algo-section">
        <div className="sidebar-algo-title">Algorithm</div>
        <div className="sidebar-algo-list">
          {DEMONSTRATOR_LIST.map((d) => (
            <button
              key={d.id}
              className={`sidebar-algo-btn ${whiteDemonstrator === d.level ? 'selected' : ''}`}
              onClick={() => setWhiteDemonstrator(d.level as AILevel)}
            >
              <span
                className="sidebar-algo-indicator"
                style={{ backgroundColor: d.accent }}
              />
              <span className="sidebar-algo-name">{d.name}</span>
              <span className="sidebar-algo-type">{d.algorithm}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        <button className="sidebar-theme-btn" onClick={toggleTheme}>
          <span className="sidebar-link-icon">{theme === 'dark' ? '☀' : '☾'}</span>
          <span className="sidebar-link-text">{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
