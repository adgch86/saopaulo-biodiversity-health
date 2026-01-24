# Historial de Sesiones - Science Team

> Este archivo contiene el registro detallado de todas las sesiones de trabajo.
> Para contexto actual del proyecto: 

---

## Notas de Sesión

### 2026-01-23 (Sesión 18 - Validación de Datos de Salud) - ✅ COMPLETADO

#### Solicitud
Adrian solicitó validar los datos de salud comparando con datos descargados manualmente por Ju desde TABNET/DATASUS para el mismo periodo (2010-2019).

#### Resultados de Validación

| Enfermedad | Correlación | Total Ju | Total Procesado | Ratio | Estado |
|------------|-------------|----------|-----------------|-------|--------|
| **Dengue** | **1.0000** | 2,221,035 | 2,221,108 | 1.0x | ✅ VALIDADO |
| **Diarrhea** | **1.0000** | 139,187 | 139,207 | 1.0x | ✅ VALIDADO |
| Leptospirose | 0.9674 | 7,253 | 44,806 | 6.2x | ⚠️ Criterio diferente |
| Malaria | 0.7909 | 1,403 | 3,400 | 2.4x | ⚠️ Criterio diferente |
| Leishmaniasis | 0.7566 | 2,609 | 8,082 | 3.1x | ⚠️ Criterio diferente |

#### Conclusiones

**VALIDADOS (r > 0.99):**
- **Dengue**: Prácticamente idénticos (73 casos de diferencia en 2.2M)
- **Diarrhea**: Prácticamente idénticos (20 casos de diferencia en 139K)
- Los índices calculados para estas enfermedades son **confiables**

**DISCREPANCIAS SISTEMÁTICAS:**

Las diferencias en leptospirose, malaria y leishmaniasis son **sistemáticas** (ratio constante), indicando criterios de clasificación diferentes:

- **Hipótesis**: Ju descargó casos **CONFIRMADOS** (laboratorio), nosotros usamos **PROVÁVEIS** (confirmados + en investigación)
- Leptospirose: ratio 6.2x (confirmación laboratorial difícil)
- Malaria: ratio 2.4x (muchos casos sin confirmación en área no endémica)
- Leishmaniasis: Ju probablemente solo descargó Visceral (2,609 ≈ 4,611/1.77)

**Verificación pendiente**: Preguntar a Ju qué criterio usó en TABNET

#### Scripts Creados

| Script | Descripción |
|--------|-------------|
| `scripts/compare_health_data_ju.py` | Comparación inicial por enfermedad |
| `scripts/compare_health_data_ju_v2.py` | Comparación detallada con leishmaniasis combinada |

---

### 2026-01-23 (Sesión 17 - Indicadores de Diarrea + Dataset v8) - ✅ COMPLETADO

#### Solicitud
Adrian identificó que las inundaciones (variable ya presente en el dataset) contribuyen a la contaminación del agua, lo que puede resultar en aumento de casos de diarrea y gastroenteritis. Solicitó procesar datos de hospitalizaciones por diarrea (CID-10 Capítulo A00-A09) para calcular indicadores epidemiológicos.

#### Datos Procesados

**Fuente**: `health_sp_Ju.csv` (DATASUS SIH/SUS)
- 645 municipios de São Paulo
- Periodo: 2010-2019
- Columna: `diarrhea` (hospitalizaciones)

#### Indicadores de Diarrea Calculados (4 variables)

| Variable | Descripción | Media | Max |
|----------|-------------|-------|-----|
| `incidence_diarrhea_mean` | Incidencia media (por 100,000 hab) | 67.4 | 1,520 |
| `incidence_diarrhea_max` | Incidencia máxima anual | 151.8 | 2,632 |
| `total_cases_diarrhea` | Casos totales 2010-2019 | 216 | 4,424 |
| `persist_diarrhea` | Persistencia (años con casos, 0-10) | 8.0 | 10 |

#### Hallazgos Clave

**Distribución:**
- **139,207** hospitalizaciones totales por diarrea (2010-2019)
- 643 municipios con al menos un caso (99.7%)
- **319 municipios** (49%) tienen diarrea presente los 10 años (persistencia = 10)
- Solo 2 municipios sin ningún caso

**Persistencia por número de años:**
- 0 años: 2 municipios
- 1-5 años: 126 municipios
- 6-9 años: 198 municipios
- 10 años: **319 municipios** (casi la mitad)

**Top 10 municipios mayor incidencia:**

| Municipio | Incidencia Media | Casos Totales | Persistencia |
|-----------|------------------|---------------|--------------|
| Herculândia | 1,520 | 1,400 | 10 |
| Aparecida d'Oeste | 1,094 | 480 | 10 |
| Monte Azul Paulista | 954 | 1,820 | 10 |
| Bastos | 909 | 1,890 | 10 |
| Parapuã | 714 | 783 | 10 |
| General Salgado | 537 | 580 | 10 |
| Cardoso | 533 | 641 | 10 |
| Cajobi | 505 | 514 | 10 |
| Flórida Paulista | 497 | 683 | 10 |
| Rinópolis | 434 | 434 | 10 |

#### Dataset Integrado v8 Creado

**Dimensiones**: 645 municipios × 104 variables (+4 respecto a v7)

**Variables por categoría:**
- Identificación: 2 variables
- Demografía: 9 variables
- UAI (Adaptación): 5 variables
- Biodiversidad: 6 variables
- Clima/Riesgo: 7 variables
- Enfermedades vectoriales: 18 variables
- **Diarrea (NUEVO)**: 4 variables
- Fuego: 12 variables
- Salud-Calor: 18 variables

**Archivos generados:**

| Archivo | Descripción |
|---------|-------------|
| `data/processed/diarrhea_indicators_SP_2010_2019.csv` | Indicadores diarrea por municipio |
| `data/processed/diarrhea_annual_SP_2010_2019.csv` | Datos anuales de diarrea |
| `outputs/municipios_integrado_v8.csv` | Dataset integrado completo |

#### Scripts Creados

| Script | Descripción |
|--------|-------------|
| `scripts/calculate_diarrhea_indicators.py` | Cálculo de indicadores de diarrea |
| `scripts/create_integrated_dataset_v8.py` | Integración dataset v8 |

#### Implicaciones para el Análisis

1. **Nexo inundación-diarrea** listo para analizar: correlacionar `flooding_exposure`/`flooding_risks` con `incidence_diarrhea_*`
2. **Persistencia alta** (49% con 10 años) sugiere problema endémico, no solo epidémico
3. **Patrón geográfico**: Municipios del interior/noroeste con mayor incidencia
4. **Vulnerabilidad social**: Analizar si `pct_pobreza` amplifica el efecto inundación→diarrea

---

### 2026-01-23 (Sesión 16 - Indicadores de Fuego + Dataset v7) - ✅ COMPLETADO

