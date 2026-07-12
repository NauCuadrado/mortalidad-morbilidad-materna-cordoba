# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, warnings, json
warnings.filterwarnings("ignore")
b=pd.read_pickle("_base.pkl").copy()
b["edad"]=pd.to_numeric(b["edad"],errors="coerce")
def edg(x): return "<20" if x<20 else ("20-34" if x<35 else "35+")
df=pd.DataFrame()
df["Edad"]=b["edad"].fillna(b["edad"].median()).map(edg)
df["Etnia"]=np.where(b["pertenencia_etnica"].astype(str).str.contains("Indigena"),"Indígena","Otra")
df["Regimen"]=np.where(b["regimen"].astype(str).str.contains("Subsidiado"),"Subsidiado","Otro")
df["Area"]=np.where(b["area_residencia"].astype(str).str.contains("Cabecera"),"Cabecera","Rural")
df["Gestante"]=np.where(b["gestante"].astype(str)=="Si","Sí","No")
peri=["Costanera","San Jorge","Alto Sinu"]
df["Zona"]=np.where(b["subregion"].isin(peri),"Periférica","Central")
df["Desenlace"]=np.where(b["desenlace_fallecio"]==1,"Muerte","Sobrevive")
from pgmpy.estimators import HillClimbSearch
B=60; parents=[]; gest_edge=0
rng=np.random.RandomState(7)
for i in range(B):
    s=df.sample(len(df),replace=True,random_state=rng.randint(1e6))
    hc=HillClimbSearch(s)
    best=hc.estimate(scoring_method="bic-d",max_indegree=3,show_progress=False)
    e=list(best.edges())
    pa=[u for (u,v) in e if v=="Desenlace"]
    parents+=pa
    if ("Gestante","Desenlace") in e: gest_edge+=1
from collections import Counter
cnt=Counter(parents)
print("Bootstrap red bayesiana (B=%d resamples):"%B)
print("  Frecuencia arco Gestante->Desenlace: %.0f%%"%(gest_edge/B*100))
print("  Padres de Desenlace (frecuencia):",{k:round(v/B*100) for k,v in cnt.most_common()})
json.dump({"B":B,"gest_edge_pct":round(gest_edge/B*100),"parents":{k:round(v/B*100) for k,v in cnt.items()}},open("_bn_boot.json","w"))

# ---- SHAP en conjunto de PRUEBA (modelo completo = analisis de fuga) ----
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, shap
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier
bb=pd.read_pickle("_base.pkl").copy()
bb["edad"]=pd.to_numeric(bb["edad"],errors="coerce"); bb["semanas_gestacion"]=pd.to_numeric(bb["semanas_gestacion"],errors="coerce")
bb["anio"]=bb["anio"].astype(int); bb["semana"]=pd.to_numeric(bb["semana"],errors="coerce")
for c in ["pertenencia_etnica","regimen","area_residencia","gestante","hospitalizada","subregion"]:
    bb[c]=bb[c].replace("","Sin dato").fillna("Sin dato").astype(str)
NUM=["edad","semanas_gestacion","anio","semana"]; CAT=["pertenencia_etnica","regimen","area_residencia","gestante","hospitalizada","subregion"]
y=bb["desenlace_fallecio"].values; tr=(bb["anio"]<=2021).values; te=(bb["anio"]>=2022).values
pre=ColumnTransformer([("num",SimpleImputer(strategy="median"),NUM),("cat",OneHotEncoder(handle_unknown="ignore",min_frequency=30,drop="if_binary"),CAT)])
Xtr=pre.fit_transform(bb[NUM+CAT][tr]); Xte=pre.transform(bb[NUM+CAT][te])
names=NUM+list(pre.named_transformers_["cat"].get_feature_names_out(CAT))
import numpy as np
Xtr=np.asarray(Xtr.todense()) if hasattr(Xtr,"todense") else np.asarray(Xtr)
Xte=np.asarray(Xte.todense()) if hasattr(Xte,"todense") else np.asarray(Xte)
gb=GradientBoostingClassifier(n_estimators=200,max_depth=3,learning_rate=0.05,random_state=42).fit(Xtr,y[tr])
sv=shap.TreeExplainer(gb).shap_values(Xte)
imp=pd.DataFrame({"variable":names,"shap":np.abs(sv).mean(0)}).sort_values("shap",ascending=False).head(12)
AZUL="#1F4E79"
fig,ax=plt.subplots(figsize=(8.4,6))
ax.barh(imp["variable"][::-1],imp["shap"][::-1],color="#5b9bd5")
ax.set_xlabel("Importancia media |SHAP| (conjunto de prueba 2022-2024)")
ax.set_title("Contribución de variables al modelo completo (SHAP, prueba)",fontsize=12.5,fontweight="bold",color=AZUL,loc="left",pad=10)
ax.text(0.99,-0.09,"Modelo completo (análisis de fuga). Codificación binaria sin categoría redundante. Fuente: SIVIGILA.",transform=ax.transAxes,ha="right",fontsize=7.3,color="#888888")
ax.tick_params(axis="y",labelsize=8); ax.grid(axis="x",alpha=0.25); fig.tight_layout()
fig.savefig("SHAP_importancia_Cordoba.png",dpi=170); plt.close(fig)
imp.to_csv("SHAP_importancia_Cordoba.csv",index=False,encoding="utf-8-sig")
print("\nSHAP (prueba) top:",imp["variable"].head(6).tolist())
