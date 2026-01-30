# Informe H6: Síntesis y Metadata de Variables

**Proyecto**: Nexus Biodiversidad-Clima-Salud-Gobernanza en São Paulo
**Investigador Principal**: Dr. Adrian David González Chaves
**Fecha de Análisis**: 29 de enero de 2026

---

## 1. Resumen del Dataset

| Estadístico | Valor |
|-------------|-------|
| **Total de variables** | 104 |
| **Total de municipios** | 645 |
| **Período de datos** | 2010-2019 |
| **Región** | Estado de São Paulo, Brasil |
| **Estructura jerárquica** | Municipio → Microrregión (63) → Mesorregión (15) |

---

## 2. Variables por Dimensión del Nexus

El marco conceptual del Nexus organiza las variables en 5 dimensiones principales más identificadores y clasificaciones.

```
         Gobernanza ←→ Biodiversidad
              ↓              ↓
         Riesgo Salud ←→ Riesgo Climático
                  ↘    ↙
              Vulnerabilidad Social
                  (central)
```

### 2.1 Conteo por Dimensión

| Dimensión | # Variables | % del Total |
|-----------|-------------|-------------|
| Identificadores | 6 | 5.8% |
| **Gobernanza** | **9** | **8.7%** |
| **Biodiversidad** | **7** | **6.7%** |
| **Riesgo Climático** | **18** | **17.3%** |
| **Riesgo Salud** | **49** | **47.1%** |
| **Vulnerabilidad Social** | **13** | **12.5%** |
| Clasificaciones | 2 | 1.9% |
| **TOTAL** | **104** | **100%** |

### 2.2 Detalle por Dimensión

#### Identificadores (6 variables)

| Variable | Descripción | Fuente |
|----------|-------------|--------|
| `cod_ibge` | Código IBGE del municipio (7 dígitos) | IBGE |
| `Municipio` | Nombre del municipio | IBGE |
| `cod_microrregiao` | Código de la microrregión | IBGE |
| `nome_microrregiao` | Nombre de la microrregión | IBGE |
| `cod_mesorregiao` | Código de la mesorregión | IBGE |
| `nome_mesorregiao` | Nombre de la mesorregión | IBGE |

#### Gobernanza (9 variables)

| Variable | Descripción | Fuente |
|----------|-------------|--------|
| `UAI_housing` | Índice de Adaptación Urbana - Vivienda (0-1) | Neder et al. 2021 |
| `UAI_env` | Índice de Adaptación Urbana - Ambiental (0-1) | Neder et al. 2021 |
| `UAI_food` | Índice de Adaptación Urbana - Alimentación (0-1) | Neder et al. 2021 |
| `UAI_mob` | Índice de Adaptación Urbana - Movilidad (0-1) | Neder et al. 2021 |
| `UAI_Crisk` | Índice de Adaptación Urbana - Riesgo Climático (0-1) | Neder et al. 2021 |
| `idx_gobernanza` | Índice compuesto = mean(UAI_*) (0-1) | Calculado |
| `idx_gobernanza_100` | Índice de gobernanza escalado 0-100 | Calculado |
| `esgoto_tratado` | Porcentaje de esgoto tratado | SNIS |
| `IDESP_ensino_medio` | Índice de Desarrollo de la Educación | SEADE |

#### Biodiversidad (7 variables)

| Variable | Descripción | Fuente |
|----------|-------------|--------|
| `mean_species_richness` | Riqueza media de especies de vertebrados | Datos pre-procesados |
| `max_species_richness` | Riqueza máxima de especies de vertebrados | Datos pre-procesados |
| `Vert_rich_risk` | Riesgo por pérdida de riqueza de vertebrados | Calculado |
| `forest_cover` | Porcentaje de cobertura forestal | MapBiomas |
| `pol_deficit` | Déficit de polinización (indicador de degradación) | Datos pre-procesados |
| `idx_biodiv` | Índice compuesto de biodiversidad (0-100) | Calculado |
| `tercil_biodiv` | Tercil de biodiversidad (1=bajo, 2=medio, 3=alto) | Calculado |

#### Riesgo Climático (18 variables)

