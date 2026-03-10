"""
Position evaluation function for the chess engine.
Uses material counting + piece-square tables for positional assessment.
"""
from utils.constants import PIECE_VALUES, PIECE_SQUARE_TABLES, KING_ENDGAME_TABLE


def evaluate(game_state) -> int:
    """Evaluate the position and return a score in centipawns.

    Positive = white advantage, negative = black advantage.
    """
    board = game_state.board
    score = 0

    # Count total material to determine if we're in endgame
    total_material = 0
    for r in range(8):
        for c in range(8):
            piece = board.get_piece(r, c)
            if piece and piece[1] != 'K':
                total_material += PIECE_VALUES.get(piece[1], 0)

    is_endgame = total_material < 2600  # roughly when queens are off + some pieces

    for r in range(8):
        for c in range(8):
            piece = board.get_piece(r, c)
            if piece is None:
                continue

            color = piece[0]
            piece_type = piece[1]
            value = PIECE_VALUES.get(piece_type, 0)

            # Positional bonus from piece-square tables
            if piece_type == 'K' and is_endgame:
                pst = KING_ENDGAME_TABLE
            else:
                pst = PIECE_SQUARE_TABLES.get(piece_type)

            positional = 0
            if pst:
                if color == 'w':
                    positional = pst[r][c]
                else:
                    # Mirror table for black (row 0 becomes row 7)
                    positional = pst[7 - r][c]

            if color == 'w':
                score += value + positional
            else:
                score -= value + positional

    return score
