"""
Position evaluation function for the chess engine.
Uses material counting + piece-square tables + pawn structure +
bishop pair bonus + rook file bonus + development bonus.
"""
from utils.constants import PIECE_VALUES, PIECE_SQUARE_TABLES, KING_ENDGAME_TABLE


# ---------------------------------------------------------------------------
# Evaluation weights (centipawns)
# ---------------------------------------------------------------------------
BISHOP_PAIR_BONUS = 30
DOUBLED_PAWN_PENALTY = -15
ISOLATED_PAWN_PENALTY = -20
PASSED_PAWN_BONUS = [0, 10, 15, 25, 40, 60, 80, 0]   # index = rank distance from promotion
ROOK_OPEN_FILE_BONUS = 25
ROOK_SEMI_OPEN_FILE_BONUS = 12
DEVELOPMENT_BONUS = 8       # per minor piece off its back rank
MOBILITY_WEIGHT = 3          # centipawns per available move
CENTER_CONTROL_BONUS = 8     # bonus for pieces on e4/d4/e5/d5
KING_SHIELD_BONUS = 10       # per pawn shielding the king

CENTER_SQUARES = {(3, 3), (3, 4), (4, 3), (4, 4)}
EXTENDED_CENTER = {(2, 2), (2, 3), (2, 4), (2, 5),
                   (3, 2), (3, 5), (4, 2), (4, 5),
                   (5, 2), (5, 3), (5, 4), (5, 5)}


def evaluate(game_state) -> int:
    """Evaluate the position and return a score in centipawns.

    Positive = white advantage, negative = black advantage.
    """
    board = game_state.board
    score = 0

    # ------------------------------------------------------------------
    # Pass 1: material count + endgame detection + piece collection
    # ------------------------------------------------------------------
    total_material = 0
    white_pieces: list[tuple[str, int, int]] = []   # (piece_type, row, col)
    black_pieces: list[tuple[str, int, int]] = []
    white_pawns_by_col: list[list[int]] = [[] for _ in range(8)]  # col -> list of rows
    black_pawns_by_col: list[list[int]] = [[] for _ in range(8)]

    for r in range(8):
        for c in range(8):
            piece = board.get_piece(r, c)
            if piece is None:
                continue
            color = piece[0]
            pt = piece[1]
            if pt != 'K':
                total_material += PIECE_VALUES.get(pt, 0)
            if color == 'w':
                white_pieces.append((pt, r, c))
                if pt == 'P':
                    white_pawns_by_col[c].append(r)
            else:
                black_pieces.append((pt, r, c))
                if pt == 'P':
                    black_pawns_by_col[c].append(r)

    is_endgame = total_material < 2600

    # ------------------------------------------------------------------
    # Pass 2: material + PST + development
    # ------------------------------------------------------------------
    for pt, r, c in white_pieces:
        value = PIECE_VALUES.get(pt, 0)
        if pt == 'K' and is_endgame:
            pst = KING_ENDGAME_TABLE
        else:
            pst = PIECE_SQUARE_TABLES.get(pt)
        positional = pst[r][c] if pst else 0
        score += value + positional

        # Development: minor pieces (N, B) off back rank (row 7 for white)
        if pt in ('N', 'B') and r != 7:
            score += DEVELOPMENT_BONUS

    for pt, r, c in black_pieces:
        value = PIECE_VALUES.get(pt, 0)
        if pt == 'K' and is_endgame:
            pst = KING_ENDGAME_TABLE
        else:
            pst = PIECE_SQUARE_TABLES.get(pt)
        positional = pst[7 - r][c] if pst else 0
        score -= value + positional

        # Development: minor pieces off back rank (row 0 for black)
        if pt in ('N', 'B') and r != 0:
            score -= DEVELOPMENT_BONUS

    # ------------------------------------------------------------------
    # Pawn structure
    # ------------------------------------------------------------------
    score += _evaluate_pawn_structure(white_pawns_by_col, black_pawns_by_col)

    # ------------------------------------------------------------------
    # Bishop pair bonus
    # ------------------------------------------------------------------
    white_bishops = sum(1 for pt, _, _ in white_pieces if pt == 'B')
    black_bishops = sum(1 for pt, _, _ in black_pieces if pt == 'B')
    if white_bishops >= 2:
        score += BISHOP_PAIR_BONUS
    if black_bishops >= 2:
        score -= BISHOP_PAIR_BONUS

    # ------------------------------------------------------------------
    # Rook on open / semi-open file
    # ------------------------------------------------------------------
    for pt, r, c in white_pieces:
        if pt == 'R':
            if not white_pawns_by_col[c]:
                if not black_pawns_by_col[c]:
                    score += ROOK_OPEN_FILE_BONUS
                else:
                    score += ROOK_SEMI_OPEN_FILE_BONUS
    for pt, r, c in black_pieces:
        if pt == 'R':
            if not black_pawns_by_col[c]:
                if not white_pawns_by_col[c]:
                    score -= ROOK_OPEN_FILE_BONUS
                else:
                    score -= ROOK_SEMI_OPEN_FILE_BONUS

    # ------------------------------------------------------------------
    # Center control: pieces occupying or attacking central squares
    # ------------------------------------------------------------------
    for pt, r, c in white_pieces:
        if (r, c) in CENTER_SQUARES:
            score += CENTER_CONTROL_BONUS
        elif (r, c) in EXTENDED_CENTER:
            score += CENTER_CONTROL_BONUS // 2
    for pt, r, c in black_pieces:
        if (r, c) in CENTER_SQUARES:
            score -= CENTER_CONTROL_BONUS
        elif (r, c) in EXTENDED_CENTER:
            score -= CENTER_CONTROL_BONUS // 2

    # ------------------------------------------------------------------
    # King safety: pawn shield in the middlegame
    # ------------------------------------------------------------------
    if not is_endgame:
        score += _king_shield_score(board, 'w', white_pieces)
        score -= _king_shield_score(board, 'b', black_pieces)

    # ------------------------------------------------------------------
    # Knight centralization bonus (cheap O(1) mobility proxy)
    # Centralized knights control more squares
    # ------------------------------------------------------------------
    for pt, r, c in white_pieces:
        if pt == 'N':
            dist_center = abs(r - 3.5) + abs(c - 3.5)
            score += max(0, int((4 - dist_center) * MOBILITY_WEIGHT))
    for pt, r, c in black_pieces:
        if pt == 'N':
            dist_center = abs(r - 3.5) + abs(c - 3.5)
            score -= max(0, int((4 - dist_center) * MOBILITY_WEIGHT))

    return score


