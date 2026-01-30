# Informe H5: Predictores de Riesgo Climático

**Proyecto**: Nexus Biodiversidad-Clima-Salud-Gobernanza en São Paulo
**Investigador Principal**: Dr. Adrian David González Chaves
**Fecha de Análisis**: 29 de enero de 2026

---

## 1. Objetivo del Análisis

**Pregunta central**: ¿Qué factores de vulnerabilidad, biodiversidad y gobernanza predicen la exposición a riesgos climáticos?

```
H5: Riesgo_Clima ~ Vulnerabilidad × (Biodiversidad + Gobernanza)
```

El riesgo climático representa la amenaza directa más evidente de los cambios climáticos. Identificar sus predictores permite anticipar qué municipios estarán más expuestos.

---

## 2. Metodología

### 2.1 Especificación del Modelo

```
Riesgo_Clima ~ predictor + (1|microrregião)
```

Para interacciones:
```
Riesgo_Clima ~ Biodiversidad/Gobernanza × Vulnerabilidad + (1|microrregião)
```

### 2.2 Variables Analizadas

| Rol | Variables |
|-----|-----------|
| **Outcomes (Y)** | flooding_risks, fire_risk_index, hydric_stress_risk |
| **Predictores - Vulnerabilidad** | pct_pobreza, pct_rural, pct_preta, pct_indigena |
| **Predictores - Biodiversidad** | forest_cover, mean_species_richness, pol_deficit |
| **Predictores - Gobernanza** | idx_gobernanza, UAI_env, UAI_Crisk |

### 2.3 Total de Modelos

- **Modelos principales**: 3 outcomes × 10 predictores = 30 modelos
- **Modelos de interacción**: 3 outcomes × 6 predictores × 4 moderadores = 72 modelos
- **Total**: 102 modelos evaluados

---

## 3. Resultados: Selección de Modelos

### 3.1 Riesgo de Inundación (flooding_risks)

| Rank | Predictor | Dimensión | β | p | ΔAIC | R²m |
|------|-----------|-----------|---|---|------|-----|
| **1** | **Déficit Polinización** | **Biodiversidad** | **-0.072** | **<0.001** | **0.00** | **26.3%** |
| 2 | Gobernanza (idx) | Gobernanza | +0.037 | <0.001 | 17.71 | 23.7% |
| 3 | UAI Riesgo Clim. | Gobernanza | +0.037 | <0.001 | 18.03 | 23.6% |
| 4 | Cobertura Forestal | Biodiversidad | +0.061 | <0.001 | 19.82 | 24.2% |
| 5 | % Pob. Negra | Vulnerabilidad | +0.034 | <0.001 | 24.56 | 22.9% |
| 6 | % Rural | Vulnerabilidad | -0.030 | <0.001 | 27.78 | 22.2% |
| 7 | % Pobreza | Vulnerabilidad | -0.024 | 0.004 | 30.71 | 22.3% |
| 8 | Riqueza Especies | Biodiversidad | +0.030 | 0.013 | 32.73 | 22.1% |
| 9 | UAI Ambiental | Gobernanza | +0.016 | 0.042 | 34.67 | 21.8% |
| 10 | % Pob. Indígena | Vulnerabilidad | -0.001 | 0.932 | 38.81 | 21.3% |

**Interpretación**: El déficit de polinización (indicador de degradación ambiental) es el mejor predictor de riesgo de inundación. Paradójicamente, **mayor degradación → menor riesgo**, posiblemente porque las zonas degradadas están en terrenos altos/secos mientras que las zonas conservadas están en valles fluviales.

### 3.2 Riesgo de Fuego (fire_risk_index)

| Rank | Predictor | Dimensión | β | p | ΔAIC | R²m |
|------|-----------|-----------|---|---|------|-----|
| **1** | **% Pobreza** | **Vulnerabilidad** | **-5.55** | **<0.001** | **0.00** | **31.0%** |
| 2 | Gobernanza (idx) | Gobernanza | +3.99 | <0.001 | 74.54 | 25.6% |
| 3 | Déficit Polinización | Biodiversidad | +4.69 | <0.001 | 88.13 | 27.7% |
| 4 | UAI Ambiental | Gobernanza | +1.95 | <0.001 | 131.17 | 22.3% |
| 5 | UAI Riesgo Clim. | Gobernanza | +1.84 | <0.001 | 135.85 | 21.7% |
| 6 | % Rural | Vulnerabilidad | -1.75 | <0.001 | 139.61 | 21.9% |
| 7 | % Pob. Negra | Vulnerabilidad | +1.14 | 0.025 | 146.03 | 21.3% |
| 8 | Cobertura Forestal | Biodiversidad | -1.35 | 0.087 | 148.25 | 21.5% |
| 9 | Riqueza Especies | Biodiversidad | +1.11 | 0.119 | 148.56 | 21.0% |
| 10 | % Pob. Indígena | Vulnerabilidad | -0.62 | 0.144 | 148.87 | 21.1% |

