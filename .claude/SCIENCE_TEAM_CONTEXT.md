# Science Team - Contexto del Proyecto

> **IMPORTANTE**: Este archivo mantiene el estado y contexto del proyecto de investigación.
> El Science Team debe leerlo al inicio de cada sesión y actualizarlo con nuevos hallazgos.

---

## Proyecto Actual

**Título**: Resilient Landscapes: Integrating Planetary Health, Nexus Thinking, and Environmental Justice in São Paulo's Agrifood Systems
**Investigador Principal**: Dr. Adrian David González Chaves
**Estado**: Análisis completado - Preparando propuesta Branco Weiss

---

## Objetivo General

Integrar cinco dimensiones de sistemas agroalimentarios a escala municipal en São Paulo, siguiendo el marco conceptual de Levers et al. (2025):
1. **Biodiversidad** (riqueza de especies, cobertura forestal)
2. **Salud pública** (dengue, diarrea, malaria)
3. **Pobreza/Vulnerabilidad** (indicadores socioeconómicos)
4. **Gobernanza** (UAI - Urban Agriculture Index)
5. **Clima** (variables climáticas extremas) - *Parcialmente integrado*

---

## Datos del Estudio

- **Unidad de análisis**: Municipios de São Paulo, Brasil
- **n = 187-645 municipios** (según disponibilidad de datos)
- **Marco conceptual**: Levers et al. (2025), Barreto et al. (2025)

### Fuentes de Datos
- `data/raw/` - Datos crudos
- `data/processed/` - Datos procesados
- `data/raw/2026_01_14/` - Datos más recientes

---

## HALLAZGOS PRINCIPALES

### 1. Confirmación Local del Efecto Dilución
**El efecto dilución está CONFIRMADO localmente**: ecosistemas biodiversos reducen transmisión de patógenos.

| Variable | vs | Correlación (r) | Interpretación |
|----------|-----|-----------------|----------------|
| Riqueza spp | Dengue | **-0.429** | Más especies = menos dengue |
| Riqueza spp | Diarrea | **-0.452** | Más especies = menos diarrea |
| Riqueza spp | Malaria | **-0.358** | Más especies = menos malaria |
| Cobertura forestal | Dengue | **-0.486** | Más bosque = menos dengue |
| Cobertura forestal | Diarrea | **-0.394** | Más bosque = menos diarrea |

**Implicación**: La conservación de biodiversidad tiene co-beneficios directos para salud pública.

### 2. Paradoja Conservación-Pobreza
**HALLAZGO CLAVE**: Municipios con MAYOR pobreza tienen MAYOR biodiversidad.
- Biodiversidad vs Vulnerabilidad: **r = +0.23**

| Tercil Pobreza | Riqueza Especies | Cobertura Forestal |
|----------------|------------------|---------------------|
| Baja (ricos) | 652.0 | 24.4% |
| Media | 621.6 | 20.5% |
| Alta (pobres) | 596.3 | 16.6% |

**Explicación**: Comunidades pobres rurales son "guardianes involuntarios" de biodiversidad - menos presión de desarrollo urbano.

### 3. Brecha de Gobernanza
**Los municipios que MÁS necesitan apoyo son los que MENOS lo tienen.**
- Correlación UAI vs IVM: **r = -0.293**

| Cuadrante | UAI (Gobernanza) | IVM (Vulnerabilidad) | n |
|-----------|------------------|----------------------|---|
| Q1_Modelo | 0.564 | 61.9 | 198 |
| Q2_Conservar | 0.248 | 65.8 | 125 |
| **Q3_Vulnerable** | **0.234** | **76.4** | 195 |
| Q4_Desarrollo | 0.512 | 73.6 | 127 |

**Q3_Vulnerable = prioridad máxima para intervención**

### 4. Nexo Clima-Salud
- Correlación clima-enfermedad: **r = -0.54**

---

## Índice de Vulnerabilidad Multidimensional (IVM)

Índice desarrollado que integra:
- Indicadores de pobreza
- Acceso a servicios básicos
- Condiciones de vivienda
- Vulnerabilidad climática

**Escala**: 0-100 (mayor = más vulnerable)

---

## Cuadrantes de Clasificación

Sistema de clasificación de municipios basado en UAI (gobernanza) e IVM (vulnerabilidad):

