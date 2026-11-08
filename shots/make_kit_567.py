"""Kit configs for scenes 5–7."""
import json

cfg = []


def P(base, var, out, roi='face'):
    cfg.append({'base': base, 'var': var, 'out': out, 'mode': 'part', 'roi': roi})


def F(base, var, out, anchor=(0, 0, 1, 1)):
    cfg.append({'base': base, 'var': var, 'out': out, 'mode': 'full', 'anchor': list(anchor)})


R, K = 'shots/shot05/raw/', 'shots/shot05/kit/'
P(R + 'he_claw_k1_v1.png', R + 'he_claw_blink_v1.png', K + 'he_claw_blink.png')
F(R + 'he_claw_k1_v1.png', R + 'he_claw_angry_v1.png', K + 'he_claw_angry.png')
F(R + 'he_claw_k1_v1.png', R + 'he_claw_sad_v1.png', K + 'he_claw_sad.png', (0, 0.6, 1, 1))
P(R + 'she_love_v1.png', R + 'she_love_blink_v1.png', K + 'she_love_blink.png')
P(R + 'she_cat_surprise_v1.png', R + 'she_cat_happy_v1.png', K + 'she_cat_happy.png')
for k in 'AEOM':
    P(R + 'he_give_v1.png', R + f'he_give_mouth_{k}_v1.png', K + f'he_give_mouth_{k}.png')
R, K = 'shots/shot06/raw/', 'shots/shot06/kit/'
F(R + 'roof_sit_v1.png', R + 'roof_sit_wind_v1.png', K + 'roof_sit_wind.png', (0, 0.5, 1, 1))
F(R + 'roof_sit_v1.png', R + 'roof_lean_mid_v1.png', K + 'roof_lean_mid.png', (0.5, 0, 1, 1))
F(R + 'roof_sit_v1.png', R + 'roof_lean_v1.png', K + 'roof_lean.png', (0.5, 0.4, 1, 1))
for k in 'AEOM':
    P(R + 'roof_mcu_v1.png', R + f'roof_mcu_mouth_{k}_v1.png', K + f'roof_mcu_mouth_{k}.png', [0.45, 0.25, 0.85, 0.6])
    P(R + 'roof_lift_v1.png', R + f'roof_lift_mouth_{k}_v1.png', K + f'roof_lift_mouth_{k}.png',
      [0.1, 0.3, 0.5, 0.65])
F(R + 'roof_mcu_v1.png', R + 'roof_lift_v1.png', K + 'roof_lift.png', (0.5, 0, 1, 1))
F(R + 'roof_mcu_v1.png', R + 'roof_kiss_v1.png', K + 'roof_kiss.png', (0.5, 0.5, 1, 1))
F(R + 'roof_mcu_v1.png', R + 'roof_after_v1.png', K + 'roof_after.png', (0.0, 0.6, 1, 1))
F(R + 'roof_after_v1.png', R + 'roof_after_smile_v1.png', K + 'roof_after_smile.png')
R, K = 'shots/shot07/raw/', 'shots/shot07/kit/'
F(R + 'sofa_a_v1.png', R + 'sofa_k2_v1.png', K + 'sofa_k2.png', (0, 0.55, 1, 1))
F(R + 'sofa_a_v1.png', R + 'sofa_k3_v1.png', K + 'sofa_k3.png', (0, 0.55, 1, 1))
F(R + 'sofa_a_v1.png', R + 'sofa_k4_v1.png', K + 'sofa_k4.png', (0, 0.0, 0.45, 0.6))
F(R + 'sofa_a_v1.png', R + 'sofa_k5_v1.png', K + 'sofa_k5.png', (0, 0.55, 1, 1))
P(R + 'sofa_k3_v1.png', R + 'sofa_k3_blink_v1.png', K + 'sofa_k3_blink.png', [0.2, 0.05, 0.6, 0.4])
json.dump(cfg, open('shots/kit_567.json', 'w'), indent=1)
