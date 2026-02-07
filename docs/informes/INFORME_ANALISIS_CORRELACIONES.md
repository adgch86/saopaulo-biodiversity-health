# INFORME DE ANALISIS: Correlaciones Multidimensionales y Cuadrantes de Riesgo
## Municipios del Estado de Sao Paulo, Brasil

**Fecha de analisis:** Enero 2026
**Datos analizados:** 645 municipios (dataset completo) + 187 municipios (con datos de salud)

---

## 1. DESCRIPCION DE LOS DATOS

### 1.1 Fuentes de Datos

| Dataset | Registros | Variables Principales |
|---------|-----------|----------------------|
| 645 sin salud.csv | 645 municipios | Biodiversidad, riesgos climaticos, UAI, deficit politico |
| 187 con salud.csv | 187 municipios | Incidencia de enfermedades, persistencia, copersistencia |

### 1.2 Variables Analizadas por Dimension

#### BIODIVERSIDAD
- `mean_species_richness`: Riqueza media de especies (rango: 350-755)
- `max_species_richness`: Riqueza maxima de especies
- `Vert_rich_risk`: Riesgo para vertebrados

#### RIESGOS CLIMATICOS
- `flooding_exposure`: Exposicion a inundaciones
- `flooding_risks`: Riesgo de inundaciones
- `hydric_stress_exp`: Exposicion a estres hidrico
- `hydric_stress_risk`: Riesgo de estres hidrico

#### INDICE DE ACCESO UNIVERSAL (UAI)
- `UAI_housing`: Acceso a vivienda
- `UAI_env`: Acceso ambiental
- `UAI_food`: Acceso a alimentacion
- `UAI_mob`: Acceso a movilidad
- `UAI_Crisk`: Riesgo climatico UAI

#### POLITICAS PUBLICAS
- `pol_deficit`: Deficit politico (0-1, donde 1 = mayor deficit)

#### SALUD (187 municipios)
- `persist_malaria/dengue/diarrhea/leptospirose/chagas`: Persistencia de enfermedades
- `incidence_*`: Incidencia de enfermedades
- `copersistence`: Indice de copersistencia de enfermedades
- `social_vulnerability`: Vulnerabilidad social

#### DEMOGRAFIA
- `population`: Poblacion total
- `pct_rural`: Porcentaje de poblacion rural
- `pct_urbana`: Porcentaje de poblacion urbana

---

## 2. ANALISIS DE CORRELACIONES (645 MUNICIPIOS)

### 2.1 Metodologia
- **Metodo**: Correlacion de Spearman (datos no normales)
- **Criterios de significancia**: p < 0.05 y |r| > 0.30
- **Total correlaciones significativas encontradas**: 23

### 2.2 Matriz de Correlaciones Completa

```
                       Biodiv  Vert_risk  Flood_risk  Hydric_risk  UAI_hous  UAI_env  UAI_food  UAI_mob  UAI_Crisk  Rural%  Pol_deficit
Biodiv                  1.000    -0.763       0.272        0.225     0.130    0.075    -0.037    0.322      0.256   -0.051       -0.567
Vert_risk              -0.763     1.000      -0.029       -0.139     0.058    0.065     0.089   -0.041     -0.071   -0.063        0.380
Flood_risk              0.272    -0.029       1.000        0.101     0.203    0.114    -0.020    0.263      0.264   -0.077       -0.353
Hydric_risk             0.225    -0.139       0.101        1.000     0.225    0.133    -0.056    0.299      0.161   -0.457       -0.083
UAI_hous                0.130     0.058       0.203        0.225     1.000    0.395     0.102    0.507      0.440   -0.415       -0.123
UAI_env                 0.075     0.065       0.114        0.133     0.395    1.000     0.195    0.416      0.416   -0.312       -0.054
UAI_food               -0.037     0.089      -0.020       -0.056     0.102    0.195     1.000    0.116      0.103    0.154       -0.010
UAI_mob                 0.322    -0.041       0.263        0.299     0.507    0.416     0.116    1.000      0.482   -0.475       -0.225
UAI_Crisk               0.256    -0.071       0.264        0.161     0.440    0.416     0.103    0.482      1.000   -0.301       -0.242
Rural%                 -0.051    -0.063      -0.077       -0.457    -0.415   -0.312     0.154   -0.475     -0.301    1.000       -0.049
Pol_deficit            -0.567     0.380      -0.353       -0.083    -0.123   -0.054    -0.010   -0.225     -0.242   -0.049        1.000
```

