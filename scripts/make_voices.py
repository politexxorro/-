"""Generate all dialogue lines (ElevenLabs eleven_multilingual_v2 via proxy) + Rhubarb phonetic lipsync.

Lines are numbered by order in the film. Two takes each; take choice is recorded in audio/VOICES.md.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import api  # noqa: E402

RHUBARB = '/home/hoplite/tools/Rhubarb-Lip-Sync-1.13.0-Linux/rhubarb'
SHE, HE = 'GN4wbsbejSnGSa1AzjH5', 'pvY1pikBdoI4SB62vEVo'
LINES = [
    ('03_he_023', HE, 'Это… так и задумано было.'),
    ('04_he_082', HE, 'Для тебя.'),
    ('05_he_093', HE, 'Знаешь… я бы хотел, чтобы каждый день был как сегодня.'),
    ('06_she_098', SHE, 'Глупый… так и будет.'),
    ('07_she_115', SHE, 'Мой самый счастливый день… и завтра будет ещё один.'),
    ('08_she_laugh_s2', SHE, 'Ха-ха-ха-ха!'),
    ('09_she_laugh_s3', SHE, 'Ха-ха!'),
    ('10_he_laugh', HE, 'Ха-ха-ха!'),
]
out = {}
for name, voice, text in LINES:
    for take in (1, 2):
        mp3 = Path(f'audio/voice/{name}_v{take}.mp3')
        if not mp3.exists():
            api.tts(text, voice, str(mp3))
        wav = mp3.with_suffix('.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(mp3), '-ar', '44100', '-ac', '1', str(wav)], check=True)
        js = Path(f'audio/lipsync/{name}_v{take}.json')
        subprocess.run([RHUBARB, '-q', '-r', 'phonetic', '-f', 'json', '--dialogFile', '/dev/null', '-o', str(js), str(wav)],
                       check=False)
        if not js.exists():
            subprocess.run([RHUBARB, '-q', '-r', 'phonetic', '-f', 'json', '-o', str(js), str(wav)], check=True)
        dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                    str(mp3)], capture_output=True, text=True).stdout)
        out[f'{name}_v{take}'] = {'voice': voice, 'text': text, 'dur': round(dur, 3)}
        print(name, take, round(dur, 2), flush=True)
json.dump(out, open('audio/voice/lines.json', 'w'), ensure_ascii=False, indent=1)
