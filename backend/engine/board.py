"""
Board representation for the chess engine.
8x8 matrix using piece codes: 'wK', 'bP', etc. None for empty squares.
"""
import copy
from utils.constants import INITIAL_BOARD


class Board:
    """8x8 chess board representation."""

    def __init__(self):
        """Initialize the board with the starting position."""
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.setup_initial_position()

    def setup_initial_position(self):
        """Set up the standard chess starting position."""
        for r in range(8):
            for c in range(8):
                self.grid[r][c] = INITIAL_BOARD[r][c]

    def get_piece(self, row: int, col: int) -> str | None:
        """Get the piece at the given position, or None if empty."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None

    def set_piece(self, row: int, col: int, piece: str | None):
        """Place a piece (or None) at the given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            self.grid[row][col] = piece

    def find_king(self, color: str) -> tuple[int, int] | None:
        """Find the king of the specified color. Returns (row, col) or None."""
        king_code = color + 'K'
        for r in range(8):
            for c in range(8):
                if self.grid[r][c] == king_code:
                    return (r, c)
        return None

    def copy(self) -> 'Board':
        """Create a deep copy of the board."""
        new_board = Board.__new__(Board)
        new_board.grid = copy.deepcopy(self.grid)
        return new_board

    def to_list(self) -> list[list[str | None]]:
        """Return the board as a plain 2D list (for JSON serialization)."""
        return [row[:] for row in self.grid]

    def __repr__(self):
        rows = []
        for r in range(8):
            row_str = ' '.join(
                (self.grid[r][c] if self.grid[r][c] else '..') for c in range(8)
            )
            rows.append(f"{8 - r} | {row_str}")
        rows.append("    a  b  c  d  e  f  g  h")
        return '\n'.join(rows)
