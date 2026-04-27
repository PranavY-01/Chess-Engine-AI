import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { useGameStore } from '../store/gameStore';

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const setTheme = useGameStore((s) => s.setTheme);

  const onClick = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    toggleTheme();
    setTheme(next);
  };

  return (
    <button className="theme-toggle" onClick={onClick} title="Toggle theme">
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  );
};

export default ThemeToggle;
