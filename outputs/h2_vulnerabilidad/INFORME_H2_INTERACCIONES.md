# Informe H2: Efecto Modulador de la Vulnerabilidad Socioeconómica

**Proyecto**: Nexus Biodiversidad-Clima-Salud-Gobernanza en São Paulo
**Investigador Principal**: Dr. Adrian David González Chaves
**Fecha de Análisis**: 29 de enero de 2026

---

## 1. Objetivo del Análisis

**Pregunta central**: ¿Cómo modula la vulnerabilidad socioeconómica el efecto de las otras dimensiones (biodiversidad, riesgo climático, riesgo de salud) sobre la gobernanza?

A diferencia de H1 donde se analizaron efectos principales, H2 evalúa **efectos interactivos (moduladores)**:

```
H2: Gobernanza ~ Vulnerabilidad × (Riesgo_clima + Riesgo_Salud + Biodiversidad)
```

**Hipótesis implícita**: El impacto de los riesgos climáticos, de salud y de la biodiversidad sobre la gobernanza puede variar según el nivel de vulnerabilidad socioeconómica del municipio.

---

## 2. Metodología

### 2.1 Especificación del Modelo

```
logit(Gobernanza) ~ Predictor × Moderador + (1|microrregião)
```

Donde:
- **Predictor (X)**: Variable de biodiversidad, clima o salud
- **Moderador (M)**: Variable de vulnerabilidad socioeconómica
- **Interacción (X×M)**: Efecto modulador de la vulnerabilidad

### 2.2 Variables Analizadas

| Rol | Variables |
|-----|-----------|
| **Outcomes (Y)** | idx_gobernanza, UAI_Crisk, UAI_env |
| **Moderadores (M)** | pct_pobreza, pct_rural, pct_preta, pct_indigena, idx_vulnerabilidad |
| **Predictores - Clima** | flooding_risks, fire_risk_index, hydric_stress_risk |
| **Predictores - Salud** | incidence_mean_dengue, incidence_mean_malaria, health_death_circ_mean |
| **Predictores - Biodiv** | forest_cover, mean_species_richness, pol_deficit |

### 2.3 Criterios de Evaluación

1. **Significancia de interacción**: p < 0.05
2. **Mejora de ajuste**: ΔAIC < 0 (modelo con interacción mejor que aditivo)
3. **Ambos criterios**: Interacción significativa Y mejora ajuste

### 2.4 Total de Modelos

- **3 outcomes × 5 moderadores × 9 predictores = 135 modelos**

---

## 3. Resultados Principales

### 3.1 Resumen de Interacciones Significativas

De 135 modelos evaluados:
- **31 interacciones significativas** (p < 0.05) = 23%
- **22 interacciones que mejoran ajuste** (ΔAIC < 0 Y p < 0.05) = 16%

### 3.2 Top 10 Interacciones Más Significativas

| Rank | Outcome | Moderador | Predictor | β_int | p | ΔAIC | Interpretación |
|------|---------|-----------|-----------|-------|---|------|----------------|
| 1 | Gobernanza | % Pobreza | Estrés Hídrico | **-0.217** | <0.001 | -55.8 | Efecto de estrés hídrico MÁS DÉBIL en municipios pobres |
| 2 | UAI Ambiental | % Pobreza | Estrés Hídrico | **-0.496** | <0.001 | -16.4 | Mismo patrón para gestión ambiental |
| 3 | UAI Ambiental | % Pobreza | Riqueza Especies | **-0.541** | <0.001 | -13.4 | Biodiversidad no beneficia a municipios pobres |
| 4 | Gobernanza | % Rural | Dengue | **-0.176** | <0.001 | -12.9 | Dengue no genera gobernanza en zonas rurales |
| 5 | Gobernanza | % Pobreza | Riesgo Fuego | **-0.128** | <0.001 | -12.2 | Fuego no genera gobernanza en municipios pobres |
| 6 | UAI Crisk | % Pobreza | Estrés Hídrico | **-0.635** | <0.001 | -11.0 | Gestión de riesgo climático afectada |
| 7 | UAI Ambiental | Vulnerab.(idx) | Estrés Hídrico | **-0.423** | <0.001 | -10.6 | Patrón consistente con índice compuesto |
| 8 | Gobernanza | % Rural | Estrés Hídrico | **-0.117** | <0.001 | -10.1 | Ruralidad también modula negativamente |
| 9 | UAI Ambiental | % Pob. Negra | Malaria | **+0.328** | <0.001 | -9.1 | Excepción: efecto MÁS FUERTE |
| 10 | UAI Crisk | % Pob. Negra | Riesgo Fuego | **-0.523** | 0.001 | -8.4 | Inequidad en respuesta a incendios |

### 3.3 Patrones Identificados

#### Patrón 1: Pobreza Atenúa Respuesta a Riesgos Climáticos

| Predictor | Outcome | β_interacción | Interpretación |
|-----------|---------|---------------|----------------|
| Estrés Hídrico | Gobernanza | -0.217 | Municipios pobres no desarrollan gobernanza ante estrés hídrico |
| Riesgo Fuego | Gobernanza | -0.128 | Municipios pobres no desarrollan gobernanza ante fuegos |
| Inundación | Gobernanza | -0.192 | Municipios pobres no responden a inundaciones |

