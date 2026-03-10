"""
Move generator for the chess engine.
Generates pseudo-legal moves for all piece types.
Pseudo-legal means the move may leave the king in check — filtering happens in move_validator.
"""


class Move:
    """Represents a chess move."""

    __slots__ = (
        'start_row', 'start_col', 'end_row', 'end_col',
        'promotion_piece', 'is_castling', 'is_en_passant',
        'captured_piece',
    )

    def __init__(
        self,
        start_row: int, start_col: int,
        end_row: int, end_col: int,
        promotion_piece: str | None = None,
        is_castling: bool = False,
        is_en_passant: bool = False,
        captured_piece: str | None = None,
    ):
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.promotion_piece = promotion_piece
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant
        self.captured_piece = captured_piece

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return (
            self.start_row == other.start_row
            and self.start_col == other.start_col
            and self.end_row == other.end_row
            and self.end_col == other.end_col
            and self.promotion_piece == other.promotion_piece
        )

    def __hash__(self):
        return hash((
            self.start_row, self.start_col,
            self.end_row, self.end_col,
            self.promotion_piece,
        ))

    def __repr__(self):
        from utils.constants import COL_TO_FILE, ROW_TO_RANK
        src = COL_TO_FILE[self.start_col] + ROW_TO_RANK[self.start_row]
        dst = COL_TO_FILE[self.end_col] + ROW_TO_RANK[self.end_row]
        promo = self.promotion_piece if self.promotion_piece else ''
        return f"Move({src}{dst}{promo})"