**Interpretación**: El coeficiente negativo de pobreza indica que **municipios menos pobres tienen más riesgo de fuego**. Esto refleja la realidad agroindustrial de São Paulo: las zonas prósperas (caña de azúcar, pastos) usan fuego para manejo de tierras.

### 3.3 Estrés Hídrico (hydric_stress_risk)

| Rank | Predictor | Dimensión | β | p | ΔAIC | R²m |
|------|-----------|-----------|---|---|------|-----|
| **1** | **% Pobreza** | **Vulnerabilidad** | **-0.062** | **<0.001** | **0.00** | **26.0%** |
| 2 | % Rural | Vulnerabilidad | -0.048 | <0.001 | 71.16 | 17.6% |
| 3 | Riqueza Especies | Biodiversidad | +0.035 | <0.001 | 122.61 | 11.5% |
| 4 | Gobernanza (idx) | Gobernanza | +0.025 | <0.001 | 126.80 | 11.2% |
| 5 | UAI Riesgo Clim. | Gobernanza | +0.016 | 0.002 | 141.88 | 9.3% |
| 6 | % Pob. Indígena | Vulnerabilidad | -0.014 | 0.003 | 142.28 | 9.4% |
| 7 | UAI Ambiental | Gobernanza | +0.011 | 0.031 | 146.47 | 8.8% |
| 8 | % Pob. Negra | Vulnerabilidad | +0.010 | 0.071 | 147.90 | 8.4% |
| 9 | Cobertura Forestal | Biodiversidad | -0.007 | 0.304 | 150.06 | 8.4% |
| 10 | Déficit Polinización | Biodiversidad | +0.005 | 0.385 | 150.35 | 8.5% |

**Interpretación**: El estrés hídrico es mayor en zonas **urbanas, desarrolladas y menos pobres**, reflejando la alta demanda de agua en las zonas metropolitanas.

---

## 4. Resumen: Mejores Predictores por Riesgo Climático

| Riesgo Climático | Mejor Predictor | Dimensión | β | p | R²m |
|-----------------|-----------------|-----------|---|---|-----|
| **Inundación** | Déficit Polinización | Biodiversidad | **-0.072** | <0.001 | 26.3% |
| **Fuego** | % Pobreza | Vulnerabilidad | **-5.55** | <0.001 | 31.0% |
| **Estrés Hídrico** | % Pobreza | Vulnerabilidad | **-0.062** | <0.001 | 26.0% |

---

## 5. Resultados: Análisis de Interacciones

### 5.1 Interacciones Significativas (p < 0.05)

Se identificaron **25 interacciones significativas** de 72 evaluadas (35%).

#### Top 10 por Mejora de Ajuste (ΔAIC)

| Predictor | Moderador | Outcome | β_int | p | ΔAIC |
|-----------|-----------|---------|-------|---|------|
| **Gobernanza** | **% Pobreza** | **Estrés Hídrico** | **-0.032** | **<0.001** | **-32.9** |
| Déficit Pol. | % Pobreza | Inundación | +0.047 | <0.001 | -17.9 |
| Déficit Pol. | % Rural | Fuego | -1.89 | <0.001 | -15.0 |
| UAI Ambiental | % Pobreza | Estrés Hídrico | -0.019 | <0.001 | -14.7 |
| UAI_Crisk | % Pob. Negra | Inundación | +0.029 | <0.001 | -14.1 |
| UAI_Crisk | % Pobreza | Estrés Hídrico | -0.019 | <0.001 | -11.0 |
| Gobernanza | % Rural | Inundación | -0.031 | <0.001 | -11.0 |
| Gobernanza | % Pob. Negra | Inundación | +0.027 | <0.001 | -10.3 |
| UAI_Crisk | % Pobreza | Inundación | -0.031 | <0.001 | -9.2 |
| Gobernanza | % Pobreza | Inundación | -0.031 | <0.001 | -9.0 |

