# Chess AI Upgrade Plan

## Current State: What's Wrong

The existing AI has **fundamental bugs** that make it barely functional, plus major performance and knowledge gaps.

### Critical Bugs

1. **Board state corruption during search** — `ai.py` modifies `tempBoard` during move exploration but never resets it between iterations. Each subsequent move evaluation operates on an increasingly corrupt board.
2. **Wrong board passed to recursion** — `game.py:212-213` deepcopies the board into `boardCpy` but passes the **original** `board` to the recursive `miniMax()` call, making all evaluations meaningless.
3. **Piece value sign is always 1** — `piece.py:8` has `value_sign = 1 if color == "white" else 1`. Both branches produce 1; black pieces were intended to be negative.
4. **Score inversion in `getBlackScore`** — `board.py:580` subtracts black piece values (`score -= piece.value`), producing a negative score that gets further confused in evaluation math.
5. **Knight move validation breaks early** — `board.py:283-284` does `break` when a knight move causes check, skipping all remaining valid knight moves.
6. **`whiteScore`/`blackScore` start at 1039 but are never used by the AI evaluator** — the AI recalculates from scratch via `getWhiteScore()`/`getBlackScore()`, while `main.py` manually tracks captures against the 1039 values. Two parallel scoring systems that don't interact.

### Performance Bottlenecks

- **`copy.deepcopy()` on every node** — for depth 6 with branching factor ~30, this means millions of full board copies per move.
- **`in_check()` deepcopies the board again** inside `calc_moves()`, compounding the cost exponentially.
- **Debug `print()` statements** in the search loop add I/O overhead on every node.
- **No move ordering** — `random.shuffle(moves)` destroys alpha-beta pruning effectiveness. Good ordering reduces branching factor from ~30 to ~5.

### Missing Chess Knowledge

- Material-only evaluation (no positional awareness)
- No piece-square tables
- No pawn structure, king safety, mobility, or endgame evaluation
- No quiescence search (horizon effect — AI stops evaluating right before losing its queen)
- No transposition table (re-evaluates identical positions)
- No iterative deepening

---

## The Plan: Replace the AI Engine

Rather than patching the broken minimax, the plan is to **replace the AI backend** with `python-chess` for board logic and use Stockfish as the engine, while keeping the existing Pygame UI for rendering and human interaction.

### Why This Approach

| Option | Strength | Effort | Maintenance |
|--------|----------|--------|-------------|
| Fix current minimax bugs | ~1200 ELO | Medium | High (fragile code) |
| Rewrite minimax with python-chess + PSTs (Sunfish-style) | ~2000 ELO | High | Medium |
| **python-chess + Stockfish** | **~3500 ELO, adjustable** | **Low-Medium** | **Low** |
| NNUE (Numbfish-style) | ~2300 ELO | High | Medium |

Stockfish gives us superhuman strength that we can **dial down** via skill level (0-20) and search depth/time limits — perfect for implementing difficulty levels later. The integration code is minimal.

---

## Implementation Steps

### Step 1: Add Dependencies

```
# requirements.txt
pygame==2.5.2
python-chess>=1.999
stockfish>=3.28.0
```

Stockfish binary: `brew install stockfish` (macOS) or download from stockfishchess.org.

### Step 2: Create the New AI Module

Create `smart_ai.py` — a clean AI class that:

1. Maintains a `chess.Board` as the authoritative game state for the AI
2. Syncs with the Pygame board (converts between our `Square`/`Piece` representation and `chess.Board`)
3. Uses Stockfish via `python-chess` UCI interface to get moves
4. Exposes a simple `get_move(difficulty) -> Move` API

```python
# smart_ai.py (sketch)
import chess
import chess.engine

class SmartAI:
    def __init__(self, stockfish_path="/opt/homebrew/bin/stockfish"):
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

    def sync_board(self, pygame_board):
        """Build FEN string from the Pygame board state."""
        # Convert our 8x8 Square grid to FEN
        ...

    def get_move(self, difficulty="medium"):
        """Get AI move. Returns (from_sq, to_sq) in our row/col format."""
        # Map difficulty to Stockfish constraints
        limits = {
            "easy":   chess.engine.Limit(depth=3, time=0.1),
            "medium": chess.engine.Limit(depth=10, time=1.0),
            "hard":   chess.engine.Limit(depth=18, time=3.0),
            "max":    chess.engine.Limit(time=5.0),
        }
        result = self.engine.play(self.board, limits[difficulty])
        uci_move = result.move  # e.g. chess.Move.from_uci("e2e4")
        return self._uci_to_internal(uci_move)

    def push_move(self, from_row, from_col, to_row, to_col, promotion=None):
        """Push a human move to keep the chess.Board in sync."""
        uci = self._internal_to_uci(from_row, from_col, to_row, to_col, promotion)
        self.board.push(chess.Move.from_uci(uci))

    def cleanup(self):
        self.engine.quit()
```

### Step 3: Create Board Sync Layer

The key challenge is keeping the `python-chess` board in sync with the Pygame board. Two approaches:

