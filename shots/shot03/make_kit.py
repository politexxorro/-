"""Scene 3 kit config."""
import json

R, K = 'shots/shot03/raw/', 'shots/shot03/kit/'
cfg = [
    {'base': R + 'couple_walk_a_v1.png', 'var': R + 'couple_walk_b_v1.png', 'out': K + 'couple_walk_b.png',
     'mode': 'full', 'anchor': [0, 0, 1, 1]},
    {'base': R + 'couple_walk_a_v1.png', 'var': R + 'couple_walk_a_blink_v1.png', 'out': K + 'couple_walk_blink.png',
     'mode': 'part', 'roi': [0.15, 0.30, 0.50, 0.55]},
    {'base': R + 'couple_pull_a_v1.png', 'var': R + 'couple_pull_b_v1.png', 'out': K + 'couple_pull_b.png',
     'mode': 'full', 'anchor': [0, 0, 1, 1]},
    {'base': R + 'she_strip_hug_v2.png', 'var': R + 'she_strip_hug_blink_v2.png', 'out': K + 'she_strip_blink.png',
     'mode': 'part', 'roi': 'face'},
]
json.dump(cfg, open('shots/shot03/kit.json', 'w'), indent=1)
