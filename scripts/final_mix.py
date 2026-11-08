"""Final audio: dialogue placed on the absolute timeline + procedural ambience/SFX (ffmpeg synthesis, since the
API key has no sound-effects model) + loudness -14 LUFS. Leaves headroom for music to be added later.
Output: audio/mix/final_mix_v1.wav (120.000 s, 48 kHz stereo) and audio/mix/stems/*.wav
"""
import subprocess
from pathlib import Path

D = Path('audio/mix')
S = D / 'stems'
S.mkdir(parents=True, exist_ok=True)
DUR = 120.0

# (file, start_s, gain, extra_filter)
VOICE = [
    ('audio/voice/01_she_011_v1.mp3', 11.083, 1.0, ''),
    ('audio/voice/02_she_giggle_v1.mp3', 12.58, 0.8, ''),
    ('audio/voice/08_she_laugh_s2_v1.mp3', 22.0, 0.8, ''),
    ('audio/voice/03_he_023_v1.mp3', 23.083, 1.0, ''),
    ('audio/voice/09_she_laugh_s3_v1.mp3', 54.2, 0.6, ''),
    ('audio/voice/10_he_laugh_v1.mp3', 54.5, 0.55, ''),
    ('audio/voice/08_she_laugh_s2_v2.mp3', 56.3, 0.6, ''),
    ('audio/voice/10_he_laugh_v2.mp3', 56.7, 0.55, ''),
    ('audio/voice/04_he_082_v1.mp3', 81.583, 1.0, ''),
    ('audio/voice/05_he_093_v1.mp3', 93.083, 1.0, ''),
    ('audio/voice/06_she_098_v1.mp3', 98.083, 1.0, ''),
    # off-screen whisper: softer, slightly darker, small room
    ('audio/voice/07_she_115_v1.mp3', 115.0, 0.75, ',lowpass=f=6500,aecho=0.7:0.6:35:0.12'),
]


def synth(name, expr):
    out = S / f'{name}.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', expr, '-t', str(DUR), '-ar', '48000', '-ac', '2',
                    str(out)], check=True)
    return out


def envelope(segments):
    """Piecewise volume expression: [(t0, t1, gain, fade)] -> ffmpeg volume expr (eval=frame)."""
    parts = []
    for t0, t1, g, fd in segments:
        parts.append(f'{g}*clip(min((t-{t0})/{fd},({t1}-t)/{fd}),0,1)')
    return '+'.join(parts)


# ambience beds (procedural)
room = synth('room', 'anoisesrc=c=brown:a=0.02:seed=1,lowpass=f=400')
rain = synth('rain', 'anoisesrc=c=pink:a=0.35:seed=2,highpass=f=300,lowpass=f=7000')
sizzle = synth('sizzle', 'anoisesrc=c=white:a=0.25:seed=3,highpass=f=2500,lowpass=f=9000,'
                         'volume=\'0.6+0.4*sin(2*PI*7*t)*sin(2*PI*3.1*t)\':eval=frame')
wind = synth('wind', 'anoisesrc=c=brown:a=0.4:seed=4,lowpass=f=700,'
                     'volume=\'0.5+0.5*sin(2*PI*0.13*t)*sin(2*PI*0.07*t+1)\':eval=frame')
street = synth('street', 'anoisesrc=c=pink:a=0.06:seed=5,lowpass=f=2500')
neon = synth('neon', 'sine=f=120:sample_rate=48000,volume=0.02')
tick = synth('tick', 'anoisesrc=c=white:a=0.6:seed=6,highpass=f=3000,'
                     'volume=\'if(lt(mod(t,1),0.012),1,0)\':eval=frame')

