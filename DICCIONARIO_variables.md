# Diccionario de variables

Descripción de las columnas de las tablas agregadas de `data/`. Todas las tasas usan nacidos vivos del DANE como denominador.

## `Caracterizacion_sociodemografica_MME_MM.csv`  (32 filas)

- `caracteristica` — variable sociodemográfica u obstétrica y categoría (edad, régimen, área, subregión, etnia, gestante al notificar, hospitalización).
- `MME_evento549_n` — frecuencia en los casos de morbilidad materna extrema (evento 549; total 8 716).
- `MME_pct` — porcentaje sobre los 8 716 casos de morbilidad materna extrema.
- `MM_evento550_n` — frecuencia en las muertes maternas notificadas (evento 550; total 247).
- `MM_pct` — porcentaje sobre las 247 muertes maternas notificadas.

## `Agregado_municipal_SIVIGILA_Cordoba.csv`  (31 filas)

- `cod_municipio` — Código DANE del municipio
- `municipio` — Nombre del municipio
- `subregion` — Subregión de Córdoba
- `casos_total` — Total de casos notificados
- `mme` — Casos de morbilidad materna extrema (evento 549)
- `muertes` — Muertes notificadas
- `letalidad_pct` — Letalidad (%)

## `Comparacion_nacional_vs_Cordoba_OFICIAL.csv`  (4 filas)

- `Indicador (periodo 2015-2024)` — Indicador comparado
- `Colombia` — Valor nacional
- `Córdoba` — Valor de Córdoba
- `Razón Córdoba/Colombia` — Cociente Córdoba/Colombia

## `Ecologico_RMM_IPM_Cordoba.csv`  (30 filas)

- `cod_municipio` — Código DANE del municipio
- `municipio` — Nombre del municipio
- `subregion` — Subregión de Córdoba
- `muertes_tempranas` — Muertes maternas tempranas (DANE, numerador oficial)
- `nacidos_vivos` — Nacidos vivos (DANE, denominador)
- `RMM_cruda` — Razón de mortalidad materna cruda (x100.000 NV)
- `RMM_EB_espacial` — RMM suavizada por bayes empírico espacial (x100.000 NV)
- `IPM` — Índice de pobreza multidimensional municipal (2018)

## `Metricas_modelo_predictivo_Cordoba.csv`  (4 filas)

- `AUROC` — Área bajo la curva ROC
- `AUPRC` — Área bajo la curva precisión-exhaustividad
- `Brier` — Puntaje de Brier
- `Sens` — Sensibilidad
- `Esp` — Especificidad
- `VPP` — Valor predictivo positivo
- `VPN` — Valor predictivo negativo
- `F1` — Puntaje F1
- `umbral` — Umbral de decisión
- `AUROC_IC` — IC 95% del AUROC
- `modelo` — Algoritmo
- `conjunto` — Conjunto de variables (conservador/ampliado)
- `n_var_entrada` — n_var_entrada

## `Ranking_departamental_RMM_temprana.csv`  (33 filas)

- `dpto` — Departamento (código)
- `muertes` — Muertes notificadas
- `nacidos` — Nacidos vivos
- `RMM` — RMM acumulada (x100.000 NV)
- `Departamento` — Departamento (nombre)
- `rank` — Puesto en el ranking

## `RedBayesiana_escenarios_Cordoba.csv`  (9 filas)

- `Escenario` — Escenario de la red bayesiana
- `P(Muerte) %` — Probabilidad condicional de muerte (%)

## `SHAP_importancia_Cordoba.csv`  (12 filas)

- `variable` — Variable del modelo
- `shap` — Valor de Shapley (importancia)

## `Serie_RMM_temprana_nacional_vs_Cordoba.csv`  (10 filas)

- `anio` — Año
- `RMM_nacional` — RMM nacional (x100.000 NV)
- `RMM_Cordoba` — RMM de Córdoba (x100.000 NV)

## `Serie_temporal_anual_Cordoba.csv`  (10 filas)

- `anio` — Año
- `MME` — Morbilidad materna extrema (conteo)
- `muertes` — Muertes notificadas
- `nacidos_vivos` — Nacidos vivos (DANE, denominador)
- `razon_MME_x1000NV` — Razón de morbilidad materna extrema (x1.000 NV)
- `RMM_x100kNV` — RMM (x100.000 NV)

## `Tabla_RMM_temprana_municipal_Cordoba.csv`  (30 filas)

- `cod_municipio` — Código DANE del municipio
- `municipio` — Nombre del municipio
- `subregion` — Subregión de Córdoba
- `muertes_tempranas` — Muertes maternas tempranas (DANE, numerador oficial)
- `nacidos_vivos` — Nacidos vivos (DANE, denominador)
- `RMM_cruda` — Razón de mortalidad materna cruda (x100.000 NV)
- `RMM_EB_espacial` — RMM suavizada por bayes empírico espacial (x100.000 NV)
- `LISA` — Indicador local de asociación espacial

## `cordoba_municipios.geojson`

- Geometría de los 30 municipios de Córdoba (geoportal DANE), con el código municipal para el enlace espacial.
