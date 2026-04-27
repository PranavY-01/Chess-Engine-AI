"""Branch exploration engine for rejected move simulation."""

import uuid
from engine.game_state import GameState
from engine.move_validator import MoveValidator
from analysis.move_suggester import MoveSuggester
from utils.constants import FILE_TO_COL, RANK_TO_ROW, COL_TO_FILE, ROW_TO_RANK


def square_to_coords(square: str) -> tuple[int, int]:
    return RANK_TO_ROW[square[1]], FILE_TO_COL[square[0]]


def coords_to_square(row: int, col: int) -> str:
    return COL_TO_FILE[col] + ROW_TO_RANK[row]


class BranchEngine:
    def __init__(self):
        self.validator = MoveValidator()
        self.sessions: dict[str, dict] = {}

    def start_branch(self, base_state: GameState, from_square: str, to_square: str, rank: int, level: int, get_ai_move_fn):
        branch_state = base_state.copy()
        legal_moves = self.validator.get_legal_moves(branch_state)

        sr, sc = square_to_coords(from_square)
        er, ec = square_to_coords(to_square)

        chosen = next(
            (
                m
                for m in legal_moves
                if m.start_row == sr and m.start_col == sc and m.end_row == er and m.end_col == ec
            ),
            None,
        )
        if chosen is None:
            raise ValueError("Rejected move is not legal in current state")

        branch_state.make_move_no_validate(chosen)

        branch_id = str(uuid.uuid4())
        self.sessions[branch_id] = {
            "id": branch_id,
            "state": branch_state,
            "base_rank": rank,
            "steps": [
                {
                    "from": from_square,
                    "to": to_square,
                    "score": None,
                    "move": "student-branch-choice",
                }
            ],
            "progress": 1,
            "max_half_moves": 5,
            "level": level,
            "get_ai_move_fn": get_ai_move_fn,
        }

        return self._serialize(branch_id)

    def advance(self, branch_id: str):
        session = self.sessions.get(branch_id)
        if not session:
            raise ValueError("Branch not found")

        if session["progress"] >= session["max_half_moves"]:
            return self._serialize(branch_id)

        state = session["state"]
        move = session["get_ai_move_fn"](state, session["level"])
        if move is None:
            return self._serialize(branch_id)

        state.make_move_no_validate(move)
        session["progress"] += 1
        session["steps"].append(
            {
                "from": coords_to_square(move.start_row, move.start_col),
                "to": coords_to_square(move.end_row, move.end_col),
                "score": None,
                "move": f"{coords_to_square(move.start_row, move.start_col)}{coords_to_square(move.end_row, move.end_col)}",
            }
        )

        return self._serialize(branch_id)

    def end(self, branch_id: str):
        if branch_id in self.sessions:
            del self.sessions[branch_id]

    def _serialize(self, branch_id: str):
        session = self.sessions[branch_id]
        state = session["state"]
        suggester = MoveSuggester(depth=2, top_n=3)
        suggestions = suggester.get_suggestions(state)
        return {
            "branch_id": branch_id,
            "board": state.board.to_list(),
            "turn": state.turn,
            "status": state.get_game_status(),
            "steps": session["steps"],
            "progress": session["progress"],
            "max_half_moves": session["max_half_moves"],
            "base_rank": session["base_rank"],
            "suggestions": suggestions,
        }
