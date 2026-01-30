# Datos y Metodología - Science Team

> Este archivo documenta las fuentes de datos, procesamiento y metodología.
> Para contexto actual: `SCIENCE_TEAM_CONTEXT.md`

---

## Datos del Estudio

- **Unidad de análisis**: Municipios de São Paulo, Brasil
- **n = 645 municipios**
- **Período**: 2010-2019
- **Marco conceptual**: Levers et al. (2025), Barreto et al. (2025)

---

## Estructura de Directorios

```
data/
├── raw/                    # Datos crudos
│   ├── 2026_01_14/        # Datos recientes
│   └── datasus/           # Archivos DBC originales
│       ├── sinan/         # SINAN (enfermedades notificables)
│       ├── sih/           # SIH (hospitalizaciones)
│       └── sim/           # SIM (mortalidad)
├── processed/             # Datos procesados
│   ├── health_*.csv       # Indicadores de salud
│   ├── fire_*.csv         # Indicadores de fuego
│   ├── diarrhea_*.csv     # Indicadores de diarrea
│   └── populacao_*.csv    # Población IBGE
├── geo/
│   └── ibge_sp/           # Shapefile IBGE 2022 (645 municipios)
└── metadata_v6.json       # Metadata trilingüe
```

---

## Fuentes de Datos

### 1. DATASUS - SINAN (Enfermedades Vectoriales)

| Enfermedad | Casos 2010-2019 | Archivos |
|------------|-----------------|----------|
| Dengue | 2,221,108 | DENGSP10-19 |
| Leptospirose | 44,806 | LEPTSP10-19 |
| Malaria | 3,400 | MALASP10-19 |
| Leish. Visceral | 4,611 | LEIVSP10-19 |
| Leish. Tegumentar | 3,471 | LTASP10-19 |

**Filtros aplicados:**
- `CLASSI_FIN != 5` (excluir descartados)
- `ID_MN_RESI` (municipio de residencia)
- Excluir código 350000 (MUNICIPIO IGNORADO)

**Archivo resultante:** `health_casos_provaveis_SP_2010_2019_regioes.csv`

### 2. DATASUS - SIH (Hospitalizaciones por Calor)

| Categoría CID-10 | Hospitalizaciones | Período |
|------------------|-------------------|---------|
| Circulatorias (I00-I99) | 2,671,894 | 2010-2019 |
| Respiratorias (J00-J99) | 2,391,281 | 2010-2019 |
| Efectos calor (T67) | 31 | 2010-2019 |

**Archivos:** 120 archivos mensuales (~1.8 GB)

### 3. DATASUS - SIM (Mortalidad)

| Categoría CID-10 | Óbitos | Período |
|------------------|--------|---------|
| Circulatorias (I00-I99) | 844,306 | 2010-2019 |
| Respiratorias (J00-J99) | 379,214 | 2010-2019 |

**Archivos:** 10 archivos anuales (~226 MB)

### 4. IBGE - Población y Regiones

- **Fuente:** SIDRA API (Tabla 6579)
- **Variables:** Población por municipio 2010-2019
- **Regiones:** 15 mesorregiões, 63 microrregiões
- **Archivo:** `populacao_SP_2010_2019.csv`

### 5. Biodiversidad

- **Riqueza de vertebrados:** mean_species_richness, max_species_richness
- **Cobertura forestal:** forest_cover (%)
- **Déficit polinización:** pol_deficit
- **Fuente:** Datos pre-procesados

### 6. Gobernanza - UAI (Urban Adaptation Index)

| Componente | Variable | Descripción |
|------------|----------|-------------|
| Vivienda | UAI_housing | Capacidad adaptativa vivienda |
| Ambiental | UAI_env | Gestión ambiental |
| Alimentación | UAI_food | Seguridad alimentaria |
| Movilidad | UAI_mob | Infraestructura movilidad |
| Riesgo | UAI_Crisk | Gestión riesgo climático |

**Referencia:** Neder et al. (2021)

### 7. Indicadores de Fuego (INPE)

