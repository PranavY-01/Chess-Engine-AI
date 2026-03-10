"""
Level 5 AI — Advanced.
Alpha-beta with move ordering, killer moves, history heuristic,
and quiescence search for a stronger playing style.
"""
import random
from engine.move_generator import Move
from engine.move_validator import MoveValidator
from ai.evaluation import evaluate
from utils.constants import PIECE_VALUES


class AdvancedAI:
    """Advanced AI with move ordering, killer moves, and quiescence search."""

    def __init__(self, depth: int = 4):
        self.depth = depth
        self.validator = MoveValidator()
        self.killer_moves = {}     # depth -> [move1, move2]
        self.history_table = {}    # (start, end) -> score
        self.nodes_searched = 0

    def get_best_move(self, game_state) -> Move | None:
        """Return the best move using advanced alpha-beta search."""
        self.killer_moves = {}
        self.history_table = {}
        self.nodes_searched = 0

        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            return None

        # Order moves at root
        legal_moves = self._order_moves(legal_moves, game_state, self.depth)

        color = game_state.turn
        is_maximizing = (color == 'w')
        best_score = float('-inf') if is_maximizing else float('inf')
        best_moves = []
        alpha = float('-inf')
        beta = float('inf')

        for move in legal_moves:
            gs_copy = game_state.copy()
            gs_copy.make_move_no_validate(move)
            score = self._alpha_beta(gs_copy, self.depth - 1, alpha, beta,
                                     not is_maximizing)

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
        """Alpha-beta search with move ordering and quiescence."""
        self.nodes_searched += 1

        if depth == 0:
            return self._quiescence(game_state, alpha, beta, is_maximizing, 4)

        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            if self.validator.is_in_check(game_state.board, game_state.turn):
                return -100000 if is_maximizing else 100000
            return 0

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

    def _quiescence(self, game_state, alpha: float, beta: float,
                    is_maximizing: bool, max_depth: int) -> int:
        """Quiescence search: only search captures to avoid horizon effect."""
        stand_pat = evaluate(game_state)

        if max_depth == 0:
            return stand_pat

        if is_maximizing:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)

        legal_moves = self.validator.get_legal_moves(game_state)
        # Only consider captures
        captures = [m for m in legal_moves if m.captured_piece is not None]

        if not captures:
            return stand_pat

        # Order captures by MVV-LVA
        captures.sort(key=lambda m: self._mvv_lva_score(m), reverse=True)

        if is_maximizing:
            for move in captures:
                gs_copy = game_state.copy()
                gs_copy.make_move_no_validate(move)
                score = self._quiescence(gs_copy, alpha, beta, False, max_depth - 1)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return alpha
        else:
            for move in captures:
                gs_copy = game_state.copy()
                gs_copy.make_move_no_validate(move)
                score = self._quiescence(gs_copy, alpha, beta, True, max_depth - 1)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return beta

    def _order_moves(self, moves: list[Move], game_state, depth: int) -> list[Move]:
        """Order moves for better pruning: captures first, then killers, then history."""
        scored_moves = []
        for move in moves:
            score = 0
            # 1. Captures scored by MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
            if move.captured_piece is not None:
                score += 10000 + self._mvv_lva_score(move)
            # 2. Killer moves
            killers = self.killer_moves.get(depth, [])
            if move in killers:
                score += 5000
            # 3. History heuristic
            key = (move.start_row, move.start_col, move.end_row, move.end_col)
            score += self.history_table.get(key, 0)
            # 4. Promotions
            if move.promotion_piece:
                score += 8000
            scored_moves.append((score, move))

        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored_moves]

    def _mvv_lva_score(self, move: Move) -> int:
        """MVV-LVA: Most Valuable Victim - Least Valuable Attacker."""
        if move.captured_piece is None:
            return 0
        victim_value = PIECE_VALUES.get(move.captured_piece[1], 0)
        # We don't have the attacker piece stored, but we can infer from position
        return victim_value

    def _store_killer(self, move: Move, depth: int):
        """Store a killer move (causes cutoff but isn't a capture)."""
        if move.captured_piece is not None:
            return  # only store quiet moves as killers
        if depth not in self.killer_moves:
            self.killer_moves[depth] = []
        killers = self.killer_moves[depth]
        if move not in killers:
            killers.insert(0, move)
            if len(killers) > 2:
                killers.pop()
        # Update history table
        key = (move.start_row, move.start_col, move.end_row, move.end_col)
        self.history_table[key] = self.history_table.get(key, 0) + depth * depth