#### Solicitud
Adrian compartió datos de focos de quemadas del INPE BDQueimadas (2010-2019) y solicitó calcular indicadores de riesgo de fuego para caracterizar cada municipio.

#### Datos Procesados

**Fuente**: INPE BDQueimadas (terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas)
- 10 archivos CSV anuales (2010-2019)
- 36,006 focos de calor en São Paulo
- 100% matching de municipios (todos los nombres mapeados a código IBGE)

#### Indicadores de Fuego Calculados (12 variables)

| Variable | Descripción | Media | Max |
|----------|-------------|-------|-----|
| `fire_incidence_mean` | Focos promedio por año | 6.27 | 51.70 |
| `fire_incidence_max` | Máximo focos en un año | 14.76 | 132 |
| `fire_frp_mean` | Intensidad media (FRP MW) | 38.56 | 180.92 |
| `fire_frp_max` | Intensidad máxima (FRP MW) | 346.75 | 3661.50 |
| `fire_total_foci` | Total focos 2010-2019 | - | - |
| `fire_frp_total` | FRP acumulado total | - | - |
| `fire_years_with_fire` | Años con al menos un foco | - | - |
| `fire_recurrence` | Proporción años con fuego (0-1) | 0.76 | 1.0 |
| `fire_cv` | Coeficiente variación interanual | 0.68 | - |
| `fire_dry_season_pct` | % focos en estación seca (jun-oct) | 79.2% | - |
| `fire_max_consecutive_years` | Máx años consecutivos con fuego | 5.9 | 10 |
| `fire_risk_index` | Índice compuesto de riesgo (0-100) | 33.97 | 84.15 |

**Índice de Riesgo Compuesto**: Combina frecuencia (40%) + intensidad (30%) + recurrencia (30%)

#### Hallazgos Clave

**Distribución espacial:**
- 637 municipios (98.8%) tienen focos de fuego
- Solo 8 municipios sin ningún foco en 10 años
- 79.2% de los focos ocurren en estación seca (jun-oct)

**Top 10 municipios mayor riesgo de fuego:**

| Municipio | Fire Risk Index | Total Focos | FRP Mean |
|-----------|-----------------|-------------|----------|
| Morro Agudo | 84.2 | 517 | 85.4 MW |
| Ituverava | 74.7 | 367 | 98.2 MW |
| Barretos | 71.9 | 376 | 77.0 MW |
| Guaíra | 71.4 | 299 | 110.5 MW |
| São Joaquim da Barra | 68.8 | 213 | 141.9 MW |
| Araraquara | 67.9 | 337 | 71.4 MW |
| Andradina | 62.6 | 179 | 113.3 MW |
| Ipuã | 62.4 | 201 | 101.9 MW |
| Araçatuba | 62.1 | 220 | 91.0 MW |
| Guará | 61.9 | 208 | 95.4 MW |

**Patrón geográfico**: Región norte de SP (área de caña de azúcar/Cerrado) concentra mayor riesgo.

#### Dataset Integrado v7 Creado

**Dimensiones**: 645 municipios × 100 variables (+30 respecto a v6)

**Nuevas variables agregadas:**
- 12 indicadores de fuego (`fire_*`)
- 18 indicadores de salud-calor (`health_*`)

**Archivos generados:**

| Archivo | Descripción |
|---------|-------------|
| `data/processed/fire_indicators_SP_2010_2019.csv` | Indicadores fuego por municipio |
| `data/processed/fire_annual_SP_2010_2019.csv` | Datos anuales de focos |
| `outputs/municipios_integrado_v7.csv` | Dataset integrado completo |

#### Scripts Creados

| Script | Descripción |
|--------|-------------|
| `scripts/calculate_fire_indicators.py` | Cálculo de indicadores de fuego |
| `scripts/create_integrated_dataset_v7.py` | Integración dataset v7 |

#### Implicaciones para el Análisis

1. **Fire risk index** listo para correlacionar con vulnerabilidad socioeconómica
2. **Estacionalidad** (79% en seca) permite planificación de intervenciones
3. **FRP** como proxy de intensidad/emisiones de carbono
4. **Recurrencia** identifica municipios con problema crónico vs esporádico

---

### 2026-01-23 (Sesión 15 - Datos SIH/SIM para Impactos del Calor) - ✅ COMPLETADO

#### Solicitud
Adrian solicitó datos de DATASUS sobre hospitalizaciones y óbitos relacionados con efectos del calor para los 645 municipios de São Paulo (2010-2019). Específicamente:
- Doenças do aparelho circulatório (CID-10: I00-I99)
- Doenças do aparelho respiratório (CID-10: J00-J99)
- Efeitos do calor e da luz (CID-10: T67.0-T67.9)

#### Datos Descargados

**SIH (Sistema de Informações Hospitalares):**
- 120 archivos mensuales (2010-2019)
- ~1.8 GB de datos
- Ubicación: `data/raw/datasus/sih/`

**SIM (Sistema de Informação sobre Mortalidade):**
- 10 archivos anuales (2010-2019)
- ~226 MB de datos
- Ubicación: `data/raw/datasus/sim/`

#### Totales São Paulo (2010-2019)

| Categoría CID-10 | Hospitalizaciones | Óbitos |
|------------------|-------------------|--------|
| Circulatorias (I00-I99) | 2,671,894 | 844,306 |
| Respiratorias (J00-J99) | 2,391,281 | 379,214 |
| Efectos del calor (T67) | 31 | 0 |

#### Incidencias Promedio (por 100,000 hab)

| Variable | Valor |
|----------|-------|
| Hosp. Circulatorias media | 826.0 |
| Hosp. Respiratorias media | 815.4 |
| Hosp. Calor media | 0.02 |
| Óbit. Circulatorias media | 200.3 |
| Óbit. Respiratorias media | 96.6 |

#### Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `data/processed/health_heat_annual_SP_2010_2019.csv` | Datos anuales (6,450 registros) |
| `data/processed/health_heat_indicators_SP_2010_2019.csv` | Indicadores por municipio (645) |

#### Variables en Dataset Final

- `inc_hosp_circ_media/max` - Incidencia hospitalizaciones circulatorias
- `inc_hosp_resp_media/max` - Incidencia hospitalizaciones respiratorias
- `inc_hosp_calor_media/max` - Incidencia hospitalizaciones por calor
- `inc_obit_circ_media/max` - Incidencia óbitos circulatorios
- `inc_obit_resp_media/max` - Incidencia óbitos respiratorios
- `inc_obit_calor_media/max` - Incidencia óbitos por calor

#### Scripts Creados

| Script | Descripción |
|--------|-------------|
| `scripts/download_sih_sim_datasus.py` | Descarga FTP de archivos DBC |
| `scripts/process_sih_sim_data.R` | Procesamiento inicial de DBC |
| `scripts/calculate_heat_health_indicators.R` | Cálculo de indicadores finales |