| Variable | Descripción | Fuente |
|----------|-------------|--------|
| `flooding_exposure` | Exposición a inundaciones (área inundable) | MapBiomas/INPE |
| `flooding_risks` | Índice de riesgo de inundación | Calculado |
| `hydric_stress_exp` | Exposición a estrés hídrico | ANA |
| `hydric_stress_risk` | Índice de riesgo de estrés hídrico | Calculado |
| `idx_clima` | Índice compuesto de riesgo climático (0-100) | Calculado |
| `tercil_clima` | Tercil de riesgo climático | Calculado |
| `fire_incidence_mean` | Incidencia media anual de focos de fuego | INPE Queimadas |
| `fire_incidence_max` | Incidencia máxima anual de focos de fuego | INPE Queimadas |
| `fire_frp_mean` | Potencia radiativa del fuego (FRP) media | INPE Queimadas |
| `fire_frp_max` | FRP máxima registrada | INPE Queimadas |
| `fire_total_foci` | Total de focos de fuego 2010-2019 | INPE Queimadas |
| `fire_frp_total` | FRP total acumulada | INPE Queimadas |
| `fire_years_with_fire` | Años con registro de fuego (0-10) | INPE Queimadas |
| `fire_recurrence` | Recurrencia de fuego (proporción de años) | Calculado |
| `fire_cv` | Coeficiente de variación de incidencia de fuego | Calculado |
| `fire_dry_season_pct` | Porcentaje de focos en época seca | INPE Queimadas |
| `fire_max_consecutive_years` | Años consecutivos máximos con fuego | Calculado |
| `fire_risk_index` | Índice compuesto de riesgo de fuego | Calculado |

#### Riesgo Salud (49 variables)

**Enfermedades Vectoriales - Persistencia (5 vars)**

| Variable | Descripción | Fuente |
|----------|-------------|--------|
| `persist_dengue` | Años con casos de dengue (0-10) | DATASUS/SINAN |
| `persist_leishmaniose` | Años con casos de leishmaniasis (0-10) | DATASUS/SINAN |
| `persist_leptospirose` | Años con casos de leptospirosis (0-10) | DATASUS/SINAN |
| `persist_malaria` | Años con casos de malaria (0-10) | DATASUS/SINAN |
| `persist_diarrhea` | Años con casos de diarrea (0-10) | DATASUS/SINAN |

**Incidencia Media (5 vars)**

| Variable | Descripción | Fuente |
|----------|-------------|--------|
| `incidence_mean_dengue` | Incidencia media de dengue (por 100k hab/año) | DATASUS/SINAN |
| `incidence_mean_leishmaniose` | Incidencia media de leishmaniasis | DATASUS/SINAN |
| `incidence_mean_leptospirose` | Incidencia media de leptospirosis | DATASUS/SINAN |
| `incidence_mean_malaria` | Incidencia media de malaria | DATASUS/SINAN |
| `incidence_diarrhea_mean` | Incidencia media de diarrea | DATASUS/SINAN |

**Incidencia Máxima (5 vars)** - `incidence_max_*`

**Total de Casos (5 vars)** - `total_cases_*`

**Co-presencia de Enfermedades (9 vars)**

| Variable | Descripción |
|----------|-------------|
| `copresence_years` | Años con 2+ enfermedades vectoriales simultáneas |
| `copresence_3plus` | Años con 3+ enfermedades vectoriales |
| `copresence_all4` | Años con las 4 enfermedades vectoriales |
| `dengue_leptospirose` | Co-ocurrencia dengue-leptospirosis |
| `dengue_malaria` | Co-ocurrencia dengue-malaria |
| ... | (y otras combinaciones) |

**Hospitalización (9 vars)** - `health_hosp_*` (circulatorias, respiratorias, calor)

**Mortalidad (9 vars)** - `health_death_*` (circulatorias, respiratorias, calor)

**Índices (2 vars)**

| Variable | Descripción |
|----------|-------------|
| `idx_carga_enfermedad` | Índice de carga de enfermedad (0-100) |
| `mort_infantil` | Tasa de mortalidad infantil (por 1000 nacidos vivos) |

#### Vulnerabilidad Social (13 variables)

