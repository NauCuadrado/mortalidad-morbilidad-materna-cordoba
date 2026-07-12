# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, glob
SV="/sessions/upbeat-modest-turing/mnt/mortalidad/01_Datos_fuente/SIVIGILA"
nat={}; cor={}
for y in range(2015,2025):
    f=glob.glob(f"{SV}/Datos_{y}_549.*")[0]
    df=pd.read_excel(f,engine="calamine",dtype=str,usecols=lambda c:str(c).strip()=="COD_DPTO_R")
    df.columns=[c.strip() for c in df.columns]
    dp=pd.to_numeric(df["COD_DPTO_R"],errors="coerce")
    nat[y]=int(len(df)); cor[y]=int((dp==23).sum())
pd.to_pickle({"nat":nat,"cor":cor},"_nac_mme.pkl")
print("MME nacional/anio:",nat)
print("MME Cordoba/anio:",cor)
print("MME nacional total:",sum(nat.values()),"| Cordoba:",sum(cor.values()))