### 5.2 Detalle: Gobernanza × Pobreza → Estrés Hídrico

**La interacción más significativa de H5 (ΔAIC = -32.9)**

```
Estrés_Hídrico = -0.018 × Gobernanza
               - 0.081 × Pobreza
               - 0.032 × (Gobernanza × Pobreza)
               + intercepto
```

| Estadístico | Valor |
|-------------|-------|
| β interacción | **-0.032** |
| SE | 0.005 |
| p-valor | **<0.001** |
| ΔAIC | **-32.9** |
| R² marginal | 29.8% |

**Interpretación por Simple Slopes**:
- En municipios **no pobres**: Gobernanza tiene efecto cercano a cero sobre estrés hídrico
- En municipios **pobres**: Mayor gobernanza → **menor estrés hídrico** (efecto protector)

Esto sugiere que la **inversión en gobernanza es más "rentable"** en municipios vulnerables para reducir estrés hídrico.

### 5.3 Detalle: Déficit Polinización × Pobreza → Inundación

```
Inundación = -0.054 × Déficit_Pol
           - 0.038 × Pobreza
           + 0.047 × (Déficit_Pol × Pobreza)
           + intercepto
```

| Estadístico | Valor |
|-------------|-------|
| β interacción | **+0.047** |
| p-valor | **<0.001** |
| ΔAIC | **-17.9** |

**Interpretación**:
- En municipios **no pobres**: Menor déficit (más biodiversidad) → menor riesgo de inundación
- En municipios **pobres**: El efecto protector de la biodiversidad **se atenúa**

La biodiversidad protege contra inundaciones, pero este efecto es menor en zonas de alta pobreza.

---

## 6. Hallazgo Paradójico: Gobernanza Reactiva

**Mayor gobernanza está asociada a MAYOR riesgo climático** en los 3 tipos de riesgo:

| Riesgo | Gobernanza (idx) | UAI Ambiental | UAI Riesgo Clim. |
|--------|------------------|---------------|------------------|
| Inundación | +0.037*** | +0.016* | +0.037*** |
| Fuego | +3.99*** | +1.95*** | +1.84*** |
| Estrés Hídrico | +0.025*** | +0.011* | +0.016** |

**Interpretación**: Esto **no significa** que la gobernanza cause riesgo. Significa que los municipios desarrollan capacidad institucional **en respuesta a** riesgos climáticos que ya enfrentan. Refuerza el hallazgo de H1 sobre **gobernanza reactiva**.

---

## 7. Síntesis de Hallazgos

### 7.1 Patrones Identificados

| Patrón | Riesgos | Explicación |
|--------|---------|-------------|
| **Desarrollo → +Riesgo** | Fuego, Estrés Hídrico | Zonas agroindustriales y metropolitanas |
| **Conservación → +Inundación** | Inundación | Zonas forestales en valles fluviales |
| **Gobernanza reactiva** | Todos | Respuesta institucional, no prevención |
| **Biodiversidad protectora (condicionada)** | Inundación | Solo efectiva en municipios no pobres |

### 7.2 Diagrama Conceptual

