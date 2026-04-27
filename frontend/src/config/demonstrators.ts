export type DemonstratorId = 'rusty' | 'goblin' | 'sage' | 'phantom' | 'oracle';

export type AILevel = 1 | 2 | 3 | 4 | 5;

export interface DemonstratorConfig {
  level: AILevel;
  id: DemonstratorId;
  name: string;
  avatar: string;
  accent: string;
  algorithm: string;
  personality: string;
}

export const DEMONSTRATORS: Record<AILevel, DemonstratorConfig> = {
  1: {
    level: 1,
    id: 'rusty',
    name: 'Rusty',
    avatar: '🤖',
    accent: '#8a8f98',
    algorithm: 'Random',
    personality: 'Confused and unpredictable',
  },
  2: {
    level: 2,
    id: 'goblin',
    name: 'Goblin',
    avatar: '👺',
    accent: '#e67e22',
    algorithm: 'Greedy',
    personality: 'Impulsive and short-sighted',
  },
  3: {
    level: 3,
    id: 'sage',
    name: 'Sage',
    avatar: '🧙',
    accent: '#2ecc71',
    algorithm: 'Minimax',
    personality: 'Methodical and patient',
  },
  4: {
    level: 4,
    id: 'phantom',
    name: 'Phantom',
    avatar: '👻',
    accent: '#3498db',
    algorithm: 'Alpha-Beta',
    personality: 'Calculating and efficient',
  },
  5: {
    level: 5,
    id: 'oracle',
    name: 'Oracle',
    avatar: '🔮',
    accent: '#9b59b6',
    algorithm: 'Advanced',
    personality: 'Deeply analytical and precise',
  },
};

export const DEMONSTRATOR_LIST = Object.values(DEMONSTRATORS);
