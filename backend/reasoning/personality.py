"""Personality and style instructions for each demonstrator."""

from utils.demonstrators import DEMONSTRATORS


def get_personality(demonstrator_id: str) -> str:
    for cfg in DEMONSTRATORS.values():
        if cfg["id"] == demonstrator_id:
            return cfg["personality"]
    return "Calm, educational, and focused on algorithm logic."
