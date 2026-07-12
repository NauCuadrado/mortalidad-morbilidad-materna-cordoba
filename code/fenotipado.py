# -*- coding: utf-8 -*-
import pandas as pd, numpy as np
from kmodes.kprototypes import KPrototypes
np.random.seed(42)
b=pd.read_pickle("_base.pkl").copy()
CAT=["pertenencia_etnica","regimen","area_residencia","gestante","subregion","hospitalizada"]
for c in CAT:
    b[c]=b[c].replace("","Sin dato").fillna("Sin dato").astype(str)
b["edad"]=pd.to_numeric(b["edad"],errors="coerce")
b["edad"]=b["edad"].fillna(b["edad"].median())
X=b[["edad"]+CAT].copy()
M=X.to_numpy(dtype=object)
catidx=list(range(1,1+len(CAT)))
costs={}
for k in [2,3,4,5,6]:
    kp=KPrototypes(n_clusters=k,init="Huang",n_init=2,max_iter=20,random_state=42,verbose=0)
    kp.fit(M,categorical=catidx)
    costs[k]=round(kp.cost_,0)
print("Costo por k:",costs)
