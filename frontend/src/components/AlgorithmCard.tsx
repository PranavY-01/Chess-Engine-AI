import React from 'react';
import type { DemonstratorConfig } from '../config/demonstrators';
import './AlgorithmCard.css';

interface AlgorithmCardProps {
  demonstrator: DemonstratorConfig;
  side?: 'white' | 'black';
  selected?: boolean;
  onClick?: () => void;
}

const AlgorithmCard: React.FC<AlgorithmCardProps> = ({ demonstrator, side, selected, onClick }) => {
  return (
    <button
      className={`algorithm-card ${selected ? 'selected' : ''}`}
      onClick={onClick}
      style={{ ['--accent' as string]: demonstrator.accent }}
    >
      <div className="algorithm-card-accent" />
      <div className="algorithm-card-header">
        <span className="algorithm-avatar">{demonstrator.avatar}</span>
        <div>
          <div className="algorithm-name">{demonstrator.name}</div>
          <div className="algorithm-meta">{demonstrator.algorithm}</div>
        </div>
      </div>
      <p className="algorithm-personality">{demonstrator.personality}</p>
      {side && <div className="algorithm-side">{side === 'white' ? 'White demonstrator' : 'Black demonstrator'}</div>}
    </button>
  );
};

export default AlgorithmCard;
