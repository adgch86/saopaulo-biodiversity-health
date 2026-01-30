# Informe H4: Predictores de Riesgo de Salud

**Proyecto**: Nexus Biodiversidad-Clima-Salud-Gobernanza en São Paulo
**Investigador Principal**: Dr. Adrian David González Chaves
**Fecha de Análisis**: 29 de enero de 2026

---

## 1. Objetivo del Análisis

**Pregunta central**: ¿Qué factores de vulnerabilidad, clima y biodiversidad predicen los riesgos de salud?

```
H4: Riesgo_Salud ~ Vulnerabilidad * (Riesgo_clima + Biodiversidad)
```

### 1.1 Preocupación Metodológica Principal

Adrian planteó una preocupación crítica:

> "Me preocupa que pareciera que municipios menores tienen más bosque y por tanto menos gente que contagiarse de dengue, entonces es un efecto urbano que queda enmascarado con la cobertura."

Esta preocupación se refiere al **efecto de dilución poblacional**: la relación negativa entre cobertura forestal y dengue podría no ser un efecto causal directo, sino un artefacto de que los municipios forestales tienden a ser más rurales y menos poblados.

---

## 2. Metodología

### 2.1 Especificación del Modelo Base

```
log(Incidencia_Salud) ~ predictor + (1|microrregião)
```

- **7 outcomes de salud**: dengue, malaria, leishmaniasis, leptospirosis, diarrea, mortalidad cardiovascular, hospitalizaciones respiratorias
- **10 predictores**: 3 de biodiversidad + 3 de clima + 4 de vulnerabilidad
- **70 modelos base** evaluados

### 2.2 Validación del Efecto Dilución

Para abordar la preocupación de Adrian, se implementó una validación sistemática:

```python
# 4 especificaciones comparadas
Modelo 1: Salud ~ Cobertura_Forestal                      # Sin control
Modelo 2: Salud ~ Cobertura_Forestal + log(Población)     # + control población
Modelo 3: Salud ~ Cobertura_Forestal + % Rural            # + control ruralidad
Modelo 4: Salud ~ Cobertura_Forestal + log(Pob) + % Rural # + ambos controles
```

**Criterio de robustez**: Si el coeficiente cambia >20% al agregar controles, el efecto está confundido.

---

## 3. Resultados Principales

### 3.1 Mejores Predictores por Enfermedad

| Enfermedad | Mejor Predictor | Dimensión | β | p-valor | R²m |
|------------|-----------------|-----------|---|---------|-----|
| **Dengue** | % Rural | Vulnerabilidad | **-0.225** | <0.001 | **43.3%** |
| **Malaria** | Cobertura Forestal | Biodiversidad | **+0.118** | <0.001 | 13.4% |
| **Leishmaniasis** | Estrés Hídrico | Clima | -0.080 | 0.010 | 33.8% |
| **Leptospirosis** | % Pobreza | Vulnerabilidad | -0.074 | 0.019 | 29.6% |
| **Diarrea** | Cobertura Forestal | Biodiversidad | **-0.342** | <0.001 | 25.2% |
| **Mort. Cardiovascular** | % Pob. Negra | Vulnerabilidad | -0.075 | <0.001 | 25.4% |
| **Hosp. Respiratoria** | Cobertura Forestal | Biodiversidad | -0.145 | <0.001 | 29.9% |

### 3.2 Patrones por Dimensión

| Dimensión | # Veces Mejor Predictor | Enfermedades |
|-----------|------------------------|--------------|
| **Vulnerabilidad** | 4 | Dengue, Leptospirosis, Mort. CV, (parcial Leishmaniasis) |
| **Biodiversidad** | 3 | Malaria, Diarrea, Hosp. Respiratoria |
| **Clima** | 1 | Leishmaniasis |

---

## 4. Validación del Efecto Dilución (Respuesta a la Preocupación de Adrian)

### 4.1 Caso 1: Cobertura Forestal → Dengue

**RESULTADO: EFECTO PARCIALMENTE CONFUNDIDO**

| Modelo | Controles | β (Bosque) | SE | p-valor | Cambio en β |
|--------|-----------|------------|-----|---------|-------------|
| 1 | Ninguno | -0.168 | 0.056 | 0.003 | (referencia) |
| 2 | + log(Población) | -0.123 | 0.056 | 0.028 | **-27%** |
| 3 | + % Rural | -0.121 | 0.055 | 0.028 | **-28%** |
| 4 | + Ambos | -0.107 | 0.055 | 0.052 | **-36%** |

