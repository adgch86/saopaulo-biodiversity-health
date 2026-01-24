# Science Team - Contexto del Proyecto

> **IMPORTANTE**: Este archivo mantiene el estado ACTUAL del proyecto.
> Para historial detallado de sesiones: `SESSION_HISTORY.md`
> Para catálogo de papers: `PAPERS_LIBRARY.md`
> Para detalles de datos/metodología: `DATA_METHODOLOGY.md`

---

## Proyecto Actual

**Título**: Resilient Landscapes: Integrating Planetary Health, Nexus Thinking, and Environmental Justice in São Paulo's Agrifood Systems

**Investigador Principal**: Dr. Adrian David González Chaves

**Estado**: Análisis completado - Preparando publicación

**Dataset actual**: `outputs/municipios_integrado_v8.csv` (645 municipios × 104 variables)

---

## HALLAZGOS PRINCIPALES

### 1. Efecto Dilución CONFIRMADO
Ecosistemas biodiversos reducen transmisión de patógenos:

| Variable | vs Enfermedad | r | Interpretación |
|----------|---------------|---|----------------|
| Riqueza spp | Dengue | **-0.45** | Más especies = menos dengue |
| Riqueza spp | Diarrea | **-0.45** | Más especies = menos diarrea |
| Biodiversidad | Carga Enfermedad | **-0.41** | Efecto protector global |
| Cobertura forestal | Déficit Polinización | **-0.77** | Muy fuerte |

### 2. Paradoja Gobernanza-Riesgo
La gobernanza (UAI) NO reduce directamente riesgos climáticos:

| Relación | r | Interpretación |
|----------|---|----------------|
| Gobernanza → Riesgo Climático | +0.29 | NO reduce |
| Gobernanza → Riesgo Fuego | +0.19 | NO reduce |
| Gobernanza → Carga Enfermedad | -0.01 | Efecto débil |

**Explicación**: Municipios más desarrollados están en zonas de mayor exposición.

### 3. Efectos Moduladores Clave
La vulnerabilidad socioeconómica modifica las relaciones:

| Relación | Modulador | Efecto |
|----------|-----------|--------|
| Gobernanza→Clima | % Pobreza | ATENÚA (-0.36) |
| Biodiv→Enfermedades | % Pob. Negra | Amplifica (+0.32) |
| Cobertura forestal→Clima | % Pob. Indígena | Amplifica (+0.32) |

### 4. Distribución por Cuadrantes

| Cuadrante | N | Riesgo | Vulnerabilidad | Estrategia |
|-----------|---|--------|----------------|------------|
| Q1_Modelo | 212 | 0.36 | 11.0 | Mantener y expandir |
| Q2_Conservar | 110 | 0.34 | 12.5 | Fortalecer gobernanza |
| **Q3_Vulnerable** | **210** | 0.28 | **24.1** | **INTERVENCIÓN URGENTE** |
| Q4_Desarrollo | 113 | 0.31 | 22.4 | Restauración ecológica |

---

## Municipios Prioritarios (Top 5)

| Rank | Municipio | Cuadrante | Riesgo | Vulnerabilidad |
|------|-----------|-----------|--------|----------------|
| 1 | **Iporanga** | Q3_Vulnerable | 0.582 | 54.2 |
| 2 | Eldorado | Q4_Desarrollo | 0.443 | 43.0 |
| 3 | Colômbia | Q3_Vulnerable | 0.440 | 35.3 |
| 4 | Paulo de Faria | Q4_Desarrollo | 0.441 | 30.0 |
| 5 | Itaoca | Q4_Desarrollo | 0.408 | 40.2 |

---

## Datasets Actuales

| Versión | Archivo | Variables | Descripción |
|---------|---------|-----------|-------------|
| **v8** | `municipios_integrado_v8.csv` | **104** | + Diarrea |
| v7 | `municipios_integrado_v7.csv` | 100 | + Fuego + Salud-calor |
| v6 | `municipios_integrado_v6.csv` | 70 | Base completa 645 mun |

---

## Archivos Recientes Generados

### Análisis Nexus (Sesión 19)
- `outputs/correlaciones_nexus_completas.csv`
- `outputs/modelos_mixtos_nexus.csv`
- `outputs/ranking_municipios_prioritarios.csv`
- `outputs/acciones_pearc_por_cuadrante.csv`
- `outputs/figures/hipotesis_h1_h2_nexus.png`
- `outputs/figures/analisis_cuadrantes_nexus.png`

### Validación Datos (Sesión 18)
- `scripts/compare_health_data_ju.py`
- `scripts/compare_health_data_ju_v2.py`
- Resultado: Dengue y Diarrea validados (r=1.0)

---

## Próximos Pasos

### Alta Prioridad
- [ ] Finalizar propuesta Branco Weiss (revisión Adrian)
- [ ] Preparar manuscrito para journal (ERL o similar)
- [ ] Registrar en OSF (Open Science Framework)

### Media Prioridad
- [ ] Análisis de sensibilidad con diferentes umbrales
- [ ] Integrar variables climáticas extremas pendientes (CDD, TX35)
- [ ] Validación cruzada con datos independientes

---

## Scripts Principales

| Script | Descripción |
|--------|-------------|
| `analisis_nexus_gobernanza_biodiversidad_v1.py` | Análisis completo H1/H2 |
| `create_integrated_dataset_v8.py` | Generador dataset v8 |
| `calculate_diarrhea_indicators.py` | Indicadores diarrea |
| `create_workshop_maps.py` | Mapas choropleth workshop |

---

## Referencias Rápidas

**Archivos de contexto extendido:**
- `SESSION_HISTORY.md` - Historial detallado de 19 sesiones
- `PAPERS_LIBRARY.md` - Catálogo de 75 papers
- `DATA_METHODOLOGY.md` - Fuentes de datos y metodología
- `REFERENTES_CIENTIFICOS.md` - Investigadores de referencia

**GitHub**: https://github.com/adgch86/saopaulo-biodiversity-health
**DOI**: 10.5281/zenodo.18303824

---

*Última actualización: 2026-01-23 (Sesión 19 - Análisis Nexus)*
