# -*- coding: utf-8 -*-
import pandas as pd, os
DL="/sessions/upbeat-modest-turing/mnt/Downloads"
FILES=[("MME",549,y,f"Datos_{y}_549.xls") for y in range(2015,2023)]+\
      [("MME",549,2023,"Datos_2023_549.xlsx"),("MME",549,2024,"Datos_2024_549.xlsx")]+\
      [("MORTALIDAD",550,y,f"Datos_{y}_550.xls") for y in range(2015,2023)]+\
      [("MORTALIDAD",550,2023,"Datos_2023_550.xlsx"),("MORTALIDAD",550,2024,"Datos_2024_550.xlsx")]

KEEP=['ANO','SEMANA','COD_EVE','Nombre_evento','EDAD','UNI_MED','SEXO','PER_ETN',
'COD_DPTO_R','Departamento_residencia','COD_MUN_R','Municipio_residencia','AREA',
'TIP_SS','GP_GESTAN','sem_ges','TIP_CAS','PAC_HOS','CON_FIN','FEC_DEF','CBMTE',
'Estado_final_de_caso','nom_est_f_caso','Nom_upgd','Departamento_ocurrencia','Municipio_ocurrencia']

def dpto(v):
    try: return int(float(v))
    except: return None

mme=[]; mort=[]; raw_all=[]; log=[]
for grupo,cod,anio,fn in FILES:
    p=os.path.join(DL,fn)
    if not os.path.exists(p):
        log.append(f"{fn}: NO EXISTE"); continue
    try:
        df=pd.read_excel(p,engine="calamine",dtype=str)
    except Exception as e:
        log.append(f"{fn}: ERROR {e}"); continue
    df.columns=[str(c).strip() for c in df.columns]
    dpcol='COD_DPTO_R' if 'COD_DPTO_R' in df.columns else None
    if not dpcol:
        log.append(f"{fn}: sin COD_DPTO_R"); continue
    df['_dp']=df[dpcol].map(dpto)
    cor=df[df['_dp']==23].copy()
    cor['anio_archivo']=anio; cor['grupo_evento']=grupo
    log.append(f"{fn}: total={len(df)} cordoba={len(cor)}")
    raw_all.append(cor)
    keep=[c for c in KEEP if c in cor.columns]
    cur=cor[keep].copy(); cur['grupo_evento']=grupo; cur['anio_archivo']=anio
    (mme if grupo=="MME" else mort).append(cur)

def cat(lst): return pd.concat(lst,ignore_index=True) if lst else pd.DataFrame()
mme_df=cat(mme); mort_df=cat(mort); raw_df=cat(raw_all)
print("\n".join(log))
print("\n=== CORDOBA 10 anios ===")
print("MME:",len(mme_df))
if len(mme_df): print(mme_df.groupby('anio_archivo').size())
print("Mortalidad materna:",len(mort_df))
if len(mort_df): print(mort_df.groupby('anio_archivo').size())
mme_df.to_pickle("_svi_mme.pkl"); mort_df.to_pickle("_svi_mort.pkl"); raw_df.to_pickle("_svi_raw.pkl")
