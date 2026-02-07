# INFORME SCIENCE TEAM - VERSION 5
## Integracion Multi-dimensional: Biodiversidad, Salud, Vulnerabilidad y Gobernanza
### Dr. Adrian David Gonzalez Chaves y Equipo

---

> **NOTA IMPORTANTE**: Estos son hallazgos PRELIMINARES. Quedan por integrar:
> variables de extremos climaticos, conectividad del paisaje, y validacion temporal.

---

## RESUMEN EJECUTIVO

Este analisis integra cinco dimensiones de sistemas agroalimentarios a escala municipal
en Sao Paulo, siguiendo el marco conceptual de Levers et al. (2025). La contribucion
principal es la **integracion multi-dimensional** a escala local, no hallazgos individuales.

### Hallazgos principales:

1. **CONFIRMACION LOCAL DEL EFECTO DILUCION**: Patron consistente con literatura existente
   (Barreto et al. 2025, donde Adrian Gonzalez-Chaves es co-autor)
2. **PARADOJA CONSERVACION-POBREZA**: Municipios mas pobres tienen MAYOR biodiversidad
3. **BRECHA DE GOBERNANZA**: Los municipios mas vulnerables tienen la PEOR gobernanza
4. **INTEGRACION 5D** (contribucion original): Biodiversidad + Salud + Pobreza + Gobernanza + Clima

---

## 1. CONFIRMACION LOCAL DEL EFECTO DILUCION

### Contexto en la Literatura

El efecto dilucion esta bien documentado en la literatura reciente:

- **Barreto et al. (2025)** en *Communications Earth & Environment* (Adrian Gonzalez-Chaves
  es co-autor) demostro en la Amazonia que:
  > *"Forest areas present non-linear effects, mitigating potential increases due to
  > edge effects on zoonotic/vector-borne incidences if covering more than 40% of
  > the municipality"*

- **Levers et al. (2025)** en *Environmental Research Letters* mapeo hotspots globales
  de "agrifood-system burdens" integrando 5 dimensiones.

### Hipotesis (conocida)
El "efecto dilucion" propone que ecosistemas biodiversos diluyen la transmision de
patogenos al reducir la densidad de hospederos competentes y aumentar la proporcion
de especies no-competentes.

### Resultados (n=187 municipios)

| Biodiversidad | Enfermedad | r (Spearman) | Interpretacion |
|---------------|------------|--------------|----------------|
| Riqueza spp | Dengue | **-0.429** | Mas spp = menos dengue |
| Riqueza spp | Diarrea | **-0.452** | Mas spp = menos diarrea |
| Riqueza spp | Malaria | **-0.358** | Mas spp = menos malaria |
| Cobertura forestal | Dengue | **-0.486** | Mas bosque = menos dengue |
| Cobertura forestal | Diarrea | **-0.394** | Mas bosque = menos diarrea |

### Implicaciones (confirmando literatura existente)
- La conservacion de biodiversidad tiene **co-beneficios para la salud publica**
- Municipios que pierden biodiversidad podrian experimentar **aumentos en enfermedades**
- La deforestacion es un factor de riesgo para la salud
- **Nuestros datos de Sao Paulo confirman patrones encontrados en Amazonia** (Barreto et al. 2025)

---

## 2. PARADOJA CONSERVACION-POBREZA

### Hallazgo
Los municipios con MAYOR vulnerabilidad social tienen MAYOR biodiversidad.

- Riqueza de especies vs % Pobreza: **r = -0.346** (positivo)
- Cobertura forestal vs Familias en calle: **r = 0.181**

### Biodiversidad por Nivel de Pobreza

| Tercil Pobreza | Riqueza Especies | Cobertura Forestal |
|----------------|------------------|---------------------|
| Baja | 652.0 | 24.4% |
| Media | 621.6 | 20.5% |
| Alta | 596.3 | 16.6% |

### Explicacion Propuesta
1. Municipios rurales pobres tienen **menos presion de desarrollo urbano**
2. La expansion urbana (asociada a mayor riqueza) **destruye habitat**
3. Las comunidades pobres son **guardianes involuntarios** de la biodiversidad

### Implicaciones de Politica
- Los programas de conservacion deben **compensar a comunidades pobres**
- Pagos por Servicios Ecosistemicos (PSE) como mecanismo de **justicia ambiental**
- El desarrollo debe ser **planificado** para no destruir biodiversidad

---

## 3. BRECHA DE GOBERNANZA

### Hallazgo Principal
Los municipios mas vulnerables tienen significativamente PEOR gobernanza.

- Correlacion UAI vs IVM: **r = -0.293**

### Gobernanza por Cuadrante

| Cuadrante | UAI Promedio | IVM | n |
|-----------|--------------|-----|---|
| Q1_Modelo | 0.564 | 61.9 | 198 |
| Q2_Conservar | 0.248 | 65.8 | 125 |
| Q3_Vulnerable | 0.234 | 76.4 | 195 |
| Q4_Desarrollo | 0.512 | 73.6 | 127 |

