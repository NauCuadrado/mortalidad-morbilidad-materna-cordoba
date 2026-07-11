# Continuo de morbilidad materna extrema y mortalidad materna en Córdoba, Colombia, 2015-2024

Datos agregados y código de análisis para la reproducción de los resultados del estudio. Este repositorio contiene tablas de resultados agregadas y el código trazable; no incluye el manuscrito, sus versiones ni las referencias bibliográficas.

## Disponibilidad de datos

Las fuentes primarias son públicas y de acceso oficial: las estadísticas vitales del DANE (registro civil de defunciones y nacidos vivos) y los microdatos de vigilancia del SIVIGILA. Este repositorio **no redistribuye bases a nivel de registro individual**. Para evitar la reidentificación de casos raros, en especial las muertes maternas en municipios pequeños, y en concordancia con las condiciones de uso de las fuentes y con la normativa colombiana de protección de datos (Ley 1581 de 2012), solo se publican tablas agregadas y derivadas. Las bases derivadas a nivel de registro pueden solicitarse al autor de correspondencia, con fines de verificación, bajo un acuerdo de uso de datos.

## Estructura

```
data/   Tablas de resultados agregadas (CSV) y geometría municipal
code/   Scripts de Python para depuración, indicadores y modelado
```

## Datos agregados (`data/`)

- `Agregado_municipal_SIVIGILA_Cordoba.csv` — conteos municipales agregados de morbilidad materna extrema, muertes notificadas y letalidad.
- `Tabla_RMM_temprana_municipal_Cordoba.csv` — razón de mortalidad materna temprana municipal (cruda y suavizada por bayes empírico espacial) e indicador local de asociación espacial.
- `Ecologico_RMM_IPM_Cordoba.csv` — muertes tempranas, nacidos vivos, RMM municipal e índice de pobreza multidimensional (2018) para el análisis ecológico.
- `Serie_temporal_anual_Cordoba.csv` — serie anual de morbilidad, muertes, nacidos vivos, razón de morbilidad e RMM.
- `Serie_RMM_temprana_nacional_vs_Cordoba.csv` — RMM temprana anual, nacional frente a Córdoba.
- `Comparacion_nacional_vs_Cordoba_OFICIAL.csv` — indicadores agregados comparados con el nivel nacional.
- `Ranking_departamental_RMM_temprana.csv` — ranking departamental de la RMM temprana acumulada.
- `Metricas_modelo_predictivo_Cordoba.csv` — métricas de clasificación (conjuntos conservador y ampliado).
- `SHAP_importancia_Cordoba.csv` — contribuciones de Shapley del análisis de clasificación.
- `RedBayesiana_escenarios_Cordoba.csv` — probabilidades condicionales por escenario de la red bayesiana.
- `cordoba_municipios.geojson` — límites de los 30 municipios (geoportal DANE) para el análisis espacial.

El diccionario de columnas de cada tabla está en `DICCIONARIO_variables.md`.

## Figuras (`figures/`)

- `Figure_1_mortality_trend` — razón de mortalidad materna, Córdoba frente a Colombia, 2015-2024 (PDF y PNG).
- `Figure_2_EB_smoothed_map` — mapa municipal de la RMM suavizada por bayes empírico espacial (PDF y PNG).
- `Figure_S1_bayesian_network` — red bayesiana de los registros notificados.
- `Figure_S2_departmental_ranking` — ranking departamental de la RMM.
- `Figure_S3_crude_map` — mapa municipal de la RMM cruda (sin suavizar).
- `Figure_S4_poverty_scatter` — relación ecológica entre pobreza (IPM 2018) y mortalidad municipal.
- `Figure_S5_shap_leakage` — contribuciones de Shapley del modelo ampliado (fuga de información).

## Código (`code/`)

Depuración e ingesta (`process_sivigila.py`, `filtra_cordoba.py`, `dane_early_master.py`), construcción de la base (`base_analitica.py`), indicadores y comparación nacional (`recompute_cordoba.py`, `recompute_nacional.py`, `national_compare.py`, `nac_deaths_births.py`, `nac_mme.py`, `count_nac.py`, `valida_rmm.py`), análisis espacial (`espacial.py`), ecológico (`ecologico.py`), temporal (`temporal_models.py`), agrupamiento (`fenotipado_final.py`), modelo predictivo (`predictivo.py`, `predictivo_conservador.py`) y red bayesiana (`bayes_net.py`, `bn_boot_shap.py`). Los scripts que operan sobre microdatos individuales requieren las bases primarias, que no se incluyen aquí por las razones expuestas en la sección de disponibilidad de datos.

## Versión alineada con el envío a Public Health

Las fuentes se separan estrictamente por función: DANE para la mortalidad poblacional (RMM, tendencia, comparación nacional, mapas, autocorrelación espacial y asociación con pobreza) y SIVIGILA para la morbilidad materna extrema, el índice de mortalidad y la clasificación retros