# ======================================================================
# Helpers
# ======================================================================

def _king_shield_score(board, color: str, pieces: list[tuple[str, int, int]]) -> int:
    """Score king pawn shield. More pawns in front of king = safer."""
    # Find king position
    king_pos = None
    for pt, r, c in pieces:
        if pt == 'K':
            king_pos = (r, c)
            break
    if king_pos is None:
        return 0

    kr, kc = king_pos
    shield = 0
    # Check the 3 squares directly in front of the king
    if color == 'w':
        # White king: pawns should be on row kr-1 (in front)
        for dc in [-1, 0, 1]:
            nc = kc + dc
            if 0 <= nc < 8 and kr - 1 >= 0:
                piece = board.get_piece(kr - 1, nc)
                if piece == 'wP':
                    shield += KING_SHIELD_BONUS
    else:
        # Black king: pawns should be on row kr+1
        for dc in [-1, 0, 1]:
            nc = kc + dc
            if 0 <= nc < 8 and kr + 1 < 8:
                piece = board.get_piece(kr + 1, nc)
                if piece == 'bP':
                    shield += KING_SHIELD_BONUS
    return shield

def _evaluate_pawn_structure(
    white_pawns_by_col: list[list[int]],
    black_pawns_by_col: list[list[int]],
) -> int:
    """Return pawn structure score (positive = white advantage)."""
    score = 0

    for c in range(8):
        # --- White pawns ---
        wp = white_pawns_by_col[c]
        if wp:
            # Doubled pawns: more than one pawn on the same file
            if len(wp) > 1:
                score += DOUBLED_PAWN_PENALTY * (len(wp) - 1)

            # Isolated pawns: no friendly pawn on adjacent files
            has_neighbor = False
            if c > 0 and white_pawns_by_col[c - 1]:
                has_neighbor = True
            if c < 7 and white_pawns_by_col[c + 1]:
                has_neighbor = True
            if not has_neighbor:
                score += ISOLATED_PAWN_PENALTY * len(wp)

            # Passed pawns: no enemy pawn on same or adjacent files ahead
            for row in wp:
                if _is_passed_pawn(row, c, 'w', black_pawns_by_col):
                    # Distance from promotion: white promotes at row 0
                    distance = row  # row 1 = 1 step away, etc.
                    score += PASSED_PAWN_BONUS[distance] if distance < 8 else 0

        # --- Black pawns ---
        bp = black_pawns_by_col[c]
        if bp:
            if len(bp) > 1:
                score -= DOUBLED_PAWN_PENALTY * (len(bp) - 1)

            has_neighbor = False
            if c > 0 and black_pawns_by_col[c - 1]:
                has_neighbor = True
            if c < 7 and black_pawns_by_col[c + 1]:
                has_neighbor = True
            if not has_neighbor:
                score -= ISOLATED_PAWN_PENALTY * len(bp)

            for row in bp:
                if _is_passed_pawn(row, c, 'b', white_pawns_by_col):
                    # Black promotes at row 7
                    distance = 7 - row
                    score -= PASSED_PAWN_BONUS[distance] if distance < 8 else 0

    return score


def _is_passed_pawn(row: int, col: int, color: str,
                    enemy_pawns_by_col: list[list[int]]) -> bool:
    """Check if a pawn is passed (no enemy pawn blocking or guarding ahead)."""
    cols_to_check = [col]
    if col > 0:
        cols_to_check.append(col - 1)
    if col < 7:
        cols_to_check.append(col + 1)

    for c in cols_to_check:
        for er in enemy_pawns_by_col[c]:
            if color == 'w' and er < row:
                # Enemy pawn is ahead (lower row = closer to rank 8)
                return False
            if color == 'b' and er > row:
                # Enemy pawn is ahead (higher row = closer to rank 1)
                return False
    return True
