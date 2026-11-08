"""Scene 4 kit config."""
import json

R, K = 'shots/shot04/raw/', 'shots/shot04/kit/'
cfg = [
    {'base': R + 'run_back_a_v1.png', 'var': R + 'run_back_b_v1.png', 'out': K + 'run_back_b.png', 'mode': 'full',
     'anchor': [0, 0, 1, 1]},
    {'base': R + 'feet_splash_a_v1.png', 'var': R + 'feet_splash_b_v1.png', 'out': K + 'feet_splash_b.png',
     'mode': 'full', 'anchor': [0, 0, 1, 1]},
    {'base': R + 'run_side_a_v1.png', 'var': R + 'run_side_b_v1.png', 'out': K + 'run_side_b.png', 'mode': 'full',
     'anchor': [0, 0, 1, 1]},
    {'base': R + 'couple_lookup_v1.png', 'var': R + 'couple_lookup_blink_v1.png', 'out': K + 'lookup_blink.png',
     'mode': 'part', 'roi': [0.15, 0.1, 0.9, 0.42]},
    {'base': R + 'awning_a_v1.png', 'var': R + 'awning_b_v1.png', 'out': K + 'awning_b.png', 'mode': 'full',
     'anchor': [0, 0.5, 1, 1]},
    {'base': R + 'hood_k1_v1.png', 'var': R + 'hood_k1_shiver_v1.png', 'out': K + 'hood_shiver.png', 'mode': 'full',
     'anchor': [0.5, 0, 1, 1]},
    {'base': R + 'hood_k1_v1.png', 'var': R + 'hood_k2_v1.png', 'out': K + 'hood_k2.png', 'mode': 'full',
     'anchor': [0.5, 0, 1, 1]},
    {'base': R + 'hood_k1_v1.png', 'var': R + 'hood_k3_v1.png', 'out': K + 'hood_k3.png', 'mode': 'full',
     'anchor': [0.5, 0, 1, 1]},
    {'base': R + 'foreheads_v1.png', 'var': R + 'foreheads_breath_v1.png', 'out': K + 'foreheads_breath.png',
     'mode': 'full', 'anchor': [0, 0, 1, 1]},
]
json.dump(cfg, open('shots/shot04/kit.json', 'w'), indent=1)