| Variable | Descripción | Fuente |
|----------|-------------|--------|
| `population` | Población total del municipio | IBGE SIDRA |
| `pct_rural` | Porcentaje de población rural | IBGE Censo |
| `pct_urbana` | Porcentaje de población urbana | IBGE Censo |
| `population_preta` | Población que se autodeclara negra | IBGE Censo |
| `population_branca` | Población que se autodeclara blanca | IBGE Censo |
| `population_indigena` | Población que se autodeclara indígena | IBGE Censo |
| `pct_pobreza` | Porcentaje de población en pobreza | IBGE/CadÚnico |
| `pct_preta` | Porcentaje de población negra | IBGE Censo |
| `pct_indigena` | Porcentaje de población indígena | IBGE Censo |
| `n_personas_pobreza` | Número de personas en pobreza | CadÚnico |
| `n_familias_rua` | Número de familias en situación de calle | CadÚnico |
| `idx_vulnerabilidad` | Índice de vulnerabilidad socioeconómica (0-100) | Calculado |
| `tercil_vuln` | Tercil de vulnerabilidad | Calculado |

#### Clasificaciones (2 variables)

| Variable | Descripción |
|----------|-------------|
| `grupo_clima_biodiv` | Grupo combinado clima-biodiversidad |
| `cuadrante` | Cuadrante gobernanza-vulnerabilidad |

---

## 3. Variables por Componente de Riesgo (IPCC)

El marco IPCC define el riesgo como función de tres componentes:

```
                 ┌──────────────┐
                 │   HAZARD     │
                 │  (Amenaza)   │
                 └──────┬───────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   ┌─────────┐     ┌─────────┐    ┌─────────────┐
   │EXPOSURE │     │  RISK   │    │VULNERABILITY│
   │(Expuesto)│ ←→ │(Riesgo) │ ←→ │(Sensibilidad│
   └─────────┘     └─────────┘    │+ Capacidad) │
                                  └─────────────┘
```

### 3.1 Conteo por Componente

| Componente | # Variables | Descripción |
|------------|-------------|-------------|
| **HAZARD** | 31 | Evento físico peligroso (amenaza) |
| **EXPOSURE** | 32 | Población/activos en zona de riesgo |
| **VULNERABILITY - Sensibilidad** | 6 | Factores que aumentan vulnerabilidad |
| **VULNERABILITY - Cap. Natural** | 4 | Ecosistemas que reducen vulnerabilidad |
| **VULNERABILITY - Cap. Institucional** | 9 | Gobernanza que reduce vulnerabilidad |
| **RISK INDICES** | 5 | Índices compuestos (H×E×V) |

### 3.2 HAZARD - Amenazas/Peligros (31 vars)

Variables que representan el evento físico peligroso o la presencia del agente de enfermedad.

**Amenazas Climáticas:**
- `flooding_exposure`, `hydric_stress_exp`
- `fire_incidence_*`, `fire_frp_*`, `fire_total_foci`
- `fire_years_with_fire`, `fire_recurrence`, `fire_cv`
- `fire_dry_season_pct`, `fire_max_consecutive_years`

**Amenazas de Salud (patógenos/vectores):**
- `incidence_mean_*`, `incidence_max_*` (dengue, malaria, leishmaniasis, leptospirosis, diarrea)
- `persist_*` (persistencia de cada enfermedad)
- `copresence_*` (co-ocurrencia de enfermedades)

### 3.3 EXPOSURE - Exposición (32 vars)

Variables que representan la población expuesta y la manifestación de exposición.

**Población Expuesta:**
- `population`, `pct_rural`, `pct_urbana`
- `population_preta`, `population_branca`, `population_indigena`
- `pct_preta`, `pct_indigena`

**Manifestación de Exposición (morbilidad/mortalidad):**
- `health_hosp_*` (hospitalizaciones por causa)
- `health_death_*` (mortalidad por causa)
- `total_cases_*` (casos totales de enfermedades)
- `mort_infantil`

### 3.4 VULNERABILITY - Vulnerabilidad (19 vars total)

#### Sensibilidad (aumenta vulnerabilidad) - 6 vars

| Variable | Descripción |
|----------|-------------|
| `pct_pobreza` | Porcentaje de población en pobreza |
| `n_personas_pobreza` | Número de personas en pobreza |
| `n_familias_rua` | Familias en situación de calle |
| `idx_vulnerabilidad` | Índice de vulnerabilidad socioeconómica |
| `Vert_rich_risk` | Riesgo por pérdida de biodiversidad |
| `pol_deficit` | Déficit de polinización |

#### Capacidad Adaptativa Natural (reduce vulnerabilidad) - 4 vars

