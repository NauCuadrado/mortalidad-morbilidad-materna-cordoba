# -*- coding: utf-8 -*-
import csv, os, datetime
import pandas as pd

BASE = "/sessions/upbeat-modest-turing/mnt/outputs/dane"
FILES = {
    2015: f"{BASE}/e2015/nofetal2015.csv",
    2016: f"{BASE}/e2016/nofetal2016.csv",
    2017: f"{BASE}/e2017/nofetal2017.csv",
    2018: f"{BASE}/e2018/nofetal2018.csv",
    2019: f"{BASE}/e2019/nofetal2019.csv",
    2020: f"{BASE}/e2020b/nofetal2020.csv",
    2021: f"{BASE}/e2021/nofetal2021.csv",
    2022: f"{BASE}/e2022/nofetal2022.csv",
    2023: f"{BASE}/eevv2023/BD-EEVV-Defuncionesnofetales-2023.csv",
    2024: f"{BASE}/e2024/BD-EEVV-Defuncionesnofetales-2024.csv",
}

# DIVIPOLA municipios de Cordoba (codigo de 3 digitos -> nombre)
MUN = {
 "001":"Monteria","068":"Ayapel","079":"Buenavista","090":"Canalete","162":"Cerete",
 "168":"Chima","182":"Chinu","189":"Cienaga de Oro","300":"Cotorra","350":"La Apartada",
 "417":"Lorica","419":"Los Cordobas","464":"Momil","466":"Montelibano","500":"Moñitos",
 "555":"Planeta Rica","570":"Pueblo Nuevo","574":"Puerto Escondido","580":"Puerto Libertador",
 "586":"Purisima","660":"Sahagun","670":"San Andres de Sotavento","672":"San Antero",
 "675":"San Bernardo del Viento","678":"San Carlos","682":"San Jose de Ure","686":"San Pelayo",
 "807":"Tierralta","815":"Tuchin","855":"Valencia",
}
SEXO = {"1":"Masculino","2":"Femenino","3":"Indeterminado"}
REG = {"1":"Contributivo","2":"Subsidiado","3":"Excepcion","4":"Especial","5":"No asegurado","9":"Sin informacion"}
ETNIA = {"1":"Indigena","2":"Rom/Gitano","3":"Raizal","4":"Palenquero","5":"Negro/Mulato/Afrocolombiano","6":"Ninguno de los anteriores","9":"Sin informacion"}
ESTCIV = {"1":"Union libre >=2 anios","2":"Union libre <2 anios","3":"Separado/Divorciado","4":"Viudo","5":"Soltero","6":"Casado","9":"Sin informacion"}
AREA = {"1":"Cabecera municipal","2":"Centro poblado","3":"Rural disperso","9":"Sin informacion"}
EMB = {"1":"Si","2":"No","9":"Sin informacion"}

def clean(v):
    return (v or "").strip()

def es_materna(cb):
    cb = cb.upper()
    return cb[:1] == "O" or cb == "A34"

def tipo_mm(cb):
    cb = cb.upper()
    if cb in ("O96","O961","O962","O969","O97","O971","O972","O979"):
        return "Materna tardia (O96-O97)"
    return "Materna temprana directa/indirecta (<=42 dias)"

CURADAS = ["anio","mes","dpto_residencia","cod_municipio_res","municipio_residencia",
           "ocurrio_en_cordoba","sexo","grupo_edad_cod","estado_civil","nivel_educ_cod",
           "regimen_seguridad_social","pertenencia_etnica","area_residencia",
           "embarazada_al_fallecer","semanas_gestacion","causa_basica_cie10","causa_agrupada_667",
           "tipo_muerte_materna","sitio_defuncion_cod","asistencia_medica"]

raw_rows = []   # todas las columnas originales
cur_rows = []   # curado y decodificado
resumen = {}

for anio, path in FILES.items():
    if not os.path.exists(path):
        print("FALTA", anio, path); continue
    with open(path, encoding="latin-1") as fh:
        r = csv.DictReader(fh)
        for row in r:
            if clean(row.get("CODPTORE")) != "23":
                continue
            cb = clean(row.get("C_BAS1"))
            if not es_materna(cb):
                continue
            if clean(row.get("SEXO")) != "2":
                continue
            # original completo + anio_archivo
            rr = dict(row); rr["ANIO_ARCHIVO"] = anio
            raw_rows.append(rr)
            munre = clean(row.get("CODMUNRE"))
            cur = {
                "anio": clean(row.get("ANO")) or anio,
                "mes": clean(row.get("MES")),
                "dpto_residencia": "Cordoba (23)",
                "cod_municipio_res": "23"+munre if munre else "",
                "municipio_residencia": MUN.get(munre, "Otro/Sin dato ("+munre+")"),
                "ocurrio_en_cordoba": "Si" if clean(row.get("COD_DPTO"))=="23" else "No (ocurrio fuera)",
                "sexo": SEXO.get(clean(row.get("SEXO")),""),
                "grupo_edad_cod": clean(row.get("GRU_ED2")),
                "estado_civil": ESTCIV.get(clean(row.get("EST_CIVIL")),clean(row.get("EST_CIVIL"))),
                "nivel_educ_cod": clean(row.get("NIVEL_EDU")),
                "regimen_seguridad_social": REG.get(clean(row.get("SEG_SOCIAL")),clean(row.get("SEG_SOCIAL"))),
                "pertenencia_etnica": ETNIA.get(clean(row.get("IDPERTET")),clean(row.get("IDPERTET"))),
                "area_residencia": AREA.get(clean(row.get("AREA_RES")),clean(row.get("AREA_RES"))),
                "embarazada_al_fallecer": EMB.get(clean(row.get("EMB_FAL")),clean(row.get("EMB_FAL"))),
                "semanas_gestacion": clean(row.get("EMB_SEM")),
                "causa_basica_cie10": cb,
                "causa_agrupada_667": clean(row.get("CAUSA_667")),
                "tipo_muerte_materna": tipo_mm(cb),
                "sitio_defuncion_cod": clean(row.get("SIT_DEFUN")),
                "asistencia_medica": clean(row.get("ASIS_MED")),
            }
            cur_rows.append(cur)
    resumen[anio] = sum(1 for c in cur_rows if str(c["anio"]) == str(anio) or c["anio"]==anio)

cur = pd.DataFrame(cur_rows, columns=CURADAS)
# normaliza anio
cur["anio"] = cur["anio"].astype(str).str[:4]
raw = pd.DataFrame(raw_rows)

# --- salidas ---
out_csv = "/sessions/upbeat-modest-turing/mnt/outputs/Mortalidad_materna_Cordoba_DANE_2015-2024.csv"
cur.to_csv(out_csv, index=False, encoding="utf-8-sig")

print("TOTAL casos:", len(cur))
print("Por anio:\n", cur["anio"].value_counts().sort_index())
print("Por tipo:\n", cur["tipo_muerte_materna"].value_counts())
print("Top municipios:\n", cur["municipio_residencia"].value_counts().head(8))
print("Temprana (estandar):", (cur["tipo_muerte_materna"].str.startswith("Materna temprana")).sum())
raw.to_pickle("/sessions/upbeat-modest-turing/mnt/outputs/_raw.pkl")
cur.to_pickle("/sessions/upbeat-modest-turing/mnt/outputs/_cur.pkl")
print("CSV ->", out_csv, "raw cols:", len(raw.columns), "raw rows:", len(raw))
