# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, glob
DANE={2015:"dane/e2015",2016:"dane/e2016",2017:"dane/e2017",2018:"dane/e2018",2019:"dane/e2019",
2020:"dane/e2020b",2021:"dane/e2021",2022:"dane/eevv2023" if False else "dane/e2022",2023:"dane/eevv2023",2024:"dane/e2024"}
def early(cb):
    cb=str(cb).strip().upper()
    if cb=="A34": return True
    if cb[:1]=="O" and cb[:3] not in ("O96","O97"): return True
    return False
dep_rows=[]; mun_rows=[]
for y,d in DANE.items():
    f=glob.glob(f"{d}/*.csv")[0]
    df=pd.read_csv(f,usecols=lambda c:str(c).strip() in ("C_BAS1","SEXO","CODPTORE","CODMUNRE"),
                   dtype=str,encoding="latin-1",low_memory=False)
    df.columns=[c.strip() for c in df.columns]
    df=df[(df["SEXO"].astype(str).str.strip()=="2")]
    df=df[df["C_BAS1"].map(early)]
    # por depto
    dp=pd.to_numeric(df["CODPTORE"],errors="coerce")
    for code,nn in dp.value_counts().items():
        if pd.notna(code): dep_rows.append({"anio":y,"dpto":int(code),"muertes":int(nn)})
    # cordoba por municipio
    cor=df[dp==23]
    mm=cor["CODMUNRE"].astype(str).str.strip().value_counts()
    for c3,nn in mm.items():
        mun_rows.append({"anio":y,"cod_municipio":"23"+c3.zfill(3),"muertes":int(nn)})
DEP=pd.DataFrame(dep_rows); MUN=pd.DataFrame(mun_rows)
DEP.to_pickle("_dane_early_dep.pkl"); MUN.to_pickle("_dane_early_mun.pkl")
print("Nacional muertes tempranas/anio:",dict(DEP.groupby("anio")["muertes"].sum()))
print("Cordoba muertes tempranas/anio:",dict(DEP[DEP.dpto==23].groupby("anio")["muertes"].sum()))
print("Cordoba municipios early total:",MUN.groupby("cod_municipio")["muertes"].sum().sum())
