"""
REST API routes for the Chess Engine.
All chess logic is computed on the backend; the frontend only calls these endpoints.
"""
import random
import asyncio
from fastapi import APIRouter, HTTPException

from api.schemas import (
    GameStartRequest, GameStartResponse, GameStateResponse,
    MoveRequest, MoveResponse, AIMoveRequest, AIMoveResponse,
    TopMovesResponse, TopMoveItem, LegalMovesResponse, UndoRedoResponse,
    ExplainRequest, ExplainResponse, BranchStartRequest, BranchAdvanceRequest,
    BranchStateResponse, HintResponse, AiVsAiStartRequest, AiVsAiPauseRequest,
    AiVsAiStepRequest, AiVsAiStateResponse, DemonstratorInfo,
    EvaluationResponse, EndSessionResponse,
)
from engine.game_state import GameState
from engine.move_validator import MoveValidator
from engine.move_generator import Move
from ai.greedy import GreedyAI
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI
from ai.advanced_ai import AdvancedAI
from ai.evaluation import evaluate
from analysis.move_suggester import MoveSuggester
from reasoning.groq_client import GroqClient
from reasoning.prompt_builder import build_explanation_prompt
from reasoning.personality import get_personality
from simulation.branch_engine import BranchEngine
from simulation.ai_vs_ai import AiVsAiManager
from utils.demonstrators import DEMONSTRATORS, ID_TO_LEVEL
from utils.constants import FILE_TO_COL, RANK_TO_ROW, COL_TO_FILE, ROW_TO_RANK

router = APIRouter()

# ---------------------------------------------------------------------------
# Global game state (single-player, single-game server)
# ---------------------------------------------------------------------------
game_state: GameState | None = None
ai_level: int = 3
validator = MoveValidator()
branch_engine = BranchEngine()
ai_vs_ai_manager = AiVsAiManager()
groq_client = GroqClient()


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


async def _get_ai_move_async(gs: GameState, level: int) -> Move | None:
    return await asyncio.to_thread(_get_ai_move, gs, level)


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


def _material_balance(gs: GameState) -> int:
    return int(evaluate(gs))


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


def _normalize_level_from_demonstrator(demonstrator_id: str) -> int:
    level = ID_TO_LEVEL.get(demonstrator_id)
    if level is None:
        raise HTTPException(status_code=400, detail="Unknown demonstrator")
    return level


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


@router.get("/demonstrators", response_model=list[DemonstratorInfo])
def get_demonstrators():
    return [
        DemonstratorInfo(
            id=cfg["id"],
            name=cfg["name"],
            emoji=cfg["emoji"],
            accent=cfg["accent"],
            algorithm=cfg["algorithm"],
        )
        for cfg in DEMONSTRATORS.values()
    ]


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
async def make_move(request: MoveRequest):
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
        ai_move = await _get_ai_move_async(game_state, ai_level)
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
async def ai_move(request: AIMoveRequest = AIMoveRequest()):
    """Get the AI to make a move."""
    global game_state

    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress.")

    status = game_state.get_game_status()
    if status != 'active':
        raise HTTPException(status_code=400, detail=f"Game is over: {status}")

    level = request.level if request.level else ai_level
    move = await _get_ai_move_async(game_state, level)

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


@router.get("/analysis/hint", response_model=HintResponse)
def get_hint():
    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress.")

    if game_state.get_game_status() != 'active':
        raise HTTPException(status_code=400, detail="Game is not active.")

    suggester = MoveSuggester(depth=3, top_n=1)
    suggestions = suggester.get_suggestions(game_state)
    if not suggestions:
        raise HTTPException(status_code=400, detail="No hint available")

    best = suggestions[0]
    return HintResponse(
        from_square=best['from'],
        to_square=best['to'],
        score=best['score'],
    )


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


@router.post("/reasoning/explain", response_model=ExplainResponse)
async def explain_move(request: ExplainRequest):
    personality = get_personality(request.demonstrator_id)
    name = DEMONSTRATORS.get(_normalize_level_from_demonstrator(request.demonstrator_id), {}).get(
        "name", "Demonstrator"
    )
    prompt = build_explanation_prompt(
        demonstrator_name=name,
        personality=personality,
        chosen_move=request.chosen_move,
        alternatives=request.alternatives,
        board_context=request.board_context,
        branch_mode=request.branch_mode,
    )
    explanation = await groq_client.explain(prompt)
    return ExplainResponse(explanation=explanation)


