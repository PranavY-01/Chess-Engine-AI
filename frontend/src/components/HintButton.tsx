import React from 'react';
import './HintButton.css';

interface HintButtonProps {
  loading: boolean;
  onAsk: () => void;
}

const HintButton: React.FC<HintButtonProps> = ({ loading, onAsk }) => {
  return (
    <button className="hint-btn" onClick={onAsk} disabled={loading}>
      {loading ? 'Consulting Oracle...' : 'Ask Oracle'}
    </button>
  );
};

export default HintButton;
