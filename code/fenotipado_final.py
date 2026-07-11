# -*- coding: utf-8 -*-
import pandas as pd, numpy as np
from kmodes.kprototypes import KPrototypes
np.random.seed(42)
b=pd.read_pickle("_base.pkl").copy()
CAT=["pertenencia_etnica","regimen","area_residencia","gestante","subregion","hospitalizada"]
for c in CAT:
    b[c]=b[c].replace("","Sin dato").fillna("Sin dato").astype(str)
b["edad"]=pd.to_numeric(b["edad"],errors="coerce"); b["edad"]=b["edad"].fillna(b["edad"].median())
M=b[["edad"]+CAT].to_numpy(dtype=object)
kp=KPrototypes(n_clusters=4,init="Huang",n_init=5,max_iter=40,random_state=42)
lab=kp.fit_predict(M,categorical=list(range(1,1+len(CAT))))
b["perfil"]=lab
# ordenar perfiles por letalidad
order=b.groupby("perfil")["desenlace_fallecio"].mean().sort_values(ascending=False).index.tolist()
remap={old:f"P{i+1}" for i,old in enumerate(order)}
b["perfil"]=b["perfil"].map(remap)
b.to_pickle("_base_perfil.pkl")

def moda(s): 
    m=s.value_counts(); return f"{m.index[0]} ({m.iloc[0]/m.sum()*100:.0f}%)"
rows=[]
for p in sorted(b["perfil"].unique()):
    g=b[b["perfil"]==p]
    rows.append({"Perfil":p,"n":len(g),"%":round(len(g)/len(b)*100,1),
        "Edad media":round(g["edad"].mean(),1),
        "Muertes":int(g["desenlace_fallecio"].sum()),
        "Letalidad %":round(g["desenlace_fallecio"].mean()*100,2),
        "Etnia":moda(g["pertenencia_etnica"]),"Régimen":moda(g["regimen"]),
        "Área":moda(g["area_residencia"]),"Gestante":moda(g["gestante"]),
        "Subregión":moda(g["subregion"]),"Hospitalizada":moda(g["hospitalizada"])})
prof=pd.DataFrame(rows)
prof.to_pickle("_perfiles.pkl")
pd.set_option("display.width",200,"display.max_columns",20)
print(prof.to_string(index=False))
