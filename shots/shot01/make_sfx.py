"""Generate scene-1 SFX (ElevenLabs text-to-sound via proxy) and the extra giggle line."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import api  # noqa: E402

D = 'audio/sfx/shot01/'
SFX = {
    'amb_morning': 'quiet cozy bedroom morning ambience, soft birds chirping outside a closed window, very distant city hum, no music',
    'clock_tick': 'soft quiet wall clock ticking in a calm room, no music',
    'poke': 'tiny soft cute cartoon poke boop sound on a cheek, very short',
    'wake_sting': 'short comedic anime surprise sting, quick whoosh and soft pop, very short',
    'rustle_pillow': 'soft duvet and pillow fabric rustle, someone pulls a pillow over their face, close up',
    'cloth_lean': 'soft hoodie fabric rustle, person leaning forward, close up, short',
    'sleep_breath': 'calm slow sleepy breathing of a young man through the nose, close up, quiet',
}
for k, v in SFX.items():
    out = Path(D + k + '_v1.mp3')
    if not out.exists():
        print(api.sfx(v, str(out)))
for i in (1, 2):
    out = Path(f'audio/voice/02_she_giggle_v{i}.mp3')
    if not out.exists():
        print(api.tts('Хи-хи-хи!', 'GN4wbsbejSnGSa1AzjH5', str(out)))
