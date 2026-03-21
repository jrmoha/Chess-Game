# Chess

A chess game built with Python and Pygame. Play against a friend, a random AI, or **Stockfish** — one of the strongest chess engines in the world.

## Features

- **Player vs Player** — two humans on the same machine
- **Random AI** — black plays random legal moves
- **Stockfish AI** — black is powered by Stockfish with selectable difficulty

## Requirements

- Python 3.9+
- Stockfish binary

### macOS

```bash
brew install stockfish
pip install -r requirements.txt
python main.py
```

### Docker (headless, VNC on port 6080)

```bash
./run.sh
# Open http://localhost:6080 in your browser
```

The Docker image installs Stockfish automatically.

## Controls

| Key | Action |
|-----|--------|
| **P** | Player vs Player mode |
| **H** | Random AI mode |
| **S** | Stockfish AI mode |
| **1** | Easy difficulty (depth 3) |
| **2** | Medium difficulty (depth 10) — default |
| **3** | Hard difficulty (depth 18) |
| **T** | Cycle board theme |
| **R** | Reset current game |

## Architecture

```
main.py       — Pygame event loop, mode/difficulty routing
game.py       — Rendering, turn management, HUD
board.py      — 8×8 board, move execution, check detection, legal move generation
smart_ai.py   — Stockfish integration via python-chess (shadow board + UCI)
piece.py      — Piece classes (Pawn, Knight, Bishop, Rook, Queen, King)
square.py     — Square with piece reference and helper predicates
move.py       — Move (initial Square → final Square)
dragger.py    — Drag-and-drop mouse state
config.py     — Themes and sounds
const.py      — Window/board dimensions
```

### Coordinate system

Our board: row 0 = top (black back rank), row 7 = bottom (white back rank).
python-chess: square 0 = a1 (bottom-left from white's perspective).
Mapping: `chess_square = chess.square(col, 7 - row)`
