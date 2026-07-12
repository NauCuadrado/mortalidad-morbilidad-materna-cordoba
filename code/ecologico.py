# -*- coding: utf-8 -*-
import pandas as pd, numpy as np
import statsmodels.api as sm
from scipy import stats
sp=pd.read_pickle("_espacial.pkl").copy()
ipm=pd.read_pickle("_ipm.pkl").copy(); ipm.columns=["cod_municipio","IPM"]
sp["cod_municipio"]=sp["cod_municipio"].astype(str)
ipm["cod_municipio"]=ipm["cod_municipio"].astype(str)
d=sp.merge(ipm,on="cod_municipio",how="left")
d["IPM"]=pd.to_numeric(d["IPM"],errors="coerce")
print("emparejados con IPM:",d["IPM"].notna().sum(),"/",len(d))

# correlaciones
rho,p=stats.spearmanr(d["IPM"],d["RMM_EB_espacial"])
rp,pp=stats.pearsonr(d["IPM"],d["RMM_cruda"])
print(f"Spearman IPM~RMM_EB = {rho:.3f} (p={p:.3f}) | Pearson IPM~RMM_cruda = {rp:.3f} (p={pp:.3f})")

# Poisson / NB: muertes ~ IPM, offset log(nacidos vivos)
d=d[d["nacidos_vivos"]>0].copy()
X=sm.add_constant(pd.DataFrame({"IPM10":d["IPM"]/10}))  # por cada 10 puntos de IPM
off=np.log(d["nacidos_vivos"].values)
poi=sm.GLM(d["muertes"],X,family=sm.families.Poisson(),offset=off).fit()
# sobredispersion
pear=poi.pearson_chi2/poi.df_resid
print(f"\nPoisson: dispersion (Pearson/df)={pear:.2f}")
nb=sm.GLM(d["muertes"],X,family=sm.families.NegativeBinomial(alpha=1.0),offset=off).fit()
m=nb
irr=np.exp(m.params["IPM10"]); ci=np.exp(m.conf_int().loc["IPM10"])
print(f"\n[Binomial negativa] IRR por +10 puntos IPM = {irr:.2f} (IC95% {ci[0]:.2f}-{ci[1]:.2f}), p={m.pvalues['IPM10']:.3f}")
print("RMM departamental esperada baja (IPM=40) vs alta (IPM=70):")
import numpy as np
for v in [40,55,70]:
    lam=np.exp(m.params['const']+m.params['IPM10']*v/10)*100000
    print(f"   IPM={v}: RMM esperada ~ {lam:.0f} x100.000")
d[["cod_municipio","municipio","subregion","muertes","nacidos_vivos","RMM_cruda","RMM_EB_espacial","IPM"]].sort_values("IPM",ascending=False).to_csv("Ecologico_RMM_IPM_Cordoba.csv",index=False,encoding="utf-8-sig")
d.to_pickle("_ecologico.pkl")
print("\nguardado tabla ecologica")
