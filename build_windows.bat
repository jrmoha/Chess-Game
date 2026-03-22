@echo off
setlocal enabledelayedexpansion

set VERSION=1.0.0
set OUT=Chess-Windows-v%VERSION%-Setup.exe

:: ── 1. Install Python dependencies ─────────────────────────────────────────
pip install pyinstaller pygame python-chess pywin32

:: ── 2. Download Stockfish for Windows ──────────────────────────────────────
if not exist stockfish mkdir stockfish
if not exist stockfish\stockfish.exe (
    echo Downloading Stockfish for Windows...
    curl -L "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-windows-x86-64-avx2.zip" -o %TEMP%\sf.zip
    tar -xf %TEMP%\sf.zip -C %TEMP%
    for /r %TEMP% %%f in (stockfish*.exe) do (
        copy "%%f" stockfish\stockfish.exe
        goto :sf_done
    )
    :sf_done
)

:: ── 3. Convert chess.png → chess.ico (requires Pillow) ─────────────────────
pip install Pillow
python -c "from PIL import Image; img=Image.open('chess.png'); img.save('chess.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"

:: ── 4. Build the .exe bundle ───────────────────────────────────────────────
pyinstaller --clean chess.spec

:: ── 5. (Optional) Create an installer with Inno Setup ──────────────────────
:: Download Inno Setup from https://jrsoftware.org/isinfo.php, then uncomment:
::
:: iscc /O. /F"Chess-Windows-v%VERSION%-Setup" installer.iss
::
:: Otherwise the distributable is the folder at dist\Chess\

echo.
echo Done! Distributable folder: dist\Chess\
echo Zip it or use Inno Setup to create an installer.
