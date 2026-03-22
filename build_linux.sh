#!/usr/bin/env bash
# Builds a self-contained Linux binary and optional AppImage.
set -euo pipefail

VERSION="1.0.0"
ARCH=$(uname -m)   # x86_64 or aarch64

# ── 1. Install Python dependencies ─────────────────────────────────────────
pip install pyinstaller pygame python-chess

# ── 2. Download Stockfish for Linux ────────────────────────────────────────
mkdir -p stockfish
SF_BIN="stockfish/stockfish"

if [ ! -f "$SF_BIN" ]; then
    echo "Downloading Stockfish for Linux ${ARCH}..."
    if [ "$ARCH" = "aarch64" ]; then
        SF_URL="https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-armv8.tar"
    else
        SF_URL="https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar"
    fi
    curl -L "$SF_URL" -o /tmp/sf.tar
    tar -xf /tmp/sf.tar -C /tmp
    find /tmp -maxdepth 2 -name "stockfish*" -type f ! -name "*.tar" | head -1 | xargs -I{} cp {} "$SF_BIN"
    chmod +x "$SF_BIN"
fi

# ── 3. Build ────────────────────────────────────────────────────────────────
pyinstaller --clean chess.spec

# ── 4. (Optional) Wrap in AppImage ─────────────────────────────────────────
# Requires appimagetool: https://appimage.github.io/appimagetool/
if command -v appimagetool &> /dev/null; then
    APPDIR="Chess.AppDir"
    rm -rf "$APPDIR"
    mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/icons"

    cp -r dist/Chess/* "$APPDIR/usr/bin/"
    cp chess.png "$APPDIR/usr/share/icons/chess.png"
    cp chess.png "$APPDIR/chess.png"

    cat > "$APPDIR/Chess.desktop" <<EOF
[Desktop Entry]
Name=Chess
Exec=Chess
Icon=chess
Type=Application
Categories=Game;
EOF

    ln -sf usr/bin/Chess "$APPDIR/AppRun"
    appimagetool "$APPDIR" "Chess-Linux-${ARCH}-v${VERSION}.AppImage"
    echo "✓ AppImage: Chess-Linux-${ARCH}-v${VERSION}.AppImage"
else
    echo "✓ Binary folder: dist/Chess/"
    echo "  (install appimagetool to produce an AppImage)"
    tar -czf "Chess-Linux-${ARCH}-v${VERSION}.tar.gz" -C dist Chess
    echo "✓ Archive: Chess-Linux-${ARCH}-v${VERSION}.tar.gz"
fi
