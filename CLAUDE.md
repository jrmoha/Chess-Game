# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A chess game built with Python and Pygame, supporting multiple game modes: player vs player, player vs random AI, player vs minimax AI, and player vs Stockfish AI.

## Running the Game

```bash
# Install dependencies
pip install -r requirements.txt   # pygame, numpy, python-chess, stockfish

# Install Stockfish binary (required for smart mode)
brew install stockfish   # macOS

# Run directly
python main.py

# Run via Docker (exposes VNC on port 6080)
./run.sh
```

## Game Controls

- **T** — cycle board theme
- **R** — reset current game
- **P** — switch to PvP mode
- **H** — switch to random AI mode (mode "r")
- **A** — switch to minimax AI mode (mode "a", depth 6)
- **I** — switch to AI class mode (mode "ai", depth 3, uses `AI.minimax`)
- **S** — switch to Stockfish AI mode (mode "smart", depth 10 / 1s per move)

## Architecture

The game uses a single-window Pygame loop in `main.py` (`Main.mainloop`) that branches on `game.mode` to handle five modes: `"pvp"`, `"r"` (random), `"a"` (minimax in Game), `"ai"` (minimax in AI class), `"smart"` (Stockfish via python-chess).

**Core classes:**

- **`Board`** (`board.py`) — 8x8 grid of `Square` objects, move execution, move validation, check detection via `in_check()` (deep-copies board to test), legal move generation via `calc_moves()`. Tracks `whiteScore`/`blackScore` (start at 1039). Piece setup in `_add_piece()`.
- **`Game`** (`game.py`) — orchestrates rendering (show_bg, show_pieces, show_moves, show_last_move, show_hover), turn management, theme/sound config. Contains its own `miniMax()` implementation (used in mode "a") separate from `AI.minimax`.
- **`AI`** (`ai.py`) — standalone minimax with alpha-beta pruning (used in mode "ai"). Uses `board.get_all_moves()` to enumerate moves.
- **`Piece`** (`piece.py`) — base class with subclasses: `Pawn`, `Knight`, `Bishop`, `Rook`, `Queen`, `King`. Each piece stores its own `moves` list, `value`, and texture path. Textures at `assets/images/imgs-{80,128}px/{color}_{name}.png`.
- **`Drager`** (`dragger.py`) — drag-and-drop state for mouse interaction.
- **`Config`** (`config.py`) — themes and sound assets. Themes: default, brown, blue, gray, USCF.
- **`Square`** (`square.py`) — holds row, col, optional piece. `in_range()` for bounds checking.
- **`Move`** (`move.py`) — initial/final Square pair.
- **`SmartAI`** (`smart_ai.py`) — Stockfish-backed AI. Maintains a `chess.Board` shadow alongside the Pygame board. `push_move()` syncs moves; `get_move()` returns Stockfish's choice. Coordinate mapping: `chess_square = chess.square(col, 7-row)`.

**Key design notes:**

- `calc_moves()` uses nested functions (`pawn_moves`, `knight_moves`, `straightline_moves`, `king_moves`) and a `bool` parameter to control whether check-validation is applied.
- Check detection deep-copies the entire board for each candidate move, making it expensive.
- There are two separate minimax implementations: `Game.miniMax()` and `AI.minimax()`, used by different modes.
- Board coordinates: row 0 is top (black back rank), row 7 is bottom (white back rank). White pawns move with dir=-1, black with dir=+1.
- Human player always plays white; AI/random plays black.
