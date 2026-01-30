# Datos y Metodologia - Science Team

> Este archivo documenta las fuentes de datos, procesamiento y metodologia.
> Para contexto actual: `SCIENCE_TEAM_CONTEXT.md`
> **Actualizado automaticamente por H6 - 2026-01-29**

---

## Marco Conceptual

### Diagrama 1: 5 Dimensiones del Nexus (Levers et al. 2025)

```
         Gobernanza <---> Biodiversidad
              |               |
              v               v
        Riesgo Salud <---> Riesgo Climatico
                  \       /
                   \     /
                    \   /
             Vulnerabilidad Social
                  (central)
```

### Diagrama 2: 3 Componentes de Riesgo (IPCC AR5/AR6)

| Componente | Definicion | Ejemplos |
|------------|------------|----------|
| **HAZARD** | Evento fisico peligroso | flooding_exposure, fire_incidence |
| **EXPOSURE** | Poblacion en zona de riesgo | population, pct_rural |
| **VULNERABILITY** | Propension a dano | Sensibilidad + Capacidad Adaptativa |

**Subcomponentes de Vulnerabilidad:**
- Sensibilidad: pct_pobreza, pct_preta, pct_indigena
- Capacidad Adaptativa Natural: forest_cover, biodiversity
- Capacidad Adaptativa Institucional: UAI components

---

## Catalogo de Variables


### Gobernanza

*Capacidad adaptativa institucional y gestion publica*

| Variable | Label | Fuente | Unidad |
|----------|-------|--------|--------|
| `UAI_housing` | UAI Vivienda | Neder et al. 2021 | 0-1 |
| `UAI_env` | UAI Ambiental | Neder et al. 2021 | 0-1 |
| `UAI_food` | UAI Alimentacion | Neder et al. 2021 | 0-1 |
| `UAI_mob` | UAI Movilidad | Neder et al. 2021 | 0-1 |
| `UAI_Crisk` | UAI Riesgo Climatico | Neder et al. 2021 | 0-1 |
| `idx_gobernanza` | Indice Gobernanza | Calculado | 0-1 |

### Biodiversidad

*Estado de ecosistemas y servicios ecosistemicos*

| Variable | Label | Fuente | Unidad |
|----------|-------|--------|--------|
| `forest_cover` | Cobertura Forestal | MapBiomas | % |
| `mean_species_richness` | Riqueza Especies | Biodiversity data | n especies |
| `max_species_richness` | Riqueza Max Especies | Biodiversity data | n especies |
| `pol_deficit` | Deficit Polinizacion | Calculated | 0-1 |
| `idx_biodiv` | Indice Biodiversidad | Calculado | 0-100 |

### Riesgo Climatico

*Exposicion a amenazas climaticas*

| Variable | Label | Fuente | Unidad |
|----------|-------|--------|--------|
| `flooding_risks` | Riesgo Inundacion | CEMADEN | 0-1 |
| `flooding_exposure` | Exposicion Inundacion | CEMADEN | 0-1 |
| `fire_risk_index` | Riesgo Fuego | INPE Queimadas | 0-100 |
| `fire_incidence_mean` | Incidencia Fuego | INPE Queimadas | focos/ano |
| `hydric_stress_risk` | Estres Hidrico | ANA | 0-1 |
| `idx_clima` | Indice Riesgo Clima | Calculado | 0-100 |

### Riesgo Salud

*Carga de enfermedad y morbimortalidad*

| Variable | Label | Fuente | Unidad |
|----------|-------|--------|--------|
| `incidence_mean_dengue` | Incidencia Dengue | DATASUS SINAN | casos/100k/ano |
| `incidence_mean_malaria` | Incidencia Malaria | DATASUS SINAN | casos/100k/ano |
| `incidence_mean_leishmaniose` | Incidencia Leishmaniasis | DATASUS SINAN | casos/100k/ano |
| `incidence_mean_leptospirose` | Incidencia Leptospirosis | DATASUS SINAN | casos/100k/ano |
| `incidence_diarrhea_mean` | Incidencia Diarrea | DATASUS SIH | casos/100k/ano |
| `health_death_circ_mean` | Mortalidad Cardiovascular | DATASUS SIM | muertes/100k/ano |
| `health_hosp_resp_mean` | Hospitalizacion Respiratoria | DATASUS SIH | hosp/100k/ano |
| `idx_carga_enfermedad` | Indice Carga Enfermedad | Calculado | 0-100 |

### Vulnerabilidad Social

*Sensibilidad y capacidad adaptativa social*

| Variable | Label | Fuente | Unidad |
|----------|-------|--------|--------|
| `pct_pobreza` | % Pobreza | IBGE Censo | % |
| `pct_rural` | % Rural | IBGE Censo | % |
| `pct_preta` | % Poblacion Negra | IBGE Censo | % |
| `pct_indigena` | % Poblacion Indigena | IBGE Censo | % |
| `idx_vulnerabilidad` | Indice Vulnerabilidad | Calculado | 0-100 |

---

## Mejores Predictores (Frecuencia H1-H5)

| Variable | Frecuencia como Mejor Predictor |
|----------|--------------------------------|
| `pct_pobreza` | 7 |
| `pol_deficit` | 6 |
| `forest_cover` | 4 |
| `fire_risk_index` | 3 |
| `incidence_mean_dengue` | 2 |
| `flooding_risks` | 2 |
| `pct_preta` | 2 |
| `incidence_mean_leptospirose` | 1 |
| `idx_vulnerabilidad` | 1 |
| `incidence_mean_leishmaniose` | 1 |
| `health_hosp_resp_mean` | 1 |
| `idx_clima` | 1 |
| `incidence_mean_malaria` | 1 |
| `pct_rural` | 1 |
| `hydric_stress_risk` | 1 |

---

## Fuentes de Datos

### DATASUS
- **SINAN**: Enfermedades de notificacion obligatoria (dengue, malaria, etc.)
- **SIH**: Sistema de Informaciones Hospitalarias
- **SIM**: Sistema de Informacion sobre Mortalidad

### IBGE
- **Censo**: Datos demograficos y socioeconomicos
- **SIDRA**: API para series temporales

### Otros
- **INPE Queimadas**: Focos de calor e incendios
- **CEMADEN**: Riesgos hidrologicos
- **MapBiomas**: Cobertura del suelo

---

## Estructura Jerarquica

```
Municipio (n=645) --> Microrregiao (n=63) --> Mesorregiao (n=15)
```

Efectos aleatorios: `(1|cod_microrregiao)` obligatorio en modelos mixtos.

---

*Generado por sintesis_h6_metadata.py*
