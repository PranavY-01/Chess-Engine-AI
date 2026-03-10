"""
Level 4 AI — Alpha-Beta Pruning.
Minimax with alpha-beta pruning at depth 4.
"""
import random
from engine.move_generator import Move
from engine.move_validator import MoveValidator
from ai.evaluation import evaluate


class AlphaBetaAI:
    """Alpha-Beta pruning AI for more efficient search."""

    def __init__(self, depth: int = 4):
        self.depth = depth
        self.validator = MoveValidator()

    def get_best_move(self, game_state) -> Move | None:
        """Return the best move using alpha-beta search."""
        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            return None

        color = game_state.turn
        is_maximizing = (color == 'w')
        best_score = float('-inf') if is_maximizing else float('inf')
        best_moves = []
        alpha = float('-inf')
        beta = float('inf')

        for move in legal_moves:
            gs_copy = game_state.copy()
            gs_copy.make_move_no_validate(move)
            score = self._alpha_beta(gs_copy, self.depth - 1, alpha, beta, not is_maximizing)

            if is_maximizing:
                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)
                alpha = max(alpha, score)
            else:
                if score < best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)
                beta = min(beta, score)

        return random.choice(best_moves) if best_moves else None

    def _alpha_beta(self, game_state, depth: int, alpha: float, beta: float,
                    is_maximizing: bool) -> int:
        """Recursive alpha-beta search."""
        if depth == 0:
            return evaluate(game_state)

        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            if self.validator.is_in_check(game_state.board, game_state.turn):
                return -100000 if is_maximizing else 100000
            return 0

        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                gs_copy = game_state.copy()
                gs_copy.make_move_no_validate(move)
                eval_score = self._alpha_beta(gs_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
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
                    break  # Alpha cutoff
            return min_eval
