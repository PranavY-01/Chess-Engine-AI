"""
Level 2 AI — Greedy.
Evaluates each legal move at depth 1 and picks the best one.
"""
import random
from engine.move_generator import Move
from engine.move_validator import MoveValidator
from ai.evaluation import evaluate


class GreedyAI:
    """Greedy AI that picks the move with the best immediate evaluation."""

    def __init__(self):
        self.validator = MoveValidator()

    def get_best_move(self, game_state) -> Move | None:
        """Return the greedy best move for the current position."""
        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            return None

        color = game_state.turn
        best_score = float('-inf') if color == 'w' else float('inf')
        best_moves = []

        for move in legal_moves:
            gs_copy = game_state.copy()
            gs_copy.make_move_no_validate(move)
            score = evaluate(gs_copy)

            if color == 'w':
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
