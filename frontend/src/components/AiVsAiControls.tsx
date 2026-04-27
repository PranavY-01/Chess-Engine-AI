import React from 'react';
import './AiVsAiControls.css';

interface Props {
  speed: number;
  paused: boolean;
  onSpeedChange: (v: number) => void;
  onPauseToggle: () => void;
  onReset: () => void;
}

const AiVsAiControls: React.FC<Props> = ({ speed, paused, onSpeedChange, onPauseToggle, onReset }) => {
  const label = speed <= 1 ? 'Slow' : speed <= 2 ? 'Normal' : 'Fast';
  return (
    <section className="aivai-controls">
      <label>Simulation speed: {label}</label>
      <input min={1} max={3} step={1} type="range" value={speed} onChange={(e) => onSpeedChange(Number(e.target.value))} />
      <div className="aivai-actions">
        <button onClick={onPauseToggle}>{paused ? 'Resume' : 'Pause'}</button>
        <button onClick={onReset}>Reset</button>
      </div>
    </section>
  );
};

export default AiVsAiControls;
