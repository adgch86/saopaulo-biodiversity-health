# Workshop SEMIL-USP: Actividad 3 - ACTUALIZADA

## Nexus Assessment and Overarching Results

**Fecha de actualización**: 2026-02-03
**Basado en**: Análisis H1-H6 (Framework de Predictores de Gobernanza)

---

## Resumen Ejecutivo

Esta actividad presenta los resultados integrados del nexus assessment con **104+ variables** para los **645 municipios de São Paulo**.

**IMPORTANTE**: Los hallazgos presentados aquí difieren significativamente del análisis original debido a:
1. Validación rigurosa del efecto de confusión por urbanización
2. Inversión de la lógica causal (riesgos → gobernanza, no al revés)
3. Identificación de que dengue NO responde a cobertura forestal

---

## Estructura de la Actividad

| Componente | Duración | Formato |
|------------|----------|---------|
| Presentación de resultados | 15 min | Plenaria |
| Discusión en grupos pequeños | 25 min | 4-5 grupos |
| Síntesis y debate | 20 min | Plenaria integrada |
| **Total** | **60 min** | |

---

## PARTE 1: Presentación de Resultados (15 min)

### Slide 1: Título

**"Lo que Aprendimos: Paradojas y Realidades del Nexus Gobernanza-Biodiversidad-Clima-Salud"**

*645 municipios • 104 variables • 6 hipótesis testeadas*

---

### Slide 2: El Cambio de Paradigma

| Enfoque Tradicional | Lo que Encontramos |
|---------------------|-------------------|
| Gobernanza → reduce riesgos | Riesgos → generan gobernanza (reactiva) |
| Biodiversidad → reduce todas las enfermedades | Depende de la enfermedad y está confundido por urbanización |
| Conservación = estrategia de salud pública | Solo para algunas enfermedades, no para dengue |

**Mensaje clave**: Las relaciones son más complejas de lo que asumíamos.

---

### Slide 3: Hallazgo 1 - Dengue es URBANO, no forestal

**Pregunta original**: ¿La biodiversidad protege contra dengue?

**Respuesta**: NO. El efecto aparente está **confundido por urbanización**.

| Análisis | Resultado |
|----------|-----------|
| Correlación simple bosque-dengue | r = -0.45 (parecía protector) |
| Controlando por población y ruralidad | **β cambia 36%, deja de ser significativo** |
| Mejor predictor de dengue | **% Rural (β = -0.225, R²m = 43%)** |

**Implicación para políticas**:
- Las intervenciones contra dengue deben focalizarse en **áreas urbanas**
- La conservación forestal NO es una estrategia efectiva contra dengue
- El vector (*Aedes aegypti*) es doméstico y peridoméstico

---

### Slide 4: Hallazgo 2 - Malaria SÍ responde a bosque (pero al revés)

**Pregunta**: ¿El bosque protege contra malaria?

**Respuesta**: NO. Más bosque = MÁS malaria.

| Modelo | β (Cobertura Forestal) | p-valor | Cambio |
|--------|------------------------|---------|--------|
| Sin controles | +0.118 | <0.001 | - |
| Con controles (población + ruralidad) | +0.122 | <0.001 | **+3%** |

**Este efecto es ROBUSTO** - no está confundido.

**Explicación ecológica**:
- El vector de malaria (*Anopheles*) requiere ecosistemas forestales
- Ciclo de vida silvestre, no doméstico
- Trade-off real entre conservación y salud en zonas de transmisión activa

---

### Slide 5: Hallazgo 3 - La Paradoja de Gobernanza

**Pregunta**: ¿La gobernanza reduce los riesgos climáticos?

**Respuesta**: Al contrario. Municipios con mayor riesgo tienen MAYOR gobernanza.

| Relación | Coeficiente | Interpretación |
|----------|-------------|----------------|
| Riesgo Fuego → Gobernanza | β = +0.315 | Más riesgo = más gobernanza |
| Riesgo Inundación → UAI Clima | β = +1.033 | Inversión reactiva |
| Riesgo Climático → UAI Movilidad | β = +1.120 | Desarrollo post-crisis |

