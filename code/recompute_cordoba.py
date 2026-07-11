# -*- coding: utf-8 -*-
import json, unicodedata, numpy as np, pandas as pd
from shapely.geometry import shape
from libpysal.weights import W
from esda.moran import Moran, Moran_Local
from esda.smoothing import Empirical_Bayes, Spatial_Empirical_Bayes
from scipy import stats
import statsmodels.api as sm
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly, Patch
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as pe
from matplotlib.colors import Normalize
np.random.seed(42)
def norm(s):
    s=str(s).strip().upper().replace("Ñ","N")
    return "".join(c for c in unicodedata.normalize("NFD",s) if unicodedata.category(c)!="Mn")
ALIAS={"PURISIMA DE LA CONCEPCION":"PURISIMA"}
SHORT={"PURISIMA DE LA CONCEPCION":"Purísima","SAN ANDRES DE SOTAVENTO":"S. Andrés Sotav.","SAN BERNARDO DEL VIENTO":"S. Bernardo Vto.","SAN JOSE DE URE":"S. José de Uré","CIENAGA DE ORO":"Ciénaga de Oro","PUERTO LIBERTADOR":"Pto. Libertador","PUERTO ESCONDIDO":"Pto. Escondido","LOS CORDOBAS":"Los Córdobas"}
def short(n): k=norm(n); return SHORT.get(k,n.title().replace("De ","de ").replace("Del ","del "))

MUN={"001":"Monteria","068":"Ayapel","079":"Buenavista","090":"Canalete","162":"Cerete","168":"Chima","182":"Chinu","189":"Cienaga de Oro","300":"Cotorra","350":"La Apartada","417":"Lorica","419":"Los Cordobas","464":"Momil","466":"Montelibano","500":"Moñitos","555":"Planeta Rica","570":"Pueblo Nuevo","574":"Puerto Escondido","580":"Puerto Libertador","586":"Purisima","660":"Sahagun","670":"San Andres de Sotavento","672":"San Antero","675":"San Bernardo del Viento","678":"San Carlos","682":"San Jose de Ure","686":"San Pelayo","807":"Tierralta","815":"Tuchin","855":"Valencia"}
SUB={"Tierralta":"Alto Sinu","Valencia":"Alto Sinu","Monteria":"Medio Sinu","Cerete":"Medio Sinu","San Pelayo":"Medio Sinu","Cienaga de Oro":"Medio Sinu","San Carlos":"Medio Sinu","Lorica":"Bajo Sinu","Cotorra":"Bajo Sinu","Momil":"Bajo Sinu","Purisima":"Bajo Sinu","Chima":"Bajo Sinu","Montelibano":"San Jorge","Puerto Libertador":"San Jorge","La Apartada":"San Jorge","Buenavista":"San Jorge","Planeta Rica":"San Jorge","Ayapel":"San Jorge","Pueblo Nuevo":"San Jorge","San Jose de Ure":"San Jorge","Sahagun":"Sabanas","Chinu":"Sabanas","San Andres de Sotavento":"Sabanas","Tuchin":"Sabanas","Moñitos":"Costanera","Puerto Escondido":"Costanera","Los Cordobas":"Costanera","Canalete":"Costanera","San Antero":"Costanera","San Bernardo del Viento":"Costanera"}

mun=pd.read_pickle("_dane_early_mun.pkl").groupby("cod_municipio")["muertes"].sum().rename("muertes").reset_index()
births=pd.read_pickle("_births_mun.pkl")[["cod_municipio","nacidos_vivos"]]
d=pd.DataFrame({"cod_municipio":["23"+c for c in MUN]})
d["municipio"]=[MUN[c] for c in MUN]; d["subregion"]=d["municipio"].map(SUB)
d=d.merge(mun,on="cod_municipio",how="left").merge(births,on="cod_municipio",how="left")
d["muertes"]=d["muertes"].fillna(0).astype(int); d["nacidos_vivos"]=d["nacidos_vivos"].fillna(0).astype(int)
d["RMM"]=np.where(d["nacidos_vivos"]>0,d["muertes"]/d["nacidos_vivos"]*1e5,np.nan)
d["k"]=d["municipio"].map(norm)

