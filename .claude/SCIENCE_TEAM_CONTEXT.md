# Science Team - Contexto del Proyecto

> **IMPORTANTE**: Este archivo mantiene el estado ACTUAL de los proyectos.
> Para historial detallado de sesiones: `SESSION_HISTORY.md`
> Para catálogo de papers: `PAPERS_LIBRARY.md`
> Para detalles de datos/metodología: `DATA_METHODOLOGY.md`

---

## PROYECTOS ACTIVOS

| Proyecto | Estado | Prioridad | Deadline |
|----------|--------|-----------|----------|
| **Air Pollution & Pollinator Networks** | EN PROGRESO | 🔴 Alta | 06/02/2026 (tabla), Abr 2026 (final) |
| Resilient Landscapes (São Paulo) | Preparando publicación | 🟡 Media | Workshop Feb 22-26 |

---

## PROYECTO: Air Pollution & Pollinator Networks (NUEVO)

**Título**: The invisible threat: Air pollution rewires pollinator networks worldwide

**PIs**: Dr. Luisa Carvalheiro & Dr. Ruben Alarcon
**Rol Adrian**: Consultor - Extracción de datos ambientales
**Presupuesto**: $600 USD ($200/mes × 3 meses)
**Timeline**: Febrero - Abril 2026

**Ubicación**: `G:\My Drive\Adrian David\Air pollution project\`

### Contexto

El manuscrito fue rechazado de *Science* por críticas metodológicas a los datos de contaminación atmosférica:

| Problema | Enfoque Original | Solución Propuesta |
|----------|------------------|-------------------|
| Resolución vertical | TROPOMI columnas totales (mol/m²) | CAMS/EAC4 superficie (0-10m) |
| Desajuste temporal | Datos 2019-2020 para todas las redes | Extraer para fechas reales de muestreo |
| Resolución espacial | Promedios diarios | Datos cada 3 horas |
| Unidades | mol/m² (sin relevancia biológica) | ppb, μg/m³ (toxicológicamente relevantes) |

### Variables a Extraer

| Variable | Fuente | Resolución | Estado |
|----------|--------|------------|--------|
| Ozono (O3) | CAMS/EAC4 | ~80km, 3h | ⏳ Pendiente |
| NO2 | CAMS/EAC4 | ~80km, 3h | ⏳ Pendiente |
| Temperatura | ERA5 | ~30km, 1h | ⏳ Pendiente |
| Precipitación | ERA5/CHIRPS | ~30km, diario | ⏳ Pendiente |
| Human Footprint | Williams et al. 2025 | 1km | ⏳ Pendiente |

### Datos del Proyecto

- **Total redes**: 1,468
- **Regiones**: Europe (496), Africa (297), S.America (291), N.America (266), Asia (61), Oceania (57)
- **Top países**: Argentina (232), USA (195), Germany (187), Egypt (122), Spain (89)
- **Top investigadores**: Norfolk (122), Chacoff & Vazquez (107), Williams (86)

### Estructura de Carpetas

```
Air pollution project/
├── README.md
├── docs/
│   ├── Meeting_Notes_Post_Science_Rejection.docx
│   ├── proposals/
│   │   └── Proposal_Data_Extraction_v1.docx
│   └── reviews/
│       └── Science_Review_Report.pdf
├── data/
│   ├── raw/
│   │   ├── networks_metadata_original.csv
│   │   └── Networks_Sampling_Dates_ToFill.xlsx  ← ENVIAR A INVESTIGADORES
│   └── processed/
├── scripts/
│   ├── R/      (pendiente: extracción CAMS/ERA5)
│   └── python/
└── outputs/
```

### Timeline & Entregables

#### Mes 1: Febrero 2026
- [x] Crear tabla de redes para llenar fechas (`Networks_Sampling_Dates_ToFill.xlsx`)
- [x] Crear propuesta económica (`Proposal_Data_Extraction_v1.docx`)
- [x] Organizar carpeta del proyecto
- [ ] **PRÓXIMO**: Enviar propuesta + Excel a Luísa y Ruben
- [ ] Configurar cuenta Copernicus ADS
- [ ] Desarrollar script R para O3/NO2 (CAMS/EAC4)
- [ ] Test con 50 redes (fechas ficticias)

#### Mes 2: Marzo 2026
- [ ] Recibir fechas completadas de investigadores
- [ ] Integrar ERA5 para temperatura/precipitación
- [ ] Revisión literatura: métricas climáticas para polinizadores
- [ ] Extraer variables climáticas para 1,468 redes

#### Mes 3: Abril 2026
- [ ] Extraer Human Footprint Index
- [ ] Integrar todas las variables en dataset final
- [ ] Validación dual (manual vs. script vs. Claude AI)
- [ ] Entregar dataset final + documentación metodológica

### Referencias de Datos

- **CAMS/EAC4**: https://ads.atmosphere.copernicus.eu/datasets/cams-global-reanalysis-eac4
- **ERA5**: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels
- **Human Footprint**: https://wcshumanfootprint.org/
- **Williams et al. 2025**: https://doi.org/10.1038/s41597-025-05990-x

---

## PROYECTO: Resilient Landscapes (São Paulo)

**Título**: Resilient Landscapes: Integrating Planetary Health, Nexus Thinking, and Environmental Justice in São Paulo's Agrifood Systems

**Investigador Principal**: Dr. Adrian David González Chaves

**Estado**: Framework H1-H6 completado - Preparando publicación

**Dataset actual**: `outputs/municipios_integrado_v8.csv` (645 municipios × 104 variables)

---

## FRAMEWORK H1-H6: Predictores de Gobernanza (2026-01-29)

> **Inversión de lógica causal**: Riesgos/Vulnerabilidad → generan Gobernanza (sociedad reactiva)

### Resumen de Hallazgos

| Hipótesis | Modelo | Hallazgo Principal |
|-----------|--------|-------------------|
| **H1** | UAI ~ Dimensión | % Pobreza explica 27% varianza UAI_housing |
| **H2** | Gob ~ Vuln × Otras | Pobreza anula efecto reactivo de gobernanza |
| **H3** | Gob ~ Clima × Salud | Dengue × Inundación significativa (β=+0.051) |
| **H4** | Salud ~ Vuln × (Clima + Biodiv) | Bosque-dengue confundido (36%), bosque-malaria robusto |
| **H5** | Clima ~ Vuln × (Biodiv + Gob) | Pobreza predice fuego/hídrico; déficit polin. → inundación |
| **H6** | Síntesis | 104 variables → 5 dim. Nexus + 3 comp. IPCC |

### Outputs Generados

```
outputs/
├── h1_gobernanza/    (informe + 15 figs + 6 CSVs)
├── h2_vulnerabilidad/ (informe + 6 figs + 1 CSV)
├── h3_clima_salud/   (informe + 4 figs + 2 CSVs)
├── h4_salud/         (informe + 3 figs + 3 CSVs)
├── h5_clima/         (informe + 12 figs + 3 CSVs)
└── h6_sintesis/      (informe + 3 figs + 10 CSVs)
```

### Commit: `db41759` (81 archivos, +3,736 líneas)

---

## HALLAZGOS PRINCIPALES

### 1. Efecto Dilución CONFIRMADO
Ecosistemas biodiversos reducen transmisión de patógenos:

| Variable | vs Enfermedad | r | Interpretación |
|----------|---------------|---|----------------|
| Riqueza spp | Dengue | **-0.45** | Más especies = menos dengue |
| Riqueza spp | Diarrea | **-0.45** | Más especies = menos diarrea |
| Biodiversidad | Carga Enfermedad | **-0.41** | Efecto protector global |
| Cobertura forestal | Déficit Polinización | **-0.77** | Muy fuerte |

### 2. Paradoja Gobernanza-Riesgo
La gobernanza (UAI) NO reduce directamente riesgos climáticos:

| Relación | r | Interpretación |
|----------|---|----------------|
| Gobernanza → Riesgo Climático | +0.29 | NO reduce |
| Gobernanza → Riesgo Fuego | +0.19 | NO reduce |
| Gobernanza → Carga Enfermedad | -0.01 | Efecto débil |

**Explicación**: Municipios más desarrollados están en zonas de mayor exposición.

### 3. Efectos Moduladores Clave
La vulnerabilidad socioeconómica modifica las relaciones:

| Relación | Modulador | Efecto |
|----------|-----------|--------|
| Gobernanza→Clima | % Pobreza | ATENÚA (-0.36) |
| Biodiv→Enfermedades | % Pob. Negra | Amplifica (+0.32) |
| Cobertura forestal→Clima | % Pob. Indígena | Amplifica (+0.32) |

### 4. Distribución por Cuadrantes

| Cuadrante | N | Riesgo | Vulnerabilidad | Estrategia |
|-----------|---|--------|----------------|------------|
| Q1_Modelo | 212 | 0.36 | 11.0 | Mantener y expandir |
| Q2_Conservar | 110 | 0.34 | 12.5 | Fortalecer gobernanza |
| **Q3_Vulnerable** | **210** | 0.28 | **24.1** | **INTERVENCIÓN URGENTE** |
| Q4_Desarrollo | 113 | 0.31 | 22.4 | Restauración ecológica |

---

## Municipios Prioritarios (Top 5)

| Rank | Municipio | Cuadrante | Riesgo | Vulnerabilidad |
|------|-----------|-----------|--------|----------------|
| 1 | **Iporanga** | Q3_Vulnerable | 0.582 | 54.2 |
| 2 | Eldorado | Q4_Desarrollo | 0.443 | 43.0 |
| 3 | Colômbia | Q3_Vulnerable | 0.440 | 35.3 |
| 4 | Paulo de Faria | Q4_Desarrollo | 0.441 | 30.0 |
| 5 | Itaoca | Q4_Desarrollo | 0.408 | 40.2 |

---

## Datasets Actuales

| Versión | Archivo | Variables | Descripción |
|---------|---------|-----------|-------------|
| **v9** | `municipios_integrado_v9.csv` | **~112** | + Estrés térmico (Xavier + MODIS LST) |
| v8 | `municipios_integrado_v8.csv` | 104 | + Diarrea |
| v7 | `municipios_integrado_v7.csv` | 100 | + Fuego + Salud-calor |
| v6 | `municipios_integrado_v6.csv` | 70 | Base completa 645 mun |

---

## Archivos Recientes Generados

### Análisis H3 - Estrés Térmico (Sesión 22-23, actualizado Sesión 31)

**⚠️ IMPORTANTE: DATOS DE ESTRÉS TÉRMICO NO EXTRAÍDOS**

Los datos de MODIS LST **NUNCA fueron extraídos**. El dataset v8 NO contiene variables de estrés térmico real. El análisis H3 usó `fire_risk_index` como proxy inadecuado.

**Estado actual (Sesión 31, 2026-02-03):**

| Paso | Estado |
|------|--------|
| Scripts GEE creados | ✅ Listos |
| GEE autenticado | ✅ Proyecto: `earthengine-legacy-486401` |
| Ejecutar extracción MODIS | ❌ **PENDIENTE** |
| Dataset v9 con estrés térmico | ❌ **PENDIENTE** |
| Re-análisis H3 con datos reales | ❌ **PENDIENTE** |

**Scripts GEE listos para ejecutar:**
- `scripts/gee_extract_modis_lst.js` — MODIS MOD11A2 (1 km, 8 días) ← **USAR ESTE**
- `scripts/gee_extract_heat_stress_xavier.js` — Xavier/BR-DWGD v3 (0.1°, diario)
- `scripts/create_integrated_dataset_v9.py` — Integración al dataset

**Proyecto GEE configurado:** `earthengine-legacy-486401` (guardado en `scripts/gee_project.txt`)

**Justificación MODIS > Xavier** (confirmado por Adrian):
- 40.8% de municipios SP tienen < 2 píxeles Xavier (0.1° ~ 121 km²)
- MODIS (1 km) garantiza mínimo 4 píxeles incluso en el municipio más pequeño
- Mediana: 2.3 píxeles Xavier vs 281 píxeles MODIS por municipio
- MODIS captura mejor las islas de calor urbano (SUHI)

**Análisis H3.1-H3.4 ejecutado** (Sesión 23, con fire_risk_index como proxy):
- Script v1: `scripts/analisis_h3_heat_stress.py` (OLS/Gaussian - ejecutado)
- Script v2: `scripts/analisis_h3_heat_stress_v2.py` (GLM Gamma + log-transform - LISTO, NO ejecutado)
- **10 archivos generados** (v1): 8 CSVs + 2 figuras PNG + 1 diagrama SEM + 1 diagnóstico distribuciones

**Correcciones metodológicas v2** (Sesión 24):
- GLM Gamma(link=log) para outcomes de salud (tasas con sesgo derecho)
- Log-transformación para variables con skewness > 1 antes de estandarizar
- 4 outcomes de salud: mort_circ, mort_resp, hosp_circ, hosp_resp (v1 solo usaba mortalidad en H3.2-H3.4)
- Bootstrap IC 95% (5000 iteraciones) para efectos indirectos (reemplaza test Sobel)
- Diagnóstico formal de distribuciones (Shapiro-Wilk, AIC Gamma vs Gaussian)
- Distribuciones problemáticas identificadas: fire_incidence (skew=2.52), forest_cover (skew=2.27), hosp rates (skew=1.4-1.6)

**Resultados clave H3 (proxy fire_risk_index)**:

| Hallazgo | Resultado | Significancia |
|----------|-----------|---------------|
| Forest -> Fire (SEM) | -0.243 | p < 0.001 *** |
| Fire_incidence -> Fire_risk | 0.798 | p < 0.001 *** |
| Fire_risk -> Mort_CV (SEM) | -0.219 | p = 0.001 ** |
| Moderación forest × rural -> fuego | 0.120 | p < 0.001 *** |
| Moderación forest × pobreza -> fuego | 0.202 | p < 0.001 *** |
| Moderación fuego × pobreza -> mort_CV | -0.103 | p = 0.021 * |
| UAI_Crisk -> forest_cover | 0.118 | p = 0.005 ** |
| UAI_Crisk -> fire_incidence | -0.119 | p = 0.005 ** |
| SEM Modelo A (Gob General) CFI | 0.949 | RMSEA = 0.101 |

**Hallazgo IMPORTANTE**: fire_risk_index correlaciona NEGATIVAMENTE con mortalidad CV (r = -0.14). Esto indica que fire_risk es un proxy inadecuado para estrés térmico en salud (confundido por urbanización). **Se necesitan datos MODIS LST** para test directo de H3.

**Simple Slopes (Biodiv -> Fuego por ruralidad)**:
- Urbano (-1SD): b = -0.393 *** (efecto protector fuerte)
- Media: b = -0.273 ***
- Rural (+1SD): b = -0.153 *** (efecto protector menor)

**Figuras adicionales** (Sesión 24):
- `outputs/figures/h3_sem_path_diagram.png` — Diagrama SEM con coeficientes H3.4
- `outputs/figures/h3_distribucion_variables.png` — Diagnóstico distribuciones (raw vs Gaussian vs Log-normal)

**Archivos en Google Drive** (`G:\My Drive\Adrian David\Outputs_Science_Team\`):
- `correlaciones/` — 8 CSVs de H3
- `figures/` — 3 PNGs (análisis completo, heatmap, SEM path)
- `reports/METODOLOGIA_ESTRES_TERMICO.md`
- `analisis_h3_heat_stress.py` (v1) + `analisis_h3_heat_stress_v2.py` (v2)

**Documento metodológico completo**: `docs/METODOLOGIA_ESTRES_TERMICO.md`

### Análisis H1 - Nexus Assessment SEM (Sesión 26)
**Script**: `scripts/analisis_h1_nexus_sem.py`
**Datos**: 645 municipios × v8 dataset

**Estructura**: 4 sub-hipótesis progresivas (como H3):
- **H1.1**: Correlaciones bivariadas Biodiv → Clima → Salud
- **H1.2**: Mediación por déficit de polinización (test Sobel)
- **H1.3**: Moderación por vulnerabilidad social (interacción OLS)
- **H1.4**: SEM completo con gobernanza (semopy, 7 modelos)

**Variables utilizadas**:
- Biodiversidad: forest_cover, mean_species_richness, pol_deficit
- Riesgo climático: flooding_risks, fire_risk_index, hydric_stress_risk
- Salud (7): dengue, malaria, leptospirosis, leishmaniasis, diarrea, mort_cardiovascular, hosp_respiratoria
- Vulnerabilidad (4): pct_pobreza, pct_rural, pct_preta, pct_indigena
- Gobernanza (2): idx_gobernanza_100, UAI_Crisk

**Resultados clave**:

| Sub-H | Resultado | Hallazgo principal |
|-------|-----------|-------------------|
| H1.1 | 38/51 significativos | forest_cover ↔ dengue r=-0.454 |
| H1.2 | 28/42 mediaciones sig. | Pol. deficit media 48.6% de forest→flooding |
| H1.3 | 14/56 moderaciones sig. | pct_preta modulador más fuerte (5+ relaciones) |
| H1.4 | 97/126 paths SEM sig. | Species richness β=-0.328*** para dengue |

**Hallazgo justicia ambiental**: El efecto protector del bosque vs dengue varía por pct_preta:
- Baja pct_preta: r = -0.635
- Alta pct_preta: r = -0.357
→ Poblaciones más vulnerables reciben menor beneficio de servicios ecosistémicos

**Archivos generados**:
- `outputs/h1_1_correlations.csv` — 51 correlaciones bivariadas
- `outputs/h1_2_mediation.csv` — 42 cadenas de mediación
- `outputs/h1_3_moderation.csv` — 56 tests de interacción
- `outputs/h1_4_sem_paths.csv` — 126 coeficientes SEM
- `outputs/figures/h1_heatmap_nexus.png` — Heatmap 13×13
- `outputs/figures/h1_sem_*.png` — 7 diagramas SEM path
- `outputs/figures/h1_scatter_*.png` — 12 scatter plots con modulación social

### Selección de Modelos AIC + Gobernanza Expandida (Sesión 27)
**Script**: `scripts/analisis_h1_model_selection.py`
**Solicitud**: Adrian (27/01/2026) — Comparar índices compuestos vs variables específicas por AIC

**Metodología**:
- `lmer(Y ~ X + (1|microrregião))` con ML (no REML) para comparar AIC entre modelos
- deltaAIC < 2 = modelos equivalentes (Burnham & Anderson)
- Comparación dentro de cada dimensión: compuesto vs cada variable específica
- R² marginal (Nakagawa & Schielzeth 2013)

**Resultado principal**: **75% de las veces, una variable específica supera al índice compuesto**

**Variables seleccionadas por enfermedad (resumen)**:

| Enfermedad | Gobernanza | Riesgo Clim. | Biodiversidad | Vulnerabilidad |
|------------|-----------|-------------|---------------|----------------|
| **Dengue** | Gob (idx)*** | fire_risk*** | Biodiv (idx)** | % Rural*** |
| **Malaria** | UAI_Crisk* | fire_risk** | forest_cover*** | ninguna sig. |
| **Leptospirosis** | ninguna sig. | ninguna sig. | Biodiv (idx)* | ninguna sig. |
| **Leishmaniasis** | ninguna sig. | hydric_stress*** | forest_cover** | Vulnerab (idx)*** |
| **Diarrea** | ninguna sig. | fire_risk* | Biodiv (idx)*** | Vulnerab (idx)** |
| **Mort. CV** | UAI_mob* | fire_risk* | ninguna sig. | % Preta*** |
| **Hosp. Resp** | UAI_mob* | ninguna sig. | forest_cover*** | % Preta*** |

**Hallazgos clave Sesión 27**:

1. **Gobernanza → TODAS las dimensiones (no solo salud)**:
   - Gob ↓ Pobreza (β=-0.020***), ↓ Ruralidad (β=-0.190***)
   - Gob ↓ Cobertura forestal (β=-0.056**) — paradoja: más gobernanza = menos bosque
   - Gob ↑ TODOS los riesgos climáticos (flooding, fire, hydric) — paradoja confirmada
   - UAI_Movilidad es el componente con mayor poder predictivo en casi todas las dimensiones

2. **UAI_Movilidad emerge como predictor dominante** (no UAI_Crisk como se asumió):
   - Mejor predictor de mortalidad CV, hosp. respiratoria, pobreza, ruralidad
   - Probablemente proxy de urbanización/desarrollo más que movilidad per se

3. **Cada enfermedad tiene su propia "firma" de predictores óptimos**:
   - Dengue: responde a gobernanza general + fuego + biodiversidad
   - Leishmaniasis: responde a estrés hídrico + bosque + vulnerabilidad (NO a gobernanza)
   - Malaria: responde a UAI_Crisk + fuego + bosque (estructura ecológica)
   - Mort. CV / Hosp. Resp: responden a UAI_Movilidad + % Pob. Negra (justicia ambiental)

4. **fire_risk_index domina entre riesgos climáticos** para dengue, malaria, diarrea, mort. CV

**Archivos generados (Sesión 27)**:
- `outputs/h1_model_selection_all.csv` — 133 comparaciones de modelos
- `outputs/h1_model_selection_best.csv` — 28 selecciones óptimas
- `outputs/h1_governance_all_dimensions.csv` — 138 relaciones gobernanza→todo
- `outputs/figures/h1_model_selection_heatmap.png` — Heatmap de selecciones
- `outputs/figures/h1_governance_all_dimensions.png` — Panel gobernanza→4 dimensiones
- `outputs/figures/h1_governance_components_heatmap.png` — Heatmap UAI componentes
- `outputs/figures/h1_ms_scatter_*.png` — 20 scatter plots con estadísticos mixtos
- `outputs/figures/h1_MAP[1-5]_bivariate_*.png` — 5 mapas bivariados choropleth

### Workshop Layers - 16 Mapas (Sesión 31)

**Carpeta**: `outputs/figures/workshop_layers/`
**Script**: `scripts/create_workshop_layers.py`

16 mapas con 3 niveles (Low/Medium/High por terciles):
1. UAI Climatic Risk
2. UAI General
3. Species Richness
4. Vegetation Cover
5. Pollination Deficit
6. Flooding Risk
7. Fire Risk Index
8. Hydric Stress
9. Dengue Incidence
10. Diarrhea Incidence
11. CV Mortality
12. Resp Hospitalization
13. Poverty %
14. Vulnerability Index
15. Rural Population
16. Leishmaniasis Incidence

**Mapas bivariados EN** (con scatter plot):
- `bivariate_Governance_vs_Vulnerability_EN.png`
- `bivariate_ClimateRisk_vs_Vulnerability_EN.png`

### Actividad 3 Workshop - ACTUALIZADA (Sesión 31)

**Documentos**:
- `docs/WORKSHOP_ACTIVIDAD_3_ACTUALIZADA.md`
- `docs/WORKSHOP_ACTIVIDAD_3_ACTUALIZADA.docx`

**Cambios vs versión original**:

| Original | Actualizado |
|----------|-------------|
| Biodiversidad reduce dengue | CONFUNDIDO - dengue es urbano |
| Efecto dilución confirmado | Solo para diarrea y resp, NO dengue |
| Gobernanza reduce riesgos | Gobernanza es REACTIVA |
| Conservación = salud pública | Depende de la enfermedad |

**Hallazgos clave para presentar**:
1. Dengue: mejor predictor es % Rural (no bosque)
2. Malaria: más bosque = más malaria (robusto)
3. Gobernanza: reactiva, no preventiva
4. Pobreza: domina todo (27% varianza)
5. Lo que SÍ funciona: bosque→polinización, bosque→respiratorio, bosque→diarrea

---

### Workshop SEMIL-USP (Sesiones 20, 25, 29)
**Fecha**: 22, 24 y 26 de febrero 2026 (días no consecutivos)
**Participantes**: 20-25 (10 equipo proyecto + 10-18 invitados; 10 confirmados al 22/01/26)
**Ubicación recursos**: `G:\My Drive\Adrian David\Forthe_worshop\`

**Estructura actualizada (Sesión 25, v2)**:
- **Day 1 (Feb 22)**: Q-Methodology sobre barreras/facilitadores de uso de evidencia (White, Di Giulio)
- **Day 2 (Feb 24)**: Dinámicas de escenarios con datos territoriales (Adrian) — 3 actividades:
  - Act 2.1: Ranking de 10 municipios con 6 variables elegidas
  - Act 2.2: "Knowledge Budgets" — compra de capas adicionales con créditos (10 créditos/grupo)
  - Act 2.3: Presentación nexus assessment + preguntas de paradojas
- **Day 3 (Feb 26) O alternativa para 2da mitad Day 2**: Co-diseño de políticas e implementación (All)
  - Act 3.1-3.3 adoptadas; Act 3.4 (Public Commitments) eliminada por Adrian

**10 municipios seleccionados para ranking** (v3 final):
Iporanga (Q3), Campinas (Q1), Santos (Q1), **São Joaquim da Barra** (Q3), **Miracatu** (Q3), Eldorado (Q4), Francisco Morato (Q4), São Paulo (Q1), Arujá (Q2), Cerquilho (Q2)
- Balance: Q1=3, Q2=2, Q3=3, Q4=2
- Morungaba removida; SJ da Barra y Miracatu reemplazan slots vacíos

**Documentos fuente (nuevos de Adrian)**:
- `propousal for day2.docx` — 3 actividades Day 2 + Day 3 (**actualizado v2 por Adrian**)
- `complementary_file.docx` — Day 1 Q-Methodology + pre-cuestionario (49 statements)
- `Prompt for the workshop.gdoc` — Brief original con contexto

**Documento integrado actualizado**: `PROPUESTA_DINAMICAS_WORKSHOP_SEMIL_USP.md`
- Integra los 3 documentos de Adrian con la propuesta anterior
- Incluye sistema de créditos, tabla de 10 municipios con datos, agendas 3 días
- Actualizado con cambios de Adrian v2 (Campinas, Santos, fechas, fuentes)

**Recursos existentes**:
- **16 mapas HTML interactivos** en `mapas_workshop/` (6 originales + 10 nuevos generados Sesión 25)
- `mapa_unificado_capas.html` - Mapa con selector de 6 capas

### Presentación PowerPoint Day 2 (Sesión 29, 02/02/2026)

**Archivos generados** en `notebooks/02_02/`:
- `SLIDES_MEJORADOS_WORKSHOP.md` — Documentación completa de 15 slides + 4 backup
- `create_workshop_pptx.py` — Script v1 (sin imágenes, 55 KB, 19 slides)
- `create_workshop_pptx_v2.py` — Script v2 (con mapas, 4 MB, 24 slides)
- `Workshop_SEMIL_USP_Day2_MEJORADO.pptx` — Versión básica
- `Workshop_SEMIL_USP_Day2_v2_con_mapas.pptx` — **Versión final con mapas**

**Estructura de la presentación (24 slides)**:
- **Bloque A (slides 1-5)**: El Problema — título, pregunta central, marco nexus, datos
- **Bloque B (slides 6-15)**: Lo que Encontramos — 4 hallazgos, cuadrantes, 10 municipios, paradojas
- **Bloque C (slides 16-18)**: ¿Y Ahora Qué? — actividades, sistema créditos, pregunta final
- **Backup (slides 19-24)**: Metodología, UAI, heatmaps, SEM, referencias, agradecimientos

**Mapas incluidos en PPT**:
- `h1_FIG1_causal_panel.png` — Diagrama causal nexus
- `h1_MAP1_bivariate_forest_dengue.png` — Bosque × Dengue
- `h1_MAP2_bivariate_governance_biodiv.png` — Gobernanza × Biodiversidad
- `h1_MAP2_bivariate_vuln_climate.png` — Vulnerabilidad × Clima
- `h1_MAP3_bivariate_governance_climate.png` — Gobernanza × Clima
- `h1_MAP5_bivariate_poverty_disease.png` — Pobreza × Enfermedad
- `h1_scatter_forest_dengue_pobreza.png` — Scatter modulación
- `h1_model_selection_heatmap.png` — Selección de modelos AIC
- `h1_governance_all_dimensions.png` — Gobernanza todas dimensiones
- `h1_governance_components_heatmap.png` — Componentes UAI
- `h1_heatmap_nexus.png` — Correlaciones nexus
- `h1_sem_dengue.png` — Modelo SEM dengue

**Pendientes Workshop**:
- [x] ~~Generar 10 heat-maps adicionales~~ — **Hecho** (Sesión 25)
- [x] ~~Confirmar municipios para ranking~~ — **Hecho**: 10 confirmados (v3 final)
- [x] ~~Preparar slides presentación nexus~~ — **Hecho** (Sesión 29, 24 slides con mapas)
- [ ] Confirmar si Day 3 es standalone (Feb 26) o segunda mitad de Day 2
- [ ] Preparar fichas impresas de municipios con datos
- [ ] Diseñar tokens de crédito para Activity 2.2
- [ ] Agregar logos USP/York a la PPT (descargar manualmente)

### Corrección Mapas + Sincronización Drive (Sesión 31, 03/02/2026)

**Problema identificado**: Todos los mapas bivariados de la Sesión 27 estaban vacíos (n=0 municipios).

**Causa raíz**: Código IBGE en shapefile tiene 7 dígitos (3500105), pero CSV tiene 6 dígitos (350010).

**Solución aplicada**:
```python
# ANTES (fallaba):
gdf['cod_ibge'] = gdf['CD_MUN'].astype(int)

