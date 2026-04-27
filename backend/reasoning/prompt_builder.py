"""Prompt construction for Groq AI reasoning output."""

from typing import Any


def build_explanation_prompt(
    demonstrator_name: str,
    personality: str,
    chosen_move: dict[str, Any],
    alternatives: list[dict[str, Any]],
    board_context: dict[str, Any],
    branch_mode: bool = False,
) -> str:
    alt_lines = "\n".join(
        [f"- {item.get('move', '?')} (score {item.get('score', 0)})" for item in alternatives[:3]]
    ) or "- none"

    mode_label = "branch exploration" if branch_mode else "main line"
    move_num = board_context.get('move_number', '?')
    balance = board_context.get('material_balance', 0)
    is_capture = board_context.get('is_capture', False)

    return f"""You are {demonstrator_name}, an algorithm demonstrator.
Personality: {personality}

State: move {move_num}, material balance {balance}cp, capture={is_capture}, mode={mode_label}.

Chosen: {chosen_move.get('move', '?')} (score {chosen_move.get('score', 0)})
Alternatives:
{alt_lines}

Respond in 2-3 SHORT sentences max. Focus only on:
- Why THIS algorithm picked this move (evaluation logic, search depth, pruning, branch quality).
- How the current game state influenced the decision.
Do NOT give chess strategy advice. Stay in character. Be concise.""".strip()
