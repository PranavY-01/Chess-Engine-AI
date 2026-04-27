import React, { useEffect, useState } from 'react';
import './ReasoningPanel.css';

interface ReasoningPanelProps {
  title: string;
  text: string;
  loading: boolean;
  onExplainClick?: () => void;
  explainLabel?: string;
}

const ReasoningPanel: React.FC<ReasoningPanelProps> = ({
  title,
  text,
  loading,
  onExplainClick,
  explainLabel = 'Give Explanation',
}) => {
  const [visibleText, setVisibleText] = useState('');

  useEffect(() => {
    if (!text) {
      setVisibleText('');
      return;
    }
    let i = 0;
    setVisibleText('');
    const timer = setInterval(() => {
      i += 1;
      setVisibleText(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(timer);
      }
    }, 8);
    return () => clearInterval(timer);
  }, [text]);

  return (
    <section className="reasoning-panel">
      <div className="reasoning-header">
        <h3>{title}</h3>
        {onExplainClick && (
          <button className="explain-btn" onClick={onExplainClick} disabled={loading}>
            {explainLabel}
          </button>
        )}
      </div>
      {loading ? (
        <div className="reasoning-skeleton">
          <span />
          <span />
          <span />
        </div>
      ) : (
        <p className="reasoning-text">
          {visibleText || 'Reasoning will appear here after explanation is requested.'}
        </p>
      )}
    </section>
  );
};

export default ReasoningPanel;
