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

*Última actualización: 2026-01-23*