| Variable | Descripción |
|----------|-------------|
| `forest_cover` | Cobertura forestal (%) |
| `mean_species_richness` | Riqueza de especies |
| `max_species_richness` | Riqueza máxima de especies |
| `idx_biodiv` | Índice de biodiversidad |

#### Capacidad Adaptativa Institucional (reduce vulnerabilidad) - 9 vars

| Variable | Descripción |
|----------|-------------|
| `UAI_housing` | Capacidad en vivienda |
| `UAI_env` | Gestión ambiental |
| `UAI_food` | Seguridad alimentaria |
| `UAI_mob` | Movilidad urbana |
| `UAI_Crisk` | Gestión de riesgo climático |
| `idx_gobernanza` | Índice de gobernanza |
| `idx_gobernanza_100` | Gobernanza (0-100) |
| `esgoto_tratado` | Saneamiento |
| `IDESP_ensino_medio` | Educación |

### 3.5 RISK INDICES - Índices Compuestos (5 vars)

| Índice | Descripción | Fórmula Conceptual |
|--------|-------------|-------------------|
| `flooding_risks` | Riesgo de inundación | flooding_exposure × población × (1 - gobernanza) |
| `hydric_stress_risk` | Riesgo de estrés hídrico | hydric_stress × demanda × (1 - capacidad) |
| `fire_risk_index` | Riesgo de incendio | fire_incidence × recurrence × intensidad |
| `idx_clima` | Índice climático compuesto | normalize(flooding + hydric_stress) |
| `idx_carga_enfermedad` | Carga de enfermedad | normalize(Σ incidencias) |

---

## 4. Mapeo Cruzado: Nexus × IPCC

| Dimensión Nexus | HAZARD | EXPOSURE | VULNERABILITY |
|-----------------|:------:|:--------:|:-------------:|
| **Gobernanza** | - | - | ✓ Cap. Institucional |
| **Biodiversidad** | - | - | ✓ Cap. Natural |
| **Riesgo Climático** | ✓ | - | - |
| **Riesgo Salud** | ✓ Patógenos | ✓ Morbilidad | - |
| **Vulnerabilidad Social** | - | ✓ Población | ✓ Sensibilidad |

---

## 5. Síntesis de Análisis H1-H5

### 5.1 Resumen de Hallazgos por Hipótesis

| Hipótesis | Pregunta | Mejor Predictor | R²m | Hallazgo Clave |
|-----------|----------|-----------------|-----|----------------|
| **H1** | ¿Qué predice gobernanza? | % Pobreza | 27% | Gobernanza es **reactiva** a riesgos |
| **H2** | ¿Vulnerabilidad modula? | Pobreza × Estrés Hídrico | - | Pobreza **anula** respuesta reactiva |
| **H3** | ¿Clima × Salud interactúan? | Hosp.Resp × Estrés Hídrico | 14% | Efectos mixtos (sinergia +/-) |
| **H4** | ¿Qué predice salud? | % Rural (dengue) | 43% | Efecto bosque-dengue **confundido** |
| **H5** | ¿Qué predice riesgo climático? | % Pobreza (fuego) | 31% | **Desarrollo → +riesgo** climático |

### 5.2 Variables Más Importantes (por frecuencia como mejor predictor)

| Variable | Dimensión | Veces Mejor Predictor | Contextos |
|----------|-----------|----------------------|-----------|
| `pct_pobreza` | Vulnerabilidad | 5+ | Gobernanza, Fuego, Estrés Hídrico, Mortalidad |
| `forest_cover` | Biodiversidad | 3 | Malaria (+), Diarrea (-), Hosp. Respiratoria (-) |
| `pct_rural` | Vulnerabilidad | 2 | Dengue (-), Estrés Hídrico (-) |
| `pol_deficit` | Biodiversidad | 2 | Gobernanza (-), Inundación (-) |
| `idx_gobernanza` | Gobernanza | 2 | Como outcome y moderador |

### 5.3 Interacciones Más Significativas

| Interacción | Outcome | ΔAIC | Interpretación |
|-------------|---------|------|----------------|
| Pobreza × Estrés Hídrico | Gobernanza | **-55.8** | Pobreza anula gobernanza reactiva |
| Gobernanza × Pobreza | Estrés Hídrico | **-32.9** | Gobernanza más efectiva en pobres |
| Déficit Pol. × Pobreza | Inundación | -17.9 | Biodiversidad protege menos en pobres |
| Hosp.Resp × Estrés Hídrico | Gobernanza | -7.7 | Sobrecarga institucional |
| Malaria × Bosque | UAI Ambiental | -9.8 | Control de malaria mejora gestión |

