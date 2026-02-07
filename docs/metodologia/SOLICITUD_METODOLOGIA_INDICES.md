# Solicitud de Metodología - Índices Compuestos

**Para:** Dr. Adrian David González Chaves
**De:** Science Team / Arlex
**Fecha:** 2026-02-03
**Asunto:** Descripción metodológica de los índices compuestos

---

Hola Adrian,

Para documentar correctamente la metodología del proyecto y asegurar la reproducibilidad de los análisis, necesitamos que describas cómo calculaste cada uno de los índices compuestos que estamos usando en los análisis de cuadrantes y modelos.

## Índices a documentar:

### 1. Índice de Vulnerabilidad (`idx_vulnerabilidad`)
- ¿Qué variables lo componen?
- ¿Cómo se ponderaron/combinaron?
- ¿Se normalizaron las variables antes de combinarlas?
- ¿Hay alguna referencia metodológica (ej. IPCC, papers)?

**Variables que parecen relacionadas en el dataset:**
- `pct_pobreza`
- `pct_rural`
- `pct_preta`
- `pct_indigena`

### 2. Índice de Biodiversidad (`idx_biodiv`)
- ¿Qué variables lo componen?
- ¿Cómo se calculó?
- ¿Qué fuentes de datos se usaron (MapBiomas, etc.)?

**Variables que parecen relacionadas:**
- `forest_cover`
- `mean_species_richness`
- `pol_deficit` (déficit de polinización)

### 3. Índice de Riesgo Climático (`idx_clima`)
- ¿Qué variables lo componen?
- ¿Cómo se combinaron los diferentes tipos de riesgo?
- ¿Hay ponderación diferencial?

**Variables que parecen relacionadas:**
- `flooding_risks` / `flooding_exposure`
- `fire_risk_index`
- `hydric_stress_risk`

### 4. Índice de Carga de Enfermedad (`idx_carga_enfermedad`)
- ¿Qué enfermedades/condiciones incluye?
- ¿Se usaron tasas de incidencia, prevalencia o mortalidad?
- ¿Cómo se normalizaron para hacerlas comparables?

**Variables que parecen relacionadas:**
- `incidence_mean_dengue`
- `incidence_mean_malaria`
- `incidence_mean_leptospirose`
- `incidence_mean_leishmaniose`
- `incidence_diarrhea_mean`
- `health_death_circ_mean` (mortalidad cardiovascular)
- `health_hosp_resp_mean` (hospitalizaciones respiratorias)

---

## Formato sugerido para la respuesta:

Para cada índice, sería ideal tener:

1. **Fórmula o método de cálculo**
2. **Variables incluidas y sus pesos (si aplica)**
3. **Método de normalización** (min-max, z-score, percentiles, etc.)
4. **Fuente de datos** para cada variable componente
5. **Referencia metodológica** (si está basado en algún framework existente)

---

Esta información es necesaria para:
- Documentar la metodología en el manuscrito
- Asegurar reproducibilidad
- Responder preguntas en el workshop SEMIL-USP
- Incluir en materiales suplementarios

¡Gracias!

---
*Generado por Science Team - 2026-02-03*
