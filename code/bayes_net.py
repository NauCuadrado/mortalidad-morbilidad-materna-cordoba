# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, warnings
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

from pgmpy.estimators import HillClimbSearch, BayesianEstimator
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.inference import VariableElimination
hc=HillClimbSearch(df)
best=hc.estimate(scoring_method="bic-d",max_indegree=3,show_progress=False)
edges=list(best.edges())
print("Aristas aprendidas:",edges)
model=DiscreteBayesianNetwork(edges if edges else [("Regimen","Desenlace")])
# asegurar que todos los nodos esten
for n in df.columns:
    if n not in model.nodes(): model.add_node(n)
model.fit(df)
infer=VariableElimination(model)
# markov blanket del desenlace
try: mb=model.get_markov_blanket("Desenlace")
except: mb=[]
print("Markov blanket de Desenlace:",mb)
# probabilidad base
base_p=infer.query(["Desenlace"],show_progress=False).values
idx_m=list(infer.query(["Desenlace"],show_progress=False).state_names["Desenlace"]).index("Muerte")
print(f"\nP(Muerte) basal = {base_p[idx_m]*100:.2f}%")
# escenarios que-pasaria-si (solo con variables en el modelo)
nodes=set(model.nodes())
escen=[("Régimen subsidiado",{"Regimen":"Subsidiado"}),("Régimen no subsidiado",{"Regimen":"Otro"}),
("Zona periférica",{"Zona":"Periférica"}),("Zona central",{"Zona":"Central"}),
("Residencia rural",{"Area":"Rural"}),("Residencia cabecera",{"Area":"Cabecera"}),
("Edad 35+",{"Edad":"35+"}),("Edad <20",{"Edad":"<20"}),
("Etnia indígena",{"Etnia":"Indígena"})]
rows=[]
for nombre,ev in escen:
    ev2={k:v for k,v in ev.items() if k in nodes}
    if not ev2: continue
    try:
        q=infer.query(["Desenlace"],evidence=ev2,show_progress=False)
        pm=q.values[list(q.state_names["Desenlace"]).index("Muerte")]*100
        rows.append({"Escenario":nombre,"P(Muerte) %":round(pm,2)})
    except Exception as e: rows.append({"Escenario":nombre,"P(Muerte) %":None})
res=pd.DataFrame(rows)
print("\nConsultas qué-pasaría-si:"); print(res.to_string(index=False))
res.to_csv("RedBayesiana_escenarios_Cordoba.csv",index=False,encoding="utf-8-sig")
import json
json.dump({"edges":edges,"markov_blanket":list(mb),"p_base":float(base_p[idx_m])},open("_bn.json","w"))
print("\nOK red bayesiana")
