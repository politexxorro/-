"""Export H3 handoff pack: 21 start frames (one per clip) from the smoothed scene renders."""
import subprocess

M = [(1, '01', 0), (2, '01', 4), (3, '01', 8), (4, '02', 0), (5, '02', 5), (6, '02', 10),
     (7, '03', 0), (8, '03', 6), (9, '03', 14), (10, '04', 0), (11, '04', 6), (12, '04', 12),
     (13, '05', 0), (14, '05', 6), (15, '05', 12), (16, '06', 0), (17, '06', 6), (18, '06', 14),
     (19, '07', 0), (20, '07', 8), (21, '07', 14)]
for n, sh, off in M:
    v = 'v2s' if sh == '01' else 'v1s'
    src = f'shots/shot{sh}/render/shot{sh}_picture_{v}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(off), '-i', src, '-vframes', '1',
                    f'handoff_h3/start_frames/clip{n:02d}.png'], check=True)
print('done', len(M))