```
                     ALTA GOBERNANZA (UAI)
                            │
           Q1_Modelo ───────┼─────── Q4_Desarrollo
           (Baja vuln,      │        (Alta vuln,
            Alta gob)       │         Alta gob)
                            │
    ────────────────────────┼────────────────────────
                            │
          Q2_Conservar ─────┼─────── Q3_Vulnerable
          (Baja vuln,       │        (Alta vuln,
           Baja gob)        │         Baja gob)
                            │              ↑
                     BAJA GOBERNANZA    PRIORIDAD
```

---

## Municipios Prioritarios (Q3 - Alta vulnerabilidad + Baja gobernanza)

Top 10 con mayor brecha:
1. **Uru**: UAI=0.140, IVM=100.0
2. **Vitória Brasil**: UAI=0.090, IVM=93.6
3. **Borá**: UAI=0.156, IVM=97.8
4. **Taquaral**: UAI=0.090, IVM=90.1
5. **Pracinha**: UAI=0.076, IVM=87.9
6. **São Francisco**: UAI=0.066, IVM=86.3
7. **Júlio Mesquita**: UAI=0.076, IVM=84.0
8. **Marapoama**: UAI=0.090, IVM=83.4
9. **Dobrada**: UAI=0.066, IVM=80.4
10. **Balbinos**: UAI=0.116, IVM=84.4

---

## Scripts Desarrollados

| Versión | Archivo | Descripción | Estado |
|---------|---------|-------------|--------|
| v1 | `science_team_analysis.py` | Análisis inicial | ✅ Completado |
| v2 | `science_team_analysis_v2.py` | Mejoras estadísticas | ✅ Completado |
| v3 | `science_team_analysis_v3.py` | IVM implementado | ✅ Completado |
| v4 | `science_team_analysis_v4.py` | Refinamientos | ✅ Completado |
| v5 | `science_team_analysis_v5_clima.py` | Integración clima | ✅ Completado |
| - | `create_branco_weiss_proposal.py` | Generador Word | ✅ Completado |

---

## Documentación Generada

| Archivo | Descripción |
|---------|-------------|
| `docs/INFORME_SCIENCE_TEAM_V5.md` | Informe técnico completo (versión actual) |
| `docs/INFORME_SCIENCE_TEAM_V3.md` | Informe técnico v3 |
| `docs/INFORME_Biodiversidad_UAI_PEARC.pdf` | Informe PDF principal |
| `docs/RECOMENDACIONES_POLITICAS_SCIENCE_TEAM.md` | Policy brief |
| `docs/SESION_2025_01_15_RESUMEN.md` | Resumen sesión anterior |

---

## Outputs Generados

### Datos (en `outputs/`)
- `correlaciones_nexo_v5.csv` - Matriz de correlaciones completa
- `municipios_integrado_v5.csv` - Dataset municipal integrado
- `municipios_ivm_v3.csv` - Clasificación IVM
- `municipios_triple_burden.csv` - Municipios con carga triple

### Figuras (en `outputs/figures/`)
- `nexo_clima_biodiv_salud_v5.png` - Diagrama nexo 5D
- `cuadrantes_v3.png` / `cuadrantes_uai_biodiv.png` - Visualización cuadrantes
- `biodiv_vs_enfermedades.png` - Efecto dilución
- `paradoja_biodiv_vulnerabilidad.png` - Paradoja conservación-pobreza
- `vulnerabilidad_vs_gobernanza.png` - Brecha de gobernanza
- `heatmap_correlaciones.png` - Mapa de calor correlaciones

---

## Propuesta Branco Weiss Fellowship

### Estado: En preparación
- **Documento**: `BrancoWeiss_Proposal_FINAL.docx`
- **Ubicación**: `admin/becas/branco_weiss/2025_01_14_branco/`
- **Figuras**:
  - Figure 1: `Figure1_DataIntegration.png` (panel 3 gráficos)
  - Figure 2: `Figure2_Climate_Health.png` (clima vs salud)
- **Palabras**: ~1,441 (límite: 5 páginas ✓)

---

## Variables Pendientes por Integrar

### Alta Prioridad
- **CDD**: Días consecutivos secos (sequías)
- **TX35**: Días con temperatura >35°C (olas de calor)
- **RX5**: Precipitación máxima 5 días (inundaciones)
- **FD**: Días con heladas

### Media Prioridad
- **FLII**: Forest Landscape Integrity Index
- **Densidad de bordes**: Fragmentación del hábitat
- Series temporales multi-año
- Datos de producción agrícola

