"""Build shots/shotNN/xsheet.md from render/xsheet_records.json: runs of identical drawing states with frame ranges."""
import glob
import json
from pathlib import Path

COLS = ['shot', 'body', 'she_eyes', 'she_mouth', 'he_eyes', 'he_mouth', 'he_brows', 'he_blush', 'cam', 'fx']
LIGHT = {
    '01': 'утро: тёплый солнечный свет из окна справа-сзади, тени персиковые, контровой тёплый',
    '02': 'кухня: тёплый кремовый свет из окна слева, мягкие тени',
    '03': 'улица днём: нейтральный дневной свет сверху-справа, лёгкие сиреневые тени',
    '04': 'дождь: холодный рассеянный свет, сине-фиолетовые тени, холодный контровой',
    '05': 'зал автоматов: неон слева, розово-фиолетовые тени, розовый контровой',
    '06': 'закат: золотой контровой справа-сзади, розово-лиловые тени, блик объектива',
    '07': 'вечер дома: янтарный свет торшера слева, мерцание экрана спереди (голубоватое)',
}
for rec_path in sorted(glob.glob('shots/shot0*/render/xsheet_records.json')):
    n = rec_path.split('/')[1][-2:]
    recs = json.load(open(rec_path))
    runs = []
    for r in recs:
        key = tuple(str(r.get(c, '')) for c in COLS)
        if runs and runs[-1][2] == key:
            runs[-1][1] = r['f']
        else:
            runs.append([r['f'], r['f'], key])
    lines = [f'# Таймшит сцены {int(n)}', '', f'Свет сцены: {LIGHT[n]}', '',
             'Кадры 24 fps. «Держ.» — сколько кадров держится состояние (персонажи на 2-ках/3-ках, камера и FX на 1-ках).', '',
             '| Кадры | Держ. | ' + ' | '.join(COLS) + ' |', '|' + '---|' * (len(COLS) + 2)]
    for a, b, key in runs:
        lines.append(f'| {a}–{b} | {b - a + 1} | ' + ' | '.join(k.replace('|', '/') for k in key) + ' |')
    Path(f'shots/shot{n}/xsheet.md').write_text('\n'.join(lines) + '\n')
    print(n, len(recs), 'frames,', len(runs), 'rows')