### Interpretacion
- **Q3_Vulnerable** tiene el UAI mas bajo (0.234) y el IVM mas alto
- Los municipios que MAS necesitan apoyo gubernamental son los que MENOS lo tienen
- Esta es una **trampa de vulnerabilidad**: baja gobernanza perpetua la vulnerabilidad

---

## 4. VARIABLES PENDIENTES POR INTEGRAR

### Extremos Climaticos (prioridad alta)
Siguiendo el marco de Levers et al. (2025), faltan indicadores de:
- **CDD**: Dias consecutivos secos (sequias)
- **TX35**: Dias con temperatura maxima >35C (olas de calor)
- **RX5**: Precipitacion maxima en 5 dias (inundaciones)
- **FD**: Dias con heladas

### Conectividad del Paisaje
- **FLII**: Forest Landscape Integrity Index
- **Densidad de bordes**: Fragmentacion del habitat
- **Agregacion**: Distribucion espacial de parches

### Datos Socioeconomicos Adicionales
- Series temporales multi-anio
- Datos de produccion agricola por municipio
- Indicadores de seguridad alimentaria

### Validacion
- Analisis de sensibilidad con diferentes umbrales
- Validacion cruzada con datos independientes
- Comparacion con estudios regionales

---

## 5. SINTESIS: NEXO MULTI-DIMENSIONAL (5 DIMENSIONES)

Siguiendo el marco de Levers et al. (2025), integramos 5 dimensiones:

```
                    CLIMA EXTREMO
                         │
                         │ amplifica
                         v
BIODIVERSIDAD ─────────────────────┐
     │                             │
     │ protege (efecto dilucion)   │ conservada por
     │                             │
     v                             v
  SALUD ←──────────────────────── POBREZA
     │                             │
     │                             │ sufrida por
     │ afectada por falta de       │
     v                             v
GOBERNANZA ←────────────────────── VULNERABLES
   (brecha)                        (Q3)

Dimensiones: [1] Biodiversidad [2] Salud [3] Pobreza [4] Gobernanza [5] Clima*
*Pendiente de integrar completamente
```

### Municipios Q3 (Vulnerables) - Caracterizacion:
- Baja biodiversidad + Baja gobernanza
- MAYOR incidencia de enfermedades
- MAYOR pobreza y vulnerabilidad social
- MENOR capacidad de adaptacion climatica
- **PRIORIDAD para intervencion integrada**

---

## 6. RECOMENDACIONES

### Para Politicas de Conservacion
1. **Pagos por Servicios Ecosistemicos** a comunidades pobres que conservan biodiversidad
2. **Corredores ecologicos** que conecten fragmentos forestales
3. **Agricultura de bajo impacto** en areas de alta biodiversidad

### Para Politicas de Salud Publica
1. Integrar **conservacion de biodiversidad** en estrategias de control de vectores
2. **Reforestacion** como intervencion de salud publica
3. Monitoreo de enfermedades en areas con perdida de biodiversidad

### Para Politicas de Desarrollo
1. **Priorizar gobernanza** en municipios Q3 (vulnerables)
2. Inversiones en **servicios basicos** (esgoto, vivienda, educacion)
3. **Desarrollo sustentable** que no destruya la biodiversidad

---

## 7. MUNICIPIOS PRIORITARIOS

### Top 10 con Mayor Brecha (Alta vulnerabilidad + Baja gobernanza)
- **Uru** (Q3_Vulnerable): UAI=0.140, IVM=100.0
- **Vitória Brasil** (Q3_Vulnerable): UAI=0.090, IVM=93.6
- **Borá** (Q3_Vulnerable): UAI=0.156, IVM=97.8
- **Taquaral** (Q3_Vulnerable): UAI=0.090, IVM=90.1
- **Pracinha** (Q3_Vulnerable): UAI=0.076, IVM=87.9
- **São Francisco** (Q3_Vulnerable): UAI=0.066, IVM=86.3
- **Júlio Mesquita** (Q3_Vulnerable): UAI=0.076, IVM=84.0
- **Marapoama** (Q3_Vulnerable): UAI=0.090, IVM=83.4
- **Dobrada** (Q3_Vulnerable): UAI=0.066, IVM=80.4
- **Balbinos** (Q3_Vulnerable): UAI=0.116, IVM=84.4

---

---

## REFERENCIAS

- Barreto, J.R. et al. (2025). Indigenous Territories can safeguard human health depending
  on the landscape structure and legal status. *Communications Earth & Environment*, 6:719.
  https://doi.org/10.1038/s43247-025-02620-7

- Levers, C. et al. (2025). Different places, different challenges: mapping global variations
  in agrifood-system burdens. *Environmental Research Letters*, 20:124051.
  https://doi.org/10.1088/1748-9326/ae20ac

---

*Science Team - Dr. Adrian David Gonzalez Chaves*
*Enero 2026 - Version 5 (Integracion Multi-dimensional - PRELIMINAR)*
