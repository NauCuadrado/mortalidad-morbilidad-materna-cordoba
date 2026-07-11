# -*- coding: utf-8 -*-
# v2 methodological refresh (Córdoba maternal mortality, manuscript v2).
# Reproduces: spatial autocorrelation on CRUDE rates (not spatially smoothed),
# Poisson ecological model with dispersion and Montería sensitivity, and the
# annual Córdoba-vs-Colombia comparison. Reads from ../data.
import warnings; warnings.filterwarnings("ignore")
import os, numpy as np, pandas as pd
import geopandas as gpd, libpysal, esda, statsmodels.api as sm, scipy.stats as st

HERE=os.path.dirname(os.path.abspath(__file__)); DATA=os.path.join(HERE,"..","data")
eco=pd.read_csv(os.path.join(DATA,"Ecologico_RMM_IPM_Cordoba.csv"))
eco["cod"]=eco["cod_municipio"].astype(str)
g=gpd.read_file(os.path.join(DATA,"cordoba_municipios.geojson")); g["cod"]=g["cod"].astype(str)
gdf=g.merge(eco,on="cod",how="left").sort_values("cod").reset_index(drop=True)

# Global empirical Bayes (Marshall 1991, moments)
dd=gdf["muertes_tempranas"].values.astype(float); nn=gdf["nacidos_vivos"].values.astype(float)
m=dd.sum()/nn.sum(); s2=max((nn*((dd/nn)-m)**2).sum()/nn.sum()-m/nn.mean(),0); C=s2/(s2+m/nn)
gdf["RMM_EBglobal"]=(m+C*((dd/nn)-m))*1e5
w=libpysal.weights.Queen.from_dataframe(gdf,use_index=False); w.transform="r"
print("== Moran's I (999 permutations) ==")
for col,lab in [("RMM_cruda","crude (primary)"),("RMM_EBglobal","global EB (sensitivity)"),("RMM_EB_espacial","spatial EB (illustrative)")]:
    np.random.seed(42); mi=esda.Moran(gdf[col].values,w,permutations=999)
    print(f"  {lab:26s} I={mi.I:.3f}  E[I]={mi.EI:.3f}  p={mi.p_sim:.3f}")
np.random.seed(42); lisa=esda.Moran_Local(gdf["RMM_cruda"].values,w,permutations=999)
print("  LISA (crude) significant clusters:",int((lisa.p_sim<0.05).sum()))

print("\n== Poisson ecological model (deaths ~ IPM/10, offset log live births) ==")
df=gdf[["municipio","cod","muertes_tempranas","nacidos_vivos","RMM_cruda","IPM"]].dropna().copy(); df["IPM10"]=df["IPM"]/10
def fit(data,lab):
    X=sm.add_constant(data["IPM10"]); off=np.log(data["nacidos_vivos"])
    mod=sm.GLM(data["muertes_tempranas"],X,offset=off,family=sm.families.Poisson()).fit()
    irr=np.exp(mod.params["IPM10"]); ci=np.exp(mod.conf_int().loc["IPM10"])
    print(f"  {lab}: IRR/10 IPM={irr:.2f} ({ci[0]:.2f}-{ci[1]:.2f}), p={mod.pvalues['IPM10']:.3f}, dispersion={mod.pearson_chi2/mod.df_resid:.2f}, n={len(data)}")
fit(df,"all (30)   "); fit(df[df.cod!="23001"],"no Montería")
rho,p=st.spearmanr(df["IPM"],df["RMM_cruda"]); print(f"  Spearman RMM-IPM rho={rho:.2f} (p={p:.2f}); IPM min {df.IPM.min():.1f} max {df.IPM.max():.1f} mean {df.IPM.mean():.1f} sd {df.IPM.std():.1f}")

# Annual Córdoba vs Colombia (if the series file is present)
sp=os.path.join(DATA,"Serie_RMM_temprana_nacional_vs_Cordoba.csv")
if os.path.exists(sp):
    s=pd.read_csv(sp); print("\n== Annual Córdoba vs Colombia ==")
    col_c=[c for c in s.columns if "ordob" in c.lower()][0]; col_n=[c for c in s.columns if "acion" in c.lower() or "olomb" in c.lower()][0]
    s["Cordoba_higher"]=s[col_c]>s[col_n]
    print(s.to_string(index=False)); print("Years Córdoba > Colombia:",int(s["Cordoba_higher"].sum()),"of",len(s))
print("\nDone.")
