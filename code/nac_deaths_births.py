# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, glob, os
DL="/sessions/upbeat-modest-turing/mnt/mortalidad/01_Datos_fuente/SIVIGILA"
NB="/sessions/upbeat-modest-turing/mnt/outputs/nac"
NDIR={2015:"n2015",2016:"n2016",2017:"n2017c",2018:"n2018",2019:"n2019",2020:"n2020",2021:"n2021b",2022:"n2022b",2023:"n2023",2024:"n2024b"}
YRS=range(2015,2025)
# --- muertes maternas nacional por dpto (SIVIGILA 550) ---
deaths=[]
for y in YRS:
    f=glob.glob(f"{DL}/Datos_{y}_550.*")[0]
    df=pd.read_excel(f,engine="calamine",dtype=str)
    df.columns=[c.strip() for c in df.columns]
    df["dp"]=pd.to_numeric(df["COD_DPTO_R"],errors="coerce")
    vc=df["dp"].value_counts()
    for dp,n in vc.items():
        if pd.notna(dp): deaths.append({"anio":y,"dpto":int(dp),"muertes":int(n)})
    deaths.append({"anio":y,"dpto":0,"muertes":len(df)})  # 0 = total nacional
D=pd.DataFrame(deaths)
# --- nacimientos nacional por dpto (DANE) ---
births=[]
for y,d in NDIR.items():
    f=glob.glob(f"{NB}/{d}/*.csv")[0]
    df=pd.read_csv(f,usecols=["CODPTORE"],dtype=str,encoding="latin-1",low_memory=False)
    df["dp"]=pd.to_numeric(df["CODPTORE"],errors="coerce")
    vc=df["dp"].value_counts()
    for dp,n in vc.items():
        if pd.notna(dp): births.append({"anio":y,"dpto":int(dp),"nacidos":int(n)})
    births.append({"anio":y,"dpto":0,"nacidos":len(df)})
Bb=pd.DataFrame(births)
D.to_pickle("_nac_deaths.pkl"); Bb.to_pickle("_nac_births.pkl")
natd=D[D.dpto==0].set_index("anio")["muertes"]; natb=Bb[Bb.dpto==0].set_index("anio")["nacidos"]
cord=D[D.dpto==23].set_index("anio")["muertes"]; corb=Bb[Bb.dpto==23].set_index("anio")["nacidos"]
print("NACIONAL muertes/anio:",dict(natd))
print("NACIONAL nacidos/anio:",dict(natb))
print("RMM nacional/anio:",{y:round(natd[y]/natb[y]*1e5,1) for y in YRS})
print("\nRMM nacional periodo:",round(natd.sum()/natb.sum()*1e5,1))
print("RMM Cordoba periodo:",round(cord.sum()/corb.sum()*1e5,1))
