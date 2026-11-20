#!/usr/bin/env bash
# One-time environment setup for the kurzgesagt-reel toolkit. Safe to re-run.
set -e
python3 -c "import skia" 2>/dev/null && python3 -c "import numpy" 2>/dev/null && { echo "skia-python ready"; } || {
  pip install -q skia-python numpy || pip install -q --break-system-packages skia-python numpy
  # skia-python needs libEGL on headless Linux
  python3 -c "import skia" 2>/dev/null || { (apt-get install -y -q libegl1 >/dev/null 2>&1 || (apt-get update -q >/dev/null 2>&1 && apt-get install -y -q libegl1 >/dev/null 2>&1)); }
  python3 -c "import skia; print('skia-python', skia.__version__)"
}
command -v ffmpeg >/dev/null || { apt-get install -y -q ffmpeg >/dev/null 2>&1 || (apt-get update -q >/dev/null && apt-get install -y -q ffmpeg >/dev/null); }
echo "ffmpeg: $(command -v ffmpeg)"
