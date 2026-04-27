import React from 'react';
import './BranchBanner.css';

const BranchBanner: React.FC<{ rank: number }> = ({ rank }) => {
  return <div className="branch-banner">Exploring Branch - Ranked #{rank} Move</div>;
};

export default BranchBanner;