- **Fuente:** INPE Queimadas
- **Variables:** fire_incidence_mean, fire_frp_mean, fire_risk_index
- **Período:** 2010-2019

### 8. Estrés Térmico (Xavier/BR-DWGD v3) - NUEVO v9

- **Fuente:** Xavier et al. (2022). Brazilian Daily Weather Gridded Data v3
- **Resolución:** 0.1° x 0.1° (~11 km) para Tmax/Tmin
- **Período:** 2010-2019 (diario)
- **Variables:**
  - heat_persistence_mean: Días/año con Tmax > 34.7°C (promedio decadal)
  - heat_persistence_sd: Desviación estándar interanual
  - heat_HAAT_mean: Grados-día acumulados sobre 34.7°C (promedio anual)
  - heat_HAAT_sd: Desviación estándar interanual
  - mmt_days_mean: Días/año con Tmedia > 22.3°C (promedio decadal)
  - mmt_days_sd: Desviación estándar interanual
- **Referencia:** Xavier et al. (2022), Int J Climatol. DOI: 10.1002/joc.7731
- **Acceso:** GEE Community Catalog (`projects/br-dwgd/assets/`)
- **Licencia:** CC BY 4.0
- **Umbrales:**
  - 34.7°C: Valverde (2023) → media ondas de calor SP = 34.9°C
  - 22.3°C: Nascimento et al. (2019) → MMT para IAM región SE

### 9. Temperatura de Superficie (MODIS LST) - NUEVO v9

- **Fuente:** MODIS/061/MOD11A2 (Terra) + MYD11A2 (Aqua)
- **Resolución:** 1 km
- **Período:** 2010-2019 (compuesto 8 días)
- **Variables:**
  - lst_day_mean: LST diurna media (°C, promedio decadal)
  - lst_night_mean: LST nocturna media (°C, promedio decadal)
  - lst_day_p95: Percentil 95 LST diurna
  - lst_day_sd: Desviación estándar LST diurna
  - lst_amplitude: Amplitud térmica día-noche
- **Referencia:** Monteiro et al. (2021), Wu et al. (2019)
- **Acceso:** GEE (`MODIS/061/MOD11A2`)
- **Nota:** LST mide temperatura de superficie, no aire. Es la métrica directa para islas de calor urbano (SUHI). SP tiene SUHI diurna de 6.60°C

---

## Indicadores Calculados

### Indicadores de Salud (por enfermedad)

| Indicador | Fórmula | Descripción |
|-----------|---------|-------------|
| persist_X | Σ(años con casos > 0) | Persistencia (0-10) |
| incidence_mean_X | Σ(casos/pop×100k)/10 | Incidencia media |
| incidence_max_X | max(casos/pop×100k) | Incidencia máxima |
| total_cases_X | Σ(casos) | Casos totales |

### Indicadores de Co-presencia

| Indicador | Descripción |
|-----------|-------------|
| copresence_years | Años con 2+ enfermedades |
| copresence_3plus | Años con 3+ enfermedades |
| copresence_all4 | Años con las 4 enfermedades |

### Índices Compuestos

| Índice | Componentes | Escala |
|--------|-------------|--------|
| idx_gobernanza | Promedio UAI (5 componentes) | 0-1 |
| idx_biodiv | Riqueza + Cobertura + Polinización | 0-100 |
| idx_clima | Inundación + Estrés hídrico | 0-100 |
| idx_vulnerabilidad | Pobreza + Rural + Demografía | 0-100 |
| idx_carga_enfermedad | Incidencia normalizada | 0-100 |

---

## Scripts de Procesamiento

| Script | Descripción |
|--------|-------------|
| `download_datasus_direct.py` | Descarga FTP DATASUS |
| `process_dbc_files.R` | Procesamiento DBC |
| `calculate_health_indicators.R` | Indicadores de salud |
| `calculate_diarrhea_indicators.py` | Indicadores diarrea |
| `create_integrated_dataset_v8.py` | Dataset integrado |

---

