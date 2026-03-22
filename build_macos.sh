#!/usr/bin/env bash
# Build Chess.app and a .dmg for the current macOS architecture.
# Run on an Intel Mac for the x86_64 .dmg; run on an M-series Mac for arm64.
set -euo pipefail

ARCH=$(uname -m)           # x86_64  or  arm64
VERSION="1.0.0"
DMG_NAME="Chess-macOS-${ARCH}-v${VERSION}.dmg"

# ── 1. Install Python dependencies ─────────────────────────────────────────
pip install pyinstaller pygame python-chess

# ── 2. Download the right Stockfish binary ─────────────────────────────────
mkdir -p stockfish
SF_BIN="stockfish/stockfish"

if [ ! -f "$SF_BIN" ]; then
    echo "Downloading Stockfish for ${ARCH}..."
    if [ "$ARCH" = "arm64" ]; then
        SF_URL="https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-macos-m1-apple-silicon.tar"
    else
        SF_URL="https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-macos-x86-64-modern.tar"
    fi
    curl -L "$SF_URL" -o /tmp/sf.tar
    tar -xf /tmp/sf.tar -C /tmp
    # The archive contains a single binary — copy it
    find /tmp -maxdepth 2 -name "stockfish*" -type f -perm +111 | head -1 | xargs -I{} cp {} "$SF_BIN"
    chmod +x "$SF_BIN"
fi

# ── 3. Convert chess.png → chess.icns ──────────────────────────────────────
if [ ! -f chess.icns ]; then
    echo "Creating chess.icns..."
    mkdir -p /tmp/chess.iconset
    for size in 16 32 64 128 256 512; do
        sips -z $size $size chess.png --out /tmp/chess.iconset/icon_${size}x${size}.png > /dev/null
        sips -z $((size*2)) $((size*2)) chess.png --out /tmp/chess.iconset/icon_${size}x${size}@2x.png > /dev/null
    done
    iconutil -c icns /tmp/chess.iconset -o chess.icns
fi

# ── 4. Build the .app ──────────────────────────────────────────────────────
pyinstaller --clean chess.spec

# ── 5. Package as .dmg ─────────────────────────────────────────────────────
if ! command -v create-dmg &> /dev/null; then
    echo "Installing create-dmg..."
    brew install create-dmg
fi

rm -f "$DMG_NAME"
create-dmg \
    --volname "Chess" \
    --volicon "chess.icns" \
    --window-pos 200 120 \
    --window-size 600 380 \
    --icon-size 100 \
    --icon "Chess.app" 175 180 \
    --hide-extension "Chess.app" \
    --app-drop-link 425 180 \
    "$DMG_NAME" \
    "dist/Chess.app"

echo ""
echo "✓ Done: $DMG_NAME"