### 2.3 Top 23 Correlaciones Significativas (ordenadas por |r|)

| Rank | Variable 1 | Variable 2 | r (Spearman) | p-value | Fuerza |
|------|------------|------------|--------------|---------|--------|
| 1 | mean_species_richness | Vert_rich_risk | -0.763 | 3.30e-124 | Fuerte |
| 2 | UAI_mob | population | 0.725 | 5.14e-106 | Fuerte |
| 3 | pct_rural | population | -0.625 | 4.41e-71 | Fuerte |
| 4 | UAI_housing | population | 0.583 | 6.87e-60 | Fuerte |
| 5 | mean_species_richness | pol_deficit | -0.567 | 3.43e-56 | Fuerte |
| 6 | UAI_housing | UAI_mob | 0.507 | 1.87e-43 | Fuerte |
| 7 | hydric_stress_risk | population | 0.500 | 3.72e-42 | Fuerte |
| 8 | UAI_Crisk | population | 0.492 | 1.39e-40 | Moderada |
| 9 | UAI_mob | UAI_Crisk | 0.482 | 7.20e-39 | Moderada |
| 10 | UAI_mob | pct_rural | -0.475 | 1.28e-37 | Moderada |
| 11 | hydric_stress_risk | pct_rural | -0.457 | 1.13e-34 | Moderada |
| 12 | UAI_housing | UAI_Crisk | 0.440 | 6.08e-32 | Moderada |
| 13 | UAI_env | population | 0.417 | 1.69e-28 | Moderada |
| 14 | UAI_env | UAI_mob | 0.416 | 2.45e-28 | Moderada |
| 15 | UAI_env | UAI_Crisk | 0.416 | 2.29e-28 | Moderada |
| 16 | UAI_housing | pct_rural | -0.415 | 2.71e-28 | Moderada |
| 17 | UAI_housing | UAI_env | 0.395 | 1.59e-25 | Moderada |
| 18 | Vert_rich_risk | pol_deficit | 0.380 | 1.55e-23 | Moderada |
| 19 | mean_species_richness | population | 0.371 | 1.66e-22 | Moderada |
| 20 | flooding_risks | pol_deficit | -0.353 | 2.04e-20 | Moderada |
| 21 | mean_species_richness | UAI_mob | 0.322 | 4.84e-17 | Moderada |
| 22 | UAI_env | pct_rural | -0.312 | 4.60e-16 | Moderada |
| 23 | UAI_Crisk | pct_rural | -0.301 | 5.80e-15 | Moderada |

---

## 3. ANALISIS DE CORRELACIONES CON SALUD (187 MUNICIPIOS)

### 3.1 Metodologia
- **Municipios analizados**: 187 (con datos epidemiologicos)
- **Variables de salud**: copersistence, incidence_dengue, incidence_diarrhea, incidence_malaria, persist_dengue
- **Criterios**: p < 0.05 y |r| > 0.20

### 3.2 Correlaciones Significativas Salud vs Otras Dimensiones

| Variable Salud | Variable Otra | r | p-value | n |
|----------------|---------------|---|---------|---|
| incidence_malaria | UAI | **-0.593** | 3.81e-19 | 187 |
| incidence_diarrhea | UAI | -0.460 | 3.49e-11 | 187 |
| incidence_dengue | UAI | -0.432 | 6.58e-10 | 187 |
| copersistence | flooding_risks | 0.277 | 1.27e-04 | 187 |
| copersistence | hydric_stress_risk | 0.275 | 1.38e-04 | 187 |
| incidence_dengue | hydric_stress_risk | 0.216 | 2.93e-03 | 187 |
| persist_dengue | hydric_stress_risk | 0.208 | 4.33e-03 | 187 |

