import sys
import os
import chess
import chess.engine

# When running as a PyInstaller bundle, look for a bundled Stockfish first
_bundle_dir = getattr(sys, "_MEIPASS", None)
_bundled = (
    [
        os.path.join(_bundle_dir, "stockfish"),
        os.path.join(_bundle_dir, "stockfish.exe"),
    ]
    if _bundle_dir
    else []
)

_STOCKFISH_PATHS = _bundled + [
    "/opt/homebrew/bin/stockfish",  # macOS (Homebrew)
    "/usr/games/stockfish",         # Debian/Ubuntu
    "/usr/local/bin/stockfish",
    "/usr/bin/stockfish",
    "stockfish",                    # PATH fallback
]

DIFFICULTY = {
    "easy":   chess.engine.Limit(depth=3,  time=0.1),
    "medium": chess.engine.Limit(depth=10, time=1.0),
    "hard":   chess.engine.Limit(depth=18, time=3.0),
}


class SmartAI:
    def __init__(self, stockfish_path=None):
        self.board = chess.Board()
        self.engine = None
        self._init_engine(stockfish_path)

    def _init_engine(self, path):
        candidates = ([path] if path else []) + _STOCKFISH_PATHS
        for p in candidates:
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(p)
                print(f"[SmartAI] Stockfish loaded from: {p}")
                return
            except Exception:
                continue
        print("[SmartAI] WARNING: Stockfish not found — AI will fall back to random moves.")

    def push_move(self, from_row, from_col, to_row, to_col, promotion=None):
        """Sync a move (human or AI) into the chess.Board."""
        uci = self._to_uci(from_row, from_col, to_row, to_col, promotion)
        try:
            self.board.push(chess.Move.from_uci(uci))
        except Exception as e:
            print(f"[SmartAI] push_move error: {e}  uci={uci}")

    def get_move(self, difficulty="medium"):
        """
        Ask Stockfish for a move.
        Returns (from_row, from_col, to_row, to_col, promotion_char_or_None)
        or None when the engine is unavailable.
        """
        if self.engine is None:
            return None
        limit = DIFFICULTY.get(difficulty, DIFFICULTY["medium"])
        result = self.engine.play(self.board, limit)
        mv = result.move
        from_row, from_col = self._sq_to_coords(mv.from_square)
        to_row, to_col = self._sq_to_coords(mv.to_square)
        promotion = chess.piece_symbol(mv.promotion) if mv.promotion else None
        return from_row, from_col, to_row, to_col, promotion

    def reset(self):
        self.board = chess.Board()

    def cleanup(self):
        if self.engine:
            self.engine.quit()
            self.engine = None

    # ---- coordinate helpers ----

    def _to_uci(self, from_row, from_col, to_row, to_col, promotion=None):
        from_name = chess.square_name(chess.square(from_col, 7 - from_row))
        to_name   = chess.square_name(chess.square(to_col,   7 - to_row))
        return from_name + to_name + (promotion or "")

    def _sq_to_coords(self, sq):
        col = chess.square_file(sq)
        row = 7 - chess.square_rank(sq)
        return row, col
