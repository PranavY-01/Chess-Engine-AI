"""
REST API routes for the Chess Engine.
All chess logic is computed on the backend; the frontend only calls these endpoints.
"""
import random
from fastapi import APIRouter, HTTPException

from api.schemas import (
    GameStartRequest, GameStartResponse, GameStateResponse,
    MoveRequest, MoveResponse, AIMoveRequest, AIMoveResponse,
    TopMovesResponse, TopMoveItem, LegalMovesResponse, UndoRedoResponse,
)
from engine.game_state import GameState
from engine.move_validator import MoveValidator
from engine.move_generator import Move
from ai.greedy import GreedyAI
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI
from ai.advanced_ai import AdvancedAI
from analysis.move_suggester import MoveSuggester
from utils.constants import FILE_TO_COL, RANK_TO_ROW, COL_TO_FILE, ROW_TO_RANK

router = APIRouter()

# ---------------------------------------------------------------------------
# Global game state (single-player, single-game server)
# ---------------------------------------------------------------------------
game_state: GameState | None = None
ai_level: int = 3
validator = MoveValidator()


def _get_ai(level: int):
    """Get the AI engine for the given difficulty level."""
    if level == 1:
        return None  # Random - handled inline
    elif level == 2:
        return GreedyAI()
    elif level == 3:
        return MinimaxAI(depth=3)
    elif level == 4:
        return AlphaBetaAI(depth=4)
    elif level == 5:
        return AdvancedAI(depth=4)
    return MinimaxAI(depth=3)


def _get_ai_move(gs: GameState, level: int) -> Move | None:
    """Compute an AI move at the given difficulty level."""
    legal_moves = validator.get_legal_moves(gs)
    if not legal_moves:
        return None

    if level == 1:
        return random.choice(legal_moves)

    ai_engine = _get_ai(level)
    if ai_engine is None:
        return random.choice(legal_moves)
    return ai_engine.get_best_move(gs)


def _square_to_coords(square: str) -> tuple[int, int]:
    """Convert algebraic notation (e.g., 'e4') to (row, col)."""
    if len(square) != 2:
        raise ValueError(f"Invalid square: {square}")
    file_char = square[0].lower()
    rank_char = square[1]
    if file_char not in FILE_TO_COL or rank_char not in RANK_TO_ROW:
        raise ValueError(f"Invalid square: {square}")
    return RANK_TO_ROW[rank_char], FILE_TO_COL[file_char]


def _coords_to_square(row: int, col: int) -> str:
    """Convert (row, col) to algebraic notation."""
    return COL_TO_FILE[col] + ROW_TO_RANK[row]


def _get_last_move_info(gs: GameState) -> dict | None:
    """Get the last move as a dict with from/to squares."""
    if not gs.move_history:
        return None
    move = gs.move_history[-1][0]
    return {
        'from': _coords_to_square(move.start_row, move.start_col),
        'to': _coords_to_square(move.end_row, move.end_col),
    }


def _is_check(gs: GameState) -> bool:
    """Check if the current side's king is in check."""
    return validator.is_in_check(gs.board, gs.turn)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/game/start", response_model=GameStartResponse)
def start_game(request: GameStartRequest = GameStartRequest()):
    """Start a new chess game."""
    global game_state, ai_level

    if not (1 <= request.ai_level <= 5):
        raise HTTPException(status_code=400, detail="AI level must be between 1 and 5")

    game_state = GameState()
    ai_level = request.ai_level

    return GameStartResponse(
        board=game_state.board.to_list(),
        turn=game_state.turn,
        status=game_state.get_game_status(),
        message=f"New game started. AI difficulty: Level {ai_level}",
    )


@router.get("/game/state", response_model=GameStateResponse)
def get_game_state():
    """Get the current game state."""
    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress. Start a new game first.")

    return GameStateResponse(
        board=game_state.board.to_list(),
        turn=game_state.turn,
        status=game_state.get_game_status(),
        move_history=game_state.get_formatted_move_history(),
        is_check=_is_check(game_state),
        last_move=_get_last_move_info(game_state),
    )


@router.post("/game/move", response_model=MoveResponse)
def make_move(request: MoveRequest):
    """Make a player move and optionally get AI response."""
    global game_state

    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress. Start a new game first.")

    status = game_state.get_game_status()
    if status != 'active':
        raise HTTPException(status_code=400, detail=f"Game is over: {status}")

    # Parse squares
    try:
        start_row, start_col = _square_to_coords(request.from_square)
        end_row, end_col = _square_to_coords(request.to_square)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Find the matching legal move
    legal_moves = validator.get_legal_moves(game_state)
    matching_move = None
    for move in legal_moves:
        if (move.start_row == start_row and move.start_col == start_col and
                move.end_row == end_row and move.end_col == end_col):
            # Check promotion match
            if move.promotion_piece:
                requested_promo = request.promotion or 'Q'
                if move.promotion_piece == requested_promo.upper():
                    matching_move = move
                    break
            else:
                matching_move = move
                break

    if matching_move is None:
        raise HTTPException(status_code=400, detail="Illegal move")

    # Execute player move
    game_state.make_move(matching_move)
    player_move_info = {
        'from': request.from_square,
        'to': request.to_square,
        'promotion': matching_move.promotion_piece,
    }

    # Check game status after player move
    status = game_state.get_game_status()
    ai_move_info = None

    # If game is still active, get AI response
    if status == 'active':
        ai_move = _get_ai_move(game_state, ai_level)
        if ai_move:
            game_state.make_move(ai_move)
            ai_move_info = {
                'from': _coords_to_square(ai_move.start_row, ai_move.start_col),
                'to': _coords_to_square(ai_move.end_row, ai_move.end_col),
                'promotion': ai_move.promotion_piece,
            }
            status = game_state.get_game_status()

    return MoveResponse(
        board=game_state.board.to_list(),
        turn=game_state.turn,
        status=status,
        move_history=game_state.get_formatted_move_history(),
        is_check=_is_check(game_state),
        player_move=player_move_info,
        ai_move=ai_move_info,
        last_move=_get_last_move_info(game_state),
        message="Move executed successfully",
    )


