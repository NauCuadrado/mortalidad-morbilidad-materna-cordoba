# -*- coding: utf-8 -*-
import pandas as pd, glob, os
from collections import defaultdict
DIRS={2015:"n2015",2016:"n2016",2017:"n2017c",2018:"n2018",2019:"n2019",
2020:"n2020",2021:"n2021b",2022:"n2022b",2023:"n2023",2024:"n2024b"}
BASE="/sessions/upbeat-modest-turing/mnt/outputs/nac"
tot=defaultdict(int); per_year={}
for y,d in DIRS.items():
    fs=glob.glob(f"{BASE}/{d}/*.csv")
    if not fs: print(y,"MISSING"); continue
    df=pd.read_csv(fs[0],usecols=["CODPTORE","CODMUNRE"],dtype=str,encoding="latin-1",low_memory=False)
    cor=df[df["CODPTORE"].astype(str).str.strip()=="23"]
    vc=cor["CODMUNRE"].astype(str).str.strip().value_counts()
    per_year[y]=int(len(cor))
    for cod,n in vc.items(): tot[cod]+=int(n)
    print(y,"nac Cordoba:",len(cor))
print("\nTotal nacidos vivos Cordoba 2015-2024:",sum(per_year.values()))
print("Por anio:",per_year)
import pandas as pd
births=pd.DataFrame([{"cod3":k,"nacidos_vivos":v} for k,v in tot.items()])
births["cod_municipio"]="23"+births["cod3"].str.zfill(3)
births.to_pickle("/sessions/upbeat-modest-turing/mnt/outputs/_births_mun.pkl")
print("municipios con nacimientos:",len(births))