#### Hallazgo Importante

Los casos directos de efectos del calor (T67) son **extremadamente raros** en São Paulo (solo 31 hospitalizaciones y 0 óbitos en 10 años). El impacto del calor se manifiesta principalmente de forma **indirecta** a través de exacerbación de enfermedades circulatorias y respiratorias.

---

### 2026-01-23 (Sesión 14 - Mapas de Calor Workshop SEMIL-USP) - ✅ COMPLETADO

#### Solicitud
Adrian organizará un **workshop de 3 días** con SEMIL (Secretaría de Medio Ambiente) y USP sobre uso de evidencia en políticas de adaptación climática (PEARC). Solicitó mapas de calor interactivos de los municipios de São Paulo.

#### Mapas Generados

**6 mapas HTML interactivos** con todos los 645 municipios de São Paulo:

| # | Mapa | Variable | Escala | Descripción |
|---|------|----------|--------|-------------|
| 1 | `01_riesgo_inundacion.html` | flooding_risks | Verde→Rojo | Índice de riesgo inundación |
| 2 | `02_riqueza_vertebrados.html` | mean_species_richness | Rojo→Verde | Biodiversidad de vertebrados |
| 3 | `03_vulnerabilidad_social.html` | pct_pobreza | Verde→Rojo | % población en pobreza |
| 4 | `04_incidencia_dengue.html` | incidence_mean_dengue | Verde→Rojo | Casos/100k hab/año |
| 5 | `05_gobernanza_UAI.html` | UAI_Crisk | Rojo→Verde | Capacidad gestión riesgo |
| 6 | `06_deficit_polinizacion.html` | pol_deficit | Verde→Rojo | Pérdida servicio ecosistémico |

**Características**:
- Zoom, arrastre, tooltips interactivos
- 645 municipios de São Paulo (shapefile IBGE 2022 completo)
- Título y leyenda de colores en cada mapa
- Tamaño: ~30 MB por HTML

#### Imágenes PNG

Se exportaron capturas PNG (1920x1080) de cada mapa para presentaciones:
- `png/01_riesgo_inundacion.png` (~0.75 MB)
- `png/02_riqueza_vertebrados.png`
- `png/03_vulnerabilidad_social.png`
- `png/04_incidencia_dengue.png`
- `png/05_gobernanza_UAI.png`
- `png/06_deficit_polinizacion.png`

#### Ubicación de Archivos

```
G:\My Drive\Adrian David\Forthe_worshop\mapas_workshop\
├── 01_riesgo_inundacion.html
├── 02_riqueza_vertebrados.html
├── 03_vulnerabilidad_social.html
├── 04_incidencia_dengue.html
├── 05_gobernanza_UAI.html
├── 06_deficit_polinizacion.html
├── README.md                  # Guía de interpretación
└── png/
    ├── 01_riesgo_inundacion.png
    ├── 02_riqueza_vertebrados.png
    ├── 03_vulnerabilidad_social.png
    ├── 04_incidencia_dengue.png
    ├── 05_gobernanza_UAI.png
    └── 06_deficit_polinizacion.png
```

#### Scripts Creados

| Script | Descripción |
|--------|-------------|
| `scripts/create_workshop_maps.py` | Generador de mapas choropleth con folium |
| `scripts/export_maps_to_png.py` | Exportador de HTML a PNG con Selenium |

#### Datos Utilizados

- **Shapefile**: `data/geo/ibge_sp/SP_Municipios_2022.shp` (descargado del IBGE, 645 municipios)
- **Datos**: `outputs/municipios_integrado_v6.csv` (645 municipios × 70 variables)
- **Merge**: Por código IBGE (6 dígitos)

#### Dinámicas Sugeridas para el Workshop

1. **"Layering the Crisis"**: Superponer capas de riesgo climático + biodiversidad + vulnerabilidad
2. **"Hotspots"**: Identificar municipios donde 3+ factores coinciden
3. **"Policy Stories"**: Cada grupo selecciona un municipio "hotspot" para proponer intervención

---

### 2026-01-22 (Sesión 13 - Actualización Masiva de Papers y Fichas) - ✅ COMPLETADO

#### Solicitud
Adrian agregó nuevos papers al sistema y solicitó revisión y actualización de la información.

#### Papers Nuevos Identificados

El script `watch_papers_daily.py` convirtió 10 nuevos PDFs a Markdown. Total biblioteca: **75 papers** (antes 65).

#### Fichas Detalladas Creadas (13 nuevas, total ahora: 25)

**Papers Propios de Adrian (2 nuevas):**
1. `GonzalezChaves2024_tree_traits_bees_FunctionalEcol.md` - Rasgos de árboles predicen diversidad de abejas
2. `GonzalezChaves2021_forest_coffee_yields_JApplEcol.md` - Cobertura forestal y rendimiento café (610 municipios)

**Base Metodológica y Supervisores (2 nuevas):**
3. `Neder2021_UAI_urban_adaptation_index.md` - **UAI - BASE del análisis** (645 municipios SP)
4. (DiGiulio2018 ya existía - actualizada)

**Brasil/PEAC (3 nuevas):**
5. `PEARC2024_consulta_publica_SP.md` - Plan Estadual Adaptación SP
6. `Oliveira2025_smallholder_pollination_vulnerability.md` - Vulnerabilidad polinización por bioma

**Ciencia-Política (2 nuevas):**
7. `Hjort2020_research_affects_policy_Brazil.md` - Experimento 2,150 municipios brasileños
8. `Tao2025_inequality_air_pollution_mortality.md` - Desigualdad mortalidad contaminación

**Salud Ambiental (5 nuevas - sesión anterior):**
9. `Mahendran2026_wildfire_dengue_brazil.md` - Incendios + dengue
10. `Requia2025_PM_O3_heat_brazil.md` - PM2.5/O3 × calor
11. `Liu2019_PM_mortality_652cities_NEJM.md` - PM mortalidad global
12. `Pan2025_precipitation_diarrhea_multicountry.md` - Precipitación + diarrea
13. `LancetCountdown2023_Brasil.md` - Cambio climático y salud

#### Hallazgos Clave de Papers Nuevos

| Paper | Hallazgo Principal | Aplicación al Proyecto |
|-------|-------------------|------------------------|
| **González-Chaves 2021** | Cobertura forestal >20% = máximo rendimiento café | Umbral aplicable a salud? |
| **Neder 2021 (UAI)** | >50% municipios SP con UAI bajo | Confirma nuestra brecha de gobernanza |
| **Oliveira 2025** | 96.8% municipios vulnerables a pérdida polinizadores | Mata Atlántica alta prioridad |
| **Hjort 2020** | +10 pp implementación cuando alcaldes reciben evidencia | Base para estrategia comunicación |
| **Tao 2025** | Patrones de desigualdad difieren entre/dentro países | Justicia ambiental compleja |
| **Mahendran 2026** | +10.5% hospitalizaciones dengue por PM2.5 incendios | Nuevo mecanismo biodiversidad-salud |