gj=json.load(open("cordoba_municipios.geojson"))
geoms=[shape(f["geometry"]) for f in gj["features"]]
keys=[ALIAS.get(norm(f["properties"]["name"]),norm(f["properties"]["name"])) for f in gj["features"]]
dm={r["k"]:r for _,r in d.iterrows()}
O=np.array([float(dm[k]["muertes"]) for k in keys]); P=np.array([float(dm[k]["nacidos_vivos"]) for k in keys])
neigh={i:[j for j,g in enumerate(geoms) if j!=i and geoms[i].buffer(0.004).intersects(g)] for i in range(len(geoms))}
w=W(neigh,id_order=list(range(len(geoms)))); w.transform="r"
rate=O/P*1e5; eb=Empirical_Bayes(O,P).r*1e5; seb=Spatial_Empirical_Bayes(O,P,w).r*1e5
mi=Moran(eb,w,permutations=999)
lisa=Moran_Local(eb,w,permutations=999,seed=42); q=lisa.q; sig=lisa.p_sim<0.05
lab={1:"Alto-Alto",2:"Bajo-Alto",3:"Bajo-Bajo",4:"Alto-Bajo"}
clus=[lab[q[i]] if sig[i] else "No significativo" for i in range(len(keys))]
tab=pd.DataFrame({"cod_municipio":[dm[k]["cod_municipio"] for k in keys],"municipio":[dm[k]["municipio"] for k in keys],
 "subregion":[dm[k]["subregion"] for k in keys],"muertes_tempranas":O.astype(int),"nacidos_vivos":P.astype(int),
 "RMM_cruda":np.round(rate,1),"RMM_EB_espacial":np.round(np.asarray(seb).ravel(),1),"LISA":clus})
tab=tab.sort_values("RMM_EB_espacial",ascending=False)
tab.to_csv("Tabla_RMM_temprana_municipal_Cordoba.csv",index=False,encoding="utf-8-sig")
print("RMM Cordoba (temprana, periodo):",round(O.sum()/P.sum()*1e5,1),"| Moran I(EB)=",round(mi.I,3),"p=",round(mi.p_sim,3))

# ECOLOGICO con IPM
ipm=pd.read_pickle("_ipm.pkl"); ipm.columns=["cod_municipio","IPM"]
e=tab.merge(ipm,on="cod_municipio",how="left"); e["IPM"]=pd.to_numeric(e["IPM"],errors="coerce")
rho,pv=stats.spearmanr(e["IPM"],e["RMM_EB_espacial"])
e2=e[e["nacidos_vivos"]>0]
X=sm.add_constant(pd.DataFrame({"IPM10":e2["IPM"]/10})); off=np.log(e2["nacidos_vivos"].values)
nb=sm.GLM(e2["muertes_tempranas"],X,family=sm.families.NegativeBinomial(alpha=1.0),offset=off).fit()
irr=np.exp(nb.params["IPM10"]); ci=np.exp(nb.conf_int().loc["IPM10"])
print(f"Ecologico (temprana): Spearman IPM~RMM_EB={rho:.3f} p={pv:.3f} | IRR/10IPM={irr:.2f} ({ci[0]:.2f}-{ci[1]:.2f}) p={nb.pvalues['IPM10']:.3f}")
e.to_pickle("_eco_temprana.pkl")

# ---- MAPAS ----
def centroid(r):
    x=np.array([p[0] for p in r]);y=np.array([p[1] for p in r]);x1=np.roll(x,-1);y1=np.roll(y,-1);cr=x*y1-x1*y;A=cr.sum()/2
    return (x.mean(),y.mean()) if abs(A)<1e-9 else (((x+x1)*cr).sum()/(6*A),((y+y1)*cr).sum()/(6*A))
def rings_of(g): return [g["coordinates"][0]] if g["type"]=="Polygon" else [p[0] for p in g["coordinates"]]
AZUL="#1F4E79"; COSL=1/np.cos(np.radians(8.5))
val={r["k"] if "k" in r else norm(r["municipio"]):r for _,r in tab.assign(k=tab["municipio"].map(norm)).iterrows()}
feats=[]
for f in gj["features"]:
    k=ALIAS.get(norm(f["properties"]["name"]),norm(f["properties"]["name"])); rec=val.get(k)
    rings=rings_of(f["geometry"]); big=max(rings,key=lambda r:abs(sum(r[i][0]*r[(i+1)%len(r)][1]-r[(i+1)%len(r)][0]*r[i][1] for i in range(len(r)))))
    cx,cy=centroid(big)
    feats.append({"name":f["properties"]["name"],"rings":rings,"cx":cx,"cy":cy,
        "eb":float(rec["RMM_EB_espacial"]),"cruda":float(rec["RMM_cruda"]),"lisa":str(rec["LISA"])})