@router.post("/reasoning/explain-branch", response_model=ExplainResponse)
async def explain_branch_move(request: ExplainRequest):
    branch_req = ExplainRequest(
        demonstrator_id=request.demonstrator_id,
        chosen_move=request.chosen_move,
        alternatives=request.alternatives,
        board_context=request.board_context,
        branch_mode=True,
    )
    return await explain_move(branch_req)


@router.post("/simulation/branch/start", response_model=BranchStateResponse)
def start_branch(request: BranchStartRequest):
    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress.")

    try:
        result = branch_engine.start_branch(
            base_state=game_state,
            from_square=request.from_square,
            to_square=request.to_square,
            rank=request.rank,
            level=request.level,
            get_ai_move_fn=_get_ai_move,
        )
        return BranchStateResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/simulation/branch/advance", response_model=BranchStateResponse)
async def advance_branch(request: BranchAdvanceRequest):
    try:
        result = await asyncio.to_thread(branch_engine.advance, request.branch_id)
        return BranchStateResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/simulation/branch/{branch_id}")
def end_branch(branch_id: str):
    branch_engine.end(branch_id)
    return {"message": "Branch ended"}


@router.post("/simulation/ai-vs-ai/start", response_model=AiVsAiStateResponse)
def start_ai_vs_ai(request: AiVsAiStartRequest):
    if request.white_level not in DEMONSTRATORS or request.black_level not in DEMONSTRATORS:
        raise HTTPException(status_code=400, detail="Invalid demonstrator level")
    return AiVsAiStateResponse(**ai_vs_ai_manager.start(request.white_level, request.black_level))


@router.post("/simulation/ai-vs-ai/pause", response_model=AiVsAiStateResponse)
def pause_ai_vs_ai(request: AiVsAiPauseRequest):
    try:
        return AiVsAiStateResponse(**ai_vs_ai_manager.set_paused(request.session_id, request.paused))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/simulation/ai-vs-ai/step", response_model=AiVsAiStateResponse)
async def step_ai_vs_ai(request: AiVsAiStepRequest):
    try:
        state = await asyncio.to_thread(ai_vs_ai_manager.step, request.session_id, _get_ai_move)
        return AiVsAiStateResponse(**state)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/simulation/ai-vs-ai/reset", response_model=AiVsAiStateResponse)
def reset_ai_vs_ai(request: AiVsAiStepRequest):
    try:
        return AiVsAiStateResponse(**ai_vs_ai_manager.reset(request.session_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/simulation/ai-vs-ai/{session_id}", response_model=AiVsAiStateResponse)
def get_ai_vs_ai_state(session_id: str):
    try:
        return AiVsAiStateResponse(**ai_vs_ai_manager.get(session_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/analysis/evaluation", response_model=EvaluationResponse)
def get_evaluation():
    """Get position evaluation for the accuracy meter."""
    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress.")

    raw_eval = evaluate(game_state)
    # Convert centipawn evaluation to a win-probability-like percentage
    # Using a sigmoid-like function: 50 + 50 * tanh(eval / 400)
    import math
    win_pct = 50 + 50 * math.tanh(raw_eval / 400)
    return EvaluationResponse(
        evaluation=round(raw_eval / 100, 2),
        white_score=round(win_pct, 1),
        black_score=round(100 - win_pct, 1),
    )


@router.post("/game/end-session", response_model=EndSessionResponse)
def end_session():
    """End the current game session and return final state for history storage."""
    global game_state
    if game_state is None:
        raise HTTPException(status_code=400, detail="No game in progress.")

    final_status = game_state.get_game_status()
    final_moves = game_state.get_formatted_move_history()
    final_eval = evaluate(game_state)
    total_moves = len(final_moves)

    # If game was still active when force-ended, mark as resigned
    if final_status == "active":
        final_status = "resigned"

    game_state = None  # Clear the session

    return EndSessionResponse(
        status=final_status,
        move_history=final_moves,
        total_moves=total_moves,
        final_evaluation=round(final_eval / 100, 2),
    )
