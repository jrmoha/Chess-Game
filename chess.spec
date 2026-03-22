# chess.spec  — PyInstaller build spec (Windows / Linux / macOS)
import sys
import os

block_cipher = None

IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"

# ------------------------------------------------------------
# Stockfish binary to bundle.
# Place the correct platform binary in the "stockfish/" folder
# before running pyinstaller. Build scripts do this automatically.
# ------------------------------------------------------------
_sf_dir = "stockfish"
if IS_WINDOWS:
    _sf_bin = os.path.join(_sf_dir, "stockfish.exe")
else:
    _sf_bin = os.path.join(_sf_dir, "stockfish")

binaries = [(_sf_bin, ".")] if os.path.exists(_sf_bin) else []

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=[
        ("assets", "assets"),
        ("chess.png", "."),
    ],
    hiddenimports=["pygame", "chess", "chess.engine"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Chess",
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon="chess.ico" if IS_WINDOWS else ("chess.icns" if IS_MAC else None),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="Chess",
)

if IS_MAC:
    app = BUNDLE(
        coll,
        name="Chess.app",
        icon="chess.icns",
        bundle_identifier="com.chess.game",
        info_plist={
            "CFBundleName": "Chess",
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "10.13",
        },
    )