#### Implicaciones para el Proyecto

1. **Papers propios de Adrian**: Metodología de análisis municipal (610 municipios Mata Atlántica) transferible
2. **UAI documentado**: Neder 2021 es referencia definitiva para nuestra variable de gobernanza
3. **PEARC como target**: Documento de consulta pública = oportunidad de contribuir
4. **Ciencia-política**: Hjort 2020 demuestra que alcaldes brasileños usan evidencia (+10 pp)
5. **Justicia ambiental**: Patrones complejos requieren análisis diferenciado

#### Estadísticas Finales

- **Biblioteca total**: 75 papers convertidos a Markdown
- **Fichas detalladas**: 25 papers con análisis completo
- **Cobertura**: 33% de la biblioteca tiene ficha detallada
- **Priorización**: Papers propios, supervisores, Brasil, y ciencia-política cubiertos

#### Archivos Actualizados

- `SCIENCE_TEAM_CONTEXT.md` - Tabla de papers actualizada, conceptos clave añadidos

---

### 2026-01-21 (Sesión 12 - Análisis Completo Hipótesis + Variables Vulnerabilidad) - ✅ COMPLETADO

#### Marco Conceptual Refinado

Adrian definió un marco analítico estructurado para explorar el nexo con todas las variables:

**Agrupación de variables:**
- **Y (dependiente)**: Riesgo/vulnerabilidad ambiental
  - SALUD: 9 variables (persistencia e incidencia de 4 enfermedades + co-presencia)
  - CLIMA: 2 variables (riesgo inundaciones, estrés hídrico)
  - NUTRICIÓN: 1 variable (déficit polinización)
- **X1 (Gobernanza)**: 6 variables (UAI_housing, UAI_env, UAI_food, UAI_mob, UAI_Crisk, idx_gobernanza)
- **X2 (Biodiversidad)**: 4 variables (riqueza sp. media/máx, cobertura forestal, idx_biodiv)
- **Z (Modulador)**: 5 variables (pct_rural, pct_pobreza, pct_preta, pct_indigena, idx_vulnerabilidad)

**Hipótesis probadas:**
- H1: Mayor gobernanza → menor riesgo ambiental (especialmente en baja vulnerabilidad)
- H2: Mayor biodiversidad → menor riesgo ambiental (especialmente en baja vulnerabilidad)

#### Hallazgos Principales del Análisis v4

**1. EFECTOS PROTECTORES CONFIRMADOS (r < 0, p < 0.05):**

| Predictor | Reduce | Correlación |
|-----------|--------|-------------|
| **Cobertura Forestal** | Déficit Polinización | **r = -0.77*** |
| Riqueza Sp. Máxima | Déficit Polinización | r = -0.59*** |
| Biodiversidad | Incidencia Dengue | **r = -0.44*** |
| Biodiversidad | Incidencia Leishmaniosis | **r = -0.49*** |
| Cobertura Forestal | Incidencia Dengue | r = -0.45*** |

**2. DISTINCIÓN CLAVE: INCIDENCIA vs PERSISTENCIA**

| Variable | Efecto de Biodiversidad | Interpretación Ecológica |
|----------|------------------------|--------------------------|
| **Incidencia** (casos/100k) | REDUCE (r=-0.44***) | Efecto dilución - menos transmisión |
| **Persistencia** (años) | AUMENTA (r=+0.43***) | Reservorio - patógeno se mantiene |

**3. MODELOS MIXTOS (ICC = 40%)**
- El 40% de la varianza está explicada por la microregión
- Los modelos mixtos son **NECESARIOS** para inferencia válida
- La estructura espacial (63 microregiones) es fundamental

**4. CORRELACIONES TOP 10 (por magnitud):**

| # | Predictor | Efecto | Riesgo | r |
|---|-----------|--------|--------|---|
| 1 | Cobertura Forestal | REDUCE | Déficit Polinización | -0.77*** |
| 2 | UAI Movilidad | AUMENTA | Persist. Leptospirosis | +0.65*** |
| 3 | UAI Movilidad | AUMENTA | Años Co-presencia | +0.61*** |
| 4 | UAI General | AUMENTA | Años Co-presencia | +0.59*** |
| 5 | Riqueza Sp. Máxima | REDUCE | Déficit Polinización | -0.59*** |
| 6 | UAI General | AUMENTA | Persist. Leptospirosis | +0.58*** |
| 7 | Biodiversidad | REDUCE | Déficit Polinización | -0.57*** |
| 8 | UAI Movilidad | AUMENTA | Persist. Malaria | +0.52*** |
| 9 | Riqueza Sp. Máxima | AUMENTA | Persist. Leptospirosis | +0.52*** |
| 10 | Biodiversidad | REDUCE | Incidencia Leishmaniosis | -0.49*** |

#### Comparación de Variables de Vulnerabilidad Social

**Correlaciones con el Índice Compuesto:**

| Variable | r con Índice | Contribución |
|----------|--------------|--------------|
| % Pobreza | +0.75 | ALTA (domina el índice) |
| % Rural | +0.65 | ALTA |
| % Pob. Negra | +0.16 | BAJA |
| % Pob. Indígena | -0.07 | CASI NULA |

**HALLAZGO CLAVE: % Población Negra es MEJOR modulador que el Índice Compuesto**

| Ranking | Variable | Poder Modulación |
|---------|----------|------------------|
| **1** | **% Pob. Negra** | **0.189** |
| 2 | % Pob. Indígena | 0.173 |
| 3 | % Rural | 0.143 |
| 4 | % Pobreza | 0.128 |
| 5 | Índice Compuesto | 0.110 |

**Interpretación:**
- El índice compuesto está dominado por pobreza + ruralidad
- % Pob. Negra captura una dimensión de **vulnerabilidad urbana** diferente
- % Pob. Negra tiene correlación NEGATIVA con % Rural (r=-0.42): población negra concentrada en áreas urbanas
- Los beneficios de conservación (cobertura forestal) son **MAYORES en municipios con bajo % Pob. Negra**
- Esto sugiere **desigualdades raciales en el acceso a servicios ecosistémicos**

**Efecto modulador específico de % Pob. Negra:**

| Relación | % Pob. Negra Bajo | % Pob. Negra Alto | Diferencia |
|----------|-------------------|-------------------|------------|
| Cobertura Forestal → Persist. Dengue | **-0.32** (protege) | +0.12 (no protege) | 0.44 |
| Biodiversidad → Persist. Dengue | **-0.19** (protege) | +0.16 (no protege) | 0.35 |
| Cobertura Forestal → Incid. Dengue | **-0.64** (protege) | -0.35 (menos) | 0.29 |