class MoveGenerator:
    """Generates pseudo-legal moves for a given game state."""

    def generate_moves(self, game_state) -> list[Move]:
        """Generate all pseudo-legal moves for the side to move."""
        moves: list[Move] = []
        color = game_state.turn
        board = game_state.board

        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece is None:
                    continue
                if piece[0] != color:
                    continue
                piece_type = piece[1]
                if piece_type == 'P':
                    self._generate_pawn_moves(game_state, r, c, color, moves)
                elif piece_type == 'N':
                    self._generate_knight_moves(board, r, c, color, moves)
                elif piece_type == 'B':
                    self._generate_bishop_moves(board, r, c, color, moves)
                elif piece_type == 'R':
                    self._generate_rook_moves(board, r, c, color, moves)
                elif piece_type == 'Q':
                    self._generate_queen_moves(board, r, c, color, moves)
                elif piece_type == 'K':
                    self._generate_king_moves(game_state, r, c, color, moves)
        return moves

    # ------------------------------------------------------------------
    # Pawn moves
    # ------------------------------------------------------------------
    def _generate_pawn_moves(self, game_state, r, c, color, moves):
        board = game_state.board
        if color == 'w':
            direction = -1          # white pawns move up (decreasing row)
            start_rank = 6          # rank 2
            promotion_rank = 0      # rank 8
            enemy = 'b'
        else:
            direction = 1           # black pawns move down (increasing row)
            start_rank = 1          # rank 7
            promotion_rank = 7      # rank 1
            enemy = 'w'

        # Single push
        next_r = r + direction
        if 0 <= next_r < 8 and board.get_piece(next_r, c) is None:
            if next_r == promotion_rank:
                for promo in ['Q', 'R', 'B', 'N']:
                    moves.append(Move(r, c, next_r, c, promotion_piece=promo))
            else:
                moves.append(Move(r, c, next_r, c))
                # Double push from starting rank
                if r == start_rank:
                    double_r = r + 2 * direction
                    if board.get_piece(double_r, c) is None:
                        moves.append(Move(r, c, double_r, c))

        # Diagonal captures
        for dc in [-1, 1]:
            nc = c + dc
            if 0 <= nc < 8 and 0 <= next_r < 8:
                target = board.get_piece(next_r, nc)
                if target is not None and target[0] == enemy:
                    if next_r == promotion_rank:
                        for promo in ['Q', 'R', 'B', 'N']:
                            moves.append(Move(r, c, next_r, nc, promotion_piece=promo,
                                              captured_piece=target))
                    else:
                        moves.append(Move(r, c, next_r, nc, captured_piece=target))

        # En passant
        if game_state.en_passant_square is not None:
            ep_r, ep_c = game_state.en_passant_square
            if ep_r == r + direction and abs(ep_c - c) == 1:
                captured = board.get_piece(r, ep_c)
                moves.append(Move(r, c, ep_r, ep_c, is_en_passant=True,
                                  captured_piece=captured))

    # ------------------------------------------------------------------
    # Knight moves (L-shape: 2+1 in any combination)
    # ------------------------------------------------------------------
    def _generate_knight_moves(self, board, r, c, color, moves):
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1),
        ]
        for dr, dc in offsets:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board.get_piece(nr, nc)
                if target is None or target[0] != color:
                    moves.append(Move(r, c, nr, nc, captured_piece=target))

    # ------------------------------------------------------------------
    # Sliding pieces: bishop, rook, queen
    # ------------------------------------------------------------------
    def _generate_sliding_moves(self, board, r, c, color, directions, moves):
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = board.get_piece(nr, nc)
                if target is None:
                    moves.append(Move(r, c, nr, nc))
                elif target[0] != color:
                    moves.append(Move(r, c, nr, nc, captured_piece=target))
                    break
                else:
                    break  # own piece blocks
                nr += dr
                nc += dc

    def _generate_bishop_moves(self, board, r, c, color, moves):
        self._generate_sliding_moves(board, r, c, color,
                                     [(-1, -1), (-1, 1), (1, -1), (1, 1)], moves)

    def _generate_rook_moves(self, board, r, c, color, moves):
        self._generate_sliding_moves(board, r, c, color,
                                     [(-1, 0), (1, 0), (0, -1), (0, 1)], moves)

    def _generate_queen_moves(self, board, r, c, color, moves):
        self._generate_sliding_moves(board, r, c, color,
                                     [(-1, -1), (-1, 1), (1, -1), (1, 1),
                                      (-1, 0), (1, 0), (0, -1), (0, 1)], moves)

    # ------------------------------------------------------------------
    # King moves (1 square in any direction + castling)
    # ------------------------------------------------------------------
    def _generate_king_moves(self, game_state, r, c, color, moves):
        board = game_state.board
        # Normal king moves
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board.get_piece(nr, nc)
                    if target is None or target[0] != color:
                        moves.append(Move(r, c, nr, nc, captured_piece=target))

        # Castling
        self._generate_castling_moves(game_state, r, c, color, moves)

    def _generate_castling_moves(self, game_state, r, c, color, moves):
        """Generate castling moves if conditions are met.

        Conditions for castling:
        1. King and rook have not moved (castling rights intact)
        2. No pieces between king and rook
        3. King is not in check
        4. King does not pass through or land on an attacked square
        """
        from engine.move_validator import MoveValidator
        validator = MoveValidator()

        # King must not be in check
        if validator.is_in_check(game_state.board, color):
            return

        rights = game_state.castling_rights
        enemy = 'b' if color == 'w' else 'w'

        # Kingside castling
        if rights.get(color + '_kingside', False):
            # Squares between king and rook must be empty
            if (game_state.board.get_piece(r, c + 1) is None and
                    game_state.board.get_piece(r, c + 2) is None):
                # King must not pass through or land on attacked square
                if (not validator.is_square_attacked(game_state.board, r, c + 1, enemy) and
                        not validator.is_square_attacked(game_state.board, r, c + 2, enemy)):
                    moves.append(Move(r, c, r, c + 2, is_castling=True))

        # Queenside castling
        if rights.get(color + '_queenside', False):
            if (game_state.board.get_piece(r, c - 1) is None and
                    game_state.board.get_piece(r, c - 2) is None and
                    game_state.board.get_piece(r, c - 3) is None):
                if (not validator.is_square_attacked(game_state.board, r, c - 1, enemy) and
                        not validator.is_square_attacked(game_state.board, r, c - 2, enemy)):
                    moves.append(Move(r, c, r, c - 2, is_castling=True))
