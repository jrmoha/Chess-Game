#!/bin/bash
set -e

Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
export SDL_AUDIODRIVER=dummy

sleep 1

x11vnc -display :99 -nopw -listen localhost -forever &>/dev/null &

websockify --web /usr/share/novnc 6080 localhost:5900 &>/dev/null &

sleep 1

python /app/main.py
