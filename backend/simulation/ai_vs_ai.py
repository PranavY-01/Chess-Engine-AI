"""In-memory AI vs AI session manager."""

import uuid
from engine.game_state import GameState
from engine.move_validator import MoveValidator
from ai.evaluation import evaluate
from utils.constants import COL_TO_FILE, ROW_TO_RANK


def _coords_to_square(row: int, col: int) -> str:
    return COL_TO_FILE[col] + ROW_TO_RANK[row]


class AiVsAiManager:
    def __init__(self):
        self.sessions: dict[str, dict] = {}
        self.validator = MoveValidator()

    def start(self, white_level: int, black_level: int):
        session_id = str(uuid.uuid4())
        state = GameState()
        self.sessions[session_id] = {
            "id": session_id,
            "state": state,
            "white_level": white_level,
            "black_level": black_level,
            "paused": False,
            "last_move": None,
        }
        return self.serialize(session_id)

    def get(self, session_id: str):
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        return self.serialize(session_id)

    def set_paused(self, session_id: str, paused: bool):
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        self.sessions[session_id]["paused"] = paused
        return self.serialize(session_id)

    def step(self, session_id: str, get_ai_move_fn):
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        session = self.sessions[session_id]
        state = session["state"]
        if session["paused"] or state.get_game_status() != "active":
            return self.serialize(session_id)

        level = session["white_level"] if state.turn == "w" else session["black_level"]
        move = get_ai_move_fn(state, level)
        if move:
            state.make_move(move)
            session["last_move"] = {
                "from": _coords_to_square(move.start_row, move.start_col),
                "to": _coords_to_square(move.end_row, move.end_col),
            }
        return self.serialize(session_id)

    def reset(self, session_id: str):
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        session = self.sessions[session_id]
        session["state"] = GameState()
        session["paused"] = False
        session["last_move"] = None
        return self.serialize(session_id)

    def serialize(self, session_id: str):
        session = self.sessions[session_id]
        state = session["state"]
        raw_eval = evaluate(state)
        import math
        win_pct = 50 + 50 * math.tanh(raw_eval / 400)
        return {
            "session_id": session_id,
            "board": state.board.to_list(),
            "turn": state.turn,
            "status": state.get_game_status(),
            "move_history": state.get_formatted_move_history(),
            "is_check": self.validator.is_in_check(state.board, state.turn),
            "paused": session["paused"],
            "white_level": session["white_level"],
            "black_level": session["black_level"],
            "last_move": session["last_move"],
            "evaluation": round(raw_eval / 100, 2),
            "white_score": round(win_pct, 1),
            "black_score": round(100 - win_pct, 1),
        }
