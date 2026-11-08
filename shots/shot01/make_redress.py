"""Scene 1 re-dress: his drawings -> hoodie outfit (client decision). Stage a: bases, stage b: face variants."""
import json
import sys

R = 'shots/shot01/raw/'
HOOD = ['characters/approved/he_emotions_hoodie_v1.png', 'characters/reference/he_fullbody_4views.png']
REDRESS = ('Повтори первое изображение пиксель в пиксель: та же поза, ракурс, кадрирование, масштаб, лицо, мимика, '
           'причёска, подушка, одеяло, руки, стиль рисовки и толщина линий. Измени ТОЛЬКО одежду парня: вместо чёрной '
           'олимпийки и цепочки — светло-серое худи на молнии с капюшоном, подкладка капюшона в тёмно-синюю клетку '
           '(клетка видна по краю молнии и в капюшоне), под ним чёрная футболка, без цепочки — строго как на втором и '
           'третьем изображениях. Ничего больше не меняй. Прозрачный фон. Без надписей, без букв, без текста.')
SAME = ('Повтори первое изображение пиксель в пиксель: та же поза, ракурс, кадрирование, масштаб, волосы, одежда, '
        'цвета, линии и стиль. Измени ТОЛЬКО {what}. Больше ничего не меняй. Прозрачный фон. Без надписей, без букв, '
        'без текста.')
FACE = ['characters/approved/he_emotions_hoodie_v1.png']
stage = sys.argv[1]
jobs = []
if stage == 'a':
    for n in ['he_sleep_mid', 'he_cu_closed', 'he_pillow_k1', 'he_pillow_k2', 'he_pillow_k3']:
        jobs.append({'out': R + n + '_v2.png', 'refs': [R + n + '_v1.png'] + HOOD, 'prompt': REDRESS,
                     'size': '1536x1024', 'quality': 'high', 'bg': 'transparent'})
else:
    def j(out, base, what):
        jobs.append({'out': R + out, 'refs': [R + base] + FACE, 'prompt': SAME.format(what=what),
                     'size': '1536x1024', 'quality': 'high', 'bg': 'transparent'})
    j('he_sleep_mid_mouthopen_v2.png', 'he_sleep_mid_v2.png', 'рот: губы чуть-чуть приоткрыты во сне, глаза закрыты')
    j('he_sleep_mid_frown_v2.png', 'he_sleep_mid_v2.png',
      'мимику: глаза закрыты, веки зажмурены чуть сильнее, брови слегка сведены, губы сжаты — морщится во сне')
    j('he_cu_open_v2.png', 'he_cu_closed_v2.png',
      'мимику и волосы: резко проснулся — глаза широко открыты, маленькие зрачки, брови подняты, рот приоткрыт '
      'буквой «о», как эмоция 3 на листе эмоций; пряди на макушке подпрыгнули вверх. Рука девушки у щеки остаётся. '
      'Ровно 5 пальцев')
    j('he_pillow_k1_eyes_closed_v2.png', 'he_pillow_k1_v2.png',
      'глаза: полностью закрыты (сонное моргание), как эмоция 6 на листе эмоций')
json.dump(jobs, open(f'shots/shot01/jobs_redress_{stage}.json', 'w'), ensure_ascii=False, indent=1)
print(len(jobs))