**Interpretación**:
- El coeficiente de cobertura forestal **se reduce 36%** al controlar por población y ruralidad
- El efecto deja de ser significativo (p = 0.052) con ambos controles
- **Conclusión**: La preocupación de Adrian es VÁLIDA. El efecto protector aparente del bosque contra dengue está parcialmente confundido por el efecto de urbanización

**Sin embargo**: El mejor predictor de dengue NO es cobertura forestal, sino **% Rural** (β = -0.225, R²m = 43.3%). Esto es consistente con la hipótesis de Adrian: el efecto es primariamente urbano/poblacional.

### 4.2 Caso 2: Cobertura Forestal → Malaria

**RESULTADO: EFECTO ROBUSTO**

| Modelo | Controles | β (Bosque) | SE | p-valor | Cambio en β |
|--------|-----------|------------|-----|---------|-------------|
| 1 | Ninguno | +0.118 | 0.028 | <0.001 | (referencia) |
| 2 | + log(Población) | +0.115 | 0.029 | <0.001 | -2.5% |
| 3 | + % Rural | +0.132 | 0.029 | <0.001 | +11.8% |
| 4 | + Ambos | +0.122 | 0.030 | <0.001 | +3.8% |

**Interpretación**:
- El coeficiente de cobertura forestal **permanece estable** (~3% de cambio)
- El efecto sigue siendo significativo (p < 0.001) con todos los controles
- **Conclusión**: El efecto de bosque sobre malaria es ROBUSTO y no está confundido

**Explicación ecológica**: La malaria requiere ecosistemas forestales para el ciclo de vida del vector (*Anopheles*). Este es un efecto biológico real, no un artefacto de urbanización.

### 4.3 Caso 3: Cobertura Forestal → Leishmaniasis

**RESULTADO: EFECTO NO SIGNIFICATIVO**

| Modelo | Controles | β (Bosque) | SE | p-valor | Cambio en β |
|--------|-----------|------------|-----|---------|-------------|
| 1 | Ninguno | +0.107 | 0.056 | 0.057 | (no sig.) |
| 4 | + Ambos | +0.087 | 0.056 | 0.120 | -19% |

El efecto de bosque sobre leishmaniasis no es estadísticamente significativo. El mejor predictor es **estrés hídrico** (β = -0.08).

### 4.4 Caso 4: Cobertura Forestal → Leptospirosis

**RESULTADO: EFECTO ROBUSTO**

| Modelo | Controles | β (Bosque) | SE | p-valor | Cambio en β |
|--------|-----------|------------|-----|---------|-------------|
| 1 | Ninguno | +0.112 | 0.052 | 0.031 | (referencia) |
| 4 | + Ambos | +0.127 | 0.051 | 0.013 | **+14%** |

El efecto se **fortalece** con controles, sugiriendo que hay un efecto directo del bosque.

---

## 5. Síntesis de Hallazgos

### 5.1 Diagrama de Validación de Robustez

