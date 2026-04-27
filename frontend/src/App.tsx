/**
 * App component — root component with routing.
 */
import { Routes, Route } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import DashboardPage from './pages/DashboardPage';
import HumanVsAiPage from './pages/HumanVsAiPage';
import AiVsAiPage from './pages/AiVsAiPage';
import GameHistoryPage from './pages/GameHistoryPage';

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/human-vs-ai" element={<HumanVsAiPage />} />
        <Route path="/ai-vs-ai" element={<AiVsAiPage />} />
        <Route path="/history" element={<GameHistoryPage />} />
      </Route>
    </Routes>
  );
}

export default App;
