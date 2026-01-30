# Informe H3: Interacción Clima × Salud sobre Gobernanza

**Proyecto**: Nexus Biodiversidad-Clima-Salud-Gobernanza en São Paulo
**Investigador Principal**: Dr. Adrian David González Chaves
**Fecha de Análisis**: 29 de enero de 2026

---

## 1. Objetivo del Análisis

**Pregunta central**: ¿Cómo interactúan los riesgos climáticos y de salud para explicar la gobernanza municipal?

```
H3: Gobernanza ~ Riesgo_Salud × Riesgo_Clima
```

Este análisis busca identificar si la **co-ocurrencia** de riesgos de salud y climáticos tiene un efecto distinto al de cada riesgo por separado (efecto sinérgico o antagónico).

---

## 2. Metodología

### 2.1 Especificación del Modelo

```
logit(Gobernanza) ~ Salud × Clima + (1|microrregião)
```

- **Una variable de salud por modelo** (modelo simple)
- **Una variable de clima por modelo** (evitar saturación)
- **Sin interacciones triples**

### 2.2 Pares Teóricamente Vinculados (Prioritarios)

Basados en la literatura epidemiológica:

| Par | Salud | Clima | Justificación Teórica |
|-----|-------|-------|----------------------|
| 1 | Diarrea | Inundación | Contaminación de agua por encharcamiento |
| 2 | Dengue | Estrés Hídrico | Almacenamiento de agua favorece mosquitos |
| 3 | Dengue | Inundación | Criaderos en agua estancada |
| 4 | Malaria | Cobertura Forestal | Vector en zonas forestales |
| 5 | Leptospirosis | Inundación | Transmisión por contacto con agua contaminada |
| 6 | Leishmaniasis | Cobertura Forestal | Vector en zonas de interfaz bosque-urbano |
| 7 | Enf. Respiratorias | Riesgo Fuego | Humo de incendios forestales |
| 8 | Mort. Cardiovascular | Riesgo Fuego | Partículas finas de combustión |

### 2.3 Variables Analizadas

| Tipo | Variables |
|------|-----------|
| **Outcomes** | idx_gobernanza, UAI_Crisk, UAI_env |
| **Salud** | dengue, malaria, leishmaniasis, leptospirosis, diarrea, mort_cardiovascular, hosp_respiratoria |
| **Clima** | flooding_risks, fire_risk_index, hydric_stress_risk, forest_cover |

### 2.4 Total de Modelos

- **Pares teóricos**: 8 pares × 3 outcomes = 24 modelos
- **Exploratorio**: 7 salud × 3 clima × 3 outcomes = 63 modelos adicionales
- **Total**: ~87 modelos únicos

---

## 3. Resultados: Pares Teóricos

### 3.1 Resumen de Pares Teóricos

De los 24 modelos de pares teóricos evaluados:
- **2 interacciones significativas (p<0.05) que mejoran ajuste (ΔAIC<0)**

| Par Teórico | Outcome | β_int | p | ΔAIC | Significativo |
|-------------|---------|-------|---|------|---------------|
| Diarrea-Inundación | idx_gobernanza | -0.09 | 0.27 | +0.80 | No |
| Diarrea-Inundación | UAI_Crisk | -0.11 | 0.82 | +1.95 | No |
| Diarrea-Inundación | UAI_env | -0.55 | 0.08 | -1.13 | No (tendencia) |
| Dengue-Estrés Hídrico | idx_gobernanza | +0.002 | 0.94 | +1.99 | No |
| Dengue-Estrés Hídrico | UAI_Crisk | -0.16 | 0.37 | +1.20 | No |
| Dengue-Estrés Hídrico | UAI_env | +0.02 | 0.85 | +1.97 | No |
| **Dengue-Inundación** | **UAI_env** | **+0.35** | **0.035** | **-2.45** | **Sí** |
| **Malaria-Bosque** | **UAI_env** | **+0.24** | **0.0006** | **-9.83** | **Sí** |
| Resp-Fuego | idx_gobernanza | +0.01 | 0.72 | +1.87 | No |
| Cardiovasc-Fuego | idx_gobernanza | +0.04 | 0.23 | +0.56 | No |
| Leptospirosis-Inundación | idx_gobernanza | -0.03 | 0.37 | +1.19 | No |
| Leishmaniasis-Bosque | idx_gobernanza | -0.003 | 0.88 | +1.98 | No |

