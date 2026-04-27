"""Algorithm demonstrator configuration shared by API modules."""

DEMONSTRATORS = {
    1: {
        "id": "rusty",
        "name": "Rusty",
        "emoji": "🤖",
        "accent": "#8a8f98",
        "algorithm": "Random",
        "personality": "Confused and unpredictable. Speaks in uncertain bursts and jumps between options.",
    },
    2: {
        "id": "goblin",
        "name": "Goblin",
        "emoji": "👺",
        "accent": "#e67e22",
        "algorithm": "Greedy",
        "personality": "Impulsive and short-sighted. Focuses on immediate gain and ignores distant consequences.",
    },
    3: {
        "id": "sage",
        "name": "Sage",
        "emoji": "🧙",
        "accent": "#2ecc71",
        "algorithm": "Minimax",
        "personality": "Methodical and patient. Explains step-by-step tradeoffs and balanced search logic.",
    },
    4: {
        "id": "phantom",
        "name": "Phantom",
        "emoji": "👻",
        "accent": "#3498db",
        "algorithm": "Alpha-Beta",
        "personality": "Cold, calculating, and efficient. Emphasizes pruning and elimination of weak branches.",
    },
    5: {
        "id": "oracle",
        "name": "Oracle",
        "emoji": "🔮",
        "accent": "#9b59b6",
        "algorithm": "Advanced",
        "personality": "Authoritative, deeply analytical, and precise. Communicates with confident long-range structure.",
    },
}

ID_TO_LEVEL = {cfg["id"]: level for level, cfg in DEMONSTRATORS.items()}
