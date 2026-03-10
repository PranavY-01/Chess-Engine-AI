"""
Level 3 AI — Minimax.
Standard minimax search at depth 3.
"""
import random
from engine.move_generator import Move
from engine.move_validator import MoveValidator
from ai.evaluation import evaluate


class MinimaxAI:
    """Minimax AI with configurable depth."""

    def __init__(self, depth: int = 3):
        self.depth = depth
        self.validator = MoveValidator()

    def get_best_move(self, game_state) -> Move | None:
        """Return the best move using minimax search."""
        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            return None

        color = game_state.turn
        is_maximizing = (color == 'w')
        best_score = float('-inf') if is_maximizing else float('inf')
        best_moves = []

        for move in legal_moves:
            gs_copy = game_state.copy()
            gs_copy.make_move_no_validate(move)
            score = self._minimax(gs_copy, self.depth - 1, not is_maximizing)

            if is_maximizing:
                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)
            else:
                if score < best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)

        return random.choice(best_moves) if best_moves else None

    def _minimax(self, game_state, depth: int, is_maximizing: bool) -> int:
        """Recursive minimax search."""
        if depth == 0:
            return evaluate(game_state)

        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            if self.validator.is_in_check(game_state.board, game_state.turn):
                # Checkmate: worst possible score
                return -100000 if is_maximizing else 100000
            return 0  # Stalemate

        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                gs_copy = game_state.copy()
                gs_copy.make_move_no_validate(move)
                eval_score = self._minimax(gs_copy, depth - 1, False)
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                gs_copy = game_state.copy()
                gs_copy.make_move_no_validate(move)
                eval_score = self._minimax(gs_copy, depth - 1, True)
                min_eval = min(min_eval, eval_score)
            return min_eval
