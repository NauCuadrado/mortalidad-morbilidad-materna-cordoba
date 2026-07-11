# -*- coding: utf-8 -*-
import pandas as pd, numpy as np
D=pd.read_pickle("_nac_deaths.pkl"); B=pd.read_pickle("_nac_births.pkl"); MM=pd.read_pickle("_nac_mme.pkl")
yrs=list(range(2015,2025))
nd=D[D.dpto==0].groupby("anio")["muertes"].sum(); nb=B[B.dpto==0].groupby("anio")["nacidos"].sum()
cd=D[D.dpto==23].groupby("anio")["muertes"].sum(); cb=B[B.dpto==23].groupby("anio")["nacidos"].sum()
nmme=MM["nat"]; cmme=MM["cor"]
def per(num,den,k): return round(num/den*k,1)
# periodo
ND,NB,NMME=int(nd.sum()),int(nb.sum()),int(sum(nmme.values()))
CD,CB,CMME=int(cd.sum()),int(cb.sum()),int(sum(cmme.values()))
tab=pd.DataFrame([
 ["Muertes maternas (n)",ND,CD],
 ["Casos de MME (n)",NMME,CMME],
 ["Nacidos vivos (n)",NB,CB],
 ["RMM (x100.000 NV)",per(ND,NB,1e5),per(CD,CB,1e5)],
 ["Razón de MME (x1.000 NV)",per(NMME,NB,1e3),per(CMME,CB,1e3)],
 ["Índice de mortalidad / letalidad (%)",round(ND/(NMME+ND)*100,2),round(CD/(CMME+CD)*100,2)],
],columns=["Indicador (periodo 2015-2024)","Colombia","Córdoba"])
tab["Razón Córdoba/Colombia"]=(pd.to_numeric(tab["Córdoba"])/pd.to_numeric(tab["Colombia"])).round(2)
tab.to_csv("Comparacion_nacional_vs_Cordoba.csv",index=False,encoding="utf-8-sig")
print(tab.to_string(index=False))

# series anuales razon MME e indice mortalidad
ser=pd.DataFrame({"anio":yrs})
ser["razonMME_nac"]=[per(nmme[y],nb[y],1e3) for y in yrs]
ser["razonMME_cor"]=[per(cmme[y],cb[y],1e3) for y in yrs]
ser["indice_nac"]=[round(nd[y]/(nmme[y]+nd[y])*100,2) for y in yrs]
ser["indice_cor"]=[round(cd[y]/(cmme[y]+cd[y])*100,2) for y in yrs]
ser.to_pickle("_serie_nac_comp.pkl")
print("\n",ser.to_string(index=False))
