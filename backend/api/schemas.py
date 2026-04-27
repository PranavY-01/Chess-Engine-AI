"""
Pydantic schemas for the REST API request/response models.
"""
from pydantic import BaseModel
from typing import Optional


class GameStartRequest(BaseModel):
    """Request to start a new game."""
    ai_level: int = 3  # default AI difficulty level (1-5)


class GameStartResponse(BaseModel):
    """Response after starting a new game."""
    board: list[list[Optional[str]]]
    turn: str
    status: str
    message: str


class GameStateResponse(BaseModel):
    """Response containing current game state."""
    board: list[list[Optional[str]]]
    turn: str
    status: str
    move_history: list[str]
    is_check: bool
    last_move: Optional[dict] = None


class MoveRequest(BaseModel):
    """Request to make a player move."""
    from_square: str   # e.g., "e2" — using from_square to avoid Python keyword
    to_square: str     # e.g., "e4"
    promotion: Optional[str] = None  # 'Q', 'R', 'B', 'N'


class MoveResponse(BaseModel):
    """Response after making a move."""
    board: list[list[Optional[str]]]
    turn: str
    status: str
    move_history: list[str]
    is_check: bool
    player_move: Optional[dict] = None
    ai_move: Optional[dict] = None
    last_move: Optional[dict] = None
    message: str


class AIMoveRequest(BaseModel):
    """Request for AI to make a move."""
    level: Optional[int] = None  # override current AI level


class AIMoveResponse(BaseModel):
    """Response after AI makes a move."""
    board: list[list[Optional[str]]]
    turn: str
    status: str
    move_history: list[str]
    is_check: bool
    ai_move: Optional[dict] = None
    last_move: Optional[dict] = None
    message: str


class TopMoveItem(BaseModel):
    """A single move suggestion."""
    move: str        # SAN notation
    score: float     # evaluation score
    from_square: str  # source square
    to_square: str    # destination square


class TopMovesResponse(BaseModel):
    """Response with top move suggestions."""
    suggestions: list[TopMoveItem]
    turn: str


class LegalMovesResponse(BaseModel):
    """Response with legal moves for a given square."""
    moves: list[dict]  # list of {to: "e4", promotion: null}


class UndoRedoResponse(BaseModel):
    """Response after undo/redo."""
    board: list[list[Optional[str]]]
    turn: str
    status: str
    move_history: list[str]
    is_check: bool
    last_move: Optional[dict] = None
    message: str


class DemonstratorInfo(BaseModel):
    id: str
    name: str
    emoji: str
    accent: str
    algorithm: str


class ExplainRequest(BaseModel):
    demonstrator_id: str
    chosen_move: dict
    alternatives: list[dict] = []
    board_context: dict = {}
    branch_mode: bool = False


class ExplainResponse(BaseModel):
    explanation: str


class BranchStartRequest(BaseModel):
    from_square: str
    to_square: str
    rank: int = 1
    level: int = 5


class BranchAdvanceRequest(BaseModel):
    branch_id: str


class BranchStateResponse(BaseModel):
    branch_id: str
    board: list[list[Optional[str]]]
    turn: str
    status: str
    steps: list[dict]
    progress: int
    max_half_moves: int
    base_rank: int
    suggestions: list[dict]


class HintResponse(BaseModel):
    from_square: str
    to_square: str
    score: float


class AiVsAiStartRequest(BaseModel):
    white_level: int
    black_level: int


class AiVsAiPauseRequest(BaseModel):
    session_id: str
    paused: bool


class AiVsAiStepRequest(BaseModel):
    session_id: str


class AiVsAiStateResponse(BaseModel):
    session_id: str
    board: list[list[Optional[str]]]
    turn: str
    status: str
    move_history: list[str]
    is_check: bool
    paused: bool
    white_level: int
    black_level: int
    last_move: Optional[dict] = None
    evaluation: float = 0
    white_score: float = 50
    black_score: float = 50


class EvaluationResponse(BaseModel):
    """Position evaluation for the accuracy meter."""
    evaluation: float        # evaluation in pawns (e.g. +0.16)
    white_score: float       # white win percentage (0-100)
    black_score: float       # black win percentage (0-100)


class EndSessionResponse(BaseModel):
    """Response when ending a game session."""
    status: str
    move_history: list[str]
    total_moves: int
    final_evaluation: float
