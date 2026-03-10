"""
Move suggester.
Uses GameTreeAnalyzer to provide top-3 move suggestions with SAN notation and scores.
"""
from analysis.game_tree import GameTreeAnalyzer
from utils.constants import COL_TO_FILE, ROW_TO_RANK


class MoveSuggester:
    """Suggests the top N moves for the current position."""

    def __init__(self, depth: int = 3, top_n: int = 3):
        self.analyzer = GameTreeAnalyzer(depth=depth)
        self.top_n = top_n

    def get_suggestions(self, game_state) -> list[dict]:
        """Return the top N move suggestions.

        Each suggestion is a dict with:
        - 'move': SAN string (e.g., 'Nf3')
        - 'score': normalized evaluation score
        - 'from': source square in algebraic notation (e.g., 'g1')
        - 'to': destination square in algebraic notation (e.g., 'f3')
        """
        scored_moves = self.analyzer.analyze(game_state)
        if not scored_moves:
            return []

        suggestions = []
        for move, raw_score in scored_moves[:self.top_n]:
            san = self._move_to_san_simple(move, game_state)
            # Normalize score to roughly -10 to +10 range
            normalized = round(raw_score / 100, 2)
            from_sq = COL_TO_FILE[move.start_col] + ROW_TO_RANK[move.start_row]
            to_sq = COL_TO_FILE[move.end_col] + ROW_TO_RANK[move.end_row]
            suggestions.append({
                'move': san,
                'score': normalized,
                'from': from_sq,
                'to': to_sq,
            })

        return suggestions

    def _move_to_san_simple(self, move, game_state) -> str:
        """Convert move to SAN (simplified — no full disambiguation for speed)."""
        piece = game_state.board.get_piece(move.start_row, move.start_col)
        if piece is None:
            return '??'

        piece_type = piece[1]

        if move.is_castling:
            return 'O-O' if move.end_col > move.start_col else 'O-O-O'

        san = ''
        if piece_type != 'P':
            san += piece_type

        target = game_state.board.get_piece(move.end_row, move.end_col)
        is_capture = target is not None or move.is_en_passant
        if is_capture:
            if piece_type == 'P':
                san += COL_TO_FILE[move.start_col]
            san += 'x'

        san += COL_TO_FILE[move.end_col] + ROW_TO_RANK[move.end_row]

        if move.promotion_piece:
            san += '=' + move.promotion_piece

        return san