**Interpretación**: La gobernanza es **REACTIVA**, no preventiva.
- Los municipios desarrollan capacidad adaptativa DESPUÉS de experimentar riesgos
- Las políticas preventivas son escasas o inefectivas
- Esto sugiere un ciclo de crisis → inversión → siguiente crisis

---

### Slide 6: Hallazgo 4 - La Pobreza Domina Todo

**Pregunta**: ¿Qué factor tiene mayor poder explicativo?

**Respuesta**: La pobreza (% familias bajo línea de pobreza).

| Variable Respuesta | Mejor Predictor | R²m |
|--------------------|-----------------|-----|
| Gobernanza general | % Pobreza | **27%** |
| UAI Vivienda | % Pobreza | 21% |
| UAI Movilidad | % Pobreza | 19% |
| Dengue | % Rural | 43% |
| Mort. Cardiovascular | % Pob. Negra | 25% |

**La vulnerabilidad socioeconómica modula TODAS las relaciones del nexus:**
- Municipios pobres: menor gobernanza Y mayor vulnerabilidad
- La pobreza anula el efecto protector de otros factores
- Sin reducir pobreza, las intervenciones ambientales tienen efecto limitado

---

### Slide 7: Hallazgo 5 - Lo que SÍ funciona

**Servicios ecosistémicos con efectos robustos:**

| Relación | Coeficiente | Validación |
|----------|-------------|------------|
| Bosque → reduce déficit de polinización | r = **-0.77** | Muy fuerte |
| Bosque → reduce hospitalizaciones respiratorias | β = -0.145 | Robusto |
| Bosque → reduce diarrea | β = -0.342 | Robusto |
| Biodiversidad → reduce incidencia general | Variable | Depende de la enfermedad |

**Mensaje**: La conservación SÍ tiene beneficios para salud, pero específicos:
- Calidad del aire (enfermedades respiratorias)
- Calidad del agua (diarrea)
- Servicios de polinización (seguridad alimentaria)
- **NO para enfermedades vectoriales urbanas (dengue)**

---

### Slide 8: Clasificación de Municipios - 4 Cuadrantes

| Cuadrante | N municipios | % Población | Característica |
|-----------|--------------|-------------|----------------|
| **Q1 - Modelo** | ~160 | ~45% | Alta gobernanza + Baja vulnerabilidad |
| **Q2 - Riesgo** | ~160 | ~20% | Alta gobernanza + Alta vulnerabilidad |
| **Q3 - Crítico** | ~160 | ~15% | Baja gobernanza + Alta vulnerabilidad |
| **Q4 - Potencial** | ~165 | ~20% | Baja gobernanza + Baja vulnerabilidad |

**Prioridad de intervención**: Q3 (Crítico) → Q2 (Riesgo) → Q4 (Potencial)

---

## PARTE 2: Discusión en Grupos (25 min)

### Instrucciones para Facilitadores

Dividir participantes en **4-5 grupos** de 4-5 personas cada uno.

Cada grupo recibe **2 preguntas provocadoras** para discutir.

---

### Preguntas Provocadoras (asignar 2 por grupo)

**Grupo 1: Dengue y Urbanización**
1. Si dengue es fundamentalmente un problema urbano, ¿tiene sentido incluir "conservación de biodiversidad" como estrategia de control de vectores en políticas de salud pública?
2. ¿Cómo deberían diferir las estrategias de salud pública entre municipios urbanos vs rurales?

**Grupo 2: La Paradoja de Gobernanza**
3. Sabiendo que la gobernanza es reactiva (responde a crisis, no las previene), ¿cómo podríamos diseñar incentivos para acción preventiva?
4. ¿Es posible o deseable que la gobernanza sea proactiva? ¿Qué barreras institucionales lo impiden?