### 5.4 Conclusión Integradora

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODELO CONCEPTUAL DEL NEXUS                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    [DESARROLLO]                    [RIESGO CLIMÁTICO]                   │
│         │                                  │                            │
│         ▼                                  ▼                            │
│    Mayor riqueza  ──────────────────► Mayor fuego                       │
│    Urbanización  ───────────────────► Mayor estrés hídrico              │
│                                                                         │
│         │                                  │                            │
│         ▼                                  ▼                            │
│    [GOBERNANZA REACTIVA]          [EFECTOS EN SALUD]                   │
│         │                                  │                            │
│         │◄─────────────────────────────────┘                            │
│         │                                                               │
│         ▼                                                               │
│    PERO: Pobreza ────► BLOQUEA respuesta reactiva                       │
│                                                                         │
│    IMPLICACIÓN: Municipios pobres NO desarrollan gobernanza             │
│                 naturalmente ante riesgos → requieren intervención      │
│                 externa                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Actualización de Fuentes de Datos

### 6.1 Fuentes Principales

| Fuente | Variables | Período | Acceso |
|--------|-----------|---------|--------|
| **DATASUS/SINAN** | Enfermedades notificables | 2010-2019 | FTP público |
| **DATASUS/SIH** | Hospitalizaciones | 2010-2019 | FTP público |
| **DATASUS/SIM** | Mortalidad | 2010-2019 | FTP público |
| **IBGE** | Población, demografía | 2010-2019 | SIDRA API |
| **Neder et al. 2021** | UAI (gobernanza) | Snapshot | Publicación |
| **MapBiomas** | Cobertura forestal | 2010-2019 | GEE |
| **INPE Queimadas** | Focos de fuego | 2010-2019 | Portal BDQ |
| **ANA** | Estrés hídrico | Variable | SNIRH |

### 6.2 Cálculo de Índices Compuestos

| Índice | Fórmula |
|--------|---------|
| `idx_gobernanza` | mean(UAI_housing, UAI_env, UAI_food, UAI_mob, UAI_Crisk) |
| `idx_biodiv` | normalize(forest_cover) + normalize(species_richness) - normalize(pol_deficit) |
| `idx_clima` | normalize(flooding_risks) + normalize(hydric_stress_risk) |
| `idx_vulnerabilidad` | normalize(pct_pobreza) + normalize(1-esgoto_tratado) + ... |
| `idx_carga_enfermedad` | normalize(Σ incidencias de todas las enfermedades) |

---

## 7. Archivos Generados

### Tablas
- `h6_variable_table.csv` - Tabla completa de 104 variables con metadata
- `h6_nexus_counts.csv` - Conteo por dimensión del Nexus
- `h6_risk_counts.csv` - Conteo por componente de riesgo IPCC

### Informes Generados (H1-H6)
- `outputs/h1_gobernanza/INFORME_H1_GOBERNANZA.md`
- `outputs/h2_vulnerabilidad/INFORME_H2_INTERACCIONES.md`
- `outputs/h3_clima_salud/INFORME_H3_CLIMA_SALUD.md`
- `outputs/h4_salud/INFORME_H4_SALUD.md`
- `outputs/h5_clima/INFORME_H5_CLIMA.md`
- `outputs/h6_sintesis/INFORME_H6_SINTESIS.md` (este archivo)

---

## 8. Recomendaciones para Futuros Análisis

1. **Priorizar variables simples sobre índices compuestos** - Los análisis H1-H5 mostraron que las variables simples (pct_pobreza, forest_cover, pct_rural) tienen mejor desempeño predictivo que los índices.

2. **Validar efectos de dilución** - Como se demostró en H4, siempre controlar por población/urbanización cuando se analice cobertura forestal.

3. **Considerar interacciones** - Las interacciones Vulnerabilidad × otras dimensiones son tan importantes como los efectos principales.

4. **Diseño longitudinal** - Los datos actuales son transversales; un panel temporal permitiría evaluar causalidad.

5. **Análisis espacial** - Los mapas bivariados generados sugieren patrones espaciales que merecen análisis de autocorrelación.

---

*Informe generado por Science Team - Nexus Assessment São Paulo*
*29 de enero de 2026*