### 3.3 Interpretacion de Hallazgos de Salud

1. **UAI como factor protector**: Las tres principales enfermedades (malaria, diarrea, dengue) muestran correlacion negativa fuerte con el UAI, indicando que el acceso universal a servicios basicos reduce significativamente la incidencia de enfermedades.

2. **Riesgos climaticos y copersistencia**: La copersistencia de enfermedades esta positivamente correlacionada con riesgos de inundacion y estres hidrico, sugiriendo que los eventos climaticos extremos aumentan la carga de enfermedad.

3. **Dengue y estres hidrico**: Tanto la incidencia como la persistencia de dengue correlacionan con estres hidrico, posiblemente por cambios en patrones de almacenamiento de agua.

---

## 4. ANALISIS DE CUADRANTES

### 4.1 Metodologia
- **Ejes**: UAI promedio (media de 5 componentes UAI) vs Riqueza de especies
- **Division**: Medianas
  - Mediana UAI promedio: 0.354
  - Mediana Biodiversidad: 620.0 especies

### 4.2 Distribucion de Municipios por Cuadrante

| Cuadrante | Descripcion | N | Porcentaje |
|-----------|-------------|---|------------|
| Q1_Modelo | Alto UAI + Alta Biodiversidad | 195 | 30.2% |
| Q2_Conservar | Bajo UAI + Alta Biodiversidad | 128 | 19.8% |
| Q3_Vulnerable | Bajo UAI + Baja Biodiversidad | 192 | 29.8% |
| Q4_Desarrollo | Alto UAI + Baja Biodiversidad | 130 | 20.2% |

### 4.3 Estadisticas por Cuadrante

| Cuadrante | Biodiv (media) | UAI (media) | Deficit Pol. | Riesgo Comp. | Rural% |
|-----------|----------------|-------------|--------------|--------------|--------|
| Q1_Modelo | 689.8 | 0.559 | 0.813 | 0.696 | 12.5% |
| Q2_Conservar | 680.2 | 0.244 | 0.856 | 0.544 | 19.2% |
| Q3_Vulnerable | 566.4 | 0.236 | **0.950** | 0.459 | 14.1% |
| Q4_Desarrollo | 551.5 | 0.521 | 0.893 | 0.555 | 8.2% |

### 4.4 Municipios Destacados por Cuadrante

#### Q1 - MUNICIPIOS MODELO (Top 10 por UAI)
| Municipio | Biodiversidad | UAI | Deficit Pol. | Riesgo |
|-----------|---------------|-----|--------------|--------|
| Piracicaba | 698.8 | 0.960 | 0.947 | 0.61 |
| Cordeiropolis | 692.1 | 0.900 | 0.978 | 0.68 |
| Sorocaba | 697.3 | 0.886 | 0.909 | 1.48 |
| Sao Jose dos Campos | 730.6 | 0.860 | 0.898 | 0.36 |
| Indaiatuba | 712.7 | 0.860 | 0.952 | 0.70 |
| Botucatu | 674.3 | 0.856 | 0.899 | 0.68 |
| Braganca Paulista | 719.0 | 0.856 | 0.911 | 0.97 |
| Jundiai | 714.1 | 0.830 | 0.874 | 0.73 |
| Itatiba | 746.3 | 0.830 | 0.903 | 0.69 |
| Socorro | 694.7 | 0.816 | 0.932 | 0.47 |

