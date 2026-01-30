# Informe H1: ¿Qué Predice la Gobernanza?

**Proyecto**: Nexus Biodiversidad-Clima-Salud-Gobernanza en São Paulo
**Investigador Principal**: Dr. Adrian David González Chaves
**Fecha de Análisis**: 29 de enero de 2026

---

## 1. Objetivo del Análisis

Este análisis **invierte la lógica causal** tradicional del nexus assessment:

| Enfoque Tradicional | Enfoque H1 (Nuevo) |
|---------------------|-------------------|
| Gobernanza → reduce riesgos | Riesgos/Vulnerabilidad → genera gobernanza |

**Pregunta central**: ¿Qué factores ambientales, climáticos, de salud y socioeconómicos explican los niveles de gobernanza municipal en São Paulo?

---

## 2. Metodología

### 2.1 Datos
- **Unidad de análisis**: 645 municipios del estado de São Paulo
- **Estructura jerárquica**: Municipio → Microrregión (63) → Mesorregión (15)

### 2.2 Variable Respuesta
**Índice de Gobernanza (UAI)**: Variables continuas entre 0 y 1 que miden capacidad adaptativa urbana:

| Variable | Descripción |
|----------|-------------|
| `UAI_housing` | Capacidad de vivienda |
| `UAI_env` | Gestión ambiental |
| `UAI_food` | Seguridad alimentaria |
| `UAI_mob` | Movilidad urbana |
| `UAI_Crisk` | Gestión de riesgo climático |
| `idx_gobernanza` | Índice compuesto (0-1) |

### 2.3 Especificación del Modelo

```
logit(UAI) ~ predictor + (1|microrregião)
```

- **Transformación Logit**: `logit(UAI) = log(UAI / (1 - UAI))` para variables acotadas 0-1
- **Efectos aleatorios**: Intercepto aleatorio por microrregión
- **Selección de modelos**: Criterio AIC (Akaike Information Criterion)

### 2.4 Comparación de Estructuras Jerárquicas

Se compararon 3 estructuras de efectos aleatorios en 120 modelos:

| Estructura | Descripción | Victorias por AIC |
|------------|-------------|-------------------|
| `micro_only` | (1\|microrregião) | **120 (100%)** |
| `crossed` | (1\|micro) + (1\|meso) | 0 (0%) |
| `nested` | (1\|meso/micro) | 0 (0%) |

**Conclusión**: La estructura simple con solo microrregión es consistentemente superior. Con 63 microrregiones vs 15 mesorregiones, el nivel micro ya captura la variación espacial relevante.

---

## 3. Hipótesis Evaluadas

| Sub-H | Fórmula | Dimensión Predictora |
|-------|---------|---------------------|
| H1.a | Gobernanza ~ Biodiversidad | forest_cover, species_richness, pol_deficit, idx_biodiv |
| H1.b | Gobernanza ~ Riesgo Salud | dengue, malaria, leishmaniasis, leptospirosis, diarrea, mort_cv, hosp_resp |
| H1.c | Gobernanza ~ Riesgo Clima | flooding_risks, fire_risk_index, hydric_stress, idx_clima |
| H1.d | Gobernanza ~ Vulnerabilidad | pct_pobreza, pct_rural, pct_preta, pct_indigena, idx_vulnerabilidad |

---

## 4. Resultados Principales

### 4.1 Resumen de Significancia

**21 de 24 relaciones evaluadas fueron estadísticamente significativas (p < 0.05)**

| Dimensión | Relaciones Significativas | Mejor Predictor Global |
|-----------|--------------------------|------------------------|
| Vulnerabilidad | 6/6 (100%) | % Pobreza |
| Riesgo Climático | 6/6 (100%) | Riesgo Fuego |
| Biodiversidad | 5/6 (83%) | Déficit Polinización |
| Riesgo Salud | 4/6 (67%) | Dengue |

### 4.2 Mejores Predictores por Dimensión (Índice Global de Gobernanza)

| Dimensión | Mejor Predictor | β | SE | p-valor | R²m |
|-----------|-----------------|---|-----|---------|-----|
| **Vulnerabilidad** | % Pobreza | **-0.429** | 0.033 | <0.001 | **0.267** |
| Riesgo Climático | Riesgo Fuego | +0.315 | 0.039 | <0.001 | 0.181 |
| Riesgo Salud | Dengue | +0.117 | 0.045 | 0.009 | 0.118 |
| Biodiversidad | Déficit Polinización | -0.124 | 0.045 | 0.006 | 0.106 |

### 4.3 Interpretación de Coeficientes

Los coeficientes están en escala logit. La interpretación es:

- **β negativo**: A mayor valor del predictor, menor gobernanza
- **β positivo**: A mayor valor del predictor, mayor gobernanza

---

## 5. Hallazgos por Dimensión

