<div align="center">

# AI Algorithm Simulation Platform

**A full-stack educational AI algorithm simulator using chess positions as a teaching surface.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)

</div>

---

## Overview

AI Algorithm Simulation Platform helps students learn how search algorithms think using interactive chess positions. It includes a custom chess engine, five demonstrator personalities, branch exploration, and Gemini-powered reasoning written for algorithm learning.

---

## ✨ Features

### 🎮 Gameplay
- **Full Chess Rules** — all standard chess rules including castling, en passant, pawn promotion, check, checkmate, and stalemate detection
- **Play vs AI** — challenge the computer at five difficulty levels
- **Legal Move Highlighting** — click a piece to see all legal squares it can move to
- **Move History** — browse through all moves played in the game
- **Undo / Redo** — step backward and forward through the move history
- **Top Move Suggestions** — get the engine's top 3 recommended moves for the current position

### 🤖 AI Difficulty Levels

| Level | Name | Algorithm | Description |
|:-----:|------|-----------|-------------|
| 1 | Random | Random Selection | Picks a random legal move |
| 2 | Greedy | Greedy Evaluation | Evaluates captures one move ahead |
| 3 | Minimax | Minimax (Depth 3) | Full game-tree search, no pruning |
| 4 | Alpha-Beta | Alpha-Beta Pruning (Depth 3) | Minimax with alpha-beta pruning |
| 5 | Advanced | Alpha-Beta + Quiescence (Depth 4) | Move ordering, killer moves, history heuristic, and quiescence search |

### 📊 Position Evaluation
- **Material Counting** — standard piece values (Pawn = 100, Knight = 320, Bishop = 330, Rook = 500, Queen = 900)
- **Piece-Square Tables** — positional bonuses for each piece type based on board location
- **Endgame Detection** — switches to endgame king tables when material is low

---

## 🏗️ Architecture

The project follows a **client-server architecture** with a clear separation of concerns:

```
Chess-Engine-AI/
├── backend/                     # Python / FastAPI
│   ├── main.py                  # App entry point & CORS config
│   ├── requirements.txt         # Python dependencies
│   ├── engine/                  # Core chess engine
│   │   ├── board.py             # 8×8 board representation
│   │   ├── game_state.py        # Turn, castling rights, move history
│   │   ├── move_generator.py    # Legal move generation for all pieces
│   │   ├── move_validator.py    # Legality checks (pins, checks)
│   │   └── rules.py             # Checkmate, stalemate, draw rules
│   ├── ai/                      # AI opponents
│   │   ├── evaluation.py        # Position evaluation function
│   │   ├── greedy.py            # Level 2 — Greedy AI
│   │   ├── minimax.py           # Level 3 — Minimax AI
│   │   ├── alphabeta.py         # Level 4 — Alpha-Beta AI
│   │   └── advanced_ai.py       # Level 5 — Advanced AI
│   ├── analysis/                # Game analysis tools
│   │   ├── game_tree.py         # Game tree exploration
│   │   └── move_suggester.py    # Top-N move suggestions
│   ├── api/                     # REST API layer
│   │   ├── routes.py            # All endpoint handlers
│   │   └── schemas.py           # Pydantic request/response models
│   ├── utils/
│   │   └── constants.py         # Piece values & piece-square tables
│   └── tests/                   # Test suite
│
└── frontend/                    # React / TypeScript / Vite
    └── src/
        ├── pages/
        │   └── GamePage.tsx     # Main game page (state management)
        ├── components/
        │   ├── ChessBoard.tsx   # Board rendering
        │   ├── Square.tsx       # Individual square
        │   ├── Piece.tsx        # Piece rendering
        │   ├── Controls.tsx     # Game controls & AI level selector
        │   ├── MoveHistory.tsx  # Move history panel
        │   └── SuggestionsPanel.tsx  # AI move suggestions
        ├── services/
        │   └── api.ts           # Backend API client
        └── types/
            └── chess.ts         # TypeScript type definitions
```

---

## 🛠️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/game/start` | Start a new game |
| `GET` | `/game/state` | Get current board state |
| `POST` | `/game/move` | Make a player move |
| `POST` | `/ai/move` | Request an AI move |
| `GET` | `/game/legal-moves/{square}` | Get legal moves for a piece |
| `GET` | `/analysis/top-moves` | Get top 3 recommended moves |
| `POST` | `/game/undo` | Undo last move(s) |
| `POST` | `/game/redo` | Redo undone move(s) |
| `POST` | `/game/set-difficulty` | Change AI difficulty level |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Chess-Engine-AI.git
cd Chess-Engine-AI
```

### 2. Start the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API server will start at **http://localhost:8000**. Visit http://localhost:8000/docs for interactive Swagger documentation.

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will open at **http://localhost:5173**.

---

## 🧠 How the AI Works

### Evaluation Function
Every board position is scored in **centipawns** (1 pawn = 100). The evaluation considers:
1. **Material balance** — sum of piece values for each side
2. **Positional bonuses** — piece-square tables reward pieces on strong squares
3. **Endgame awareness** — king evaluation switches to an endgame table when material drops below a threshold

### Search Algorithms

- **Minimax** — exhaustively searches the game tree to a fixed depth, choosing the move that maximizes the minimum guaranteed score.
- **Alpha-Beta Pruning** — optimized minimax that prunes branches that cannot affect the final decision, dramatically reducing nodes searched.
- **Advanced (Level 5)** — extends alpha-beta with:
  - **Move Ordering** — searches promising moves first (captures, promotions, killer moves) for better pruning
  - **MVV-LVA** — Most Valuable Victim / Least Valuable Attacker ordering for captures
  - **Killer Moves** — remembers non-capture moves that caused beta cutoffs at each depth
  - **History Heuristic** — tracks moves that have been historically good across the search
  - **Quiescence Search** — continues searching capture sequences beyond the depth limit to avoid the horizon effect

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python, FastAPI, Pydantic, Uvicorn |
| **Frontend** | React 19, TypeScript 5.9, Vite 7 |
| **Tooling** | ESLint, TypeScript Compiler |

---

## 👤 Developer

**Pranav** — Full-Stack Developer & AI Enthusiast

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).