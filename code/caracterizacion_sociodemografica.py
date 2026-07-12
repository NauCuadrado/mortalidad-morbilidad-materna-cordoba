# -*- coding: utf-8 -*-
# Caracterizacion sociodemografica y obstetrica basica agregada de los casos
# notificados de morbilidad materna extrema (evento 549) y muerte materna (evento 550).
# Produce data/Caracterizacion_sociodemografica_MME_MM.csv (Tabla 1 del manuscrito).
#
# Requiere la base individual de vigilancia SIVIGILA (no incluida en este repositorio
# por proteccion de datos; disponible por solicitud al autor de correspondencia).
import pandas as pd

# Ruta a la base primaria de SIVIGILA (ajustar segun el entorno local)
SRC = "Base_analitica_con_perfil_SIVIGILA_Cordoba.csv"

df = pd.read_csv(SRC)
MME = df[df.evento == "Morbilidad materna extrema"]
MM  = df[df.evento == "Mortalidad materna"]
nM, nD = len(MME), len(MM)

def npct(sub, var, cat):
    a = int((sub[var] == cat).sum())
    return a, round(a / len(sub) * 100, 1)

filas = []
q1, q3 = MME.edad.quantile([.25, .75]); filas.append(("Edad mediana (RIC)", f"{MME.edad.median():.0f} ({q1:.0f}-{q3:.0f})", "", f"{MM.edad.median():.0f} ({MM.edad.quantile(.25):.0f}-{MM.edad.quantile(.75):.0f})", ""))
for var, cats in [
    ("grupo_edad", ["10-14","15-19","20-24","25-29","30-34","35-39","40-44","45+"]),
    ("regimen", ["Subsidiado","Contributivo","No asegurado","Excepcion","Especial","Indeterminado"]),
    ("area_residencia", ["Cabecera","Centro poblado","Rural disperso"]),
    ("subregion", ["Medio Sinu","San Jorge","Sabanas","Alto Sinu","Costanera","Bajo Sinu","Sin asignar"]),
    ("pertenencia_etnica", ["Otro/Ninguno","Indigena","Negro/Mulato/Afrocolombiano","ROM/Gitano","Raizal","Palenquero"]),
]:
    for c in cats:
        aM, pM = npct(MME, var, c); aD, pD = npct(MM, var, c)
        filas.append((f"{var}: {c}", aM, pM, aD, pD))
for var in ["gestante", "hospitalizada"]:
    aM, pM = npct(MME, var, "Si"); aD, pD = npct(MM, var, "Si")
    filas.append((f"{var} (Si)", aM, pM, aD, pD))

out = pd.DataFrame(filas, columns=["caracteristica", f"MME_evento549_n", "MME_pct", f"MM_evento550_n", "MM_pct"])
out.to_csv("Caracterizacion_sociodemografica_MME_MM.csv", index=False, encoding="utf-8-sig")
print(f"OK: MME n={nM}, MM n={nD}, filas={len(out)}")