## Validación de Datos

### Comparación con TABNET (Sesión 18)

| Enfermedad | Correlación | Estado |
|------------|-------------|--------|
| Dengue | r = 1.0000 | ✅ VALIDADO |
| Diarrea | r = 1.0000 | ✅ VALIDADO |
| Leptospirose | r = 0.9674 | Diferente criterio |
| Malaria | r = 0.7909 | Diferente criterio |
| Leishmaniasis | r = 0.7566 | Diferente criterio |

**Nota:** Diferencias en Leptospirose, Malaria y Leishmaniasis se deben a uso de "Casos Confirmados" vs "Casos Prováveis".

---

## Cuadrantes de Clasificación

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

## Referencias Metodológicas Clave

1. **Barreto et al. (2025)** - Efecto dilución Amazonía
   - DOI: 10.1038/s43247-025-02620-7
   - Adrian González-Chaves es co-autor

2. **Levers et al. (2025)** - Marco 5 dimensiones agrifood
   - DOI: 10.1088/1748-9326/ae20ac

3. **Neder et al. (2021)** - UAI Urban Adaptation Index
   - Base metodológica para gobernanza

---

---

## Clasificación de Variables por Dimensión del Nexus

El dataset contiene **104 variables** organizadas en 5 dimensiones principales:

### Conteo por Dimensión

| Dimensión | # Variables |
|-----------|-------------|
| Identificadores | 6 |
| **Gobernanza** | 9 |
| **Biodiversidad** | 7 |
| **Riesgo Climático** | 18 |
| **Riesgo Salud** | 49 |
| **Vulnerabilidad Social** | 13 |
| Clasificaciones | 2 |
| **TOTAL** | 104 |

### Diagrama del Nexus

```
         Gobernanza ←→ Biodiversidad
              ↓              ↓
         Riesgo Salud ←→ Riesgo Climático
                  ↘    ↙
              Vulnerabilidad Social
                  (central)
```

---

## Clasificación por Componentes de Riesgo (IPCC)

| Componente | # Variables | Descripción |
|------------|-------------|-------------|
| **HAZARD** | 31 | Amenazas físicas (fuego, inundación, patógenos) |
| **EXPOSURE** | 32 | Población expuesta, morbilidad, mortalidad |
| **VULNERABILITY** | 19 | Sensibilidad (6) + Cap. Natural (4) + Cap. Institucional (9) |
| **RISK INDICES** | 5 | Índices compuestos H×E×V |

### Diagrama IPCC

```
       HAZARD ←──────→ EXPOSURE
           ↘              ↙
              RISK
           ↙              ↘
    VULNERABILITY ←→ VULNERABILITY
    (Sensibilidad)   (Cap. Adaptativa)
```

---

## Catálogo Completo de Variables

### Variables de Gobernanza

| Variable | Descripción | Fuente | Escala |
|----------|-------------|--------|--------|
| `UAI_housing` | Capacidad adaptativa vivienda | Neder et al. 2021 | 0-1 |
| `UAI_env` | Gestión ambiental | Neder et al. 2021 | 0-1 |
| `UAI_food` | Seguridad alimentaria | Neder et al. 2021 | 0-1 |
| `UAI_mob` | Movilidad urbana | Neder et al. 2021 | 0-1 |
| `UAI_Crisk` | Gestión riesgo climático | Neder et al. 2021 | 0-1 |
| `idx_gobernanza` | mean(UAI_*) | Calculado | 0-1 |
| `idx_gobernanza_100` | Gobernanza escalada | Calculado | 0-100 |
| `esgoto_tratado` | % esgoto tratado | SNIS | % |
| `IDESP_ensino_medio` | Índice educación | SEADE | index |

### Variables de Biodiversidad