xs=[p[0] for f in feats for r in f["rings"] for p in r]; ys=[p[1] for f in feats for r in f["rings"] for p in r]
def choro(field,titulo,sub,cmap_name,fname,fmt="{:.0f}"):
    vals=np.array([f[field] for f in feats]); nz=Normalize(np.nanmin(vals),np.nanmax(vals)); cmap=matplotlib.colormaps[cmap_name]
    fig,ax=plt.subplots(figsize=(9.2,10.4)); pts=[];cols=[]
    for f in feats:
        c=cmap(nz(f[field]))
        for r in f["rings"]: pts.append(MplPoly(r,closed=True)); cols.append(c)
    ax.add_collection(PatchCollection(pts,facecolor=cols,edgecolor="white",linewidths=0.7,zorder=2))
    for f in feats:
        t=ax.text(f["cx"],f["cy"],short(f["name"]),ha="center",va="center",fontsize=5.9,color="#15202b",zorder=5);t.set_path_effects([pe.withStroke(linewidth=1.6,foreground="white")])
        t2=ax.text(f["cx"],f["cy"]-0.035,fmt.format(f[field]),ha="center",va="center",fontsize=6.4,color="#6a0a0a",fontweight="bold",zorder=5);t2.set_path_effects([pe.withStroke(linewidth=1.6,foreground="white")])
    ax.set_xlim(min(xs)-0.05,max(xs)+0.05); ax.set_ylim(min(ys)-0.05,max(ys)+0.05); ax.set_aspect(COSL); ax.axis("off")
    sm2=matplotlib.cm.ScalarMappable(norm=nz,cmap=cmap); sm2.set_array([]); cb=fig.colorbar(sm2,ax=ax,fraction=0.035,pad=0.01,shrink=0.6); cb.set_label("RMM (x100.000 NV)",fontsize=9)
    fig.suptitle(titulo,x=0.06,y=0.965,ha="left",fontsize=14.5,fontweight="bold",color=AZUL)
    ax.set_title(sub,loc="left",fontsize=9.5,color="#595959",pad=8)
    fig.text(0.06,0.045,"Muerte materna temprana (DANE registro, CIE-10 capítulo O excl. O96-O97). Denom: nacidos vivos DANE. Elab.: Naudith C.",fontsize=7.0,color="#888888")
    fig.subplots_adjust(top=0.9,bottom=0.07,left=0.03,right=0.99); fig.savefig(fname,dpi=170); plt.close(fig); print("guardado",fname)
choro("cruda","Razón de mortalidad materna por municipio (definición oficial)","Muertes maternas tempranas por 100.000 NV, Córdoba 2015-2024","YlOrRd","Coropletico_RMM_temprana_Cordoba.png")
choro("eb","RMM suavizada por bayes empírico espacial (definición oficial)","Estimación estabilizada de áreas pequeñas, Córdoba 2015-2024","YlOrRd","Coropletico_RMMsuavizada_temprana_Cordoba.png")
# LISA
COL={"Alto-Alto":"#c0392b","Bajo-Bajo":"#2c7fb8","Alto-Bajo":"#f39c12","Bajo-Alto":"#9ecae1","No significativo":"#eeeeee"}
fig,ax=plt.subplots(figsize=(9.2,10.4)); pts=[];cols=[]
for f in feats:
    for r in f["rings"]: pts.append(MplPoly(r,closed=True)); cols.append(COL.get(f["lisa"],"#eee"))
ax.add_collection(PatchCollection(pts,facecolor=cols,edgecolor="white",linewidths=0.7,zorder=2))
for f in feats:
    t=ax.text(f["cx"],f["cy"],short(f["name"]),ha="center",va="center",fontsize=5.9,color="#15202b",zorder=5);t.set_path_effects([pe.withStroke(linewidth=1.6,foreground="white")])
ax.set_xlim(min(xs)-0.05,max(xs)+0.05); ax.set_ylim(min(ys)-0.05,max(ys)+0.05); ax.set_aspect(COSL); ax.axis("off")
ax.legend(handles=[Patch(facecolor=COL[k],edgecolor="white",label=k) for k in COL],loc="lower left",fontsize=8,frameon=False,title="Conglomerado LISA (p<0,05)",title_fontsize=8.5)
fig.suptitle("Conglomerados locales de mortalidad materna (LISA, def. oficial)",x=0.06,y=0.965,ha="left",fontsize=14,fontweight="bold",color=AZUL)
ax.set_title(f"Moran I global = {mi.I:.2f} (p={mi.p_sim:.2f}). Córdoba 2015-2024",loc="left",fontsize=9.5,color="#595959",pad=8)
fig.subplots_adjust(top=0.9,bottom=0.07,left=0.03,right=0.99); fig.savefig("Coropletico_LISA_temprana_Cordoba.png",dpi=170); plt.close(fig); print("guardado LISA")