@router.post("/ai/move", response_model=AIMoveResponse)
def ai_move(request: AIMoveRequest = AIMoveRequest()):
    """Get the AI to make a move."""
    global game_state

    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress.")

    status = game_state.get_game_status()
    if status != 'active':
        raise HTTPException(status_code=400, detail=f"Game is over: {status}")

    level = request.level if request.level else ai_level
    move = _get_ai_move(game_state, level)

    if move is None:
        raise HTTPException(status_code=400, detail="No legal moves available")

    game_state.make_move(move)

    return AIMoveResponse(
        board=game_state.board.to_list(),
        turn=game_state.turn,
        status=game_state.get_game_status(),
        move_history=game_state.get_formatted_move_history(),
        is_check=_is_check(game_state),
        ai_move={
            'from': _coords_to_square(move.start_row, move.start_col),
            'to': _coords_to_square(move.end_row, move.end_col),
            'promotion': move.promotion_piece,
        },
        last_move=_get_last_move_info(game_state),
        message="AI move executed",
    )


@router.get("/analysis/top-moves", response_model=TopMovesResponse)
def get_top_moves():
    """Get top 3 recommended moves for the current position."""
    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress.")

    status = game_state.get_game_status()
    if status != 'active':
        return TopMovesResponse(suggestions=[], turn=game_state.turn)

    suggester = MoveSuggester(depth=3, top_n=3)
    suggestions = suggester.get_suggestions(game_state)

    items = [
        TopMoveItem(
            move=s['move'],
            score=s['score'],
            from_square=s['from'],
            to_square=s['to'],
        )
        for s in suggestions
    ]

    return TopMovesResponse(suggestions=items, turn=game_state.turn)


@router.get("/game/legal-moves/{square}", response_model=LegalMovesResponse)
def get_legal_moves_for_square(square: str):
    """Get legal moves for a piece on the given square."""
    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress.")

    try:
        row, col = _square_to_coords(square)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    piece = game_state.board.get_piece(row, col)
    if piece is None:
        return LegalMovesResponse(moves=[])

    if piece[0] != game_state.turn:
        return LegalMovesResponse(moves=[])

    all_legal = validator.get_legal_moves(game_state)
    moves_from_square = [
        m for m in all_legal
        if m.start_row == row and m.start_col == col
    ]

    result = []
    for m in moves_from_square:
        move_data = {
            'to': _coords_to_square(m.end_row, m.end_col),
            'promotion': m.promotion_piece,
        }
        result.append(move_data)

    return LegalMovesResponse(moves=result)


@router.post("/game/undo", response_model=UndoRedoResponse)
def undo_move():
    """Undo the last move(s). Undoes both AI move and player move."""
    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress.")

    # Undo AI move + player move (2 moves if AI played)
    success = game_state.undo_move()
    if not success:
        raise HTTPException(status_code=400, detail="Nothing to undo")

    # Also undo AI's move if the undo brought us to AI's turn
    if game_state.turn != 'w':
        game_state.undo_move()

    return UndoRedoResponse(
        board=game_state.board.to_list(),
        turn=game_state.turn,
        status=game_state.get_game_status(),
        move_history=game_state.get_formatted_move_history(),
        is_check=_is_check(game_state),
        last_move=_get_last_move_info(game_state),
        message="Move undone",
    )


@router.post("/game/redo", response_model=UndoRedoResponse)
def redo_move():
    """Redo the last undone move(s)."""
    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress.")

    success = game_state.redo_move()
    if not success:
        raise HTTPException(status_code=400, detail="Nothing to redo")

    # Also redo AI's move if available
    if game_state.redo_stack:
        game_state.redo_move()

    return UndoRedoResponse(
        board=game_state.board.to_list(),
        turn=game_state.turn,
        status=game_state.get_game_status(),
        move_history=game_state.get_formatted_move_history(),
        is_check=_is_check(game_state),
        last_move=_get_last_move_info(game_state),
        message="Move redone",
    )


@router.post("/game/set-difficulty")
def set_difficulty(level: int):
    """Set the AI difficulty level."""
    global ai_level
    if not (1 <= level <= 5):
        raise HTTPException(status_code=400, detail="AI level must be between 1 and 5")
    ai_level = level
    return {"message": f"AI difficulty set to Level {level}", "level": level}