### 3.2 Detalle: Malaria × Bosque → UAI Ambiental

**La interacción más significativa de los pares teóricos**

```
logit(UAI_env) = -0.78 × Malaria
                 - 0.04 × Cobertura_Forestal
                 + 0.24 × (Malaria × Bosque)
                 + intercepto
```

| Estadístico | Valor |
|-------------|-------|
| β interacción | +0.238 |
| SE | 0.069 |
| p-valor | **0.0006** |
| ΔAIC | **-9.83** |
| R² marginal | 3.7% |

**Interpretación**:
- En municipios con **baja cobertura forestal**, mayor malaria → menor UAI ambiental (β negativo)
- En municipios con **alta cobertura forestal**, el efecto negativo de malaria se **atenúa** (interacción positiva)
- Posible explicación: Los municipios forestales con malaria endémica han desarrollado programas de control que mejoran su gestión ambiental

### 3.3 Detalle: Dengue × Inundación → UAI Ambiental

```
logit(UAI_env) = +0.03 × Dengue
                 + 0.48 × Inundación
                 + 0.35 × (Dengue × Inundación)
                 + intercepto
```

| Estadístico | Valor |
|-------------|-------|
| β interacción | +0.350 |
| SE | 0.165 |
| p-valor | **0.035** |
| ΔAIC | **-2.45** |

**Interpretación**:
- El efecto de inundación sobre UAI ambiental es **amplificado** cuando también hay alto dengue
- La co-ocurrencia de ambos riesgos parece generar mayor respuesta institucional en gestión ambiental
- Municipios que enfrentan ambos problemas simultáneamente desarrollan capacidad de respuesta

---

## 4. Resultados: Análisis Exploratorio

### 4.1 Interacciones Significativas con Mejora de Ajuste

| Salud | Clima | Outcome | β_int | p | ΔAIC |
|-------|-------|---------|-------|---|------|
| **Hosp. Respiratoria** | **Estrés Hídrico** | **Gobernanza** | **-0.109** | **0.002** | **-7.66** |
| **Malaria** | **Riesgo Fuego** | **UAI Ambiental** | **-0.308** | **0.007** | **-5.15** |
| **Hosp. Respiratoria** | **Estrés Hídrico** | **UAI Ambiental** | **-0.311** | **0.016** | **-3.80** |
| Mort. Cardiovascular | Riesgo Inundación | UAI Crisk | +0.428 | 0.031 | -2.64 |
| Malaria × Bosque | UAI Ambiental | +0.238 | 0.0006 | -9.83 |
| Dengue × Inundación | UAI Ambiental | +0.350 | 0.035 | -2.45 |

### 4.2 Hallazgo Inesperado: Hosp. Respiratoria × Estrés Hídrico

Esta interacción no estaba en los pares teóricos originales pero resultó la más significativa:

```
logit(Gobernanza) = -0.10 × Hosp_Resp
                    + 0.16 × Estrés_Hídrico
                    - 0.11 × (Hosp_Resp × Estrés_Hídrico)
```

| Estadístico | Valor |
|-------------|-------|
| β interacción | **-0.109** |
| SE | 0.035 |
| p-valor | **0.002** |
| ΔAIC | **-7.66** |
| R² marginal | 14.1% |

**Interpretación**:
- La interacción es **negativa**: cuando hay alto estrés hídrico Y altas hospitalizaciones respiratorias, la gobernanza es menor de lo esperado
- Posible explicación: El estrés hídrico puede estar asociado a condiciones áridas con polvo/partículas que aumentan enfermedades respiratorias, y ambos factores ocurren en zonas con menor desarrollo institucional
- Esta combinación de riesgos podría indicar "sobrecarga institucional"

---

## 5. Síntesis de Hallazgos

### 5.1 Patrones Identificados

| Patrón | Interacciones | Interpretación |
|--------|---------------|----------------|
| **Sinergia positiva** | Dengue×Inundación, Malaria×Bosque, Cardiovasc×Inundación | La co-ocurrencia genera MAYOR gobernanza (respuesta reactiva) |
| **Sinergia negativa** | Resp×Estrés, Malaria×Fuego | La co-ocurrencia genera MENOR gobernanza (sobrecarga institucional) |