# DESPUÉS (funciona):
gdf['cod_ibge'] = gdf['CD_MUN'].astype(str).str[:6].astype(int)
```

**Scripts corregidos**:
- `scripts/analisis_h1_model_selection.py` (línea 745-756)
- `scripts/analisis_h5_clima_predictors.py` (línea 456)
- `scripts/analisis_cuadrantes_4combinaciones.py` (nuevo)

**Sincronización automática con Google Drive**:
- `scripts/sync_to_drive.ps1` — Script PowerShell que usa robocopy /MIR
- `scripts/create_task_hourly.ps1` — Crea tarea programada "SyncAdrianDavidToDrive"
- **Frecuencia**: Cada hora automáticamente
- **Destino**: `G:\My Drive\Adrian David\Outputs_Science_Team\`

**Carpetas sincronizadas**:
- figures/, h1_gobernanza/, h2_vulnerabilidad/, h3_clima_salud/
- h4_salud/, h5_clima/, h6_sintesis/, docs/, notebooks/, CSVs

**Figuras generadas (2026-02-03)**:
- `mapa_workshop_10municipios.png` — Gobernanza con 10 municipios destacados
- `mapa_microrregiones_sp.png` — Mapa de referencia microrregiones SP
- `cuadrantes_Gobernanza_vs_Biodiversidad.png`
- `cuadrantes_Gobernanza_vs_Salud.png`
- `cuadrantes_Gobernanza_vs_Clima.png`
- `cuadrantes_Biodiversidad_vs_Vulnerabilidad.png`

**Organización de outputs**: Nueva estructura con carpetas por fecha (`outputs/figures/2026-02-03/`)

---

### Metodología Índices Compuestos (documentado Sesión 31)

**Fuente**: `scripts/create_integrated_dataset_v6.py`

#### 1. `idx_vulnerabilidad` — Promedio ponderado (0-100)
```python
idx_vulnerabilidad = (
    normalize_0_100(pct_rural) * 0.25 +
    normalize_0_100(pct_pobreza) * 0.35 +
    normalize_0_100(pct_preta) * 0.25 +
    normalize_0_100(pct_indigena) * 0.15
)
```
- **Pesos**: Pobreza (35%) > Rural/Preta (25% c/u) > Indígena (15%)
- **Normalización**: Min-max (0-100) por variable antes de ponderar

#### 2. `idx_biodiv` — Solo riqueza de especies (0-100)
```python
idx_biodiv = (
    (mean_species_richness - min) / (max - min)
) * 100
```
- **Variables incluidas**: Solo `mean_species_richness`
- **NO incluye**: forest_cover, pol_deficit (están como variables separadas)
- **Normalización**: Min-max simple

#### 3. `idx_clima` — Promedio simple (0-100)
```python
idx_clima = mean([flooding_risks, hydric_stress_risk]) * 100
```
- **Variables incluidas**: flooding_risks, hydric_stress_risk
- **NO incluye**: fire_risk_index (está como variable separada)
- **Normalización**: Las variables ya están en escala 0-1, multiplicadas por 100

#### 4. `idx_carga_enfermedad` — Promedio de 4 enfermedades normalizadas
```python
norm_cols = [normalize_0_100(col) for col in inc_cols]
idx_carga_enfermedad = mean(norm_cols)
```
- **Variables incluidas**: dengue, leishmaniose, leptospirose, malaria
- **NO incluye**: diarrea, muerte cardiovascular, hospitalización respiratoria
- **Normalización**: Min-max por enfermedad antes de promediar

**Solicitud pendiente**: Adrian debe confirmar/corregir esta metodología (`docs/SOLICITUD_METODOLOGIA_INDICES.md`)

---

### Análisis de Cuadrantes - 4 Combinaciones (Sesión 31)

**Script**: `scripts/analisis_cuadrantes_4combinaciones.py`

**Resultados por combinación**:

| Análisis | Q1 Óptimo | Q2 Riesgo | Q3 Crítico | Q4 Potencial |
|----------|-----------|-----------|------------|--------------|
| Gob vs Biodiv | ~160 mun | ~160 mun | ~160 mun | ~160 mun |
| Gob vs Salud | ~160 mun | ~160 mun | ~160 mun | ~160 mun |
| Gob vs Clima | ~160 mun | ~160 mun | ~160 mun | ~160 mun |
| Biodiv vs Vuln | ~160 mun | ~160 mun | ~160 mun | ~160 mun |

**Archivos generados**:
- `outputs/analisis_cuadrantes_4combinaciones.csv` — Estadísticas completas
- 4 mapas + scatter plots (uno por combinación)

---

### Análisis Nexus (Sesión 19)
- `outputs/correlaciones_nexus_completas.csv`
- `outputs/modelos_mixtos_nexus.csv`
- `outputs/ranking_municipios_prioritarios.csv`
- `outputs/acciones_pearc_por_cuadrante.csv`
- `outputs/figures/hipotesis_h1_h2_nexus.png`
- `outputs/figures/analisis_cuadrantes_nexus.png`

### Validación Datos (Sesión 18)
- `scripts/compare_health_data_ju.py`
- `scripts/compare_health_data_ju_v2.py`
- Resultado: Dengue y Diarrea validados (r=1.0)

---

## Próximos Pasos

### Alta Prioridad

#### 🔴 Air Pollution Project (Deadline: Feb-Abr 2026)
- [x] ~~Crear tabla Excel con 1,468 redes~~ — **Hecho** (Sesión 30)
- [x] ~~Crear propuesta económica $600~~ — **Hecho** (Sesión 30)
- [x] ~~Organizar carpeta del proyecto~~ — **Hecho** (Sesión 30)
- [ ] **PRÓXIMO**: Enviar propuesta + Excel a Luísa y Ruben
- [ ] Configurar cuenta Copernicus ADS (Adrian)
- [ ] Desarrollar script R extracción O3/NO2 (CAMS/EAC4)
- [ ] Esperar fechas de muestreo de investigadores

#### 🟡 Workshop SEMIL-USP (Feb 22-26)
- [x] ~~**ANÁLISIS H1-H6**: Framework completo~~ — **Hecho** (commit db41759, 81 archivos)
- [x] ~~**WORKSHOP**: Generar heat-maps adicionales para Day 2~~ — **Hecho** (16 mapas totales)
- [x] ~~**WORKSHOP**: Confirmar municipios para ranking~~ — **Hecho** (10 confirmados, v3 final)
- [x] ~~**WORKSHOP**: Preparar slides presentación nexus~~ — **Hecho** (Sesión 29, 15 slides + 4 backup)
- [ ] **WORKSHOP**: Confirmar formato Day 3 con Adrian (standalone o 2da mitad Day 2)
- [ ] **WORKSHOP**: Implementar slides en PowerPoint (basado en `SLIDES_MEJORADOS_WORKSHOP.md`)
- [ ] **WORKSHOP**: Imprimir materiales (fichas municipios, tokens crédito, Q-Sort cards)

#### 🟢 Publicación
- [x] ~~Finalizar propuesta Branco Weiss~~ — **Entregada**
- [ ] Preparar manuscrito para journal (ERL o similar)
- [ ] Registrar en OSF (Open Science Framework)

### 🔴 CRÍTICO - Datos Faltantes
- [ ] **EXTRAER DATOS MODIS LST** — GEE configurado (proyecto: `earthengine-legacy-486401`), solo falta ejecutar
- [ ] **Crear dataset v9** con variables de estrés térmico reales
- [ ] **Re-ejecutar análisis H3** con datos MODIS (no el proxy fire_risk_index)

### Media Prioridad
- [x] ~~**Ejecutar scripts GEE** para extraer datos MODIS LST (requiere GCP project)~~ — GEE CONFIGURADO, pendiente extracción
- [ ] **Crear dataset v9** con variables de estrés térmico (MODIS LST)
- [x] **Modelar H3** con proxy fire_risk_index (completado Sesión 23)
- [x] **Corregir script H3** con GLM Gamma + 4 outcomes (v2 listo, Sesión 24)
- [ ] **Ejecutar script H3 v2** (pendiente aprobación Adrian)
- [ ] **Re-modelar H3** con datos MODIS LST directos (pendiente datos GEE)
- [ ] Análisis de sensibilidad con diferentes umbrales
- [ ] Integrar variables climáticas extremas pendientes (CDD, TX35)
- [ ] Validación cruzada con datos independientes

---

## PLAN DE NEGOCIO: TerraRisk Analytics

> **Informe completo**: `docs/INFORME_TERRARISK_PLAN_NEGOCIO.md`

### Concepto
Comercializar los análisis territoriales como plataforma de inteligencia territorial (SaaS/API/Consultoría).

### Estado: EN VALIDACIÓN

### Hallazgos Clave

| Aspecto | Estado | Nota |
|---------|--------|------|
| Oportunidad de mercado | ✅ Alta | ISSB 2026, EUDR, COP30 crean demanda |
| Viabilidad técnica | ✅ Viable | 60% backend existe |
| **DATASUS** | 🔴 BLOQUEANTE | Licencia CC-BY-NC-SA prohíbe uso comercial |
| Otras fuentes | ✅ OK | IBGE, MapBiomas, satélites permitidos |
| Competencia | ⚠️ Alta | Agrotools ($21M), WayCarbon (Santander) |

### Problema Crítico: DATASUS
Los datos de salud (dengue, diarrea, mortalidad) tienen licencia **Non-Commercial**.
- **Opción A**: Solicitar licencia comercial al Ministerio de Salud
- **Opción B**: Excluir datos de salud del producto
- **Opción C**: Modelo híbrido académico-comercial (RECOMENDADO)

### Acciones Pendientes

| Prioridad | Acción | Responsable | Estado |
|-----------|--------|-------------|--------|
| 🔴 1 | Email formal a DATASUS sobre licencia comercial | Adrian | PENDIENTE |
| 🔴 2 | Mapear gaps exactos vs MapBiomas | Equipo | PENDIENTE |
| 🟡 3 | 5 llamadas validación con clientes potenciales | Arlex | PENDIENTE |
| 🟡 4 | Consulta abogado LGPD Brasil | - | PENDIENTE |
| 🟡 5 | Cotización seguro E&O | - | PENDIENTE |

### Financieros Estimados
- **Inversión MVP (6 meses)**: USD 148,000
- **Break-even**: Mes 10-12
- **ARR objetivo Y1**: USD 500k-800k

### Mercados Objetivo
1. Seguros agrícolas (USD 50-150k/año)
2. Agribusiness/ESG - EUDR compliance (USD 80-200k/año)
3. Gobiernos estaduales (USD 200-500k proyecto)
4. Real Estate - due diligence climática (USD 15-40k)
5. Impact Investing (USD 30-100k/año)

### Competidores Principales
- **Agrotools**: $21M funding, Cargill/JBS/Itaú
- **WayCarbon**: 80% Santander, Natura/Braskem
- **MapBiomas**: GRATUITO (pero solo datos raw, no análisis)

### Gap de Mercado (Nuestra Ventaja)
Ningún competidor ofrece:
1. Scoring municipal integrado (clima + biodiv + gobernanza)
2. Nexo gobernanza-biodiversidad-bienestar (metodología Adrian)
3. Due diligence climática para real estate

### Decisiones Pendientes (Arlex + Adrian)
1. ¿Incluir datos de salud? → Depende de respuesta DATASUS
2. ¿Estructura legal? → Unidad AP Digital vs empresa separada
3. ¿Modelo de negocio? → SaaS puro vs híbrido académico-comercial

---

## Scripts Principales

### Framework H1-H6 (nuevo 2026-01-29)
| Script | Descripción |
|--------|-------------|
| `analisis_h1_gobernanza_predictors.py` | H1: ¿Qué predice gobernanza (UAI)? |
| `analisis_h2_vulnerabilidad_interaccion.py` | H2: Vulnerabilidad × otras dimensiones |
| `analisis_h3_clima_salud_interaccion.py` | H3: Clima × Salud → Gobernanza |
| `analisis_h4_salud_predictors.py` | H4: Predictores de riesgo de salud |
| `analisis_h5_clima_predictors.py` | H5: Predictores de riesgo climático |
| `sintesis_h6_metadata.py` | H6: Síntesis y clasificación variables |

### Otros Scripts
| Script | Descripción |
|--------|-------------|
| `analisis_h3_heat_stress.py` | Estrés térmico v1 (OLS) |
| `analisis_h3_heat_stress_v2.py` | Estrés térmico v2 (GLM Gamma) |
| `analisis_h1_nexus_sem.py` | Nexus SEM (semopy) |
| `analisis_h1_model_selection.py` | Selección modelos AIC |
| `create_integrated_dataset_v8.py` | Generador dataset v8 |
| `create_workshop_maps.py` | 6 mapas choropleth workshop |

---

## Referencias Rápidas

**Archivos de contexto extendido:**
- `SESSION_HISTORY.md` - Historial detallado de 19 sesiones
- `PAPERS_LIBRARY.md` - Catálogo de 75 papers
- `DATA_METHODOLOGY.md` - Fuentes de datos y metodología
- `REFERENTES_CIENTIFICOS.md` - Investigadores de referencia

**GitHub**: https://github.com/adgch86/saopaulo-biodiversity-health
**DOI**: 10.5281/zenodo.18303824

---

*Última actualización: 2026-02-03 (Sesión 31 - Bug fix IBGE, sync Drive, GEE configurado, 16+2 workshop layers, Actividad 3 actualizada, mapas bivariados EN, PENDIENTE extraer MODIS LST)*