| Variable | Descripción | Fuente | Escala |
|----------|-------------|--------|--------|
| `forest_cover` | Cobertura forestal | MapBiomas | % |
| `mean_species_richness` | Riqueza especies vertebrados | Pre-procesado | count |
| `max_species_richness` | Riqueza máxima vertebrados | Pre-procesado | count |
| `pol_deficit` | Déficit polinización | Pre-procesado | index |
| `Vert_rich_risk` | Riesgo pérdida riqueza | Calculado | index |
| `idx_biodiv` | Índice biodiversidad | Calculado | 0-100 |
| `tercil_biodiv` | Tercil biodiversidad | Calculado | 1-3 |

### Variables de Riesgo Climático

| Variable | Descripción | Fuente | Escala |
|----------|-------------|--------|--------|
| `flooding_exposure` | Exposición inundaciones | MapBiomas/INPE | index |
| `flooding_risks` | Riesgo inundación | Calculado | index |
| `hydric_stress_exp` | Exposición estrés hídrico | ANA | index |
| `hydric_stress_risk` | Riesgo estrés hídrico | Calculado | index |
| `fire_incidence_mean` | Incidencia media fuego | INPE | rate |
| `fire_risk_index` | Riesgo compuesto fuego | Calculado | index |
| `idx_clima` | Índice riesgo climático | Calculado | 0-100 |

### Variables de Vulnerabilidad Social

| Variable | Descripción | Fuente | Escala |
|----------|-------------|--------|--------|
| `population` | Población total | IBGE SIDRA | count |
| `pct_rural` | % población rural | IBGE Censo | % |
| `pct_pobreza` | % en pobreza | CadÚnico | % |
| `pct_preta` | % población negra | IBGE Censo | % |
| `pct_indigena` | % población indígena | IBGE Censo | % |
| `idx_vulnerabilidad` | Índice vulnerabilidad | Calculado | 0-100 |

### Variables de Riesgo Salud (principales)

| Variable | Descripción | Fuente | Escala |
|----------|-------------|--------|--------|
| `incidence_mean_dengue` | Incidencia dengue | DATASUS/SINAN | por 100k/año |
| `incidence_mean_malaria` | Incidencia malaria | DATASUS/SINAN | por 100k/año |
| `incidence_mean_leishmaniose` | Incidencia leishmaniasis | DATASUS/SINAN | por 100k/año |
| `incidence_mean_leptospirose` | Incidencia leptospirosis | DATASUS/SINAN | por 100k/año |
| `incidence_diarrhea_mean` | Incidencia diarrea | DATASUS/SINAN | por 100k/año |
| `health_hosp_resp_mean` | Hosp. respiratorias | DATASUS/SIH | rate |
| `health_death_circ_mean` | Mort. cardiovascular | DATASUS/SIM | rate |
| `persist_*` | Años con casos (0-10) | Calculado | count |
| `copresence_*` | Co-ocurrencia enfermedades | Calculado | count |

---

## Hallazgos Principales del Análisis (H1-H5)

### H1: ¿Qué predice gobernanza?
- **Mejor predictor**: `pct_pobreza` (β = -0.43, R²m = 27%)
- **Hallazgo**: Gobernanza es **reactiva** a riesgos (más riesgo → más gobernanza)

### H2: ¿Vulnerabilidad modula?
- **Interacción más fuerte**: Pobreza × Estrés Hídrico (ΔAIC = -55.8)
- **Hallazgo**: Pobreza **anula** la respuesta reactiva a riesgos

### H3: ¿Clima × Salud interactúan?
- **Interacción inesperada**: Hosp.Resp × Estrés Hídrico (p = 0.002)
- **Hallazgo**: Efectos mixtos (sinergias positivas y negativas)

### H4: ¿Qué predice salud?
- **Mejor predictor dengue**: `pct_rural` (β = -0.22, R²m = 43%)
- **Hallazgo**: Efecto bosque-dengue está **confundido** por urbanización (36% cambio con controles)

### H5: ¿Qué predice riesgo climático?
- **Mejor predictor fuego**: `pct_pobreza` (β = -5.55, negativo)
- **Hallazgo**: Desarrollo económico → **mayor** riesgo climático (paradoja)

---

*Última actualización: 2026-01-29 (+ Análisis H1-H6 completo)*