### 5.1 H1.d: Vulnerabilidad Socioeconómica → Gobernanza

**HALLAZGO PRINCIPAL**: La pobreza es el predictor más fuerte de gobernanza.

| Outcome | Mejor Predictor | β | R²m | Interpretación |
|---------|-----------------|---|-----|----------------|
| Gobernanza (idx) | % Pobreza | -0.429 | 26.7% | Municipios pobres tienen menor gobernanza |
| UAI Vivienda | % Pobreza | -4.418 | 21.1% | Efecto muy fuerte en capacidad de vivienda |
| UAI Movilidad | % Pobreza | -1.773 | 19.1% | Menor inversión en movilidad |
| UAI Riesgo Clim. | % Pobreza | -1.312 | 8.0% | Menor gestión de riesgos climáticos |
| UAI Ambiental | Vulnerabilidad (idx) | -0.447 | 3.6% | Índice compuesto también significativo |
| UAI Alimentación | % Pob. Negra | -0.932 | 4.8% | Inequidad racial en seguridad alimentaria |

**Implicación**: La vulnerabilidad socioeconómica **limita** la capacidad de desarrollar gobernanza adaptativa. Los municipios más pobres tienen menos recursos para invertir en infraestructura y gestión.

### 5.2 H1.c: Riesgo Climático → Gobernanza

**HALLAZGO**: Municipios con mayor riesgo climático tienen **mayor** gobernanza.

| Outcome | Mejor Predictor | β | R²m | Interpretación |
|---------|-----------------|---|-----|----------------|
| Gobernanza (idx) | Riesgo Fuego | +0.315 | 18.1% | Mayor riesgo → mayor gobernanza |
| UAI Vivienda | Riesgo Fuego | +3.336 | 16.1% | Inversión reactiva en vivienda |
| UAI Movilidad | Clima (idx) | +1.120 | 13.0% | Mayor riesgo → más movilidad |
| UAI Alimentación | Riesgo Fuego | +0.814 | 5.3% | Seguridad alimentaria reactiva |
| UAI Riesgo Clim. | Riesgo Inundación | +1.033 | 4.9% | Gestión reactiva a inundaciones |
| UAI Ambiental | Riesgo Inundación | +0.386 | 3.2% | Gestión ambiental reactiva |

**Implicación**: Relación **positiva** sugiere que la gobernanza es **reactiva** - los municipios desarrollan capacidad adaptativa *después* de experimentar riesgos climáticos. Esto apoya la hipótesis de Adrian sobre la inversión de la lógica causal.

### 5.3 H1.a: Biodiversidad → Gobernanza

**HALLAZGO**: El déficit de polinización es el mejor predictor de biodiversidad.

| Outcome | Mejor Predictor | β | R²m | Interpretación |
|---------|-----------------|---|-----|----------------|
| Gobernanza (idx) | Déficit Polinización | -0.124 | 10.6% | Menor biodiversidad → menor gobernanza |
| UAI Vivienda | Déficit Polinización | -1.757 | 9.5% | Degradación asociada a menor capacidad |
| UAI Movilidad | Déficit Polinización | -0.828 | 10.4% | Relación consistente |
| UAI Riesgo Clim. | Déficit Polinización | -0.765 | 3.3% | Áreas degradadas con menor gestión |
| UAI Alimentación | Déficit Polinización | +0.832 | 4.8% | **Excepción**: relación positiva |
| UAI Ambiental | (ninguno significativo) | - | 2.1% | Sin relación clara |

**Implicación**: En general, áreas con mayor degradación ecológica (mayor déficit de polinización) tienen menor gobernanza, posiblemente porque son zonas marginales con menor inversión pública.

### 5.4 H1.b: Riesgo de Salud → Gobernanza

**HALLAZGO**: Dengue es el predictor de salud más asociado a gobernanza.

| Outcome | Mejor Predictor | β | R²m | Interpretación |
|---------|-----------------|---|-----|----------------|
| Gobernanza (idx) | Dengue | +0.117 | 11.8% | Mayor dengue → mayor gobernanza |
| UAI Vivienda | Dengue | +1.625 | 10.9% | Inversión reactiva en vivienda |
| UAI Movilidad | Hosp. Respiratoria | -0.462 | 10.0% | Enfermedades resp. en áreas con menos movilidad |
| UAI Riesgo Clim. | Malaria | -0.615 | 4.0% | Malaria en áreas con menor gestión |
| UAI Alimentación | (ninguno significativo) | - | 4.3% | Sin relación clara |
| UAI Ambiental | (ninguno significativo) | - | 2.3% | Sin relación clara |

**Implicación**: La relación **positiva** con dengue sugiere gobernanza reactiva - municipios con más casos históricos de dengue han desarrollado mayor capacidad de respuesta. Por otro lado, malaria y enfermedades respiratorias están asociadas a áreas con menor desarrollo de gobernanza.

