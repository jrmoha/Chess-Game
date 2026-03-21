#!/bin/bash
set -e

docker build -t chess-game .

docker run --rm -p 6080:6080 \
  -v "$(pwd)":/app \
  chess-game