#### Scripts Creados

| Archivo | Descripción |
|---------|-------------|
| `scripts/analisis_hipotesis_v2.py` | Análisis con modelos mixtos (ICC) |
| `scripts/analisis_hipotesis_v3_gaps.py` | Identificación de gaps de gobernanza |
| `scripts/analisis_completo_hipotesis_v4.py` | Análisis exhaustivo 120 combinaciones |
| `scripts/comparar_variables_vulnerabilidad.py` | Comparación moduladores |

#### Archivos Generados

**Datos:**
- `outputs/correlaciones_completas_v4.csv` - 120 combinaciones de variables
- `outputs/modelos_mixtos_v4.csv` - Resultados OLS vs Mixto con ICC
- `outputs/mejores_predictores_v4.csv` - Top predictores por tipo riesgo
- `outputs/comparacion_moduladores_vuln.csv` - Poder modulador por variable

**Figuras:**
- `outputs/figures/correlaciones_completas_v4.png` - Heatmap 3 paneles (Salud, Clima, Nutrición)
- `outputs/figures/mejores_predictores_v4.png` - Regresiones 6 paneles
- `outputs/figures/efecto_estratificado_v4.png` - Barras por vulnerabilidad
- `outputs/figures/correlaciones_vulnerabilidad.png` - Matriz correlaciones vuln.
- `outputs/figures/comparacion_moduladores.png` - Ranking moduladores
- `outputs/figures/mejor_modulador_detalle.png` - Top 3 efectos % Pob. Negra

#### Gráficos con DOS Moduladores

Se generaron gráficos de regresión idénticos usando dos moduladores diferentes:
1. **% Población Negra** (mejor modulador, captura vulnerabilidad urbana)
2. **Índice Compuesto** (dominado por pobreza r=0.75, captura vulnerabilidad rural)

**Terciles de cada modulador:**

| Modulador | Bajo/Baja | Medio/Media | Alto/Alta |
|-----------|-----------|-------------|-----------|
| % Pob. Negra | 3.2% | 4.8% | 7.2% |
| Idx Vulnerabilidad | 10.1 | 16.0 | 26.5 |

**Comparación de correlaciones estratificadas:**

| Relación | % Pob. Negra (Bajo→Alto) | Idx Vuln (Baja→Alta) |
|----------|--------------------------|----------------------|
| Biodiversidad → Carga Enferm. | **-0.60 → -0.28*** | -0.46 → -0.44*** |
| UAI Movilidad → Riesgo Clima | +0.23 → +0.49*** | +0.24 → +0.14* |
| UAI Riesgo Clim → Déficit Polin | -0.12 → -0.26*** | -0.25 → -0.25*** |
| Cobertura Forestal → Déficit Polin | -0.75 → -0.78*** | -0.71 → -0.80*** |

**Hallazgos de la comparación:**
1. **% Pob. Negra** tiene mayor gradiente para Biodiversidad → Carga Enfermedad
2. **Idx Vulnerabilidad** tiene mayor gradiente para Cobertura Forestal → Déficit Polinización
3. Capturan **dimensiones diferentes**: urbana/racial vs rural/pobreza

**Archivos generados:**
- `outputs/figures/regresion_modulador_pct_negra.png`
- `outputs/figures/regresion_modulador_idx_vuln.png`
- `outputs/figures/comparacion_dos_moduladores.png`
- `outputs/correlaciones_dos_moduladores.csv`

**Script creado:**
- `scripts/graficos_dos_moduladores.py`

#### Implicaciones para Política Pública

1. **Conservación forestal** tiene efecto protector muy fuerte para déficit de polinización (r=-0.77***)
2. **Biodiversidad** reduce incidencia de enfermedades (efecto dilución confirmado)
3. **Desigualdades raciales**: Los beneficios ecosistémicos llegan menos a municipios con mayor % población negra
4. **Modelos mixtos necesarios**: La estructura regional explica 40% de la varianza
5. **Usar AMBOS moduladores** en publicaciones: capturan dimensiones complementarias de vulnerabilidad

---

### 2026-01-21 (Sesión 11 - Dataset Integrado v6 + Metadata Trilingüe) - ✅ COMPLETADO

#### Solicitud
Adrian solicitó crear un dataset integrado con los 645 municipios (en lugar de los 187 del análisis anterior) y actualizar la metadata con descripciones en 3 idiomas (español, portugués, inglés).

#### Dataset Integrado v6 Creado

**Archivos generados:**
- `outputs/municipios_integrado_v6.csv` - Dataset principal (645 municipios × 70 columnas)
- `data/metadata_v6.json` - Metadata trilingüe completa

**Contenido del dataset v6:**

| Categoría | Variables | Cobertura |
|-----------|-----------|-----------|
| ID (identificación) | 6 | 100% |
| VULNERABILITY (socio-económica) | 14 | 100% |
| GOVERNANCE (UAI) | 5+2 índices | 100% |
| BIODIVERSITY | 5+1 índice | 100% |
| CLIMATE | 4+1 índice | 100% |
| HEALTH | 25 | 100% |
| INDEX (derivados) | 6 | 100% |
| CLASSIFICATION | 5 | 100% |

**Mejoras respecto a v5:**
1. **645 municipios** (antes 187) - cobertura completa de São Paulo
2. **Datos de salud actualizados**: casos prováveis (filtro CLASSI_FIN != 5)
3. **4 enfermedades**: Dengue, Leishmaniose (visceral+tegumentar), Leptospirose, Malaria
4. **Variables de región**: cod/nome_microrregiao, cod/nome_mesorregiao (63 micro, 15 meso)
5. **Metadata trilingüe**: ES, PT, EN para todas las 70 variables

**Distribución de cuadrantes (n=645):**
- Q1_Modelo: 212 (32.9%)
- Q2_Conservar: 110 (17.1%)
- Q3_Vulnerable: 210 (32.6%) ← Prioridad
- Q4_Desarrollo: 113 (17.5%)

**Scripts creados:**
- `scripts/create_integrated_dataset_v6.py` - Integración de datasets

---

### 2026-01-21 (Sesión 10 - Análisis de Hipótesis + Automatización Papers) - ✅ COMPLETADO

#### Marco Conceptual para Análisis de Hipótesis

Adrian definió un marco analítico estructurado para explorar el nexo:

**Agrupación de variables:**
- **Y (dependiente)**: Riesgo/vulnerabilidad ambiental (salud, clima, polinización)
- **X1**: Gobernanza (UAI)
- **X2**: Biodiversidad
- **Z (modulador)**: Vulnerabilidad socio-económica (rural, pobreza, raza)