**Option A — Shadow board (recommended):** Maintain a `chess.Board` alongside the Pygame board. Every time a move is made (human or AI), push it to both boards. The Pygame board handles rendering; the `chess.Board` handles AI logic.

**Option B — FEN conversion:** Before each AI move, convert the entire Pygame board to a FEN string and set it on `chess.Board`. Simpler but slightly more error-prone.

The sync layer needs to handle coordinate mapping:
- Our board: row 0 = top (black back rank), row 7 = bottom (white back rank)
- python-chess: square 0 = a1 (bottom-left from white's perspective)
- Conversion: `chess_square = chess.square(col, 7 - row)`

### Step 4: Integrate into Main Loop

Modify `main.py` to use `SmartAI` instead of the old `AI` class and `Game.miniMax`:

```python
# In Main.__init__
from smart_ai import SmartAI
self.smart_ai = SmartAI()

# In the AI turn branch (replacing the current mode "ai" / "a" blocks):
if game.next_player == "black":
    # Sync human's last move
    self.smart_ai.push_move(last_from_row, last_from_col, last_to_row, last_to_col)

    # Get AI response
    ai_from, ai_to = self.smart_ai.get_move(difficulty="medium")

    # Execute on Pygame board
    piece = board.squares[ai_from[0]][ai_from[1]].piece
    initial = Square(ai_from[0], ai_from[1])
    final = Square(ai_to[0], ai_to[1])
    move = Move(initial, final)
    board.move(piece, move)

    # Push to chess.Board
    self.smart_ai.push_move(ai_from[0], ai_from[1], ai_to[0], ai_to[1])

    game.next_turn()
```

### Step 5: Add a New Game Mode

Add a new mode `"smart"` (key: **S**) that uses the Stockfish-backed AI, keeping old modes available for comparison:

- `main.py` key handler: `pygame.K_s` → `game.mode = "smart"`
- New branch in the main loop event handling for `mode == "smart"`

### Step 6: Clean Up Old AI Code

Once the new AI is working:
- Remove `ai.py` (old AI class)
- Remove `Game.miniMax()` and `Game.evaluate()` from `game.py`
- Remove `Board.getWhiteScore()`, `Board.getBlackScore()`, `Board.get_score()`, `Board.whiteScore`, `Board.blackScore` (only used by old AI)
- Remove modes `"a"` and `"ai"` from `main.py`, replace with `"smart"`
- Keep mode `"r"` (random) as the easiest difficulty

### Step 7: Handle Edge Cases

- **Pawn promotion:** Stockfish returns moves like `e7e8q`. Detect the promotion piece and apply it on the Pygame board.
- **Castling:** Stockfish returns king move `e1g1`. Detect castling and move the rook on the Pygame board as well.
- **En passant:** Stockfish handles this internally. On the Pygame side, detect the en passant capture and remove the captured pawn.
- **Game over:** Use `self.board.is_checkmate()`, `is_stalemate()`, `is_insufficient_material()` from python-chess for reliable game-over detection (currently missing from the project).
- **Stockfish not found:** Graceful fallback to random moves with a warning message.

---

## File Changes Summary

| File | Action |
|------|--------|
| `smart_ai.py` | **NEW** — Stockfish-backed AI with board sync |
| `main.py` | **MODIFY** — add "smart" mode, wire up SmartAI |
| `game.py` | **MODIFY** — remove `miniMax()`, `evaluate()`, add "smart" mode support |
| `ai.py` | **DELETE** — replaced by smart_ai.py |
| `board.py` | **MODIFY** — remove dead scoring methods after migration |
| `requirements.txt` | **MODIFY** — add `python-chess`, `stockfish` |
| `config.py` | **MODIFY** — add Stockfish path config |

---

## Future: Difficulty Levels

Once this foundation is in place, difficulty levels become trivial:

```python
DIFFICULTY_LEVELS = {
    "beginner":     {"depth": 1,  "time": 0.05, "skill_level": 0},
    "easy":         {"depth": 3,  "time": 0.1,  "skill_level": 5},
    "medium":       {"depth": 8,  "time": 0.5,  "skill_level": 10},
    "hard":         {"depth": 15, "time": 2.0,  "skill_level": 15},
    "grandmaster":  {"depth": 20, "time": 5.0,  "skill_level": 20},
}
```

Stockfish's skill level parameter (0-20) introduces deliberate inaccuracies at lower levels, making it a natural difficulty dial. Combined with depth/time limits, this gives fine-grained control.

---

## Alternative: Self-Contained Engine (No Stockfish Dependency)

If avoiding external binaries is important, a Sunfish-style approach using `python-chess` for move generation with piece-square table evaluation would reach ~2000 ELO in ~200 lines of code. This trades strength for portability. The implementation would:

1. Use `python-chess` for legal move generation (no custom `calc_moves` needed)
2. Implement negamax with alpha-beta, iterative deepening, transposition table
3. Use piece-square tables from Sunfish for evaluation
4. Add quiescence search for captures

This could be a fallback when Stockfish is not installed, providing a stronger AI than the current one without any external binary dependency.