**Interpretación**: La pobreza **anula el efecto reactivo** que vimos en H1. Mientras que en H1 encontramos que mayor riesgo climático → mayor gobernanza, en H2 vemos que esto **solo aplica a municipios no pobres**.

#### Patrón 2: Ruralidad Modula Negativamente Respuesta a Salud

| Predictor | Outcome | β_interacción | Interpretación |
|-----------|---------|---------------|----------------|
| Dengue | Gobernanza | -0.176 | Zonas rurales no desarrollan gobernanza ante dengue |
| Estrés Hídrico | Gobernanza | -0.117 | Similar para riesgos climáticos |
| Riesgo Fuego | Gobernanza | -0.075 | Patrón consistente |

**Interpretación**: La ruralidad también atenúa la respuesta institucional a los riesgos.

#### Patrón 3: Biodiversidad No Beneficia a Municipios Vulnerables

| Predictor | Outcome | Moderador | β_interacción |
|-----------|---------|-----------|---------------|
| Riqueza Especies | UAI Ambiental | % Pobreza | -0.541 |
| Riqueza Especies | Gobernanza | % Pobreza | -0.091 |
| Cobertura Forestal | UAI Crisk | % Pobreza | -0.315 |

**Interpretación**: Los beneficios de la biodiversidad para la gobernanza son capturados principalmente por municipios menos vulnerables.

---

## 4. Análisis Detallado: Interacción Pobreza × Estrés Hídrico

Esta es la interacción más significativa (p < 0.001, ΔAIC = -55.8).

### 4.1 Modelo

```
logit(Gobernanza) = -0.04 × Estrés_Hídrico
                    - 0.57 × Pobreza
                    - 0.22 × (Estrés_Hídrico × Pobreza)
                    + intercepto + efecto_aleatorio
```

### 4.2 Simple Slopes (Efecto de Estrés Hídrico por Nivel de Pobreza)

| Nivel de Pobreza | Pendiente | SE | p | Significativo |
|------------------|-----------|-----|---|---------------|
| Baja (-1 SD) | +0.18 | 0.04 | <0.001 | Sí (positivo) |
| Media (0) | -0.04 | 0.03 | 0.25 | No |
| Alta (+1 SD) | **-0.26** | 0.04 | <0.001 | Sí (negativo) |

### 4.3 Interpretación

- **Municipios de baja pobreza**: Mayor estrés hídrico → MAYOR gobernanza (+0.18)
  - Desarrollan capacidad adaptativa en respuesta al riesgo
- **Municipios de pobreza media**: Sin efecto significativo
- **Municipios de alta pobreza**: Mayor estrés hídrico → MENOR gobernanza (-0.26)
  - El riesgo no genera respuesta institucional
  - Posible "trampa de pobreza-vulnerabilidad"

---

## 5. Análisis por Variable de Vulnerabilidad

### 5.1 % Pobreza como Moderador (12 interacciones significativas)

| Predictor | Outcome | β_int | ΔAIC | Dirección |
|-----------|---------|-------|------|-----------|
| Estrés Hídrico | Gobernanza | -0.22 | -55.8 | Atenúa |
| Riesgo Fuego | Gobernanza | -0.13 | -12.2 | Atenúa |
| Inundación | Gobernanza | -0.19 | -3.5 | Atenúa |
| Malaria | Gobernanza | -0.11 | -4.3 | Atenúa |
| Riqueza Especies | Gobernanza | -0.09 | -4.6 | Atenúa |
| Mort. Cardiovasc. | Gobernanza | +0.07 | -3.4 | Amplifica |
| Estrés Hídrico | UAI Ambiental | -0.50 | -16.4 | Atenúa |
| Riqueza Especies | UAI Ambiental | -0.54 | -13.4 | Atenúa |
| Mort. Cardiovasc. | UAI Ambiental | +0.24 | -2.6 | Amplifica |
| Riesgo Fuego | UAI Ambiental | -0.27 | -1.9 | Atenúa |
| Estrés Hídrico | UAI Crisk | -0.64 | -11.0 | Atenúa |
| Riqueza Especies | UAI Crisk | -0.45 | -2.7 | Atenúa |

**Síntesis**: La pobreza consistentemente **atenúa** el efecto de los riesgos sobre la gobernanza, excepto para mortalidad cardiovascular donde lo amplifica.

### 5.2 % Rural como Moderador (4 interacciones significativas)

| Predictor | Outcome | β_int | ΔAIC |
|-----------|---------|-------|------|
| Dengue | Gobernanza | -0.18 | -12.9 |
| Estrés Hídrico | Gobernanza | -0.12 | -10.1 |
| Riesgo Fuego | Gobernanza | -0.08 | -2.1 |
| Estrés Hídrico | UAI Ambiental | -0.34 | -5.3 |

### 5.3 % Población Negra como Moderador (5 interacciones significativas)