**Hipótesis originales:**
- H1: Mayor gobernanza → menor riesgo ambiental, especialmente en baja vulnerabilidad
- H2: Mayor biodiversidad → menor riesgo ambiental, especialmente en baja vulnerabilidad

#### Hallazgos del Análisis de Hipótesis

**1. PARADOJA DE LA GOBERNANZA**
- Gobernanza REDUCE riesgo de salud: **r = -0.45***
- Pero AUMENTA riesgo climático: **r = +0.44***
- Interpretación: Ciudades urbanizadas tienen mejor salud pero más exposición a inundaciones

**2. ROL PROTECTOR DE BIODIVERSIDAD**
- Reduce riesgo de salud: **r = -0.53***
- Reduce déficit polinización: **r = -0.66*** (muy fuerte)
- Pero áreas biodiversas tienen más eventos climáticos: **r = +0.34***

**3. EFECTO COMPENSATORIO (Hallazgo clave)**
- **Contrario a la hipótesis inicial**: El efecto protector de gobernanza es MÁS FUERTE en municipios con ALTA vulnerabilidad
- Gobernanza vs Riesgo Salud por vulnerabilidad:
  - Baja vulnerabilidad: r = -0.29
  - Alta vulnerabilidad: **r = -0.61***
- La gobernanza "compensa" la vulnerabilidad social

**4. Confirmación: Incidencia SÍ considera población**
- Las variables de incidencia (`incidence_dengue`, etc.) son tasas por 100,000 habitantes
- El `idx_carga_enfermedad` se basa en estas tasas normalizadas

#### Archivos generados - Análisis de Hipótesis

| Archivo | Descripción |
|---------|-------------|
| `scripts/analisis_hipotesis_gobernanza_biodiv.py` | Script principal de análisis |
| `scripts/visualizaciones_hipotesis_detalle.py` | Visualizaciones detalladas |
| `outputs/figures/heatmap_riesgo_factores.png` | Heatmap correlaciones |
| `outputs/figures/hipotesis_gobernanza_biodiv.png` | Regresiones con modulador |
| `outputs/figures/sintesis_efecto_diferencial.png` | Efecto por vulnerabilidad |
| `outputs/figures/regresion_componentes_detalle.png` | Detalle por componente |
| `outputs/correlaciones_estratificadas.csv` | Tabla correlaciones por grupo |
| `outputs/resumen_hipotesis_hallazgos.txt` | Resumen interpretativo |
| `outputs/analisis_hipotesis_data.csv` | Dataset con índices compuestos |

#### Automatización de Conversión de Papers

Adrian tiene papers en `G:\My Drive\Adrian David\Papers`. Se creó sistema automático de conversión diaria.

**Scripts creados:**
- `scripts/watch_papers_daily.py` - Detecta PDFs nuevos y los convierte a Markdown
- `scripts/run_watch_papers.bat` - Archivo batch para ejecutar
- `scripts/setup_scheduled_task.ps1` - Configura tarea programada

**Tarea programada en Windows:**
- Nombre: "Watch Papers Daily - Science Team"
- Frecuencia: Diaria a las 8:00 AM
- Estado: ✅ Configurada y activa
- Logs: `C:\Users\arlex\Documents\Adrian David\logs\papers_conversion_YYYYMM.log`

**Estado actual de papers:**
- Total PDFs: 68
- Ya convertidos: 65
- Pendientes: 3 (incluyendo Statistical Rethinking - libro grande)

---

### 2026-01-21 (Sesión 9 - Reprocesamiento TODAS las enfermedades) - ✅ COMPLETADO

#### Solicitud
Adrian identificó que el problema de extracción de datos de Dengue probablemente afectaba también a las otras enfermedades. Solicitó extraer "casos prováveis" (excluyendo descartados) para todas las enfermedades por municipio de residencia y año de notificación.

#### Problemas identificados en el script original (`process_dbc_files.R`)

1. **Columna de municipio incorrecta**: Usaba `ID_MUNICIP` (municipio de notificación) en lugar de `ID_MN_RESI` (municipio de residencia)
2. **Falta de filtro CLASSI_FIN**: No excluía casos descartados (`CLASSI_FIN = 5`)

#### Solución implementada

Nuevo script: `scripts/process_all_diseases_casos_provaveis.R`
- Usa `ID_MN_RESI` (municipio de residencia) ✓
- Aplica filtro `CLASSI_FIN != 5` (excluye descartados) ✓
- Excluye código 350000 (MUNICIPIO IGNORADO) ✓
- Procesa las 5 enfermedades: Dengue, Leptospirose, Malaria, Leish. Visceral, Leish. Tegumentar

#### Resultado: Casos Prováveis por Enfermedad (2010-2019)

| Enfermedad | Casos Prováveis (nuevo) | Total original | Reducción |
|------------|------------------------|----------------|-----------|
| Dengue | 2,221,108 | 3,807,950 | -42% |
| Leptospirose | 44,806 | 61,617 | -27% |
| Malaria | 3,400 | 5,421 | -37% |
| Leish. Visceral | 4,611 | 6,581 | -30% |
| Leish. Tegumentar | 3,471 | 4,528 | -23% |

#### Hallazgo clave por enfermedad

| Enfermedad | CLASSI_FIN = 5 | Reducción por columna |
|------------|----------------|----------------------|
| **Dengue** | 27-89% excluidos | Mínima |
| Leptospirose | 0% (no tiene) | ~1% (ID_MN_RESI vs ID_MUNICIP) |
| Malaria | 0% (no tiene) | 5-10% |
| Leish. Visceral | 0% (no tiene) | 3-5% |
| Leish. Tegumentar | 0% (no tiene) | 1-3% |

**Conclusión**: El filtro `CLASSI_FIN != 5` solo afecta significativamente a Dengue. Las otras enfermedades no tienen casos descartados en SINAN-SP, pero la corrección de columna de municipio (residencia vs notificación) sí impacta los números.

#### Archivo generado
- `data/processed/health_casos_provaveis_SP_2010_2019.csv`
  - **645 municipios** × 10 años × 5 enfermedades
  - **51 columnas**: cod_ibge + 10 columnas por enfermedad (prefijo_año)
  - Formato: `deng_2010`, `lept_2015`, `mala_2019`, etc.
  - Filtros aplicados: CLASSI_FIN != 5, ID_MN_RESI, excluye 350000

#### Scripts creados
- `scripts/process_all_diseases_casos_provaveis.R` - Procesamiento completo
- `scripts/compare_old_new_health.py` - Comparación antes/después
- `scripts/check_column_usage.R` - Verificación de columnas DBC

#### Adición de Micro y Mesorregiões do IBGE

Descargados de la API do IBGE (`servicodados.ibge.gov.br`) y agregados al dataset de salud.

