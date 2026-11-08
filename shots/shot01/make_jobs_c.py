"""Write jobs_c.json: face-kit variants (edits of approved base drawings) + wake-up close-ups."""
import json

SAME = ('Повтори первое изображение пиксель в пиксель: та же поза, ракурс, кадрирование, масштаб, волосы, одежда, '
        'цвета, линии и стиль. Измени ТОЛЬКО {what}. Больше ничего не меняй: нос, форма лица, родинка, причёска, '
        'брови и линии остаются как были. Прозрачный фон. Без надписей, без букв, без текста.')
R = 'shots/shot01/raw/'
SHE = ['characters/reference/she_emotions.png']
HE = ['characters/reference/he_emotions.png']
jobs = []


def j(out, refs, what, size='1024x1024'):
    jobs.append({'out': R + out, 'refs': refs, 'prompt': SAME.format(what=what), 'size': size, 'quality': 'high',
                 'bg': 'transparent'})


talk = [R + 'she_talk_base_v1.png'] + SHE
mouths = {
    'A': 'рот: широко открыт на звуке «А», видны верхние зубы и язык, губы того же цвета, что на эталоне',
    'O': 'рот: округлён на звуке «О/У», губы вытянуты кружочком, рот приоткрыт',
    'E': 'рот: растянут на звуке «Э/И», приоткрыт узко, видны зубы, уголки в улыбке',
    'M': 'рот: губы плотно сомкнуты на звуке «М/Б/П», лёгкая улыбка',
    'half': 'рот: полуоткрыт, небольшая щель между губами, мягкая улыбка',
    'laugh': 'рот: звонкий смех как эмоция 1 на листе эмоций — широко открытая улыбка, видны верхние зубы',
}
for k, w in mouths.items():
    j(f'she_talk_mouth_{k}_v1.png', talk, w)
j('she_talk_eyes_closed_v1.png', talk, 'глаза: полностью закрыты дугами вниз, ресницы как на эмоции 6 на листе эмоций (моргание)')
j('she_talk_eyes_half_v1.png', talk, 'глаза: веки опущены наполовину (середина моргания), взгляд тот же')
j('she_poke_p1_eyes_closed_v1.png', [R + 'she_poke_p1.png'] + SHE,
  'глаза: полностью закрыты дугами вниз (моргание), ресницы как на эмоции 6 на листе эмоций', size='1024x1536')
j('he_pillow_p1_eyes_closed_v1.png', [R + 'he_pillow_p1.png'] + HE,
  'глаза: полностью закрыты (медленное сонное моргание), как эмоция 6 на листе эмоций')

cu = [R + 'he_cu_closed_v1.png'] + HE
jobs.append({'out': R + 'he_cu_open_v1.png', 'refs': cu, 'size': '1536x1024', 'quality': 'high', 'bg': 'transparent',
             'prompt': SAME.format(what='мимику и волосы: он резко проснулся — глаза широко открыты, маленькие зрачки, '
                                        'брови подняты, рот приоткрыт буквой «о», как эмоция 3 на листе эмоций; пряди '
                                        'волос на макушке подпрыгнули вверх. Рука девушки с пальцем у щеки остаётся. '
                                        'Ровно 5 пальцев')})
json.dump(jobs, open('shots/shot01/jobs_c.json', 'w'), ensure_ascii=False, indent=1)
print(len(jobs))
