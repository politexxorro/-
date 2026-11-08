"""Pop magnitudes old vs new, counting only boundaries inside one shot (by xsheet shot names)."""
import json

import numpy as np

lens = [336, 384, 432, 480, 384, 432, 432]
paths = [f'shots/shot0{i + 1}/render/xsheet_records.json' for i in range(7)]
shots = []
for p, n in zip(paths, lens):
    recs = json.load(open(p))
    shots += [f'{p}:{r.get("shot")}' for r in recs[:n]]
old = np.load('/tmp/old.npy')
new = np.load('/tmp/new.npy')
sel = [i for i in range(len(old)) if old[i] > 10 and shots[i + 1] == shots[i]
       and (i == 0 or old[i - 1] < 0.6 * old[i])]
o, n = old[sel], new[sel]
loc = np.maximum(np.maximum(new[[max(0, i - 1) for i in sel]], n), new[[min(len(new) - 1, i + 1) for i in sel]])
print(f'true within-shot pops: {len(sel)}')
print(f'old: mean {o.mean():.1f}  p90 {np.percentile(o, 90):.1f}  max {o.max():.1f}')
print(f'new (local max): mean {loc.mean():.1f}  p90 {np.percentile(loc, 90):.1f}  max {loc.max():.1f}')
