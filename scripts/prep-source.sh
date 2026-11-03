#!/usr/bin/env bash
# Regenerate public/source.mp4 (60fps H.264 proxy, not committed — 72MB) from the original clip.
# Usage: scripts/prep-source.sh path/to/input.mov
set -euo pipefail
ffmpeg -y -i "$1" -an -vf "format=yuv420p" -c:v libx264 -crf 14 -preset fast -g 15 public/source.mp4
