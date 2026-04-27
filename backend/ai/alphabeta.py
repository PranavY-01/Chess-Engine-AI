"""
Level 4 AI — Alpha-Beta Pruning.
Minimax with alpha-beta pruning at depth 5, MVV-LVA move ordering,
and killer move heuristic.
"""
import random
from engine.move_generator import Move
from engine.move_validator import MoveValidator
from ai.evaluation import evaluate
from utils.constants import PIECE_VALUES


class AlphaBetaAI:
    """Alpha-Beta pruning AI with MVV-LVA ordering and killer moves."""

    def __init__(self, depth: int = 4):
        self.depth = depth
        self.validator = MoveValidator()
        self.killer_moves: dict[int, list[Move]] = {}

    def get_best_move(self, game_state) -> Move | None:
        """Return the best move using alpha-beta search."""
        self.killer_moves = {}
        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            return None

        legal_moves = self._order_moves(legal_moves, game_state, self.depth)

        color = game_state.turn
        is_maximizing = (color == 'w')
        best_score = float('-inf') if is_maximizing else float('inf')
        best_moves: list[Move] = []
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
        """Recursive alpha-beta search with move ordering and killer moves."""
        if depth == 0:
            return evaluate(game_state)

        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            if self.validator.is_in_check(game_state.board, game_state.turn):
                return -(100000 + depth) if is_maximizing else (100000 + depth)
            return 0  # Stalemate

        legal_moves = self._order_moves(legal_moves, game_state, depth)

        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                gs_copy = game_state.copy()
                gs_copy.make_move_no_validate(move)
                eval_score = self._alpha_beta(gs_copy, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    self._store_killer(move, depth)
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                gs_copy = game_state.copy()
                gs_copy.make_move_no_validate(move)
                eval_score = self._alpha_beta(gs_copy, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                beta = min(beta, eval_score)
                if beta <= alpha:
                    self._store_killer(move, depth)
                    break
            return min_eval

    def _order_moves(self, moves: list[Move], game_state, depth: int) -> list[Move]:
        """Order moves: captures by MVV-LVA, then promotions, then killers, then quiet."""
        scored = []
        killers = self.killer_moves.get(depth, [])
        for move in moves:
            score = 0
            # MVV-LVA for captures: 10*victim - attacker gives PxQ highest score
            if move.captured_piece is not None:
                victim_val = PIECE_VALUES.get(move.captured_piece[1], 0)
                attacker = game_state.board.get_piece(move.start_row, move.start_col)
                attacker_val = PIECE_VALUES.get(attacker[1], 0) if attacker else 0
                score += 10000 + 10 * victim_val - attacker_val
            # Promotions
            if move.promotion_piece:
                score += 9000
            # Killer moves
            if move in killers:
                score += 5000
            scored.append((score, move))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored]

    def _store_killer(self, move: Move, depth: int):
        """Store quiet moves that cause cutoffs as killer moves."""
        if move.captured_piece is not None:
            return
        if depth not in self.killer_moves:
            self.killer_moves[depth] = []
        killers = self.killer_moves[depth]
        if move not in killers:
            killers.insert(0, move)
            if len(killers) > 2:
                killers.pop()