beds = [
    (room, envelope([(0, 14, 0.5, 0.5), (102, 120, 0.5, 1.0)])),
    (tick, envelope([(0, 14, 0.12, 0.8), (102, 118, 0.10, 1.0)])),
    (sizzle, envelope([(14, 20, 0.35, 0.4)])),
    (street, envelope([(30, 48.5, 0.8, 0.5)])),
    (rain, envelope([(48, 49.5, 0.25, 0.3), (49.5, 64, 0.55, 1.0), (64, 68, 0.28, 0.8)])),
    (neon, envelope([(68, 78.5, 1.0, 0.5), (80.2, 84, 1.0, 0.3)])),
    (wind, envelope([(84, 97.0, 0.35, 1.0), (98.0, 101.8, 0.3, 0.6)])),   # silence before the kiss
]

# one-shot SFX (procedural): (start, filter source, gain)
SHOTS = []
for i in range(4):  # photo booth: click + flash whine
    t = 30 + (192 + 48 * i) / 24
    SHOTS.append((t, 'anoisesrc=c=white:a=0.9:seed=%d,highpass=f=1500,afade=t=out:st=0:d=0.06' % (10 + i), 0.5, 0.08))
SHOTS.append((14 + 150 / 24, 'sine=f=70,afade=t=out:st=0:d=0.18', 0.8, 0.2))           # pancake splat (thump)
SHOTS.append((14 + 150 / 24, 'anoisesrc=c=pink:a=0.8:seed=20,lowpass=f=1200,afade=t=out:st=0:d=0.15', 0.5, 0.16))
SHOTS.append((8 + 216 / 24 - 8, 'sine=f=880,afade=t=out:st=0:d=0.12', 0.25, 0.13))     # wake-up sting (9.0 s)
for t in (48 + 122 / 24, 48 + 130 / 24):                                                # puddle splashes
    SHOTS.append((t, 'anoisesrc=c=pink:a=0.9:seed=30,bandpass=f=900:w=800,afade=t=out:st=0:d=0.25', 0.6, 0.26))
SHOTS.append((68 + 240 / 24 + 0.4, 'sine=f=1800,afade=t=out:st=0:d=0.08', 0.25, 0.09))  # coin
SHOTS.append((68 + 304 / 24, 'sine=f=180,afade=t=out:st=0:d=0.12', 0.5, 0.13))          # plush lands in chute
SHOTS.append((102 + 216 / 24, 'anoisesrc=c=pink:a=0.5:seed=40,lowpass=f=1800,afade=t=in:d=0.3,afade=t=out:st=0.4:d=0.6',
              0.35, 1.0))                                                               # blanket rustle

inputs, filt, labels = [], [], []
k = 0
for path, t0, g, extra in VOICE:
    inputs += ['-i', path]
    filt.append(f'[{k}]aresample=48000,pan=stereo|c0=c0|c1=c0,volume={g}{extra},adelay={int(t0 * 1000)}|{int(t0 * 1000)}[v{k}]')
    labels.append(f'[v{k}]')
    k += 1
for path, env in beds:
    inputs += ['-i', str(path)]
    filt.append(f"[{k}]volume='{env}':eval=frame[b{k}]")
    labels.append(f'[b{k}]')
    k += 1
for t0, src, g, d in SHOTS:
    inputs += ['-f', 'lavfi', '-t', str(d), '-i', src]
    filt.append(f'[{k}]aresample=48000,pan=stereo|c0=c0|c1=c0,volume={g},adelay={int(t0 * 1000)}|{int(t0 * 1000)}[s{k}]')
    labels.append(f'[s{k}]')
    k += 1
filt.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0,apad=whole_dur={DUR},atrim=0:{DUR}[mix]')
raw = D / 'final_mix_raw.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[mix]',
                '-ar', '48000', '-ac', '2', str(raw)], check=True)
r = subprocess.run(['ffmpeg', '-hide_banner', '-y', '-i', str(raw), '-af', 'acompressor=threshold=0.08:ratio=4:attack=5:release=150:makeup=2,alimiter=limit=0.7,loudnorm=I=-14:TP=-1.5:LRA=9:print_format=summary,volume=2.6dB,alimiter=limit=0.82:level=false',
                    '-ar', '48000', str(D / 'final_mix_v1.wav')], capture_output=True, text=True)
print('\n'.join(l for l in r.stderr.splitlines() if 'Integrated' in l or 'True Peak' in l))