### 5.2 Comparación con H1 y H2

| Aspecto | H1 | H2 | H3 |
|---------|-----|-----|-----|
| Pregunta | ¿Qué predice gobernanza? | ¿Vulnerabilidad modula? | ¿Clima×Salud interactúan? |
| Hallazgo | Riesgo → +gobernanza | Pobreza anula efecto | Depende de la combinación |
| Mejor predictor | % Pobreza (R²=27%) | Pobreza×Estrés Hídrico | Hosp.Resp×Estrés (R²=14%) |

### 5.3 Diagrama Conceptual

```
                    SINERGIA POSITIVA
                    ┌─────────────────────────┐
 Dengue + Inundación│ → Mayor UAI Ambiental   │ ← Respuesta integrada
 Malaria + Bosque   └─────────────────────────┘

                    SINERGIA NEGATIVA
                    ┌─────────────────────────┐
 Hosp.Resp + Estrés │ → Menor Gobernanza      │ ← Sobrecarga/marginación
 Malaria + Fuego    └─────────────────────────┘
```

---

## 6. Nota sobre Variables Compuestas

El análisis H3 **no utilizó variables compuestas** (índices agregados). Todas las variables son mediciones directas:

| Variable | Tipo | Fuente |
|----------|------|--------|
| incidence_mean_dengue | Tasa | DATASUS - casos notificados |
| incidence_mean_malaria | Tasa | DATASUS - casos confirmados |
| health_hosp_resp_mean | Tasa | DATASUS - hospitalizaciones |
| flooding_risks | Índice simple | Mapbiomas/INPE - área inundable |
| fire_risk_index | Índice simple | INPE - focos de calor |
| forest_cover | Proporción | Mapbiomas - cobertura forestal |

---

## 7. Limitaciones

1. **Causalidad**: Diseño transversal no permite inferir direccionalidad
2. **Pares teóricos no significativos**: La mayoría de los pares epidemiológicamente esperados (diarrea×inundación, dengue×estrés hídrico) no mostraron interacción significativa con gobernanza
3. **Varianza explicada modesta**: R² marginal entre 3-14% indica que otros factores (como pobreza, H1-H2) son más determinantes
4. **Especificidad del outcome**: Los efectos fueron más claros para UAI_env que para idx_gobernanza general

---

## 8. Conclusiones

### 8.1 Hallazgos Principales

1. **Solo 2 de 8 pares teóricos mostraron interacción significativa**: Malaria×Bosque y Dengue×Inundación

2. **El hallazgo más robusto fue exploratorio**: Hosp.Respiratoria × Estrés Hídrico (p=0.002, ΔAIC=-7.66)

3. **Las interacciones Clima×Salud tienen efectos mixtos**:
   - Algunos pares generan gobernanza (sinergia positiva)
   - Otros la reducen (sobrecarga institucional)

4. **La hipótesis de gobernanza reactiva (H1) se mantiene parcialmente**:
   - Algunos pares de riesgos sí generan gobernanza
   - Pero otros la sobrecargan

### 8.2 Implicaciones

1. **No asumir efectos uniformes**: La combinación específica de riesgos importa

2. **Priorizar intervenciones integradas**: Municipios con Malaria+Bosque o Dengue+Inundación pueden beneficiarse de programas integrados salud-ambiente

3. **Atención a zonas con múltiples riesgos negativos**: Áreas con estrés hídrico + enfermedades respiratorias requieren apoyo externo

---

## 9. Archivos Generados

### Tablas
- `h3_interactions.csv` - Todos los modelos (87)
- `h3_theory_pairs.csv` - Solo pares teóricos (24)

### Figuras
- `figures/h3_interaction_matrix.png` - Matriz de coeficientes
- `figures/h3_summary_table.png` - Tabla resumen top 15
- `figures/h3_theory_Dengue_Inundacion.png` - Simple slopes par teórico
- `figures/h3_theory_Malaria_Bosque.png` - Simple slopes par teórico

---

*Informe generado por Science Team - Nexus Assessment São Paulo*
*29 de enero de 2026*
