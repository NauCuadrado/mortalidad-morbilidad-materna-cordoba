# -*- coding: utf-8 -*-
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
DEP={5:"Antioquia",8:"Atlántico",11:"Bogotá",13:"Bolívar",15:"Boyacá",17:"Caldas",18:"Caquetá",19:"Cauca",20:"Cesar",23:"Córdoba",25:"Cundinamarca",27:"Chocó",41:"Huila",44:"La Guajira",47:"Magdalena",50:"Meta",52:"Nariño",54:"N. Santander",63:"Quindío",66:"Risaralda",68:"Santander",70:"Sucre",73:"Tolima",76:"Valle",81:"Arauca",85:"Casanare",86:"Putumayo",88:"San Andrés",91:"Amazonas",94:"Guainía",95:"Guaviare",97:"Vaupés",99:"Vichada"}
AZUL="#1F4E79"; ROJO="#c0392b"
D=pd.read_pickle("_nac_deaths.pkl"); B=pd.read_pickle("_nac_births.pkl")
D=D[D.dpto.isin(DEP)]; B=B[B.dpto.isin(DEP)]
# ranking periodo
dd=D.groupby("dpto")["muertes"].sum(); bb=B.groupby("dpto")["nacidos"].sum()
rk=pd.DataFrame({"dpto":dd.index}).assign(muertes=dd.values)
rk["nacidos"]=rk["dpto"].map(bb); rk["RMM"]=(rk["muertes"]/rk["nacidos"]*1e5).round(1)
rk["Departamento"]=rk["dpto"].map(DEP)
rk=rk[rk["nacidos"]>=2000].sort_values("RMM",ascending=False).reset_index(drop=True)
rk["rank"]=rk.index+1
natR=88.4
pos=int(rk[rk.dpto==23]["rank"].iloc[0]); ncol=len(rk)
print(f"Córdoba: puesto {pos} de {ncol} departamentos en RMM (mayor a menor).")
print(rk[["rank","Departamento","muertes","nacidos","RMM"]].head(12).to_string(index=False))
rk.to_csv("Ranking_departamental_RMM_2015-2024.csv",index=False,encoding="utf-8-sig")

# serie nacional vs Cordoba
yrs=list(range(2015,2025))
natd=D.groupby("anio")["muertes"].sum() ; 
# total nacional incluye dpto=0 que se filtró; recomputar nacional desde pickle original
Dall=pd.read_pickle("_nac_deaths.pkl"); Ball=pd.read_pickle("_nac_births.pkl")
nd=Dall[Dall.dpto==0].groupby("anio")["muertes"].sum(); nb=Ball[Ball.dpto==0].groupby("anio")["nacidos"].sum()
cd=Dall[Dall.dpto==23].groupby("anio")["muertes"].sum(); cb=Ball[Ball.dpto==23].groupby("anio")["nacidos"].sum()
rmm_nac={y:round(float(nd[y])/float(nb[y])*1e5,1) for y in yrs}
rmm_cor={y:round(float(cd[y])/float(cb[y])*1e5,1) for y in yrs}
ser=pd.DataFrame({"anio":yrs,"RMM_nacional":[rmm_nac[y] for y in yrs],"RMM_Cordoba":[rmm_cor[y] for y in yrs]})
ser.to_csv("Serie_RMM_nacional_vs_Cordoba.csv",index=False,encoding="utf-8-sig")
print("\n",ser.to_string(index=False))

# Fig 1: serie
fig,ax=plt.subplots(figsize=(8.6,5.2))
ax.axvspan(2019.5,2021.5,color="#f2d7d5",alpha=0.6,label="Pandemia")
ax.plot(yrs,ser["RMM_nacional"],"-o",color=AZUL,lw=2,label="Colombia")
ax.plot(yrs,ser["RMM_Cordoba"],"-s",color=ROJO,lw=2,label="Córdoba")
ax.axhline(70,ls=":",color="#555"); ax.text(2015,72,"Meta ODS = 70",fontsize=8,color="#555")
ax.set_ylabel("RMM (x100.000 NV)"); ax.set_xlabel("Año"); ax.set_xticks(yrs); ax.set_ylim(0,140); ax.grid(alpha=0.25)
ax.set_title("Razón de mortalidad materna: Córdoba frente a Colombia",fontsize=13,fontweight="bold",color=AZUL,loc="left",pad=22)
ax.text(0,1.02,"2015-2024. Córdoba se mantiene por encima del nivel nacional (104,8 vs 88,4 en el periodo).",transform=ax.transAxes,fontsize=8.5,color="#595959")
ax.legend(fontsize=9,frameon=False)
ax.text(0.99,-0.13,"Fuentes: SIVIGILA, DANE nacidos vivos (2024 preliminar). Elab.: Naudith C.",transform=ax.transAxes,ha="right",fontsize=7.3,color="#888888")
fig.tight_layout(); fig.savefig("Serie_RMM_nacional_vs_Cordoba.png",dpi=170); plt.close(fig)

# Fig 2: ranking
fig,ax=plt.subplots(figsize=(8.2,9))
cols=["#c0392b" if d==23 else "#9ec3e0" for d in rk["dpto"]]
ax.barh(rk["Departamento"][::-1],rk["RMM"][::-1],color=cols[::-1])
ax.axvline(natR,ls="--",color="#333",lw=1.2); ax.text(natR+2,1,"Nacional 88,4",fontsize=8,color="#333",rotation=90,va="bottom")
ax.set_xlabel("RMM acumulada 2015-2024 (x100.000 NV)")
ax.set_title("Mortalidad materna por departamento (Córdoba resaltado)",fontsize=12.5,fontweight="bold",color=AZUL,loc="left",pad=14)
ax.text(0.99,-0.07,f"Córdoba: puesto {pos} de {ncol}. Fuentes: SIVIGILA, DANE. Elab.: Naudith C.",transform=ax.transAxes,ha="right",fontsize=7.3,color="#888888")
ax.tick_params(axis="y",labelsize=7.5); ax.grid(axis="x",alpha=0.25)
fig.tight_layout(); fig.savefig("Ranking_departamental_RMM.png",dpi=170); plt.close(fig)
print("\nfiguras nacionales guardadas | Cordoba puesto",pos,"de",ncol)
