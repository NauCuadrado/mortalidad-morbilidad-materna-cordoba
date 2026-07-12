# -*- coding: utf-8 -*-
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
DEPN={5:"Antioquia",8:"Atlántico",11:"Bogotá",13:"Bolívar",15:"Boyacá",17:"Caldas",18:"Caquetá",19:"Cauca",20:"Cesar",23:"Córdoba",25:"Cundinamarca",27:"Chocó",41:"Huila",44:"La Guajira",47:"Magdalena",50:"Meta",52:"Nariño",54:"N. Santander",63:"Quindío",66:"Risaralda",68:"Santander",70:"Sucre",73:"Tolima",76:"Valle",81:"Arauca",85:"Casanare",86:"Putumayo",88:"San Andrés",91:"Amazonas",94:"Guainía",95:"Guaviare",97:"Vaupés",99:"Vichada"}
AZUL="#1F4E79"; ROJO="#c0392b"
DEP=pd.read_pickle("_dane_early_dep.pkl"); B=pd.read_pickle("_nac_births.pkl")
DEP=DEP[DEP.dpto.isin(DEPN)]
yrs=list(range(2015,2025))
# nacional y cordoba por anio
nd=DEP.groupby("anio")["muertes"].sum(); nb=B[B.dpto==0].groupby("anio")["nacidos"].sum()
cd=DEP[DEP.dpto==23].groupby("anio")["muertes"].sum(); cb=B[B.dpto==23].groupby("anio")["nacidos"].sum()
natR=round(nd.sum()/nb.sum()*1e5,1); corR=round(cd.sum()/cb.sum()*1e5,1)
print("RMM nacional (temprana) periodo:",natR,"| Cordoba:",corR,"| razon:",round(corR/natR,2))
ser=pd.DataFrame({"anio":yrs,"RMM_nacional":[round(nd[y]/nb[y]*1e5,1) for y in yrs],"RMM_Cordoba":[round(cd[y]/cb[y]*1e5,1) for y in yrs]})
ser.to_csv("Serie_RMM_temprana_nacional_vs_Cordoba.csv",index=False,encoding="utf-8-sig")
print(ser.to_string(index=False))
# ranking
bb=B[B.dpto.isin(DEPN)].groupby("dpto")["nacidos"].sum(); dd=DEP.groupby("dpto")["muertes"].sum()
rk=pd.DataFrame({"dpto":dd.index}).assign(muertes=dd.values); rk["nacidos"]=rk["dpto"].map(bb)
rk["RMM"]=(rk["muertes"]/rk["nacidos"]*1e5).round(1); rk["Departamento"]=rk["dpto"].map(DEPN)
rk=rk[rk["nacidos"]>=2000].sort_values("RMM",ascending=False).reset_index(drop=True); rk["rank"]=rk.index+1
pos=int(rk[rk.dpto==23]["rank"].iloc[0]); ncol=len(rk)
print(f"Cordoba puesto {pos} de {ncol} (def. oficial)")
rk.to_csv("Ranking_departamental_RMM_temprana.csv",index=False,encoding="utf-8-sig")
# Fig serie
fig,ax=plt.subplots(figsize=(8.6,5.2))
ax.axvspan(2019.5,2021.5,color="#f2d7d5",alpha=0.6,label="Pandemia")
ax.plot(yrs,ser["RMM_nacional"],"-o",color=AZUL,lw=2,label="Colombia"); ax.plot(yrs,ser["RMM_Cordoba"],"-s",color=ROJO,lw=2,label="Córdoba")
ax.axhline(70,ls=":",color="#555"); ax.text(2015,72,"Meta ODS = 70",fontsize=8,color="#555")
ax.set_ylabel("RMM (x100.000 NV)"); ax.set_xlabel("Año"); ax.set_xticks(yrs); ax.grid(alpha=0.25); ax.set_ylim(0,140)
ax.set_title("Razón de mortalidad materna (definición oficial): Córdoba vs Colombia",fontsize=12.5,fontweight="bold",color=AZUL,loc="left",pad=22)
ax.text(0,1.02,f"2015-2024. Córdoba {corR} vs Colombia {natR} en el periodo. Muertes maternas tempranas, registro DANE.",transform=ax.transAxes,fontsize=8.3,color="#595959")
ax.legend(fontsize=9,frameon=False); ax.text(0.99,-0.13,"Fuentes: DANE-EEVV. Elab.: Naudith C.",transform=ax.transAxes,ha="right",fontsize=7.3,color="#888888")
fig.tight_layout(); fig.savefig("Serie_RMM_temprana_nacional_vs_Cordoba.png",dpi=170); plt.close(fig)
# Fig ranking
fig,ax=plt.subplots(figsize=(8.2,9)); cols=["#c0392b" if d==23 else "#9ec3e0" for d in rk["dpto"]]
ax.barh(rk["Departamento"][::-1],rk["RMM"][::-1],color=cols[::-1])
ax.axvline(natR,ls="--",color="#333",lw=1.2); ax.text(natR+1,1,f"Nacional {natR}",fontsize=8,color="#333",rotation=90,va="bottom")
ax.set_xlabel("RMM acumulada 2015-2024 (x100.000 NV, def. oficial)")
ax.set_title("Mortalidad materna por departamento (def. oficial, Córdoba resaltado)",fontsize=11.5,fontweight="bold",color=AZUL,loc="left",pad=14)
ax.text(0.99,-0.07,f"Córdoba: puesto {pos} de {ncol}. Fuente: DANE-EEVV. Elab.: Naudith C.",transform=ax.transAxes,ha="right",fontsize=7.3,color="#888888")
ax.tick_params(axis="y",labelsize=7.5); ax.grid(axis="x",alpha=0.25)
fig.tight_layout(); fig.savefig("Ranking_departamental_RMM_temprana.png",dpi=170); plt.close(fig)
print("figuras nacionales (temprana) guardadas")