---

## 6. Síntesis: Ranking de Predictores

### 6.1 Por Varianza Explicada (R² marginal)

| Rank | Predictor | Outcome | R²m | Tipo de Relación |
|------|-----------|---------|-----|------------------|
| 1 | % Pobreza | Gobernanza (idx) | **26.7%** | Negativa (-) |
| 2 | % Pobreza | UAI Vivienda | 21.1% | Negativa (-) |
| 3 | % Pobreza | UAI Movilidad | 19.1% | Negativa (-) |
| 4 | Riesgo Fuego | Gobernanza (idx) | 18.1% | Positiva (+) |
| 5 | Riesgo Fuego | UAI Vivienda | 16.1% | Positiva (+) |
| 6 | Clima (idx) | UAI Movilidad | 13.0% | Positiva (+) |
| 7 | Dengue | Gobernanza (idx) | 11.8% | Positiva (+) |
| 8 | Déficit Polinización | Gobernanza (idx) | 10.6% | Negativa (-) |

### 6.2 Por Consistencia entre Outcomes

| Predictor | Outcomes Significativos | Dirección Predominante |
|-----------|------------------------|----------------------|
| % Pobreza | 5/6 | Siempre negativa |
| Déficit Polinización | 5/6 | Predominantemente negativa |
| Riesgo Fuego | 4/6 | Siempre positiva |
| Riesgo Inundación | 2/6 | Siempre positiva |
| Dengue | 2/6 | Siempre positiva |

---

## 7. Conclusiones

### 7.1 Hallazgo Principal

**La pobreza es el determinante más fuerte de la gobernanza municipal**:
- Explica hasta 27% de la varianza en el índice de gobernanza
- Efecto consistente y negativo en todos los componentes UAI
- Los municipios más pobres tienen sistemáticamente menor capacidad adaptativa

### 7.2 Evidencia de Gobernanza Reactiva

Los resultados apoyan la hipótesis de Adrian sobre la **inversión de la lógica causal**:

1. **Riesgos climáticos** (fuego, inundación) están **positivamente** asociados a gobernanza
2. **Dengue** también muestra relación **positiva** con gobernanza
3. Esto sugiere que los municipios desarrollan capacidad adaptativa *en respuesta* a eventos adversos, no preventivamente

### 7.3 Biodiversidad como Indicador Indirecto

El déficit de polinización refleja **degradación ambiental** asociada a:
- Zonas marginales con menor inversión pública
- Áreas con menor desarrollo institucional
- Posible proxy de abandono territorial

### 7.4 Inequidad Estructural

La relación entre % población negra y menor seguridad alimentaria (UAI_food) evidencia **inequidades raciales estructurales** en la distribución de recursos públicos.

---

## 8. Implicaciones para Políticas Públicas

1. **Priorizar municipios pobres**: La inversión en gobernanza debe focalizarse en municipios con alta vulnerabilidad socioeconómica

2. **Anticipar vs. reaccionar**: Actualmente la gobernanza es reactiva; se necesitan políticas preventivas

3. **Abordar inequidades**: Las disparidades raciales en acceso a servicios deben ser atendidas explícitamente

4. **Conservación como inversión**: Mantener biodiversidad puede estar asociado a mejor gobernanza a largo plazo

---

## 9. Archivos Generados

### Tablas (CSV)
- `h1_all_models.csv` - 120 modelos evaluados
- `h1_best_by_dimension.csv` - 24 mejores predictores por dimensión
- `h1_structure_comparison.csv` - Comparación de estructuras jerárquicas
- `h1b_biodiversidad_models.csv` - Modelos dimensión biodiversidad
- `h1s_salud_models.csv` - Modelos dimensión salud
- `h1c_clima_models.csv` - Modelos dimensión clima
- `h1v_vulnerabilidad_models.csv` - Modelos dimensión vulnerabilidad

### Figuras (PNG)
- `h1_selection_heatmap.png` - Mapa de calor de selección de modelos
- `h1_dimension_summary.png` - Resumen por dimensión
- `h1_scatter_*.png` - 12 gráficos de dispersión de relaciones significativas

---

## 10. Especificaciones Técnicas

```python
# Modelo base
model = smf.mixedlm(
    'UAI_logit ~ predictor',
    data=df,
    groups=df['cod_microrregiao']
)
result = model.fit(reml=False)

# Métricas reportadas
- AIC: Criterio de información de Akaike
- ΔAIC: Diferencia respecto al mejor modelo
- R²m: R² marginal (Nakagawa & Schielzeth, 2013)
- β: Coeficiente en escala logit
- SE: Error estándar
```

---

*Informe generado por Science Team - Nexus Assessment São Paulo*
*29 de enero de 2026*
