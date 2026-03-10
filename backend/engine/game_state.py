"""
Game state manager for the chess engine.
Holds the complete game state and manages move execution, undo/redo,
and game status detection.
"""
import copy
from engine.board import Board
from engine.move_generator import Move
from engine.rules import Rules
from utils.constants import COL_TO_FILE, ROW_TO_RANK


class GameState:
    """Complete chess game state with make/undo/redo support."""

    def __init__(self):
        """Initialize a new game from the starting position."""
        self.board = Board()
        self.turn = 'w'  # 'w' or 'b'
        self.castling_rights = {
            'w_kingside': True,
            'w_queenside': True,
            'b_kingside': True,
            'b_queenside': True,
        }
        self.en_passant_square = None  # (row, col) or None
        self.halfmove_clock = 0  # for 50-move rule
        self.fullmove_number = 1
        self.move_history = []       # list of (move, state_snapshot) tuples
        self.redo_stack = []         # for redo support
        self.position_history = {}   # position hash -> count (for threefold repetition)
        self.move_log = []           # list of SAN strings for display

        # Record initial position
        self._record_position()

    def _record_position(self):
        """Record current position for threefold repetition detection."""
        pos_hash = Rules.generate_position_hash(
            self.board, self.turn, self.castling_rights, self.en_passant_square
        )
        self.position_history[pos_hash] = self.position_history.get(pos_hash, 0) + 1

    def _save_state_snapshot(self):
        """Save a snapshot of the current state for undo."""
        return {
            'turn': self.turn,
            'castling_rights': dict(self.castling_rights),
            'en_passant_square': self.en_passant_square,
            'halfmove_clock': self.halfmove_clock,
            'fullmove_number': self.fullmove_number,
            'position_history': dict(self.position_history),
        }

    def _restore_state_snapshot(self, snapshot):
        """Restore state from a snapshot."""
        self.turn = snapshot['turn']
        self.castling_rights = dict(snapshot['castling_rights'])
        self.en_passant_square = snapshot['en_passant_square']
        self.halfmove_clock = snapshot['halfmove_clock']
        self.fullmove_number = snapshot['fullmove_number']
        self.position_history = dict(snapshot['position_history'])

    def make_move(self, move: Move):
        """Execute a move and update all game state.

        This is the full version that records history for undo/redo.
        """
        san = self._move_to_san(move)

        snapshot = self._save_state_snapshot()
        board_backup = self.board.copy()
        self.move_history.append((move, snapshot, board_backup))
        self.redo_stack.clear()

        self.make_move_no_validate(move)
        self.move_log.append(san)

    def make_move_no_validate(self, move: Move):
        """Execute a move on the board without recording history.

        Used by AI search and move validation (on copies).
        """
        piece = self.board.get_piece(move.start_row, move.start_col)
        if piece is None:
            return

        color = piece[0]
        piece_type = piece[1]

        # Update halfmove clock
        captured = self.board.get_piece(move.end_row, move.end_col)
        if piece_type == 'P' or captured is not None or move.is_en_passant:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Handle en passant capture
        if move.is_en_passant:
            # Remove the captured pawn (it's on the same row as the moving pawn)
            self.board.set_piece(move.start_row, move.end_col, None)

        # Handle castling - move the rook
        if move.is_castling:
            if move.end_col == move.start_col + 2:
                # Kingside: move rook from col 7 to col 5
                rook = self.board.get_piece(move.start_row, 7)
                self.board.set_piece(move.start_row, 7, None)
                self.board.set_piece(move.start_row, 5, rook)
            elif move.end_col == move.start_col - 2:
                # Queenside: move rook from col 0 to col 3
                rook = self.board.get_piece(move.start_row, 0)
                self.board.set_piece(move.start_row, 0, None)
                self.board.set_piece(move.start_row, 3, rook)

        # Move the piece
        self.board.set_piece(move.end_row, move.end_col, piece)
        self.board.set_piece(move.start_row, move.start_col, None)

        # Handle pawn promotion
        if move.promotion_piece:
            self.board.set_piece(move.end_row, move.end_col, color + move.promotion_piece)

        # Update en passant square
        self.en_passant_square = None
        if piece_type == 'P' and abs(move.end_row - move.start_row) == 2:
            # Double pawn push — set en passant square
            ep_row = (move.start_row + move.end_row) // 2
            self.en_passant_square = (ep_row, move.start_col)

        # Update castling rights
        self._update_castling_rights(move, piece, color)

        # Update turn
        if self.turn == 'w':
            self.turn = 'b'
        else:
            self.turn = 'w'
            self.fullmove_number += 1

        # Record position for repetition detection
        self._record_position()

    def _update_castling_rights(self, move: Move, piece: str, color: str):
        """Update castling rights after a move."""
        # If king moves, lose both castling rights
        if piece[1] == 'K':
            self.castling_rights[color + '_kingside'] = False
            self.castling_rights[color + '_queenside'] = False

        # If rook moves from its starting square, lose that side's right
        if piece[1] == 'R':
            if color == 'w':
                if move.start_row == 7 and move.start_col == 0:
                    self.castling_rights['w_queenside'] = False
                elif move.start_row == 7 and move.start_col == 7:
                    self.castling_rights['w_kingside'] = False
            else:
                if move.start_row == 0 and move.start_col == 0:
                    self.castling_rights['b_queenside'] = False
                elif move.start_row == 0 and move.start_col == 7:
                    self.castling_rights['b_kingside'] = False

        # If a rook is captured on its starting square, lose that right
        if move.end_row == 0 and move.end_col == 0:
            self.castling_rights['b_queenside'] = False
        elif move.end_row == 0 and move.end_col == 7:
            self.castling_rights['b_kingside'] = False
        elif move.end_row == 7 and move.end_col == 0:
            self.castling_rights['w_queenside'] = False
        elif move.end_row == 7 and move.end_col == 7:
            self.castling_rights['w_kingside'] = False

    def undo_move(self) -> bool:
        """Undo the last move. Returns True if successful."""
        if not self.move_history:
            return False

        move, snapshot, board_backup = self.move_history.pop()
        self.redo_stack.append((move, self._save_state_snapshot(), self.board.copy(),
                                self.move_log[-1] if self.move_log else ''))

        self.board = board_backup
        self._restore_state_snapshot(snapshot)
        if self.move_log:
            self.move_log.pop()
        return True

    def redo_move(self) -> bool:
        """Redo the last undone move. Returns True if successful."""
        if not self.redo_stack:
            return False

        move, _, _, san = self.redo_stack.pop()
        # Save current state for undo
        snapshot = self._save_state_snapshot()
        board_backup = self.board.copy()
        self.move_history.append((move, snapshot, board_backup))

        self.make_move_no_validate(move)
        self.move_log.append(san)
        return True

    def copy(self) -> 'GameState':
        """Deep copy for AI search."""
        gs = GameState.__new__(GameState)
        gs.board = self.board.copy()
        gs.turn = self.turn
        gs.castling_rights = dict(self.castling_rights)
        gs.en_passant_square = self.en_passant_square
        gs.halfmove_clock = self.halfmove_clock
        gs.fullmove_number = self.fullmove_number
        gs.move_history = []  # not needed for search
        gs.redo_stack = []
        gs.position_history = dict(self.position_history)
        gs.move_log = []
        return gs

    def get_game_status(self) -> str:
        """Get the current game status.

        Returns one of:
        - 'active'
        - 'checkmate_white' (white wins)
        - 'checkmate_black' (black wins)
        - 'stalemate'
        - 'draw_50_move'
        - 'draw_insufficient'
        - 'draw_repetition'
        """
        from engine.move_validator import MoveValidator
        validator = MoveValidator()

        # Check draw conditions first
        if Rules.is_insufficient_material(self.board):
            return 'draw_insufficient'
        if Rules.is_fifty_move_rule(self.halfmove_clock):
            return 'draw_50_move'
        if Rules.is_threefold_repetition(self.position_history):
            return 'draw_repetition'

        # Check for checkmate or stalemate
        legal_moves = validator.get_legal_moves(self)
        if len(legal_moves) == 0:
            if validator.is_in_check(self.board, self.turn):
                winner = 'white' if self.turn == 'b' else 'black'
                return f'checkmate_{winner}'
            else:
                return 'stalemate'

        return 'active'

    def _move_to_san(self, move: Move) -> str:
        """Convert a move to Standard Algebraic Notation (SAN)."""
        piece = self.board.get_piece(move.start_row, move.start_col)
        if piece is None:
            return '??'

        piece_type = piece[1]

        # Castling
        if move.is_castling:
            if move.end_col > move.start_col:
                return 'O-O'
            else:
                return 'O-O-O'

        san = ''

        # Piece letter (pawns have no letter)
        if piece_type != 'P':
            san += piece_type

        # Disambiguation: check if another piece of the same type can move to the same square
        if piece_type != 'P':
            from engine.move_validator import MoveValidator
            validator = MoveValidator()
            legal_moves = validator.get_legal_moves(self)
            ambiguous_moves = [
                m for m in legal_moves
                if m.end_row == move.end_row and m.end_col == move.end_col
                and self.board.get_piece(m.start_row, m.start_col) == piece
                and (m.start_row != move.start_row or m.start_col != move.start_col)
            ]
            if ambiguous_moves:
                same_col = any(m.start_col == move.start_col for m in ambiguous_moves)
                same_row = any(m.start_row == move.start_row for m in ambiguous_moves)
                if not same_col:
                    san += COL_TO_FILE[move.start_col]
                elif not same_row:
                    san += ROW_TO_RANK[move.start_row]
                else:
                    san += COL_TO_FILE[move.start_col] + ROW_TO_RANK[move.start_row]

        # Capture
        target = self.board.get_piece(move.end_row, move.end_col)
        is_capture = target is not None or move.is_en_passant
        if is_capture:
            if piece_type == 'P':
                san += COL_TO_FILE[move.start_col]
            san += 'x'

        # Destination square
        san += COL_TO_FILE[move.end_col] + ROW_TO_RANK[move.end_row]

        # Promotion
        if move.promotion_piece:
            san += '=' + move.promotion_piece

        # Check / Checkmate indicators
        gs_copy = self.copy()
        gs_copy.make_move_no_validate(move)
        from engine.move_validator import MoveValidator
        v = MoveValidator()
        if v.is_in_check(gs_copy.board, gs_copy.turn):
            if v.is_checkmate(gs_copy):
                san += '#'
            else:
                san += '+'

        return san

    def get_formatted_move_history(self) -> list[str]:
        """Return move history formatted as standard notation.

        Example: ['1. e4 e5', '2. Nf3 Nc6']
        """
        result = []
        for i in range(0, len(self.move_log), 2):
            move_num = i // 2 + 1
            white_move = self.move_log[i]
            if i + 1 < len(self.move_log):
                black_move = self.move_log[i + 1]
                result.append(f"{move_num}. {white_move} {black_move}")
            else:
                result.append(f"{move_num}. {white_move}")
        return result