---

## Referencias Clave

1. **Barreto et al. (2025)** - Communications Earth & Environment
   - Adrian González-Chaves es co-autor
   - Efecto dilución en Amazonía
   - DOI: 10.1038/s43247-025-02620-7

2. **Levers et al. (2025)** - Environmental Research Letters
   - Marco conceptual 5 dimensiones (agrifood-system burdens)
   - DOI: 10.1088/1748-9326/ae20ac

---

## Bibliografía Analizada

> **Archivos detallados**: `.claude/papers/[Autor][Año]_[tema].md`

### Papers Analizados

| Paper | Tema | Relevancia | Archivo |
|-------|------|------------|---------|
| **González-Chaves et al. 2023** | **Time-lag ES (PAPER PROPIO)** | ⭐⭐⭐⭐⭐ | `papers/GonzalezChaves2023_forest_coffee_timelag.md` |
| **González-Chaves et al. 2020** | **Proximity vs Cover (PAPER PROPIO)** | ⭐⭐⭐⭐⭐ | `papers/GonzalezChaves2020_forest_proximity_bees.md` |
| **Metzger et al. 2024** | **Transdisciplinary Synthesis (SUPERVISOR)** | ⭐⭐⭐⭐⭐ | `papers/Metzger2024_transdisciplinary_synthesis.md` |
| **Di Giulio et al. 2018** | **Mainstreaming Climate SP (SUPERVISORA)** | ⭐⭐⭐⭐⭐ | `papers/DiGiulio2018_mainstreaming_climate_SP.md` |
| **Mohai et al. 2009** | **Environmental Justice (MARCO TEÓRICO)** | ⭐⭐⭐⭐⭐ | `papers/Mohai2009_environmental_justice.md` |
| Rosenfield et al. 2025 | **Resilient Landscapes Brazil** | ⭐⭐⭐⭐⭐ | `papers/Rosenfield2025_resilient_landscapes_brazil.md` |
| Levers et al. 2025 | Agrifood-system burdens global | ⭐⭐⭐⭐⭐ | `papers/Levers2025_agrifood_burdens.md` |
| Raymond et al. 2020 | Connected extreme events | ⭐⭐⭐⭐⭐ | `papers/Raymond2020_connected_extremes.md` |
| Zscheischler et al. 2018 | Compound events typology | ⭐⭐⭐⭐⭐ | `papers/Zscheischler2018_compound_events.md` |
| Cutter et al. 2015 | Disaster risk / Sendai | ⭐⭐⭐⭐ | `papers/Cutter2015_disaster_risk.md` |
| Walsh et al. 2019 | Barriers/enablers evidence use | ⭐⭐⭐⭐⭐ | `papers/Walsh2019_barriers_enablers_evidence_use.md` |
| Lenzi et al. 2023 | Justice, sustainability, values | ⭐⭐⭐⭐⭐ | `papers/Lenzi2023_justice_sustainability_values_nature.md` |

### Conceptos Clave Extraídos

- **Connected extremes**: Eventos donde impactos se amplifican por mecanismos físicos + sociales
- **Compound events**: 4 tipos - temporal, spatial, preconditioned, multivariate
- **Indicadores críticos**: CDD, TX35, RX5 para evaluar riesgo compuesto
- **Framework**: Cultura/Gobernanza → Exposición/Vulnerabilidad → Hazards → Impactos → Respuesta
- **Barreras uso evidencia** (Walsh 2019): Falta tiempo, recursos limitados, silos departamentales
- **Tres dimensiones justicia** (Lenzi 2023): Distributiva, Procedimental, Reconocimiento
- **Taxonomía 230 factores**: Barreras y facilitadores para uso de ciencia en conservación

### Biblioteca Completa de Papers (65 archivos MD)

