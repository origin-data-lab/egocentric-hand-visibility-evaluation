"""Build the per-frame table (det_<recording>.csv) from raw detection JSON files in $ODL_RAW_DIR (default ./raw)."""
import json,glob,numpy as np,pandas as pd
import os,sys
F=os.environ.get('ODL_RAW_DIR','raw/')
MARGIN=0.005
def load(rec):
    rows=[]
    for f in sorted(glob.glob(F+f'raw_{rec}_*.json')):rows+=json.load(open(f))
    rows.sort(key=lambda r:r['frame']);return rows
def per_side(hands):
    out={'L':None,'R':None};conflict=0
    for h in sorted(hands,key=lambda h:-h['score']):
        if out[h['side']] is None:out[h['side']]=h
        else:conflict=1
    return out,conflict
def trunc(h):return int(h['x0']<MARGIN or h['y0']<MARGIN or h['x1']>1-MARGIN or h['y1']>1-MARGIN)
def table(rec):
    rows=load(rec);T=[]
    for r in rows:
        s,conf=per_side(r['full']);fs,_=per_side(r['flip']);ls,_=per_side(r['lite'])
        d=dict(frame=r['frame'],n_full=len(r['full']),n_flip=len(r['flip']),n_lite=len(r['lite']),side_conflict=conf)
        for k in 'LR':
            h=s[k];d[f'det_{k}']=int(h is not None);d[f'score_{k}']=round(h['score'],4) if h else np.nan
            d[f'trunc_{k}']=trunc(h) if h else 0
            for a in ('x0','x1','y0','y1','wx','wy','cx','cy'):d[f'{a}_{k}']=round(h[a],4) if h else np.nan
            d[f'flip_{k}']=int(fs[k] is not None);d[f'lite_{k}']=int(ls[k] is not None)
        T.append(d)
    t=pd.DataFrame(T)
    t['det_both']=t.det_L*t.det_R
    t['det_any']=((t.det_L+t.det_R)>0).astype(int)
    t['full_both']=t.det_both*(1-t.trunc_L)*(1-t.trunc_R)
    t['agree_count']=((t.n_full==t.n_flip)&(t.n_full==t.n_lite)).astype(int)
    t['agree_sides']=((t.det_L==t.flip_L)&(t.det_R==t.flip_R)&(t.det_L==t.lite_L)&(t.det_R==t.lite_R)).astype(int)
    n=t.n_full.values;fl=np.zeros(len(t),int);fl[1:-1]=((n[:-2]==n[2:])&(n[1:-1]!=n[:-2])).astype(int);t['flicker']=fl
    ms=t[['score_L','score_R']].min(axis=1);t['low_score']=(ms<0.7).fillna(False).astype(int)
    t['order_ok']=np.where(t.det_both==1,(t.cx_L<t.cx_R).astype(int),np.nan)
    t['suspect']=((t.agree_sides==0)|(t.flicker==1)|(t.side_conflict==1)|(t.low_score==1)|(t.order_ok==0)).astype(int)
    t.insert(0,'recording',rec)
    return t
if __name__=='__main__':
    for rec in ['s1','sample_A_knife','sample_B_seasoning']:
        t=table(rec);t.to_csv(os.path.join(F,f'det_{rec}.csv'),index=False)
        print(rec,len(t),'any',round(t.det_any.mean(),3),'both',round(t.det_both.mean(),3),'fullboth',round(t.full_both.mean(),3),'L',round(t.det_L.mean(),3),'R',round(t.det_R.mean(),3),'agree',round(t.agree_sides.mean(),3),'suspect',round(t.suspect.mean(),3),'order_ok',round(t.order_ok.mean(),3))
