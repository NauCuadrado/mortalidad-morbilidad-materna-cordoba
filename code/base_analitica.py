# -*- coding: utf-8 -*-
import pandas as pd, numpy as np
raw=pd.read_pickle("_svi_raw.pkl")

MUN={"001":"Monteria","068":"Ayapel","079":"Buenavista","090":"Canalete","162":"Cerete",
"168":"Chima","182":"Chinu","189":"Cienaga de Oro","300":"Cotorra","350":"La Apartada",
"417":"Lorica","419":"Los Cordobas","464":"Momil","466":"Montelibano","500":"Moñitos",
"555":"Planeta Rica","570":"Pueblo Nuevo","574":"Puerto Escondido","580":"Puerto Libertador",
"586":"Purisima","660":"Sahagun","670":"San Andres de Sotavento","672":"San Antero",
"675":"San Bernardo del Viento","678":"San Carlos","682":"San Jose de Ure","686":"San Pelayo",
"807":"Tierralta","815":"Tuchin","855":"Valencia"}
SUB={"Tierralta":"Alto Sinu","Valencia":"Alto Sinu",
"Monteria":"Medio Sinu","Cerete":"Medio Sinu","San Pelayo":"Medio Sinu","Cienaga de Oro":"Medio Sinu","San Carlos":"Medio Sinu",
"Lorica":"Bajo Sinu","Cotorra":"Bajo Sinu","Momil":"Bajo Sinu","Purisima":"Bajo Sinu","Chima":"Bajo Sinu",
"Montelibano":"San Jorge","Puerto Libertador":"San Jorge","La Apartada":"San Jorge","Buenavista":"San Jorge",
"Planeta Rica":"San Jorge","Ayapel":"San Jorge","Pueblo Nuevo":"San Jorge","San Jose de Ure":"San Jorge",
"Sahagun":"Sabanas","Chinu":"Sabanas","San Andres de Sotavento":"Sabanas","Tuchin":"Sabanas",
"Moñitos":"Costanera","Puerto Escondido":"Costanera","Los Cordobas":"Costanera","Canalete":"Costanera",
"San Antero":"Costanera","San Bernardo del Viento":"Costanera"}
REG={'C':'Contributivo','S':'Subsidiado','P':'Excepcion','E':'Especial','N':'No asegurado','I':'Indeterminado'}
ETN={'1':'Indigena','2':'ROM/Gitano','3':'Raizal','4':'Palenquero','5':'Negro/Mulato/Afrocolombiano','6':'Otro/Ninguno'}
AREA={'1':'Cabecera','2':'Centro poblado','3':'Rural disperso'}
SN={'1':'Si','2':'No'}

def s(x): return ("" if pd.isna(x) else str(x).strip())
def numv(x):
    try: return int(float(str(x).strip()))
    except: return np.nan

d=pd.DataFrame()
d["id_caso"]=range(1,len(raw)+1)
d["anio"]=raw["anio_archivo"].astype(int)
d["semana"]=raw["SEMANA"].map(numv)
d["evento"]=raw["grupo_evento"].map({"MME":"Morbilidad materna extrema","MORTALIDAD":"Mortalidad materna"})
d["desenlace_fallecio"]=(raw["grupo_evento"]=="MORTALIDAD").astype(int)
d["edad"]=raw["EDAD"].map(numv)
d["pertenencia_etnica"]=raw["PER_ETN"].map(lambda x:ETN.get(s(x),s(x)))
d["regimen"]=raw["TIP_SS"].map(lambda x:REG.get(s(x),s(x)))
d["area_residencia"]=raw["AREA"].map(lambda x:AREA.get(s(x),s(x)))
d["gestante"]=raw["GP_GESTAN"].map(lambda x:SN.get(s(x),s(x)))
d["semanas_gestacion"]=raw["sem_ges"].map(numv)
d["hospitalizada"]=raw["PAC_HOS"].map(lambda x:SN.get(s(x),s(x)))
d["cod_municipio"]=raw["COD_MUN_R"].map(lambda x:"23"+s(x).zfill(3) if s(x) else "")
d["municipio"]=raw["COD_MUN_R"].map(lambda x:MUN.get(s(x).zfill(3),"Otro/Sin dato"))
d["subregion"]=d["municipio"].map(lambda m:SUB.get(m,"Sin asignar"))
# referencia (no predictora)
d["causa_cie10_ref"]=raw["CBMTE"].map(s)   # solo en fallecidas; NO usar como predictora
d["grupo_edad"]=pd.cut(d["edad"],bins=[9,14,19,24,29,34,39,44,60],
    labels=["10-14","15-19","20-24","25-29","30-34","35-39","40-44","45+"])

PRED=["edad","grupo_edad","pertenencia_etnica","regimen","area_residencia","gestante",
"semanas_gestacion","hospitalizada","municipio","subregion","anio","semana"]
print("BASE:",len(d),"| desenlace=1:",int(d["desenlace_fallecio"].sum()),
      f"({d['desenlace_fallecio'].mean()*100:.2f}%)")
print("Predictoras:",PRED)
d.to_pickle("_base.pkl")
d.to_csv("Base_analitica_SIVIGILA_Cordoba_2015-2024.csv",index=False,encoding="utf-8-sig")

# agregado municipal (para mapas)
g=d.groupby(["cod_municipio","municipio","subregion"]).agg(
    casos_total=("id_caso","count"),
    mme=("desenlace_fallecio",lambda x:(x==0).sum()),
    muertes=("desenlace_fallecio","sum")).reset_index()
g["letalidad_pct"]=(g["muertes"]/g["casos_total"]*100).round(2)
g=g.sort_values("casos_total",ascending=False)
g.to_csv("Agregado_municipal_SIVIGILA_Cordoba.csv",index=False,encoding="utf-8-sig")
g.to_pickle("_agg_mun.pkl")
print("\nAgregado municipal (top):")
print(g.head(8).to_string(index=False))
print("\nMunicipios con mayor letalidad:")
print(g[g["casos_total"]>=20].sort_values("letalidad_pct",ascending=False).head(6)[["municipio","casos_total","muertes","letalidad_pct"]].to_string(index=False))