#### Q2 - PRIORIDAD CONSERVACION (Top 10 por Biodiversidad)
| Municipio | Biodiversidad | UAI | Deficit Pol. | Riesgo |
|-----------|---------------|-----|--------------|--------|
| Aruja | 755.5 | 0.316 | 0.689 | 0.66 |
| Aracariguama | 755.3 | 0.254 | 0.658 | 0.60 |
| Igarata | 753.6 | 0.180 | 0.793 | 0.50 |
| Salto de Pirapora | 746.9 | 0.350 | 0.909 | 0.44 |
| Aparecida | 746.2 | 0.286 | 0.938 | 0.44 |
| Pirapora do Bom Jesus | 743.5 | 0.170 | 0.717 | 0.47 |
| Roseira | 738.6 | 0.330 | 0.970 | 0.65 |
| Cachoeira Paulista | 737.8 | 0.210 | 0.952 | 0.45 |
| Cacapava | 736.3 | 0.336 | 0.955 | 0.44 |
| Nazare Paulista | 735.9 | 0.256 | 0.695 | 0.63 |

#### Q3 - MUNICIPIOS VULNERABLES (Top 10 por Riesgo)
| Municipio | Biodiversidad | UAI | Deficit Pol. | Riesgo |
|-----------|---------------|-----|--------------|--------|
| Cafelandia | 594.0 | 0.040 | 0.937 | 0.91 |
| Pacaembu | 490.3 | 0.296 | 0.978 | 0.87 |
| Parapua | 543.5 | 0.346 | 0.978 | 0.86 |
| Palmares Paulista | 591.9 | 0.266 | 0.903 | 0.77 |
| Santa Ernestina | 564.8 | 0.314 | 0.989 | 0.70 |
| Vista Alegre do Alto | 583.7 | 0.320 | 0.941 | 0.70 |
| Monte Aprazivel | 613.0 | 0.220 | 0.967 | 0.70 |
| Elisiario | 604.9 | 0.324 | 0.961 | 0.69 |
| Urupes | 604.1 | 0.130 | 0.962 | 0.68 |
| Guararapes | 539.9 | 0.216 | 0.978 | 0.68 |

#### Q4 - DESARROLLO SIN CONSERVACION (Top 10 por UAI)
| Municipio | Biodiversidad | UAI | Deficit Pol. | Riesgo |
|-----------|---------------|-----|--------------|--------|
| Sao Paulo | 565.1 | 0.886 | 0.580 | 1.44 |
| Santos | 608.6 | 0.846 | 0.497 | 1.35 |
| Sao Vicente | 616.1 | 0.800 | 0.840 | 0.63 |
| Presidente Epitacio | 424.4 | 0.780 | 0.982 | 0.35 |
| Sao Jose do Rio Preto | 554.1 | 0.780 | 0.950 | 0.74 |
| Sertaozinho | 569.4 | 0.756 | 0.958 | 0.71 |
| Franca | 604.2 | 0.756 | 0.894 | 0.64 |
| Penapolis | 567.7 | 0.750 | 0.974 | 0.69 |
| Presidente Venceslau | 458.1 | 0.746 | 0.986 | 0.41 |
| Jaboticabal | 570.8 | 0.740 | 0.975 | 0.44 |

---

## 5. INTERPRETACION PARA POLITICAS PUBLICAS

### 5.1 Hallazgos Clave

#### BIODIVERSIDAD Y GOBERNANZA
- **Correlacion fuerte negativa (r = -0.57)** entre biodiversidad y deficit politico
- **Implicacion**: Los municipios con mejor gobernanza tienden a conservar mejor su biodiversidad
- **Recomendacion**: Fortalecer capacidades institucionales como estrategia de conservacion

#### SALUD Y ACCESO UNIVERSAL
- **Correlacion fuerte negativa (r = -0.59)** entre incidencia de malaria y UAI
- **Implicacion**: Mejorar el acceso universal reduce significativamente la carga de enfermedad
- **Recomendacion**: Priorizar inversiones en UAI como politica de salud publica

