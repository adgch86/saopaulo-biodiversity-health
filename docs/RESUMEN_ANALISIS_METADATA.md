# Resumen del Analisis de Datos - Sao Paulo

**Fecha:** Enero 2026
**Fuentes:** AdaptaBrasil MCTI, DATASUS, IBGE

---

## 1. Descripcion de los Datos

### Variables por Categoria (33 total)

| Categoria | Variables | Descripcion |
|-----------|-----------|-------------|
| **Riesgos Climaticos** | 4 | flooding_exposure, flooding_risks, hydric_stress_exp/risk |
| **Salud** | 11 | persist_* e incidence_* para malaria, dengue, diarrea, leptospirosis, chagas + copersistence |
| **Capacidad Adaptativa (UAI)** | 6 | UAI_housing, UAI_env, UAI_food, UAI_mob, UAI_Crisk |
| **Vulnerabilidad Social** | 6 | population, population_preta/indigena/branca, pct_rural |
| **Biodiversidad** | 3 | mean/max_species_richness, Vert_rich_risk |
| **Seguridad Alimentaria** | 1 | pol_deficit |
| **Identificadores** | 2 | COD, Municipality |

---

## 2. Estadisticas Descriptivas

### Riesgos Climaticos (645 municipios)
- **Exposicion a inundaciones:** Media 0.52 (rango 0.07-0.94)
- **Riesgo de inundacion:** Media 0.08 (75% de municipios = 0)
- **Estres hidrico:** Media 0.49 (rango 0-0.77)

### Biodiversidad
- **Riqueza de especies:** Media 623 (rango 252-757)
- **Riesgo para vertebrados:** Media 9.8 (rango 0-44)

### Indice de Acceso Universal (UAI)
| Componente | Media | Min | Max |
|------------|-------|-----|-----|
| UAI_housing | 0.34 | 0 | 1 |
| UAI_env | 0.49 | 0 | 1 |
| UAI_food | 0.41 | 0 | 1 |
| UAI_mob | 0.41 | 0 | 1 |
| UAI_Crisk | 0.32 | 0 | 1 |

### Salud (187 municipios)
- **Dengue:** Persistencia media 6.6 anos (de 10)
- **Malaria:** Incidencia media 16.9 por 100k
- **Copersistencia:** Media 7.5 (indice de coexistencia de enfermedades)

---

## 3. Correlaciones Clave

### En 645 municipios

| Relacion | r | p | Interpretacion |
|----------|---|---|----------------|
| Biodiversidad vs Deficit Politico | **-0.567** | <0.001 | Mayor biodiversidad = menor deficit |
| Riesgo Vertebrados vs Biodiversidad | **-0.763** | <0.001 | Relacion inversa fuerte |
| UAI_mob vs Poblacion | **+0.725** | <0.001 | Ciudades grandes tienen mejor movilidad |
| % Rural vs UAI_housing | **-0.415** | <0.001 | Areas rurales con peor acceso a vivienda |
| Biodiversidad vs Riesgo Inundacion | +0.272 | <0.001 | Areas biodiversas con mayor exposicion |

### En 187 municipios (con datos de salud)

| Relacion | r | p | Interpretacion |
|----------|---|---|----------------|
| Malaria vs UAI | **-0.593** | <0.001 | UAI protege contra malaria |
| Diarrea vs UAI | **-0.460** | <0.001 | UAI protege contra diarrea |
| Dengue vs UAI | **-0.432** | <0.001 | UAI protege contra dengue |
| Malaria vs % Rural | **+0.600** | <0.001 | Mayor incidencia en areas rurales |

---

## 4. Clasificacion por Cuadrantes

| Cuadrante | N | % | UAI | Biodiv. | Deficit | Descripcion |
|-----------|---|---|-----|---------|---------|-------------|
| **Q1 - Modelo** | 195 | 30.2% | 0.56 | 690 | 0.81 | Mejor desempeno integral |
| **Q2 - Conservar** | 128 | 19.8% | 0.24 | 680 | 0.86 | Alta biodiversidad, bajo acceso |
| **Q3 - Vulnerable** | 192 | 29.8% | 0.24 | 566 | **0.95** | Requiere intervencion urgente |
| **Q4 - Desarrollo** | 130 | 20.2% | 0.52 | 552 | 0.89 | Desarrollo sin conservacion |

### Municipios Destacados
- **Q1 (Modelo):** Guarulhos, Campinas, Sao Bernardo do Campo
- **Q3 (Vulnerable):** Sao Joaquim da Barra, Jardinopolis, Pontal
- **Q4 (Desarrollo):** Sao Paulo, Santo Andre, Osasco

---

## 5. Analisis de Justicia Ambiental

### Composicion Demografica por Cuadrante

| Cuadrante | % Negra | % Indigena | % Rural |
|-----------|---------|------------|---------|
| Q1 - Modelo | 5.35% | 0.11% | 12.5% |
| Q2 - Conservar | 4.74% | 0.21% | 19.2% |
| Q3 - Vulnerable | 4.86% | 0.13% | 14.1% |
| Q4 - Desarrollo | 5.25% | 0.08% | 8.2% |

### Paradoja Biodiversidad-Vulnerabilidad
- **127 municipios** tienen alta biodiversidad pero bajo acceso a servicios
- Estos municipios presentan deficit politico de 0.86 (alto)
- Concentran poblacion rural (19.3%)

### Correlaciones Demograficas
- % Indigena vs Biodiversidad: r=0.145 (p<0.001) - Poblaciones indigenas en areas mas biodiversas
- % Negra vs UAI: r=0.160 (p<0.001) - Correlacion positiva debil

---

## 6. Hallazgos Principales

1. **El UAI es factor protector:** Correlaciones negativas fuertes con malaria (-0.59), diarrea (-0.46) y dengue (-0.43)

2. **Biodiversidad asociada a menor deficit politico:** r=-0.57, sugiere que la conservacion esta vinculada a mejor gobernanza

3. **192 municipios vulnerables (30%)** requieren intervencion prioritaria - tienen el mayor deficit politico (0.95) y menor biodiversidad

4. **Areas rurales mas expuestas:** Mayor incidencia de malaria y menor acceso a vivienda

5. **Poblaciones indigenas** estan significativamente asociadas a areas de mayor biodiversidad

---

## 7. Recomendaciones de Politicas

### Prioridad Alta (Q3 - Vulnerable)
- Inversion en infraestructura basica y UAI
- Fortalecimiento institucional (reducir deficit politico)
- Restauracion ecologica

### Prioridad Media (Q2 - Conservar)
- Proteger biodiversidad existente
- Mejorar acceso a servicios sin degradar ecosistemas
- Desarrollo sostenible

### Monitoreo (Q1 - Modelo)
- Documentar y replicar buenas practicas
- Mantener equilibrio biodiversidad-desarrollo

---

## 8. Archivos Generados

- `outputs/figures/analisis_completo_metadata.png` - Visualizacion de 6 paneles
- `outputs/figures/heatmap_correlaciones.png` - Matriz de correlaciones
- `outputs/figures/cuadrantes_analisis.png` - Analisis de cuadrantes

---

*Analisis realizado con datos de AdaptaBrasil MCTI, DATASUS e IBGE*
