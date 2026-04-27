import React from 'react';
import './AccuracyMeter.css';

interface AccuracyMeterProps {
  evaluation: number;    // e.g. +0.16 (positive = white advantage)
  whiteScore: number;    // 0-100 percentage
  blackScore: number;    // 0-100 percentage
}

const AccuracyMeter: React.FC<AccuracyMeterProps> = ({
  evaluation,
  whiteScore,
  blackScore,
}) => {
  const whitePct = Math.max(2, Math.min(98, whiteScore));
  const isWhiteWinning = evaluation > 0.5;
  const isBlackWinning = evaluation < -0.5;

  const scoreText = evaluation > 0
    ? `+${evaluation.toFixed(1)}`
    : evaluation.toFixed(1);

  // Position the score label near the divider line
  const scoreBottom = whitePct;
  const isScoreInWhiteZone = whitePct > 50;

  return (
    <div className="accuracy-meter">
      <span className="accuracy-meter-side">BLACK</span>
      <span className="accuracy-meter-label">{blackScore.toFixed(0)}%</span>

      <div
        className={`accuracy-meter-bar-wrapper ${
          isWhiteWinning ? 'winning-white' : isBlackWinning ? 'winning-black' : ''
        }`}
      >
        {/* White fill from bottom */}
        <div
          className="accuracy-meter-white"
          style={{ height: `${whitePct}%` }}
        />

        {/* Divider line */}
        <div
          className="accuracy-meter-divider"
          style={{ bottom: `${whitePct}%` }}
        />

        {/* Score label */}
        <div
          className={`accuracy-meter-score ${isScoreInWhiteZone ? 'score-white' : 'score-black'}`}
          style={{ bottom: `calc(${scoreBottom}% - 11px)` }}
        >
          {scoreText}
        </div>
      </div>

      <span className="accuracy-meter-label">{whiteScore.toFixed(0)}%</span>
      <span className="accuracy-meter-side">WHITE</span>
    </div>
  );
};

export default AccuracyMeter;