**15 Mesorregiões de São Paulo:**
| Código | Nome | Municípios |
|--------|------|------------|
| 3501 | São José do Rio Preto | 109 |
| 3502 | Ribeirão Preto | 66 |
| 3503 | Araçatuba | 36 |
| 3504 | Bauru | 56 |
| 3505 | Araraquara | 21 |
| 3506 | Piracicaba | 26 |
| 3507 | Campinas | 49 |
| 3508 | Presidente Prudente | 54 |
| 3509 | Marília | 20 |
| 3510 | Assis | 35 |
| 3511 | Itapetininga | 36 |
| 3512 | Macro Metropolitana Paulista | 36 |
| 3513 | Vale do Paraíba Paulista | 39 |
| 3514 | Litoral Sul Paulista | 17 |
| 3515 | Metropolitana de São Paulo | 45 |

**63 Microrregiões**: Listadas en el script `download_ibge_regioes.py`

#### Archivos finales generados
- `data/processed/health_casos_provaveis_SP_2010_2019_regioes.csv`
  - **645 municipios** × 56 columnas
  - Incluye: cod_ibge, nome_municipio, cod/nome_microrregiao, cod/nome_mesorregiao + datos de salud
  - **100% match** con datos IBGE
- `data/processed/municipios_regioes_SP.csv` - Tabla de referencia IBGE
- `scripts/download_ibge_regioes.py` - Script de descarga y merge

#### Git commit
- Commit: `54a21d7` - "Add health data with IBGE regions and fix disease extraction"
- Push: ✅ Completado a `origin/master`

#### Cálculo de Indicadores de Salud (Incidencia, Persistencia, Co-presencia)

Inspirado en `scripts/health_variables.R` de Julia. Se creó script para calcular indicadores epidemiológicos.

**4 enfermedades analizadas** (Leishmaniose = Visceral + Tegumentar combinadas):
- Dengue
- Leptospirose
- Malaria
- Leishmaniose

**Indicadores calculados:**

| Indicador | Variables | Descripción |
|-----------|-----------|-------------|
| Persistencia | persist_X | Años con casos (0-10) |
| Incidencia Media | incidence_mean_X | Casos/100,000 hab promedio |
| Incidencia Máxima | incidence_max_X | Pico máximo en un año |
| Casos Totales | total_cases_X | Suma 2010-2019 |
| Co-presencia 2+ | copresence_years | Años con 2+ enfermedades |
| Co-presencia 3+ | copresence_3plus | Años con 3+ enfermedades |
| Co-presencia 4 | copresence_all4 | Años con todas las 4 |
| Pares | dengue_leptospirose, etc. | 6 pares de enfermedades |

**Resultados clave:**

| Indicador | Valor |
|-----------|-------|
| Municipios con 2+ enfermedades algún año | **96.7%** (624/645) |
| Persistencia media dengue | 8.9 años |
| Persistencia media leptospirose | 5.3 años |
| Persistencia media leishmaniose | 3.8 años |
| Persistencia media malaria | 1.4 años |
| Par más frecuente | dengue + leptospirose (5.0 años) |

**Archivos generados:**
- `data/processed/health_indicators_SP_2010_2019.csv` - 645 municipios × 31 columnas
- `data/processed/populacao_SP_2010_2019.csv` - Población IBGE 2010-2019

**Scripts creados:**
- `scripts/calculate_health_indicators.R` - Cálculo de indicadores
- `scripts/download_ibge_populacao.py` - Descarga población SIDRA API

**Git commit:**
- Commit: `19bcddb` - "Add health indicators: incidence, persistence and co-presence"
- Push: ✅ Completado a `origin/master`

---

### 2026-01-20 (Sesión 8 - Validación DATASUS vs Datos Adrian) - ✅ RESUELTO

#### Datos recibidos de Adrian
- **URL compartida**: `http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguesp.def`
- **Archivo CSV**: `data/raw/sinannet_cnv_denguebsp213738186_212_98_169_paraArlex.csv`
- **Período**: 2014-2016
- **Contenido**: "Casos Prováveis por Município de residência e Ano notificação"

#### ✅ HALLAZGO CLAVE: Diferencia entre "Casos Prováveis" y "Total Notificaciones"

**TABNET (Adrian) usa "Casos Prováveis"**:
- Definición: "Todas notificações, exceto casos descartados"
- Filtro implícito: Excluye CLASSI_FIN = 5 (Descartado) en versión 2014+
- Uso epidemiológico: Vigilancia de casos probables/confirmados

**Nuestros DBC usan "Total Notificaciones"**:
- Sin filtro: Incluye todas las notificaciones
- Incluye: Confirmados + En investigación + Descartados
- Uso: Conteo bruto de notificaciones

#### Comparación Totales Estatales 2014-2016

| Año  | TABNET (Adrian) | DBC (Nuestros) | Diferencia | % Descartados |
|------|-----------------|----------------|------------|---------------|
| 2014 | 226,939         | 385,116        | -158,177   | 41%           |
| 2015 | 749,791         | 1,033,070      | -283,279   | 27%           |
| 2016 | 203,229         | 465,567        | -262,338   | 56%           |

#### Comparación Municipios Específicos (2015)

| Municipio    | TABNET | DBC Total | DBC Confirmados | Interpretación |
|--------------|--------|-----------|-----------------|----------------|
| DIADEMA      | 3,996  | 6,953     | 5,720           | TABNET < Total |
| CRAVINHOS    | 144    | 207       | 192             | TABNET < Total |
| COTIA        | 2,191  | 3,680     | 3,429           | TABNET < Total |

#### ✅ Conclusión
- **Los datos de Adrian son CORRECTOS** para análisis epidemiológico
- TABNET excluye casos descartados (no confirmados por laboratorio)
- Para nuestro análisis, **usar los datos de TABNET de Adrian**
- Archivo procesado: `outputs/tabnet_casos_provaveis_adrian.csv` (644 municipios)

#### ✅ Solución: Reprocesar DBC con filtro CLASSI_FIN

**Pregunta**: ¿Nuestra base de datos puede excluir casos descartados?
**Respuesta**: ¡SÍ! Los archivos DBC tienen la variable `CLASSI_FIN`.

**Filtro aplicado**: `CLASSI_FIN != 5` (excluir descartados)

**Validación con datos de Adrian**:
| Año | Nuestro DBC (filtrado) | TABNET Adrian | Diferencia |
|-----|------------------------|---------------|------------|
| 2014 | 227,591 | 226,939 | +0.29% |
| 2015 | 750,304 | 749,791 | +0.07% |
| 2016 | 203,519 | 203,229 | +0.14% |

**Conclusión**: Diferencias < 0.3% - Los datos son equivalentes.

