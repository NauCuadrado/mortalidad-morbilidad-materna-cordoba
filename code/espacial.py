# -*- coding: utf-8 -*-
import json, unicodedata, numpy as np, pandas as pd
from shapely.geometry import shape
from libpysal.weights import W
from esda.moran import Moran, Moran_Local
from esda.smoothing import Empirical_Bayes, Spatial_Empirical_Bayes
np.random.seed(42)
def norm(s):
    s=str(s).strip().upper().replace("Ñ","N")
    return "".join(c for c in unicodedata.normalize("NFD",s) if unicodedata.category(c)!="Mn")
ALIAS={"PURISIMA DE LA CONCEPCION":"PURISIMA"}

gj=json.load(open("cordoba_municipios.geojson"))
geoms=[]; names=[]
for f in gj["features"]:
    geoms.append(shape(f["geometry"])); names.append(f["properties"]["name"])
keys=[ALIAS.get(norm(n),norm(n)) for n in names]

agg=pd.read_pickle("_agg_mun.pkl"); agg=agg[agg["municipio"]!="Otro/Sin dato"]
births=pd.read_pickle("_births_mun.pkl")[["cod_municipio","nacidos_vivos"]]
d=agg.merge(births,on="cod_municipio",how="left")
d["k"]=d["municipio"].map(norm)
dm={r["k"]:r for _,r in d.iterrows()}
O=np.array([int(dm[k]["muertes"]) for k in keys],float)
P=np.array([int(dm[k]["nacidos_vivos"]) for k in keys],float)

# adyacencia (contigüidad) con tolerancia por simplificación
neigh={}
for i,gi in enumerate(geoms):
    gib=gi.buffer(0.004)
    nb=[j for j,gj_ in enumerate(geoms) if j!=i and gib.intersects(gj_)]
    neigh[i]=nb
w=W(neigh, id_order=list(range(len(geoms)))); w.transform="r"
print("vecinos promedio:",round(np.mean([len(v) for v in neigh.values()]),2),
      "| islas:",[names[i] for i,v in neigh.items() if len(v)==0])

rate=O/P*1e5
eb=Empirical_Bayes(O,P).r*1e5
seb=Spatial_Empirical_Bayes(O,P,w).r*1e5

mi=Moran(rate,w,permutations=999)
mi_eb=Moran(eb,w,permutations=999)
print(f"Moran I (RMM cruda) = {mi.I:.3f}  p={mi.p_sim:.3f}")
print(f"Moran I (RMM EB)    = {mi_eb.I:.3f}  p={mi_eb.p_sim:.3f}")

lisa=Moran_Local(eb,w,permutations=999,seed=42)
q=lisa.q; sig=lisa.p_sim<0.05
labmap={1:"Alto-Alto",2:"Bajo-Alto",3:"Bajo-Bajo",4:"Alto-Bajo"}
clus=[labmap[q[i]] if sig[i] else "No significativo" for i in range(len(keys))]

out=pd.DataFrame({"cod_municipio":[str(dm[k]["cod_municipio"]) for k in keys],
  "municipio":[str(dm[k]["municipio"]) for k in keys],"subregion":[str(dm[k]["subregion"]) for k in keys],
  "muertes":[int(x) for x in O],"nacidos_vivos":[int(x) for x in P],
  "RMM_cruda":list(np.round(rate,1)),"RMM_EB_global":list(np.round(np.asarray(eb).ravel(),1)),
  "RMM_EB_espacial":list(np.round(np.asarray(seb).ravel(),1)),
  "LISA":list(clus),"LISA_p":list(np.round(np.asarray(lisa.p_sim).ravel(),3))})
out=out.sort_values("RMM_EB_espacial",ascending=False)
out.to_pickle("_espacial.pkl"); out.to_csv("Espacial_RMM_suavizada_Cordoba.csv",index=False,encoding="utf-8-sig")
print("\nTop por RMM suavizada espacial:")
print(out.head(10)[["municipio","muertes","nacidos_vivos","RMM_cruda","RMM_EB_espacial","LISA"]].to_string(index=False))
print("\nConglomerados LISA significativos:")
print(out[out["LISA"]!="No significativo"][["municipio","RMM_EB_espacial","LISA","LISA_p"]].to_string(index=False))
