"""Reproduce the Field Note #07 numbers from the public CSV files.

Usage: python analyze_hand_visibility.py data/hand_visibility_frames.csv data/ai_review_labels.csv
"""
import sys, json
import numpy as np, pandas as pd

WINDOW = 2  # frames on each side (±67 ms at 30 fps)


def wilson(k, n, z=1.96):
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def consensus(df, side, window=WINDOW):
    p3 = ((df[f'single_{side}'] + df[f'flip_{side}'] + df[f'lite_{side}']) >= 1).astype(int)
    return p3.rolling(2 * window + 1, center=True, min_periods=1).max().astype(int)


def main(frames_csv, review_csv):
    F = pd.read_csv(frames_csv)
    L = pd.read_csv(review_csv)
    out = {}
    for rec, d in F.groupby('recording', sort=False):
        d = d.sort_values('frame').reset_index(drop=True)
        cL, cR = consensus(d, 'L'), consensus(d, 'R')
        assert (cL == d.consensus_L).all() and (cR == d.consensus_R).all(), 'consensus mismatch'
        o = {'frames': len(d),
             'single_both': d.single_both.mean(),
             'pass3_both': d.pass3_both.mean(),
             'consensus_both': (cL * cR).mean(),
             'passes_disagree': 1 - d.passes_agree.mean()}
        r = L[L.recording == rec]
        n = len(r)
        vis = ((r.review_L != 'N') & (r.review_R != 'N')).sum()
        full = ((r.review_L == 'F') & (r.review_R == 'F')).sum()
        o['review_n'] = n
        o['review_both_visible'] = int(vis)
        o['review_both_visible_ci'] = wilson(vis, n)
        o['review_both_fully_inside'] = int(full)
        idx = d.set_index('frame')
        hits_s, hits_c = [], []
        for _, row in r.iterrows():
            for s in 'LR':
                if row[f'review_{s}'] != 'N':
                    hits_s.append(idx.loc[row.frame, f'single_{s}'])
                    hits_c.append(idx.loc[row.frame, f'consensus_{s}'])
        o['visible_hands'] = len(hits_s)
        o['recall_single'] = float(np.mean(hits_s))
        o['recall_consensus'] = float(np.mean(hits_c))
        o['recall_single_ci'] = wilson(sum(hits_s), len(hits_s))
        o['recall_consensus_ci'] = wilson(sum(hits_c), len(hits_c))
        out[rec] = o
    for rec, o in out.items():
        print(f"{rec:18s} frames {o['frames']:5d} | both: single {o['single_both']:.3f}  pass3 {o['pass3_both']:.3f}  "
              f"consensus {o['consensus_both']:.3f} | review {o['review_both_visible']}/{o['review_n']} | "
              f"recall single {o['recall_single']:.3f} -> consensus {o['recall_consensus']:.3f}")
    return out


if __name__ == '__main__':
    res = main(sys.argv[1], sys.argv[2])
    json.dump(res, open('reproduced_results.json', 'w'), indent=1, default=float)
