"""Scene 2 kit config: face parts + registered full pose variants."""
import json

R = 'shots/shot02/raw/'
K = 'shots/shot02/kit/'
cfg = []


def P(base, var, out):
    cfg.append({'base': R + base, 'var': R + var, 'out': K + out, 'mode': 'part', 'roi': 'face'})


def F(base, var, out, anchor='face'):
    cfg.append({'base': R + base, 'var': R + var, 'out': K + out, 'mode': 'full', 'anchor': anchor})


P('she_whisk_a_v1.png', 'she_whisk_a_blink_v1.png', 'she_whisk_blink.png')
F('she_whisk_a_v1.png', 'she_whisk_b_v1.png', 'she_whisk_b.png')
F('she_whisk_a_v1.png', 'she_whisk_c_v1.png', 'she_whisk_c.png')
P('he_flip_k1_v2.png', 'he_flip_k1_blink_v1.png', 'he_flip_blink.png')
F('he_flip_k1_v2.png', 'he_flip_k2_v1.png', 'he_flip_k2.png')
F('he_flip_k1_v2.png', 'he_flip_k3_v1.png', 'he_flip_k3.png')
F('he_flip_k1_v2.png', 'he_flip_k4_v1.png', 'he_flip_k4.png', anchor=[0.3, 0.45, 1.0, 1.0])
F('she_laugh_k1_v1.png', 'she_laugh_k2_v1.png', 'she_laugh_k2.png', anchor=[0.0, 0.6, 1.0, 1.0])
for k in ['A', 'O', 'E', 'M', 'half', 'smile']:
    P('he_pout_base_v1.png', f'he_pout_mouth_{k}_v1.png', f'he_pout_mouth_{k}.png')
P('he_pout_base_v1.png', 'he_pout_blink_v1.png', 'he_pout_blink.png')
F('he_cu_pancake_v2.png', 'he_cu_k2_v1.png', 'he_cu_k2.png')
F('he_cu_pancake_v2.png', 'he_cu_k3_v1.png', 'he_cu_k3.png', anchor=[0.2, 0.55, 0.8, 1.0])
F('he_cu_pancake_v2.png', 'he_cu_k4_v1.png', 'he_cu_k4.png', anchor=[0.2, 0.55, 0.8, 1.0])
P('he_cu_k4_v1.png', 'he_cu_k4_blush_v1.png', 'he_cu_k4_blush_raw.png')
P('he_cu_k4_v1.png', 'he_cu_k4_blink_v1.png', 'he_cu_k4_blink_raw.png')
json.dump(cfg, open('shots/shot02/kit.json', 'w'), indent=1)
