"""Objective checks for a voice take: STT transcript (scribe_v1), duration, median F0.
usage: python3 scripts/voice_check.py file.mp3 [...]
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import requests

sys.path.insert(0, str(Path(__file__).parent))
import api  # noqa: E402


def f0_median(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    fr, hop, sr = 1024, 256, 16000
    f0s = []
    for i in range(0, len(x) - fr, hop):
        w = x[i:i + fr] * np.hanning(fr)
        if np.sqrt((w ** 2).mean()) < 0.02:
            continue
        ac = np.correlate(w, w, 'full')[fr - 1:]
        lo, hi = sr // 400, sr // 70
        lag = lo + np.argmax(ac[lo:hi])
        if ac[lag] > 0.3 * ac[0]:
            f0s.append(sr / lag)
    return float(np.median(f0s)) if f0s else 0.0, len(x) / sr


for p in sys.argv[1:]:
    with open(p, 'rb') as f:
        r = requests.post(f'{api.BASE}/audio/transcriptions', headers=api.H,
                          files={'file': f}, data={'model': 'scribe_v1'}, timeout=300)
    text = r.json().get('text', r.text[:200]) if r.ok else f'HTTP {r.status_code} {r.text[:200]}'
    f0, dur = f0_median(p)
    print(f'{Path(p).name:28s} dur={dur:4.2f}s F0≈{f0:5.0f}Hz  «{text}»')
