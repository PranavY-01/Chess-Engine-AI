"""
Special rules for the chess engine.
Handles draw conditions: insufficient material, fifty-move rule, threefold repetition.
"""


class Rules:
    """Static methods for special chess rules and draw conditions."""

    @staticmethod
    def is_insufficient_material(board) -> bool:
        """Check if the position has insufficient material for checkmate.

        Insufficient material cases:
        - King vs King
        - King + Bishop vs King
        - King + Knight vs King
        - King + Bishop vs King + Bishop (same colored squares)
        """
        white_pieces = []
        black_pieces = []

        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece is None:
                    continue
                if piece[0] == 'w':
                    white_pieces.append((piece[1], r, c))
                else:
                    black_pieces.append((piece[1], r, c))

        white_types = [p[0] for p in white_pieces]
        black_types = [p[0] for p in black_pieces]

        # King vs King
        if len(white_pieces) == 1 and len(black_pieces) == 1:
            return True

        # King + minor piece vs King
        if len(white_pieces) == 1 and len(black_pieces) == 2:
            non_king = [t for t in black_types if t != 'K']
            if non_king and non_king[0] in ('B', 'N'):
                return True

        if len(black_pieces) == 1 and len(white_pieces) == 2:
            non_king = [t for t in white_types if t != 'K']
            if non_king and non_king[0] in ('B', 'N'):
                return True

        # King + Bishop vs King + Bishop on same color squares
        if len(white_pieces) == 2 and len(black_pieces) == 2:
            w_non_king = [(t, r, c) for t, r, c in white_pieces if t != 'K']
            b_non_king = [(t, r, c) for t, r, c in black_pieces if t != 'K']
            if (len(w_non_king) == 1 and w_non_king[0][0] == 'B' and
                    len(b_non_king) == 1 and b_non_king[0][0] == 'B'):
                # Same color diagonal?
                w_sq_color = (w_non_king[0][1] + w_non_king[0][2]) % 2
                b_sq_color = (b_non_king[0][1] + b_non_king[0][2]) % 2
                if w_sq_color == b_sq_color:
                    return True

        return False

    @staticmethod
    def is_fifty_move_rule(halfmove_clock: int) -> bool:
        """Check if the fifty-move rule applies (100 half-moves)."""
        return halfmove_clock >= 100

    @staticmethod
    def is_threefold_repetition(position_history: dict) -> bool:
        """Check if any position has occurred three or more times."""
        for count in position_history.values():
            if count >= 3:
                return True
        return False

    @staticmethod
    def generate_position_hash(board, turn: str, castling_rights: dict,
                               en_passant_square: tuple | None) -> str:
        """Generate a hash string representing the current position.

        Includes: board state, turn, castling rights, en passant square.
        Used for threefold repetition detection.
        """
        parts = []
        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                parts.append(piece if piece else '..')
        parts.append(turn)
        parts.append(str(castling_rights))
        parts.append(str(en_passant_square))
        return '|'.join(parts)
