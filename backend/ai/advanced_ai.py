"""
Level 5 AI — Advanced.
Alpha-beta with improved move ordering (MVV-LVA), killer moves,
history heuristic, quiescence search, and check extension.
"""
import random
from engine.move_generator import Move
from engine.move_validator import MoveValidator
from ai.evaluation import evaluate
from utils.constants import PIECE_VALUES


class AdvancedAI:
    """Advanced AI — strongest algorithmic player."""

    def __init__(self, depth: int = 4):
        self.depth = depth
        self.validator = MoveValidator()
        self.killer_moves: dict[int, list[Move]] = {}
        self.history_table: dict[tuple, int] = {}
        self.nodes_searched = 0

    def get_best_move(self, game_state) -> Move | None:
        """Return the best move using alpha-beta search."""
        self.killer_moves = {}
        self.history_table = {}
        self.nodes_searched = 0

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
        """Alpha-beta with check extension, killer/history ordering, quiescence."""
        self.nodes_searched += 1

        in_check = self.validator.is_in_check(game_state.board, game_state.turn)

        # Check extension: extend by 1 ply when in check at leaf
        if in_check and depth == 0:
            depth = 1

        if depth == 0:
            return self._quiescence(game_state, alpha, beta, is_maximizing, 2)

        legal_moves = self.validator.get_legal_moves(game_state)
        if not legal_moves:
            if in_check:
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

    def _quiescence(self, game_state, alpha: float, beta: float,
                    is_maximizing: bool, max_depth: int) -> int:
        """Quiescence search: extend captures and promotions to avoid horizon effect."""
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

        # Only consider captures and promotions
        tactical_moves = [
            m for m in legal_moves
            if m.captured_piece is not None or m.promotion_piece is not None
        ]

        if not tactical_moves:
            return stand_pat

        # Order by MVV-LVA
        tactical_moves.sort(
            key=lambda m: self._mvv_lva_score(m, game_state) + (8000 if m.promotion_piece else 0),
            reverse=True,
        )

        if is_maximizing:
            for move in tactical_moves:
                gs_copy = game_state.copy()
                gs_copy.make_move_no_validate(move)
                score = self._quiescence(gs_copy, alpha, beta, False, max_depth - 1)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return alpha
        else:
            for move in tactical_moves:
                gs_copy = game_state.copy()
                gs_copy.make_move_no_validate(move)
                score = self._quiescence(gs_copy, alpha, beta, True, max_depth - 1)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return beta

    def _order_moves(self, moves: list[Move], game_state, depth: int) -> list[Move]:
        """Order moves: captures (MVV-LVA), promotions, killers, history heuristic."""
        scored_moves = []
        killers = self.killer_moves.get(depth, [])
        for move in moves:
            score = 0
            # 1. MVV-LVA for captures: 10*victim - attacker
            if move.captured_piece is not None:
                score += 10000 + self._mvv_lva_score(move, game_state)
            # 2. Promotions
            if move.promotion_piece:
                score += 9000
            # 3. Killer moves
            if move in killers:
                score += 5000
            # 4. History heuristic
            key = (move.start_row, move.start_col, move.end_row, move.end_col)
            score += self.history_table.get(key, 0)
            scored_moves.append((score, move))

        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored_moves]

    def _mvv_lva_score(self, move: Move, game_state) -> int:
        """MVV-LVA: 10 * victim_value - attacker_value.
        PxQ = 10*900 - 100 = 8900 (excellent)
        NxQ = 10*900 - 320 = 8680 (great)
        QxQ = 10*900 - 900 = 8100 (acceptable)
        QxP = 10*100 - 900 = 100  (bad trade, search last)
        """
        if move.captured_piece is None:
            return 0
        victim_value = PIECE_VALUES.get(move.captured_piece[1], 0)
        attacker = game_state.board.get_piece(move.start_row, move.start_col)
        attacker_value = PIECE_VALUES.get(attacker[1], 0) if attacker else 0
        return 10 * victim_value - attacker_value

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
        # Update history table
        key = (move.start_row, move.start_col, move.end_row, move.end_col)
        self.history_table[key] = self.history_table.get(key, 0) + depth * depth
