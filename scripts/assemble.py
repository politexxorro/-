"""Assemble final.mp4: 7 scene pictures (scene 1 trimmed to 14 s) + final mix + burned-in .ass subtitles.
Output spec: 1920x1080, 24 fps, H.264 yuv420p CRF 18, AAC 48 kHz, exactly 120.000 s (2880 frames).
"""
import subprocess

SCENES = [('shots/shot01/render/shot01_picture_v2.mp4', 336),
          ('shots/shot02/render/shot02_picture_v1.mp4', 384),
          ('shots/shot03/render/shot03_picture_v1.mp4', 432),
          ('shots/shot04/render/shot04_picture_v1.mp4', 480),
          ('shots/shot05/render/shot05_picture_v1.mp4', 384),
          ('shots/shot06/render/shot06_picture_v1.mp4', 432),
          ('shots/shot07/render/shot07_picture_v1.mp4', 432)]
assert sum(n for _, n in SCENES) == 2880
inp, flt = [], []
for i, (p, n) in enumerate(SCENES):
    inp += ['-i', p]
    flt.append(f'[{i}:v]trim=end_frame={n},setpts=PTS-STARTPTS,fps=24,format=yuv420p[v{i}]')
flt.append(''.join(f'[v{i}]' for i in range(len(SCENES))) + f'concat=n={len(SCENES)}:v=1:a=0[cat]')
flt.append('[cat]ass=subtitles.ass:fontsdir=fonts[out]')
inp += ['-i', 'audio/mix/final_mix_v1.wav']
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inp, '-filter_complex', ';'.join(flt), '-map', '[out]',
                '-map', f'{len(SCENES)}:a', '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                '-r', '24', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', '120', '-movflags', '+faststart',
                'final.mp4'], check=True)
# animatic-size preview for sharing
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'final.mp4', '-vf', 'scale=1280:720', '-c:v', 'libx264', '-crf', '25',
                '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '128k',
                'final_720p.mp4'], check=True)