#### Nuevo archivo generado
- `data/processed/dengue_casos_provaveis_SP_2010_2019.csv`
  - **644 municipios** × 10 años (2010-2019)
  - Filtro: Casos Prováveis (excluye descartados)
  - Limpiado: eliminados código 350000 (MUNICIPIO IGNORADO) y NaN
  - Comparable con TABNET oficial (644 municipios también)
  - Nota: 1 municipio de SP no tuvo casos de dengue en el período

#### Scripts creados
- `scripts/comparar_tabnet_adrian.py` - Comparación TABNET vs DBC
- `scripts/process_dbc_casos_provaveis.R` - Reprocesamiento con filtro CLASSI_FIN

### 2026-01-20 (Sesión 7 - Conversión Papers PDF a Markdown) - COMPLETADA
- **Solicitud**: Crear script para convertir PDFs de papers a Markdown
- **Script creado**: `scripts/convert_papers_to_md.py`
- **Dependencias**: `pip install pymupdf pymupdf4llm`
- **Directorio entrada**: `G:\My Drive\Adrian David\Papers\` (65 PDFs)
- **Directorio salida**: `G:\My Drive\Adrian David\Papers\markdown\` (65 convertidos ✅)
- **Índice generado**: `_INDEX.md` con tabla de todos los papers
- **Catálogo creado**: Biblioteca completa categorizada en SCIENCE_TEAM_CONTEXT.md
  - 4 papers propios de Adrian
  - 4 papers de supervisores (Di Giulio, Metzger)
  - 11 categorías temáticas: Nexo, Justicia Ambiental, Ciencia-Política, Confianza, Polinización, Clima, Brasil, Transformación, Monitoreo, Metodología, Ciudades
- **Características del script**:
  - `--file "nombre"` - Convertir archivo específico
  - `--skip-existing` - Saltar ya convertidos
  - `--basic` - Método rápido para archivos grandes
  - Detecta automáticamente archivos >10MB y usa método básico

### 2026-01-20 (Sesión 6 - DATASUS Health Data) - COMPLETADA
- **Solicitud**: Adrian necesita datos de DATASUS para completar análisis de salud
- **R instalado**: R 4.5.2 + Rtools 4.5 + tidyverse + read.dbc
- **50 archivos DBC descargados** del FTP de DATASUS (~680 MB)
- **Dataset generado**: `data/processed/health_data_SP_2010_2019.csv`
- **Cobertura final**: 647 municipios x 10 años = 6,963 registros
- **Casos totales en SP (2010-2019)**:
  - Dengue: 3,807,952
  - Leptospirose: 61,617
  - Malaria: 5,421
  - Leishmaniose Visceral: 6,581
  - Leishmaniose Tegumentar: 4,528
- **Scripts creados**:
  - `scripts/download_datasus_direct.py` - Descarga FTP
  - `scripts/process_dbc_files.R` - Procesamiento DBC
- **Documentación**: `docs/GUIA_DESCARGA_DATASUS.md`
- **Nota**: Diarrea (DDA) NO disponible en SINAN (usar SIH/SIVEP-DDA)

### 2026-01-19 (Sesión 5 - Implementación FAIR completa)
- **FAIR implementado**: 13 archivos nuevos creados
- **Archivos creados**:
  - `LICENSE` (MIT)
  - `CITATION.cff` (con ORCID y DOI)
  - `CHANGELOG.md`, `PROVENANCE.md`, `LIMITATIONS.md`
  - `DATA_ACCESS.md`, `REUSE_GUIDE.md`
  - `data/SOURCES.md`, `data/metadata.json`, `data/schema.json`, `data/vocabulary_mapping.json`
  - `docs/METHODOLOGY_IVM.md`
- **README.md actualizado** con badges FAIR, DOI, sección de cumplimiento
- **GitHub publicado**: https://github.com/adgch86/saopaulo-biodiversity-health
- **DOI Zenodo creado**: 10.5281/zenodo.18303824
- **Score FAIR**: 5.5/10 → 9/10
- **Pendiente**: Registrar en OSF (instrucciones guardadas arriba)

### 2026-01-19 (Sesión 4 - Enlaces y Proyectos de Referencia)
- **Solicitud**: Adrian compartió enlace a documento de Google Drive para guardar referencias
- **Documento de enlaces**: https://docs.google.com/document/d/1mSuS8ZQsusjvjUhV6CqF--IfIXKVsCvQXrJl_zRl6yA/edit
- **Proyectos ITV identificados**:
  1. **DatalakeDS** (ITV, Belém) - Plataforma FAIR integrando biodiversidad, clima, uso de suelo, socioeconomía
  2. **Plataforma Socioambiental Bahías** (ITV, São Luís) - Datos físicos + biológicos + sociales costeros
- **Investigadora clave identificada**: Dra. Tereza Giannini (ITV) - experta en modelado de polinizadores
- **Actualización**: Agregada sección "Proyectos de Referencia" a REFERENTES_CIENTIFICOS.md
- **Estructura Google Drive**: Confirmada estructura en `G:\My Drive\Adrian David\` con subcarpetas organizadas

### 2026-01-16 (Sesión 3 - Referentes Científicos)
- **Audio transcrito**: WhatsApp Ptt 2026-01-16 at 09.39.55.ogg
- **Solicitud**: Adrian quiere que el Science Team tenga como referentes a investigadores clave
- **Investigadores identificados**: 10 perfiles completos creados
- **Documento creado**: `.claude/REFERENTES_CIENTIFICOS.md`
- **Script Whisper mejorado**: `scripts/transcribe_audio.py` actualizado para uso futuro
- **Gabriela di Giulio identificada como supervisora/jefa** - su UAI es base del análisis

### 2026-01-16 (Sesión 2 - Prototipo Dashboard)
- **Transcripción de audios**: Instalado Whisper + ffmpeg para transcribir notas de voz
- **Workshop febrero**: Adrian necesita prototipo de herramienta para presentar
- **Dashboard generado**: 5 visualizaciones interactivas creadas:
  1. `01_dashboard_cuadrantes.html/png` - Clasificación municipal gobernanza vs vulnerabilidad
  2. `02_nexo_correlaciones.html/png` - Matriz de correlaciones + efecto dilución
  3. `03_municipios_prioritarios.html/png` - Top 15 municipios Q3 con mayor brecha
  4. `04_recomendaciones_peac.html/png` - Matriz de acciones PEAC por perfil
  5. `05_resumen_ejecutivo.html/png` - KPIs principales del estado
- **Ubicación**: `outputs/dashboard_mockups/`
- **Lista prioritarios**: `municipios_prioritarios_top20.csv`

### 2026-01-16 (Sesión 1)
- Creado sistema de contexto persistente para Science Team
- Archivo SCIENCE_TEAM_CONTEXT.md inicializado con datos del proyecto

### 2026-01-15 (sesión anterior)
- Creada propuesta Branco Weiss
- Generadas Figure 1 y Figure 2
- Corregidas referencias (Mooren → Monden)
- Documento listo para revisión final

---