```
┌─────────────────────────────────────────────────────────────────────┐
│                 PREDICTORES DE RIESGO CLIMÁTICO                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   INUNDACIÓN                                                        │
│   ├─ Déficit Polinización (-) → Zonas degradadas = terrenos altos   │
│   ├─ Cobertura Forestal (+) → Bosques en valles fluviales           │
│   └─ Gobernanza (+) → Respuesta reactiva                            │
│                                                                     │
│   FUEGO                                                             │
│   ├─ Pobreza (-) → Zonas agroindustriales prósperas                 │
│   ├─ Gobernanza (+) → Desarrollo implica quema agrícola             │
│   └─ Déficit Polinización (+) → Agricultura intensiva               │
│                                                                     │
│   ESTRÉS HÍDRICO                                                    │
│   ├─ Pobreza (-) → Zonas urbanas/metropolitanas                     │
│   ├─ Ruralidad (-) → Ciudades demandan más agua                     │
│   └─ Gobernanza (+) → Desarrollo = más consumo                      │
│                                                                     │
│   INTERACCIÓN CLAVE: Gobernanza × Pobreza → Estrés Hídrico          │
│   └─ Gobernanza reduce estrés hídrico SOLO en municipios pobres     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8. Implicaciones para Políticas Públicas

### 8.1 Focalización de Intervenciones

| Riesgo | Municipios Prioritarios | Intervención Sugerida |
|--------|------------------------|----------------------|
| **Inundación** | Alta cobertura forestal + baja gobernanza | Sistemas de alerta temprana |
| **Fuego** | Agroindustriales prósperos | Regulación de quema controlada |
| **Estrés Hídrico** | Metropolitanos + pobres | Gestión de demanda + gobernanza |

### 8.2 Eficiencia de la Gobernanza

La interacción Gobernanza × Pobreza muestra que:
- En municipios **ricos**: La gobernanza no reduce significativamente el estrés hídrico (ya tienen infraestructura)
- En municipios **pobres**: La gobernanza tiene **alto retorno** en reducción de estrés hídrico

**Recomendación**: Priorizar inversión en capacidad institucional en municipios vulnerables.

---

## 9. Conexión con Hipótesis Anteriores

| Hipótesis | Hallazgo | Conexión con H5 |
|-----------|----------|-----------------|
| **H1** | Riesgo → +Gobernanza | H5 confirma: gobernanza es reactiva |
| **H2** | Pobreza atenúa respuesta | H5: Pobreza modula efecto de biodiversidad |
| **H3** | Clima × Salud → efectos mixtos | H5: Riesgos climáticos en zonas desarrolladas |
| **H4** | Bosque → +Malaria | H5: Bosque → +Inundación (zonas húmedas) |

---

## 10. Limitaciones

1. **Causalidad invertida**: La gobernanza puede ser consecuencia, no causa, del riesgo
2. **Definición de variables**: Los índices de riesgo combinan hazard, exposición y vulnerabilidad
3. **Escala temporal**: Los riesgos climáticos tienen efectos acumulativos no capturados
4. **Paradoja del desarrollo**: Las relaciones positivas requieren cautela interpretativa
5. **Fuego agrícola vs. incendio**: El índice de fuego incluye quema controlada

---

## 11. Archivos Generados

### Tablas
- `h5_all_models.csv` - 30 modelos principales
- `h5_best_predictors.csv` - 3 mejores predictores
- `h5_interactions.csv` - 72 modelos de interacción

### Figuras - Scatter Plots
- `figures/h5_scatter_pobreza_fire.png` - % Pobreza → Riesgo Fuego
- `figures/h5_scatter_pol_deficit_fire.png` - Déficit Pol. → Riesgo Fuego
- `figures/h5_scatter_pol_deficit_floodings.png` - Déficit Pol. → Inundación
- `figures/h5_scatter_pobreza_hydric_stress.png` - % Pobreza → Estrés Hídrico
- `figures/h5_scatter_gobernanza_fire.png` - Gobernanza → Riesgo Fuego
- `figures/h5_scatter_forest_cover_floodings.png` - Cobertura Forestal → Inundación

### Figuras - Mapas Bivariados
- `figures/h5_bivar_floodings_pol_defici.png` - Inundación × Déficit Polinización
- `figures/h5_bivar_floodings_gobernanza.png` - Inundación × Gobernanza
- `figures/h5_bivar_floodings_UAI_Crisk.png` - Inundación × UAI Riesgo Climático
- `figures/h5_bivar_floodings_forest_cov.png` - Inundación × Cobertura Forestal
- `figures/h5_bivar_floodings_preta.png` - Inundación × % Población Negra
- `figures/h5_bivar_floodings_rural.png` - Inundación × % Rural

---

## 12. Conclusiones

### 12.1 Hallazgo Principal

**El riesgo climático no sigue el patrón esperado de "pobres = más vulnerables"**:
- **Fuego y Estrés Hídrico**: Mayor en zonas desarrolladas (agroindustria, metrópolis)
- **Inundación**: Mayor en zonas conservadas (valles fluviales con bosque)
- **Gobernanza**: Es reactiva a los riesgos, no preventiva

### 12.2 Implicación Clave

La **interacción Gobernanza × Pobreza** (ΔAIC = -32.9) demuestra que invertir en capacidad institucional en municipios pobres tiene alto retorno en reducción de estrés hídrico. Esto complementa H2: mientras la pobreza atenúa la respuesta institucional natural (H2), la inversión externa en gobernanza puede compensar esta brecha (H5).

---

*Informe generado por Science Team - Nexus Assessment São Paulo*
*29 de enero de 2026*
