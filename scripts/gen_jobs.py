"""Run a batch of image jobs from a JSON file: [{"out":..., "prompt":..., "refs":[...], "size":..., "quality":..., "bg":...}].

Jobs without refs use text-to-image (backgrounds/props only). Existing outputs are skipped (never overwritten).
usage: python3 scripts/gen_jobs.py jobs.json [parallel]
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import api  # noqa: E402


def run(j):
    if Path(j['out']).exists():
        return f"skip {j['out']}"
    kw = dict(size=j.get('size', '1536x1024'), quality=j.get('quality', 'high'), background=j.get('bg'))
    try:
        if j.get('refs'):
            api.edit(j['refs'], j['prompt'], j['out'], **kw)
        else:
            api.generate(j['prompt'], j['out'], **kw)
        return f"ok   {j['out']}"
    except Exception as e:  # keep batch going, report at end
        return f"FAIL {j['out']}: {e}"


if __name__ == '__main__':
    jobs = json.load(open(sys.argv[1]))
    par = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    with ThreadPoolExecutor(par) as ex:
        for r in ex.map(run, jobs):
            print(r, flush=True)
