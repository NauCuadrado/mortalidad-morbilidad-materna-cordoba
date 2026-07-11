# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, glob, csv
DANE={2015:"dane/e2015",2016:"dane/e2016",2017:"dane/e2017",2018:"dane/e2018",2019:"dane/e2019",
2020:"dane/e2020b",2021:"dane/e2021",2022:"dane/e2022",2023:"dane/eevv2023",2024:"dane/e2024"}
def is_early(cb):
    cb=(cb or "").strip().upper()
    if cb=="A34": return True
    if cb[:1]=="O":
        if cb[:3] in ("O96","O97"): return False  # tardia/secuela
        return True
    return False
def is_O(cb):
    cb=(cb or "").strip().upper(); return cb[:1]=="O" or cb=="A34"
rows=[]
for y,d in DANE.items():
    f=glob.glob(f"{d}/*.csv")[0]
    nat_e=nat_all=cor_e=cor_all=0
    with open(f,encoding="latin-1") as fh:
        r=csv.DictReader(fh)
        for row in r:
            cb=row.get("C_BAS1") or ""
            if not is_O(cb): continue
            if (row.get("SEXO") or "").strip()!="2": continue
            e=is_early(cb)
            nat_all+=1; nat_e+=1 if e else 0
            if (row.get("CODPTORE") or "").strip()=="23":
                cor_all+=1; cor_e+=1 if e else 0
    rows.append({"anio":y,"DANE_nac_early":nat_e,"DANE_nac_all":nat_all,"DANE_cor_early":cor_e,"DANE_cor_all":cor_all})
v=pd.DataFrame(rows)
# nacidos
B=pd.read_pickle("_nac_births.pkl"); nb=B[B.dpto==0].groupby("anio")["nacidos"].sum(); cb=B[B.dpto==23].groupby("anio")["nacidos"].sum()
v["nac_NV"]=v["anio"].map(nb); v["cor_NV"]=v["anio"].map(cb)
v["RMM_nac_DANE_early"]=(v["DANE_nac_early"]/v["nac_NV"]*1e5).round(1)
v["RMM_cor_DANE_early"]=(v["DANE_cor_early"]/v["cor_NV"]*1e5).round(1)
print("== Validación numerador: DANE (registro) ==")
print(v[["anio","DANE_nac_early","DANE_nac_all","RMM_nac_DANE_early","DANE_cor_early","RMM_cor_DANE_early"]].to_string(index=False))
print("\nPERIODO Nacional: DANE early total=%d  RMM=%.1f | DANE todas=%d"%(v["DANE_nac_early"].sum(),v["DANE_nac_early"].sum()/v["nac_NV"].sum()*1e5,v["DANE_nac_all"].sum()))
print("PERIODO Cordoba : DANE early total=%d  RMM=%.1f | DANE todas=%d"%(v["DANE_cor_early"].sum(),v["DANE_cor_early"].sum()/v["cor_NV"].sum()*1e5,v["DANE_cor_all"].sum()))
print("\n(Comparar: SIVIGILA-based RMM nacional periodo=88.4 ; Cordoba=104.8)")
v.to_pickle("_valida.pkl")
