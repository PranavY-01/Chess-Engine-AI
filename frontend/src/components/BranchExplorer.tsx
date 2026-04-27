import React from 'react';
import './BranchExplorer.css';

interface BranchExplorerProps {
  active: boolean;
  progress: number;
  maxHalfMoves: number;
  onAdvance: () => void;
  onEnd: () => void;
  onMainLine: () => void;
  onBranchLine: () => void;
  showingBranch: boolean;
}

const BranchExplorer: React.FC<BranchExplorerProps> = ({
  active,
  progress,
  maxHalfMoves,
  onAdvance,
  onEnd,
  onMainLine,
  onBranchLine,
  showingBranch,
}) => {
  if (!active) return null;

  return (
    <section className="branch-explorer">
      <div className="branch-tabs">
        <button className={!showingBranch ? 'active' : ''} onClick={onMainLine}>Main Line</button>
        <button className={showingBranch ? 'active' : ''} onClick={onBranchLine}>Branch</button>
      </div>
      <div className="branch-controls">
        <span>Branch moves: {progress}/{maxHalfMoves}</span>
        <button onClick={onAdvance} disabled={progress >= maxHalfMoves}>Advance Branch</button>
        <button onClick={onEnd}>End Branch</button>
      </div>
    </section>
  );
};

export default BranchExplorer;