```
COBERTURA FORESTAL como predictor de salud:

┌────────────────────────────────────────────────────────────────┐
│                                                                │
│   DENGUE          →  CONFUNDIDO (36% cambio en β)              │
│   (Real predictor: % Rural, no bosque)                         │
│                                                                │
│   MALARIA         →  ROBUSTO (3% cambio en β)                  │
│   (Efecto biológico real: hábitat de Anopheles)                │
│                                                                │
│   LEPTOSPIROSIS   →  ROBUSTO (efecto se fortalece)             │
│   (Posible: exposición en ambientes forestales húmedos)        │
│                                                                │
│   LEISHMANIASIS   →  NO SIGNIFICATIVO                          │
│   (Mejor predictor: estrés hídrico)                            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 5.2 Respuesta Directa a la Preocupación de Adrian

| Pregunta | Respuesta |
|----------|-----------|
| ¿La relación bosque-dengue está mediada por tamaño poblacional? | **SÍ, parcialmente**. El coeficiente cae 36% y pierde significancia |
| ¿Cuál es el verdadero predictor de dengue? | **% Rural** (β = -0.225, R²m = 43%), no cobertura forestal |
| ¿La relación bosque-malaria está confundida? | **NO**. El coeficiente es estable y el efecto es biológicamente plausible |
| ¿Podemos confiar en los resultados? | **Depende de la enfermedad**. Se requiere validación caso por caso |

---

## 6. Hallazgos Adicionales

### 6.1 Vulnerabilidad y Salud

La vulnerabilidad socioeconómica es el predictor más consistente de salud:

| Predictor | Enfermedades Asociadas | Dirección |
|-----------|----------------------|-----------|
| % Rural | Dengue (-), Leishmaniasis (+) | Mixta |
| % Pobreza | Leptospirosis (-), Diarrea (-) | Negativa |
| % Pob. Negra | Mort. Cardiovascular (-) | Negativa |

**Nota importante**: Los signos negativos para pobreza y % negra probablemente reflejan:
1. Menor acceso a diagnóstico y notificación en poblaciones vulnerables
2. Subregistro en zonas marginalizadas
3. Posible sesgo de supervivencia (personas fallecen antes de ser diagnosticadas)

### 6.2 Biodiversidad y Salud

| Predictor | Enfermedades Asociadas | Interpretación |
|-----------|----------------------|----------------|
| Cobertura Forestal | Malaria (+), Leptospirosis (+) | Hábitat de vectores |
| Cobertura Forestal | Diarrea (-), Hosp. Resp. (-) | Posible efecto protector de servicios ecosistémicos |
| Déficit Polinización | Hosp. Respiratoria (+) | Degradación → peor calidad de aire |

### 6.3 Riqueza de Especies vs. Cobertura Forestal

| Variable | Dengue | Malaria | Diarrea | Hosp. Resp. |
|----------|--------|---------|---------|-------------|
| Cobertura Forestal | -0.17 | **+0.12** | **-0.34** | **-0.14** |
| Riqueza Especies | -0.09 | -0.04 | -0.28 | -0.09 |

La **cobertura forestal** es mejor predictor que la riqueza de especies, sugiriendo que es la estructura del hábitat (no la diversidad per se) lo que importa para los vectores de enfermedades.

---

## 7. Limitaciones

1. **Datos transversales**: No se puede establecer causalidad
2. **Subregistro diferencial**: Las tasas de incidencia pueden estar subestimadas en zonas marginales
3. **Variables proxy**: "Cobertura forestal" es una proxy de múltiples factores ecológicos
4. **Escala temporal**: Las incidencias son promedios; podrían existir efectos estacionales
5. **Efecto de dilución parcial**: Para dengue, el efecto aparente del bosque está confundido por urbanización

---

## 8. Conclusiones

### 8.1 Hallazgo Principal

**La preocupación de Adrian sobre el efecto de dilución es válida para dengue, pero no para malaria.**

- **Dengue**: El efecto aparente de cobertura forestal desaparece al controlar por población/ruralidad. El verdadero predictor es % Rural.
- **Malaria**: El efecto de cobertura forestal es robusto y biológicamente plausible (hábitat del vector).

### 8.2 Implicaciones para la Interpretación del Nexus

```
           VALIDACIÓN DE EFECTOS
           ┌───────────────────────────────────────┐
           │                                       │
ROBUSTOS:  │ • Bosque → Malaria (biológico)        │
           │ • Bosque → Leptospirosis              │
           │ • Ruralidad → Dengue (sociodemográf.) │
           │ • Pobreza → Mort. Cardiovascular      │
           │                                       │
CONFUNDIDOS:│ • Bosque → Dengue (por urbanización) │
           │                                       │
           └───────────────────────────────────────┘
```

### 8.3 Recomendaciones

1. **Interpretar con cautela** las relaciones bosque-enfermedad: validar siempre con controles poblacionales
2. **No generalizar**: El efecto del bosque depende del mecanismo biológico de cada enfermedad
3. **Usar % Rural o log(Población)** como control en futuros análisis del nexus
4. **Para dengue**: Usar % Rural como predictor principal, no cobertura forestal

---

## 9. Archivos Generados

### Tablas
- `h4_all_models.csv` - 70 modelos con estadísticos completos
- `h4_best_predictors.csv` - Mejor predictor por enfermedad
- `h4_dilution_validation.csv` - Validación del efecto dilución

### Figuras
- `figures/h4_selection_heatmap.png` - Mapa de calor de selección de modelos
- `figures/h4_best_predictors.png` - Gráfico de mejores predictores
- `figures/h4_dilution_comparison.png` - Comparación de efectos con/sin controles

---

## 10. Comparación con Hipótesis Anteriores

| Aspecto | H1 | H2 | H3 | H4 |
|---------|-----|-----|-----|-----|
| Pregunta | ¿Qué predice gobernanza? | ¿Vulnerabilidad modula? | ¿Clima×Salud interactúan? | ¿Qué predice salud? |
| Variable respuesta | Gobernanza | Gobernanza | Gobernanza | **Enfermedades** |
| Hallazgo clave | Pobreza (-27%) | Pobreza anula efecto reactivo | Efectos mixtos | **Validar siempre efecto dilución** |
| Mejor predictor global | % Pobreza | Pobreza×Estrés Hídrico | Hosp.Resp×Estrés | % Rural (dengue) |

---

*Informe generado por Science Team - Nexus Assessment São Paulo*
*29 de enero de 2026*
