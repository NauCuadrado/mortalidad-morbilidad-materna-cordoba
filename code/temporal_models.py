# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, statsmodels.api as sm
t=pd.read_pickle("_serie_anual.pkl").copy()
t["yc"]=t["anio"]-2015
t["covid"]=t["anio"].isin([2020,2021]).astype(int)
off=np.log(t["nacidos_vivos"].values)

def fit(y,fam,nombre):
    X=sm.add_constant(t[["yc","covid"]])
    m=sm.GLM(t[y],X,family=fam,offset=off).fit()
    apc=(np.exp(m.params["yc"])-1)*100
    ci=(np.exp(m.conf_int().loc["yc"])-1)*100
    rr=np.exp(m.params["covid"]); rrci=np.exp(m.conf_int().loc["covid"])
    print(f"\n[{nombre}]")
    print(f"   Cambio anual (APC) = {apc:+.1f}% (IC95% {ci[0]:+.1f} a {ci[1]:+.1f}), p={m.pvalues['yc']:.3f}")
    print(f"   Efecto pandemia (RR 2020-21) = {rr:.2f} (IC95% {rrci[0]:.2f}-{rrci[1]:.2f}), p={m.pvalues['covid']:.3f}")
    return m

print("== MORTALIDAD MATERNA (RMM) ==")
fit("muertes",sm.families.Poisson(),"RMM, Poisson")
print("\n== MORBILIDAD MATERNA EXTREMA (razon) ==")
fit("MME",sm.families.NegativeBinomial(alpha=0.5),"Razon MME, NB  [OJO: confundido por mejora de notificacion]")
