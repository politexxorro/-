"""Thin client for the InfarModel OpenAI-compatible proxy.

Key/base are read from ~/.secrets (never from the repo). Every call is appended to
logs/api_calls.jsonl so PROGRESS.md generation counters can be rebuilt.
"""
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests

SECRETS = Path.home() / '.secrets'
BASE = (SECRETS / 'infar_base').read_text().strip().rstrip('/') + '/v1'
KEY = (SECRETS / 'infar_key').read_text().strip()
H = {'Authorization': f'Bearer {KEY}'}
IMAGE_MODEL = 'gpt-image-2.6-sunburst'
TTS_MODEL = 'eleven_multilingual_v2'
LOG = Path(__file__).resolve().parent.parent / 'logs' / 'api_calls.jsonl'

NO_TEXT = ' Без надписей, без букв, без текста, без водяных знаков.'
KEEP_CHAR = ('Сохрани персонажа полностью идентичным референсу: лицо, глаза, причёска, одежда, цвета, '
             'пропорции, стиль рисовки. Не меняй причёску, одежду, цвета, форму лица, возраст, стиль, '
             'не добавляй аксессуаров.')


def _post(url, retries=8, **kw):
    """POST with backoff on proxy overload (503/429/502/504). Multipart files are re-opened by caller via factory."""
    files_factory = kw.pop('files_factory', None)
    for i in range(retries):
        if files_factory:
            kw['files'] = files_factory()
        try:
            r = requests.post(url, headers=H, **kw)
        except requests.exceptions.ConnectionError as e:
            print(f'  connection error, retry in 20s: {e}', file=sys.stderr)
            time.sleep(20)
            continue
        if r.status_code not in (429, 502, 503, 504):
            return r
        wait = min(15 * (i + 1), 90)
        print(f'  {r.status_code}, retry in {wait}s: {r.text[:120]}', file=sys.stderr)
        time.sleep(wait)
    return r


def _log(rec):
    LOG.parent.mkdir(exist_ok=True)
    rec['t'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    with LOG.open('a') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def _save_images(r, out, kind, prompt, extra):
    if r.status_code != 200:
        _log({'kind': kind, 'status': r.status_code, 'err': r.text[:500], 'out': str(out), **extra})
        raise RuntimeError(f'{kind} HTTP {r.status_code}: {r.text[:800]}')
    data = r.json()['data']
    outs = []
    for i, d in enumerate(data):
        p = Path(out) if len(data) == 1 else Path(out).with_stem(f'{Path(out).stem}_{i}')
        p.parent.mkdir(parents=True, exist_ok=True)
        if d.get('b64_json'):
            p.write_bytes(base64.b64decode(d['b64_json']))
        else:
            p.write_bytes(requests.get(d['url'], timeout=300).content)
        outs.append(str(p))
    _log({'kind': kind, 'status': 200, 'out': outs, 'prompt': prompt, **extra})
    return outs


def edit(refs, prompt, out, size='1536x1024', quality='high', background=None, n=1):
    """Image edit with one or more reference images (multipart image[])."""
    ff = lambda: [('image[]', (Path(p).name, open(p, 'rb'), 'image/png')) for p in refs]
    data = {'model': IMAGE_MODEL, 'prompt': prompt, 'size': size, 'quality': quality, 'n': str(n)}
    if background:
        data['background'] = background
    r = _post(f'{BASE}/images/edits', files_factory=ff, data=data, timeout=900)
    return _save_images(r, out, 'image_edit', prompt, {'refs': [str(p) for p in refs], 'size': size, 'quality': quality})


def generate(prompt, out, size='1536x1024', quality='high', background=None):
    body = {'model': IMAGE_MODEL, 'prompt': prompt, 'size': size, 'quality': quality}
    if background:
        body['background'] = background
    r = _post(f'{BASE}/images/generations', json=body, timeout=900)
    return _save_images(r, out, 'image_gen', prompt, {'size': size, 'quality': quality})


def tts(text, voice, out, fmt='mp3', model=TTS_MODEL, **extra):
    body = {'model': model, 'input': text, 'voice': voice, 'response_format': fmt, **extra}
    r = _post(f'{BASE}/audio/speech', json=body, timeout=300)
    if r.status_code != 200:
        _log({'kind': 'tts', 'status': r.status_code, 'err': r.text[:500], 'text': text, 'voice': voice})
        raise RuntimeError(f'tts HTTP {r.status_code}: {r.text[:800]}')
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_bytes(r.content)
    _log({'kind': 'tts', 'status': 200, 'out': str(out), 'text': text, 'voice': voice, 'model': model, **extra})
    return out


def sfx(text, out, model='eleven_text_to_sound_v2', fmt='mp3'):
    r = requests.post(f'{BASE}/audio/speech', headers=H,
                      json={'model': model, 'input': text, 'response_format': fmt}, timeout=300)
    if r.status_code != 200:
        _log({'kind': 'sfx', 'status': r.status_code, 'err': r.text[:500], 'text': text})
        raise RuntimeError(f'sfx HTTP {r.status_code}: {r.text[:800]}')
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_bytes(r.content)
    _log({'kind': 'sfx', 'status': 200, 'out': str(out), 'text': text, 'model': model})
    return out


def alignment(audio, text):
    with open(audio, 'rb') as f:
        r = requests.post(f'{BASE}/audio/alignment', headers=H, files={'file': f}, data={'text': text}, timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f'alignment HTTP {r.status_code}: {r.text[:800]}')
    return r.json()


if __name__ == '__main__':
    # usage: python3 scripts/api.py edit OUT "PROMPT" REF [REF...]  [--size WxH] [--quality q] [--bg transparent]
    a = sys.argv[1:]
    opts = {}
    for k in ('--size', '--quality', '--bg'):
        if k in a:
            i = a.index(k)
            opts[k] = a[i + 1]
            del a[i:i + 2]
    kw = dict(size=opts.get('--size', '1536x1024'), quality=opts.get('--quality', 'high'), background=opts.get('--bg'))
    if a[0] == 'edit':
        print(edit(a[3:], a[2], a[1], **kw))
    elif a[0] == 'gen':
        print(generate(a[2], a[1], **kw))
    elif a[0] == 'tts':
        print(tts(a[2], a[3], a[1]))