**Grupo 3: Pobreza como Factor Dominante**
5. Si la pobreza domina todas las relaciones del nexus, ¿deberíamos enfocarnos primero en reducir pobreza antes de implementar intervenciones ambientales?
6. ¿Cómo evitar que las intervenciones de conservación aumenten las desigualdades existentes?

**Grupo 4: Trade-offs Biodiversidad-Salud**
7. La malaria aumenta con la cobertura forestal - ¿existen trade-offs inevitables entre conservación y salud? ¿Cómo manejarlos?
8. ¿Cómo comunicar al público que "más naturaleza" no siempre significa "mejor salud"?

**Grupo 5: Implicaciones para Políticas**
9. Dados estos hallazgos, ¿qué recomendaciones específicas harían para el Plan Estadual de Adaptación Climática de São Paulo?
10. ¿Cómo integrar estos hallazgos en la planificación municipal sin recursos técnicos especializados?

---

### Formato de Discusión

| Tiempo | Actividad |
|--------|-----------|
| 0-5 min | Lectura de preguntas, aclaraciones |
| 5-20 min | Discusión grupal |
| 20-25 min | Preparar 2-3 puntos clave para presentar |

---

## PARTE 3: Síntesis y Debate (20 min)

### Estructura

| Tiempo | Actividad |
|--------|-----------|
| 0-12 min | Cada grupo presenta sus 2-3 puntos clave (2-3 min/grupo) |
| 12-18 min | Debate abierto sobre puntos de convergencia/divergencia |
| 18-20 min | Síntesis del facilitador |

---

### Guía para el Facilitador - Síntesis Final

**Puntos a destacar:**

1. **Complejidad ≠ Parálisis**: Los resultados son complejos, pero ofrecen direcciones claras para acción.

2. **Especificidad importa**: No hay soluciones "one-size-fits-all". Cada enfermedad, cada municipio, requiere estrategias diferenciadas.

3. **La pobreza es el elefante en la habitación**: Sin abordar vulnerabilidad socioeconómica, las intervenciones técnicas tienen efecto limitado.

4. **Gobernanza reactiva es una oportunidad**: Si sabemos que las crisis generan inversión, podemos diseñar sistemas que anticipen y preparen.

5. **Trade-offs son reales**: Debemos ser honestos sobre los costos de la conservación y diseñar compensaciones justas.

---

## Materiales de Apoyo

### Para imprimir:

- [ ] Tarjetas con preguntas provocadoras (1 set por grupo)
- [ ] Resumen de hallazgos (1 página, 1 por participante)
- [ ] Mapa de cuadrantes municipales (1 poster grande)

### Digitales:

- Presentación PowerPoint (8 slides)
- Dataset de municipios para consulta
- Mapas interactivos (si hay proyector disponible)

---

## Anexo: Comparación Original vs Actualizado

| Tema | Presentación Original | Presentación Actualizada |
|------|----------------------|-------------------------|
| Efecto dilución dengue | "Confirmado" (r=-0.45) | **Confundido por urbanización** |
| Mejor predictor dengue | Biodiversidad | **% Rural (urbanización)** |
| Efecto bosque-malaria | No mencionado | **Positivo y robusto** (más bosque = más malaria) |
| Paradoja gobernanza | "Explicada por urbanización" | **Gobernanza es reactiva, no preventiva** |
| Protección forestal-polinización | Mencionado | **Confirmado** (r=-0.77) |
| Factor dominante | Vulnerabilidad (general) | **Pobreza específicamente** (R²m=27%) |
| Mensaje de conservación | "Conservación protege salud" | **"Depende de la enfermedad y el contexto"** |

---

## Referencias Metodológicas

- **Framework H1-H6**: Análisis de predictores de gobernanza (2026-01-29)
- **Validación efecto dilución**: Modelos con controles de población y ruralidad
- **Selección de modelos**: Criterio AIC con efectos mixtos por microrregión
- **Dataset**: municipios_integrado_v8.csv (645 municipios × 104 variables)

---

*Documento preparado por Science Team para Workshop SEMIL-USP*
*Febrero 2026*
