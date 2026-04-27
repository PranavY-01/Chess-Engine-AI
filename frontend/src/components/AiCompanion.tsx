import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useGameStore } from '../store/gameStore';
import { DEMONSTRATORS } from '../config/demonstrators';
import * as api from '../services/api';
import './AiCompanion.css';

const AiCompanion: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [explaining, setExplaining] = useState(false);
  const messagesRef = useRef<HTMLDivElement>(null);
  const {
    chatMessages,
    sessionActive,
    mode,
    whiteDemonstrator,
    blackDemonstrator,
    addChatMessage,
  } = useGameStore();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [chatMessages]);

  // Auto-open when a new AI message arrives
  useEffect(() => {
    if (chatMessages.length > 0 && sessionActive) {
      setIsOpen(true);
    }
  }, [chatMessages.length, sessionActive]);

  const handleExplain = useCallback(async () => {
    if (explaining || chatMessages.length === 0) return;

    // Find the last move message in chat
    const lastMoveMsg = [...chatMessages].reverse().find((m) => m.move);
    if (!lastMoveMsg) {
      addChatMessage({
        type: 'system',
        text: 'No move to explain yet.',
        timestamp: Date.now(),
      });
      return;
    }

    // Determine which demonstrator made the last move
    // In human-vs-ai, AI is always black (whiteDemonstrator is the AI level)
    // In ai-vs-ai, we figure out from the move text
    let demonstratorLevel = whiteDemonstrator;
    if (mode === 'ai-vs-ai') {
      const whiteDem = DEMONSTRATORS[whiteDemonstrator];
      const blackDem = DEMONSTRATORS[blackDemonstrator];
      // Check which demonstrator name is in the message text
      if (lastMoveMsg.text.includes(blackDem.name)) {
        demonstratorLevel = blackDemonstrator;
      } else if (lastMoveMsg.text.includes(whiteDem.name)) {
        demonstratorLevel = whiteDemonstrator;
      }
    }

    const demonstrator = DEMONSTRATORS[demonstratorLevel];
    const moveLabel = lastMoveMsg.move || '?';

    setExplaining(true);
    addChatMessage({
      type: 'system',
      text: `Asking ${demonstrator.name} to explain...`,
      timestamp: Date.now(),
    });

    try {
      const response = await api.explainMove({
        demonstrator_id: demonstrator.id,
        chosen_move: { move: moveLabel, score: 0 },
        alternatives: [],
        board_context: {
          material_balance: 0,
          move_number: 0,
          is_capture: false,
        },
      });
      addChatMessage({
        type: 'ai',
        text: response.explanation,
        timestamp: Date.now(),
      });
    } catch {
      addChatMessage({
        type: 'ai',
        text: "Couldn't get reasoning right now — try again.",
        timestamp: Date.now(),
      });
    } finally {
      setExplaining(false);
    }
  }, [explaining, chatMessages, mode, whiteDemonstrator, blackDemonstrator, addChatMessage]);

  const hasUnread = chatMessages.length > 0 && !isOpen;

  return (
    <>
      {/* Toggle button */}
      <button
        className={`ai-companion-toggle ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title="AI Companion"
      >
        {isOpen ? '✕' : '🤖'}
        {hasUnread && <span className="ai-companion-badge" />}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div className="ai-companion-panel">
          <div className="ai-companion-header">
            <div className="ai-companion-avatar">🧠</div>
            <div className="ai-companion-title">
              <h4>AI Companion</h4>
              <span>On-demand reasoning</span>
            </div>
            <div className="ai-companion-status" />
          </div>

          <div className="ai-companion-messages" ref={messagesRef}>
            {chatMessages.length === 0 ? (
              <div className="ai-companion-empty">
                <div className="ai-companion-empty-icon">🤖</div>
                <p>Start a game session. Click "Why this move?" after any AI move to get algorithm reasoning.</p>
              </div>
            ) : (
              chatMessages.map((msg, i) => (
                <div key={i} className={`ai-companion-msg ${msg.type}`}>
                  {msg.move && <span className="msg-move">{msg.move}</span>}
                  <TypewriterText text={msg.text} animate={i === chatMessages.length - 1 && msg.type === 'ai'} />
                </div>
              ))
            )}
          </div>

          {sessionActive && (
            <div className="ai-companion-actions">
              <button
                className="ai-companion-explain-btn"
                onClick={handleExplain}
                disabled={explaining || chatMessages.length === 0}
              >
                {explaining ? (
                  <><span className="spinner-sm" /> Thinking...</>
                ) : (
                  <>💡 Why this move?</>
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </>
  );
};

/** Typewriter effect for the latest AI message */
const TypewriterText: React.FC<{ text: string; animate: boolean }> = ({ text, animate }) => {
  const [visible, setVisible] = useState(animate ? '' : text);

  useEffect(() => {
    if (!animate) {
      setVisible(text);
      return;
    }
    let i = 0;
    setVisible('');
    const timer = setInterval(() => {
      i += 1;
      setVisible(text.slice(0, i));
      if (i >= text.length) clearInterval(timer);
    }, 10);
    return () => clearInterval(timer);
  }, [text, animate]);

  return <>{visible}</>;
};

export default AiCompanion;