| Predictor | Outcome | β_int | ΔAIC | Nota |
|-----------|---------|-------|------|------|
| Malaria | UAI Ambiental | +0.33 | -9.1 | Amplifica |
| Riesgo Fuego | UAI Crisk | -0.52 | -8.4 | Atenúa |
| Mort. Cardiovasc. | Gobernanza | +0.11 | -7.9 | Amplifica |
| Riesgo Fuego | Gobernanza | -0.08 | -5.8 | Atenúa |
| Riqueza Especies | UAI Crisk | +0.39 | -1.9 | Amplifica |

**Nota**: Patrones mixtos. Algunas interacciones amplifican en lugar de atenuar.

### 5.4 Índice de Vulnerabilidad (compuesto)

| Predictor | Outcome | β_int | ΔAIC |
|-----------|---------|-------|------|
| Estrés Hídrico | Gobernanza | -0.17 | -29.5 |
| Riesgo Fuego | Gobernanza | -0.09 | -5.3 |
| Estrés Hídrico | UAI Ambiental | -0.42 | -10.6 |
| Riqueza Especies | UAI Ambiental | -0.41 | -9.4 |

---

## 6. Síntesis de Hallazgos

### 6.1 Hallazgo Principal

**La vulnerabilidad socioeconómica actúa como un "inhibidor institucional"** que impide a los municipios desarrollar gobernanza adaptativa en respuesta a riesgos.

### 6.2 Diagrama Conceptual

```
                    Municipios NO vulnerables
                    ┌─────────────────────────┐
 Riesgo Climático ──│ → Mayor Gobernanza (+)  │ ← Respuesta REACTIVA
                    └─────────────────────────┘

                    Municipios VULNERABLES
                    ┌─────────────────────────┐
 Riesgo Climático ──│ → Sin efecto o negativo │ ← Trampa de vulnerabilidad
                    └─────────────────────────┘
```

### 6.3 Implicaciones

1. **Políticas diferenciadas**: No se puede asumir que todos los municipios responderán igual a los riesgos
2. **Focalización proactiva**: Los municipios vulnerables requieren intervención externa, no generarán gobernanza reactiva
3. **Ciclo vicioso**: La pobreza impide desarrollar capacidad adaptativa, lo que perpetúa la vulnerabilidad

---

## 7. Comparación H1 vs H2

| Aspecto | H1 (Efectos Principales) | H2 (Interacciones) |
|---------|-------------------------|-------------------|
| Pregunta | ¿Qué predice gobernanza? | ¿Para quién aplica ese efecto? |
| Hallazgo clave | Riesgo climático → +gobernanza | Solo en municipios NO vulnerables |
| Pobreza | Predictor negativo más fuerte | Moderador que atenúa otros efectos |
| Implicación | Gobernanza es reactiva | Solo para quienes tienen recursos |

---

## 8. Figuras Generadas

### 8.1 Mapa de Calor de Interacciones
`h2_interaction_heatmap.png` - Muestra coeficientes de interacción significativos

### 8.2 Forest Plot
`h2_forest_plot.png` - Interacciones que mejoran ajuste del modelo

### 8.3 Gráficos de Simple Slopes
Muestran cómo varía el efecto del predictor según nivel del moderador:
- `h2_slopes_hydric_str_pobreza.png` - Estrés hídrico × Pobreza
- `h2_slopes_fire_risk__pobreza.png` - Riesgo fuego × Pobreza
- `h2_slopes_flooding_r_pobreza.png` - Inundación × Pobreza
- `h2_slopes_malaria_pobreza.png` - Malaria × Pobreza
- `h2_slopes_death_circ_pobreza.png` - Mort. cardiovascular × Pobreza
- `h2_slopes_mean_speci_pobreza.png` - Riqueza especies × Pobreza

---

## 9. Limitaciones y Consideraciones

1. **Causalidad**: Los datos son transversales; la direccionalidad es teórica
2. **Multicolinealidad**: Algunas variables de vulnerabilidad están correlacionadas entre sí
3. **Interacciones de orden superior**: No se evaluaron interacciones triples (X × M1 × M2)
4. **Umbrales**: Los "simple slopes" a ±1 SD son arbitrarios; podrían existir umbrales no lineales

---

## 10. Recomendaciones para Políticas Públicas

1. **Priorización por vulnerabilidad**: Intervenciones de gobernanza deben focalizarse en municipios con alta pobreza y ruralidad

2. **No esperar respuesta reactiva**: Los municipios vulnerables no desarrollarán gobernanza "naturalmente" ante riesgos

3. **Inversión anticipada**: Se requiere inversión proactiva en capacidad institucional antes de que ocurran eventos climáticos

4. **Abordar desigualdades estructurales**: La pobreza es tanto predictor directo (H1) como moderador (H2) de la gobernanza

---

## 11. Archivos Generados

### Tablas
- `h2_interactions.csv` - 135 modelos con estadísticos completos

### Figuras
- `figures/h2_interaction_heatmap.png`
- `figures/h2_forest_plot.png`
- `figures/h2_slopes_*.png` (6 gráficos de simple slopes)

---

*Informe generado por Science Team - Nexus Assessment São Paulo*
*29 de enero de 2026*
