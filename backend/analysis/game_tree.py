"""
Game tree analyzer.
Runs alpha-beta search and collects scored root moves for analysis.
"""
from engine.move_validator import MoveValidator
from ai.evaluation import evaluate
from utils.constants import PIECE_VALUES


class GameTreeAnalyzer:
    """Analyzes the game tree and scores all legal moves."""

    def __init__(self, depth: int = 3):
        self.depth = depth
        self.validator = MoveValidator()

    def analyze(self, game_state) -> list[tuple]:
        """Analyze all legal moves and return a sorted list of (move, score).

        Sorted by score: best for the current side first.
        """
        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            return []

        color = game_state.turn
        scored_moves = []

        for move in legal_moves:
            gs_copy = game_state.copy()
            gs_copy.make_move_no_validate(move)
            score = self._alpha_beta(
                gs_copy, self.depth - 1,
                float('-inf'), float('inf'),
                color != 'w'  # next player is maximizing if they're white
            )
            scored_moves.append((move, score))

        # Sort: best for current side first
        if color == 'w':
            scored_moves.sort(key=lambda x: x[1], reverse=True)
        else:
            scored_moves.sort(key=lambda x: x[1])

        return scored_moves

    def _alpha_beta(self, game_state, depth: int, alpha: float, beta: float,
                    is_maximizing: bool) -> int:
        """Alpha-beta search for analysis."""
        if depth == 0:
            return evaluate(game_state)

        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            if self.validator.is_in_check(game_state.board, game_state.turn):
                return -100000 if is_maximizing else 100000
            return 0

        # Simple move ordering: captures first
        legal_moves.sort(
            key=lambda m: PIECE_VALUES.get(
                m.captured_piece[1], 0) if m.captured_piece else 0,
            reverse=True
        )

        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                gs_copy = game_state.copy()
                gs_copy.make_move_no_validate(move)
                eval_score = self._alpha_beta(gs_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                gs_copy = game_state.copy()
                gs_copy.make_move_no_validate(move)
                eval_score = self._alpha_beta(gs_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