#### RIESGOS CLIMATICOS Y SALUD
- **Correlacion positiva (r = 0.28)** entre copersistencia de enfermedades y riesgos climaticos
- **Implicacion**: Los eventos climaticos extremos exacerban problemas de salud
- **Recomendacion**: Integrar politicas de adaptacion climatica con politicas de salud

#### UAI Y RURALIDAD
- **Correlacion negativa fuerte (r = -0.48)** entre UAI_movilidad y porcentaje rural
- **Implicacion**: Las zonas rurales tienen menor acceso a servicios
- **Recomendacion**: Politicas diferenciadas para municipios rurales

### 5.2 Priorizacion de Intervenciones

#### ALTA PRIORIDAD - Q3 (Vulnerable)
- **192 municipios** con bajo UAI Y baja biodiversidad
- Presentan el **MAYOR deficit politico (0.95)**
- **Accion urgente**: Inversion en infraestructura basica, fortalecimiento institucional, y restauracion ecologica

#### MEDIA-ALTA PRIORIDAD - Q2 (Conservar)
- **128 municipios** con alta biodiversidad pero bajo UAI
- **Oportunidad critica**: Proteger biodiversidad mientras se mejora acceso
- **Accion**: Programas de desarrollo sostenible que no comprometan capital natural

#### MEDIA PRIORIDAD - Q4 (Desarrollo)
- **130 municipios** con alto UAI pero baja biodiversidad
- **Desafio**: Desarrollo historico a costa del ambiente
- **Accion**: Programas de restauracion ecologica urbana, infraestructura verde

#### MONITOREO - Q1 (Modelo)
- **195 municipios** con buen desempeno en ambas dimensiones
- **Accion**: Estudiar y replicar practicas exitosas

### 5.3 Recomendaciones Especificas

1. **Politicas Integradas**: Disenar intervenciones que aborden simultaneamente biodiversidad, salud y acceso, dado que estan interrelacionadas.

2. **Focalizacion Territorial**: Priorizar los 192 municipios del Q3 (vulnerables) para intervenciones urgentes.

3. **Gobernanza Ambiental**: Reducir el deficit politico como estrategia indirecta de conservacion de biodiversidad.

4. **Adaptacion Climatica**: Integrar politicas de salud con adaptacion al cambio climatico, especialmente en zonas con alto riesgo de inundacion.

5. **Equidad Rural-Urbana**: Implementar politicas diferenciadas para cerrar brechas de acceso en municipios rurales.

---

## 6. ARCHIVOS GENERADOS

| Archivo | Descripcion |
|---------|-------------|
| heatmap_correlaciones.png | Matriz de correlaciones visualizada |
| cuadrantes_analisis.png | Graficos de analisis de cuadrantes (3 paneles) |
| df_sin_cuadrantes.pkl | Dataset con clasificacion de municipios |
| df_sin_parsed.pkl | Dataset 645 municipios procesado |
| df_salud_parsed.pkl | Dataset 187 municipios procesado |
| df_merged.pkl | Dataset combinado |

---

## 7. LIMITACIONES DEL ANALISIS

1. **Causalidad**: Las correlaciones no implican causalidad; se requieren estudios adicionales para establecer relaciones causales.

2. **Variables omitidas**: Las variables codificadas (de201, ge101, etc.) no fueron incluidas por falta de diccionario de datos.

3. **Temporalidad**: Los datos representan un corte transversal; no capturan dinamicas temporales.

4. **Escala**: El analisis es a nivel municipal; puede haber heterogeneidad intra-municipal no capturada.

---

## 8. REFERENCIAS METODOLOGICAS

- **Correlacion de Spearman**: Utilizada por la no normalidad de los datos
- **Umbral de significancia**: p < 0.05 con correccion implicita por interpretacion conservadora (|r| > 0.30)
- **Clasificacion de cuadrantes**: Basada en medianas para robustez ante outliers

---

*Documento generado automaticamente a partir del analisis de datos.*
*Para mas informacion, consultar los archivos de datos y graficos generados.*