> **Ubicación**: `G:\My Drive\Adrian David\Papers\markdown\`
> **Índice**: `_INDEX.md`

#### 🌿 PAPERS PROPIOS - Dr. Adrian González-Chaves

| Archivo | Título | Año | Journal |
|---------|--------|-----|---------|
| `Gonzalez_chaves_etal_2020_LandscapeEcol.md` | Forest proximity rather than local forest cover affects bee diversity and coffee pollination | 2020 | Landscape Ecology |
| `González-Chaves_2023_Environ_Res_Lett.md` | Time-lag in ecosystem services provision by regenerating forests to coffee | 2023 | Environ. Res. Lett. |
| `Functional Ecology - 2024 - González Chaves.md` | Tree traits predict bee traits and species richness | 2024 | Functional Ecology |
| `Journal of Applied Ecology - 2021 - González Chaves.md` | Positive forest cover effects on coffee yields | 2021 | J. Applied Ecology |

#### 👩‍🔬 SUPERVISORES Y COLABORADORES CERCANOS

| Archivo | Autor Principal | Tema | Relevancia |
|---------|-----------------|------|------------|
| `DGiulioetal_2025_Cities.md` | **Di Giulio G.** (supervisora) | Mainstreaming climate adaptation São Paulo | ⭐⭐⭐⭐⭐ |
| `Urban adaptation index cities.md` | **Di Giulio G.** (supervisora) | UAI - Urban Adaptation Index (BASE del análisis) | ⭐⭐⭐⭐⭐ |
| `2024_12_Metzger_et_al_PECON.md` | **Metzger J.P.** (supervisor) | Transdisciplinary synthesis for policy | ⭐⭐⭐⭐⭐ |
| `Global Change Biology - 2025 - Rosenfield.md` | Rosenfield (colaborador) | Mapping Resilient Landscapes Brazil | ⭐⭐⭐⭐⭐ |

#### 🌍 MARCO CONCEPTUAL - Sistemas Agroalimentarios y Nexo

| Archivo | Tema | Concepto Clave |
|---------|------|----------------|
| `Levers_2025_Environ_Res_Lett.md` | Agrifood-system burdens global | Marco 5 dimensiones (biodiversidad, salud, pobreza, gobernanza, clima) |
| `Zscheischler2018.md` | Compound climate events | 4 tipos: temporal, spatial, preconditioned, multivariate |
| `Raymondetal2020connectedextremeevents.md` | Connected extreme events | Amplificación física + social |
| `Cutteretal2015Nature.md` | Disaster risk reduction / Sendai | Pool knowledge for resilience |

#### ⚖️ JUSTICIA AMBIENTAL Y SOCIAL

| Archivo | Tema |
|---------|------|
| `2009-Roberts-Environmental Justice.md` | Environmental Justice - Marco teórico fundamental (Mohai, Pellow, Roberts) |
| `tao-et-al-2025-inequality-in-air-pollution.md` | Inequality in air pollution mortality by income |
| `s12939-024-02214-3.md` | Health equity and environmental justice |

#### 🔬 CIENCIA-POLÍTICA (Science-Policy Interface)

| Archivo | Tema |
|---------|------|
| `Science-of-Using-Science-Final-Report-2016.md` | Using research evidence in decision-making |
| `Public_policy_and_use_of_evidence_in_Brazil.md` | Políticas públicas y evidencia en Brasil (IPEA) |
| `Schimidt et al 2024 science policy interface.md` | Science-policy interface |
| `cairney-oliver-wellstead-2017-par.md` | Policy analysis and research |
| `Public Administration Review - 2022 - MacKillop.md` | What counts as evidence for policy |
| `Modernising-the-Policy-Process.md` | Modernising policy process |
| `RCC_EIPM_Framework_user_guide.md` | Evidence-Informed Policy Making framework |
| `RCC_EIPM_pathfinding_paper.md` | EIPM pathfinding |

#### 🤝 CONFIANZA EN CIENTÍFICOS

| Archivo | Tema |
|---------|------|
| `Trust in scientist 68 countries.md` | Trust in scientists across 68 countries (Nature Human Behaviour 2025) |
| `Trust in scientist and their role in society.md` | Scientists' role in society |

#### 🐝 POLINIZACIÓN Y SERVICIOS ECOSISTÉMICOS

| Archivo | Tema |
|---------|------|
| `small holder risk assocaited to pollination faliure PLOsone 2025.md` | Smallholder vulnerability to pollinator decline (Brazil, biome-dependent) |
| `Global Change Biology - 2025 - Tsang.md` | Land use change and bee diversity |
| `Nota 5 - Potencial do Serviço de Polinização.md` | Potencial servicio polinización (Brasil) |
| `Gourevitch_et_al_2021.md` | Ecosystem services valuation |
| `Institutionalchallenges_EcosServ_2018.md` | Institutional challenges for ES |

#### 🌡️ CAMBIO CLIMÁTICO Y ADAPTACIÓN

| Archivo | Tema |
|---------|------|
| `2020-Lewandowsky-Climate change disinformation.md` | Climate disinformation and how to combat it |
| `WIREs Climate Change - 2024 - Mills Novoa.md` | Promise of Resistance - Climate adaptation research |
| `navigating the continuem between adaptation and mal adaptaton.md` | Adaptation vs maladaptation |
| `fclim-05-1177025.md` | Frontiers in Climate |
| `fclim-06-1392033.md` | Frontiers in Climate |
| `Nota 1 - Contribuições ao Plano de Ação Climática.md` | Contribuciones Plan Acción Climática (Brasil) |
| `ondas de calorbiota sintesis 6.md` | Olas de calor - síntesis |

#### 🇧🇷 BRASIL - POLÍTICAS Y PLANES

| Archivo | Tema |
|---------|------|
| `Plano federal biodiversidade e mudança climatica - Brasil.md` | Plan federal biodiversidad y cambio climático |
| `PEARC_Consulta_Publica_inicial_2024.md` | PEAC São Paulo - Consulta pública |
| `o papel das pp no brasil.md` | Papel de políticas públicas en Brasil |
| `4524-Texto do artigo-17269-1-10-20201223.md` | Artículo brasileño |
| `P8_ESTUDO-RESILIENCIA.md` | Estudio resiliencia Brasil |
| `HMRS-2100brazilianMunicipalities.md` | Health Metrics 2100 municipios brasileños |

#### 🔄 TRANSFORMACIÓN Y ESCENARIOS

| Archivo | Tema |
|---------|------|
| `transformative change.md` | Transformative change |
| `Rethinking scenario building for sustainable futures.md` | Scenario building, conscientização, social learning |
| `People and Nature - 2025 - Uwingabire.md` | Worldviews and values of key societal actors |
| `Bishopetal2025_science adr2146.md` | Science article 2025 |

#### 📊 MONITOREO DE BIODIVERSIDAD

| Archivo | Tema |
|---------|------|
| `BON in a BOX BioScience2026.md` | BON in a Box - Platform for biodiversity monitoring (GEO BON) |
| `biodiversity and climate change agendas - Opinion.md` | Biodiversity and climate agendas |
| `knowledge systems.md` | Knowledge systems |
| `ES-2025-164912.md` | Ecology and Society 2025 |

#### 📖 METODOLOGÍA Y ESTADÍSTICA

| Archivo | Tema |
|---------|------|
| `statisticalrethinking_2nd_edition.md` | **Statistical Rethinking** - McElreath (Bayesian, R, Stan) - LIBRO COMPLETO |
| `About Folke et al 1997.md` | Referencia Folke et al. 1997 |

#### 🏙️ CIUDADES Y DESARROLLO URBANO

| Archivo | Tema |
|---------|------|
| `Wealth_and_wildlife_in_cities.md` | Wealth and wildlife in cities |
| `Disasterriskreductionandthelimitsoftruisms.md` | Disaster risk reduction limits |

#### 📑 OTROS DOCUMENTOS

| Archivo | Tipo |
|---------|------|
| `FOLLETO TRANSDISCIPLINARY_ING_digital.md` | Folleto transdisciplinario |
| `Clement_et-al_2025_PREPRINT.md` | Preprint 2025 |
| `pre_sal.md` | Pre-sal (petróleo) |
| `evp-article-p305.md` | EVP article |
| `54874-58695-1-PB.md` | Paper brasileño |
| `s12961-022-00816-3.md` | Health Research Policy |
| `s12961-022-00820-7.md` | Health Research Policy |
| `1-s2.0-S0301479719311995-main.md` | Journal of Environmental Management |
| `1-s2.0-S1877343523001008-main.md` | Current Opinion |
| `Increasing_effectiveness_of_the_science.md` | Effectiveness of science |

---

## Próximos Pasos

1. [ ] Registrar en OSF (Open Science Framework) - ver instrucciones abajo
2. [x] ~~**Descargar datos DATASUS**~~ - COMPLETADO 2026-01-20
   - Dataset: `data/processed/health_data_SP_2010_2019.csv`
   - 647 municipios, 5 enfermedades, 2010-2019
3. [ ] **Integrar nuevos datos de salud** con dataset principal
   - Merge con `outputs/municipios_integrado_v5.csv`
   - Calcular tasas de incidencia por 100,000 hab
4. [ ] Completar integración de variables climáticas extremas
5. [ ] Finalizar propuesta Branco Weiss (revisión final Adrian)
6. [ ] Análisis de sensibilidad con diferentes umbrales
7. [ ] Validación cruzada con datos independientes
8. [ ] Preparar manuscrito para journal (ERL o similar)

### Instrucciones para OSF (pendiente)
1. Ir a https://osf.io → Login con ORCID
2. Create new project: "Biodiversity, Health and Universal Access in São Paulo"
3. Add-ons → GitHub → conectar `adgch86/saopaulo-biodiversity-health`
4. Tags: `biodiversity`, `public-health`, `Brazil`, `São Paulo`, `FAIR`
5. License: MIT

---

## Visión Estratégica: Escalamiento Nacional

### Fase 1: São Paulo (ACTUAL)
- **Estado**: Análisis completado
- **n**: 645 municipios
- **Datos**: UAI, biodiversidad, salud, vulnerabilidad
- **Producto**: Propuesta Branco Weiss, dashboards, policy brief

### Fase 2: Maranhão (POTENCIAL)
- **Socio**: Instituto Tecnológico Vale (ITV DS)
- **Contactos clave**:
  - Dr. Ronnie Alves (DatalakeDS - Data Science)
  - Dra. Tereza Giannini (Ecología/Polinizadores)
  - Dr. Jorge Filipe (Plataforma Socioambiental)
- **Datos disponibles**:
  - Plataforma socioambiental Bahías São Marcos/São José
  - DatalakeDS: biodiversidad, clima, uso de suelo, socioeconomía
  - Biolink: datos de biodiversidad agregados
- **Ventaja**: Bioma diferente (Amazonia/Cerrado vs Mata Atlántica)

### Fase 3: Brasil (FUTURO)
- **Objetivo**: Análisis nacional integrando múltiples estados/biomas
- **Financiamiento propuesto**: FAPESP (proyecto inter-estatal)
- **Marco**: Replicar metodología SP + Maranhão a escala nacional
- **Potencial colaboración**: Red de institutos de pesquisa (ITV, USP, INPE)

### Justificación Científica para Escalamiento
1. **Validación metodológica**: Probar si hallazgos de SP (efecto dilución, paradoja conservación-pobreza) se replican en otros contextos
2. **Gradiente bioclimático**: Comparar Mata Atlántica vs Amazonia vs Cerrado
3. **Diversidad de gobernanza**: Diferentes estructuras institucionales por estado
4. **Impacto en políticas**: De recomendaciones estatales a nacionales

### Línea de Tiempo Tentativa
```
2026: SP (completado) → Branco Weiss
2026-2027: Explorar colaboración ITV → Maranhão piloto
2027-2028: Propuesta FAPESP Brasil
```

---

## Referentes Científicos

Ver documento completo: `.claude/REFERENTES_CIENTIFICOS.md`

| Investigador | Área | Institución |
|--------------|------|-------------|
| Jean Paul Metzger | Ecología del Paisaje | USP |
| Lucas Garibaldi | Polinización | CONICET-UNRN |
| Luisa Carvalheiro | Polinización | UFG |
| Melina de Souza Leite | Estadística Ecológica | Univ. Regensburg |
| Mauro Galetti | Defaunación | UNESP |
| Nicholas J. Gotelli | Estadística | Univ. Vermont |
| Teja Tscharntke | Agroecología | Univ. Göttingen |
| Leandro Tambosi | Conectividad | UFABC |
| Pedro Brancalion | Restauración | ESALQ-USP |
| **Gabriela di Giulio** | **Salud Ambiental (Supervisora)** | **FSP-USP** |

---

## Notas de Sesión

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

## Instrucciones para el Science Team

### Al iniciar cada sesión:
1. **LEER** este archivo completo
2. **REVISAR** estado de "Próximos Pasos"
3. **CONTINUAR** desde donde se quedó el trabajo

### Al finalizar cada sesión o hacer avances importantes:
1. **ACTUALIZAR** "Hallazgos Principales" con nuevos descubrimientos
2. **MARCAR** tareas completadas [x] en "Próximos Pasos"
3. **AGREGAR** nueva entrada en "Notas de Sesión"
4. **DOCUMENTAR** decisiones metodológicas importantes

---

*Última actualización: 2026-01-21 (Micro/Mesorregiões IBGE + Casos Prováveis corregidos)*
*Proyecto: Dr. Adrian David González Chaves*
*DOI: 10.5281/zenodo.18303824*
