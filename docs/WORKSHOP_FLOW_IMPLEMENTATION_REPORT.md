# TerraRisk Workshop Flow - Reporte de Implementacion

**Fecha:** 2026-02-05
**Implementado por:** Science Team (Dante/Santiago)
**Solicitado por:** Dr. Adrian David Gonzalez Chaves (Punto 10 de sus notas)

---

## 1. Resumen Ejecutivo

Se implemento el flujo completo de 4 fases para el Workshop SEMIL-USP (Feb 22-26, 2026). El flujo permite a los participantes:

1. **Fase 1 - Ranking Inicial:** Priorizar 10 municipios "a ciegas" (sin datos)
2. **Fase 2 - Exploracion:** Comprar y explorar capas de datos en el mapa
3. **Fase 3 - Ranking Revisado + Acciones PEARC:** Re-priorizar con datos + seleccionar acciones
4. **Fase 4 - Resultados:** Comparar ranking del grupo vs ranking optimo de la plataforma

**Estado:** Backend y Frontend completos. Build exitoso. Tests de API pasados (6/6 endpoints).

---

## 2. Arquitectura del Flujo

```
FASE 1                    FASE 2                 FASE 3                    FASE 4
Ranking Inicial    -->    Explorar Mapa    -->   Ranking Revisado    -->   Comparacion
(click-to-rank)          (comprar capas)         + Acciones PEARC          Spearman/Kendall
10 municipios             MapViewer+Sidebar       Split view 50/50          User vs Platform
```

### Flujo de datos:

```
Frontend                              Backend
---------                             --------
MunicipalityRanking                   POST /api/workshop/ranking
  |                                     -> save_ranking() [SQLite]
  v
MapViewer + Sidebar                   GET /api/layers, /api/municipalities
  |                                     (existentes)
  v
MunicipalityRanking (revised)         POST /api/workshop/ranking
  + ActionsSelector                   POST /api/workshop/actions/save
  |                                     -> save_selected_actions() [SQLite]
  v
RankingComparison                     GET /api/workshop/comparison/{group_id}
                                        -> compute_platform_ranking()
                                        -> compute_ranking_difference()
                                        -> Spearman + Kendall
```

---

## 3. Archivos Creados (7 nuevos)

### Backend (3 archivos)

| Archivo | Lineas | Funcion |
|---------|--------|---------|
| `backend/core/pearc_actions.py` | 235 | Catalogo de 15 acciones PEARC con links a dimensiones de riesgo |
| `backend/core/ranking_algorithm.py` | 257 | Ranking optimo (composite score) + Spearman/Kendall sin scipy |
| `backend/api/workshop_flow.py` | 364 | 6 endpoints API para todo el flujo |

### Frontend (4 archivos)

| Archivo | Lineas | Funcion |
|---------|--------|---------|
| `frontend/src/components/workshop/WorkshopStepper.tsx` | 97 | Barra de progreso horizontal (4 fases) |
| `frontend/src/components/workshop/MunicipalityRanking.tsx` | 257 | Grid de municipios + panel de prioridad click-to-rank |
| `frontend/src/components/workshop/ActionsSelector.tsx` | 180 | Selector de 15 acciones PEARC con toggle |
| `frontend/src/components/workshop/RankingComparison.tsx` | 281 | Resultados finales: correlacion, rankings lado a lado, acciones |

---

## 4. Archivos Modificados (9 existentes)

| Archivo | Cambio |
|---------|--------|
| `backend/main.py` | Agregado workshop router (`/api/workshop`) |
| `backend/core/database.py` | 2 tablas nuevas (rankings, selected_actions) + 4 funciones CRUD |
| `frontend/src/lib/types.ts` | 6 tipos nuevos + 2 configs (QUADRANT_CONFIG, PHASE_CONFIG) |
| `frontend/src/lib/store.ts` | Estado workshop (phase, municipalities, ranking, actions, comparison) |
| `frontend/src/app/workshop/page.tsx` | Reescrito completo con 4 fases + transiciones |
| `frontend/messages/en.json` | +45 keys (workshopFlow, actionNames, actionDescriptions) |
| `frontend/messages/es.json` | +45 keys (traduccion completa) |
| `frontend/messages/pt.json` | +45 keys (traduccion completa) |

---

## 5. Detalle Tecnico

### 5.1. PEARC Actions Catalog (15 acciones)

Cada accion tiene links ponderados (1-3) a dimensiones de riesgo:

| ID | Categoria | Links | Evidencia Promedio |
|----|-----------|-------|--------------------|
| reforestation | biodiversity | 7 dimensiones | 2.29 |
| urban_drainage | climate | 3 dimensiones | 2.00 |
| vector_surveillance | health | 2 dimensiones | 3.00 |
| water_management | climate | 3 dimensiones | 2.00 |
| protected_areas | biodiversity | 4 dimensiones | 2.25 |
| climate_agriculture | climate | 4 dimensiones | 1.75 |
| community_health | health | 4 dimensiones | 2.25 |
| green_infrastructure | climate | 4 dimensiones | 1.75 |
| environmental_monitoring | governance | 3 dimensiones | 2.00 |
| land_use_zoning | governance | 4 dimensiones | 2.00 |
| social_protection | social | 4 dimensiones | 2.00 |
| emergency_response | climate | 3 dimensiones | 2.67 |
| biodiversity_corridors | biodiversity | 4 dimensiones | 2.00 |
| pollution_control | health | 3 dimensiones | 2.33 |
| climate_education | governance | 3 dimensiones | 1.67 |

### 5.2. Ranking Algorithm

**Composite Score** = Risk Score + Protective Score

- **Risk Score** (10 dimensiones, higher = worse):
  fire_risk, flooding, hydric_stress, dengue, diarrhea, cv_mortality, resp_hosp, leishmaniasis, poverty, vulnerability

- **Protective Score** (4 dimensiones, inverted: lower = worse):
  governance_general, governance_climatic, biodiversity, natural_habitat

- Normalizacion: min-max por dimension (solo sobre los 10 municipios del workshop)
- Posicion 1 = mayor composite score = mayor prioridad

### 5.3. Correlacion Estadistica

Implementacion pura en Python (sin scipy):

- **Spearman:** `rho = 1 - (6 * sum(d^2)) / (n * (n^2 - 1))`
- **Kendall:** `tau = (concordant - discordant) / (n * (n-1) / 2)`

### 5.4. 10 Municipios del Workshop

| Municipio | Cuadrante | Descripcion |
|-----------|-----------|-------------|
| Iporanga | Q3 | Baja gobernanza, alta biodiversidad |
| Campinas | Q1 | Alta gobernanza, alta biodiversidad |
| Santos | Q1 | Alta gobernanza, alta biodiversidad |
| Sao Joaquim da Barra | Q3 | Baja gobernanza, alta biodiversidad |
| Miracatu | Q3 | Baja gobernanza, alta biodiversidad |
| Eldorado | Q4 | Baja gobernanza, baja biodiversidad |
| Francisco Morato | Q4 | Baja gobernanza, baja biodiversidad |
| Sao Paulo | Q1 | Alta gobernanza, alta biodiversidad |
| Aruja | Q2 | Alta gobernanza, baja biodiversidad |
| Cerquilho | Q2 | Alta gobernanza, baja biodiversidad |

### 5.5. API Endpoints

| Metodo | Ruta | Funcion |
|--------|------|---------|
| GET | `/api/workshop/municipalities` | 10 municipios con riskSummary por categoria |
| GET | `/api/workshop/actions` | 15 acciones PEARC con estadisticas |
| POST | `/api/workshop/ranking` | Guardar ranking (initial/revised) |
| GET | `/api/workshop/rankings/{group_id}` | Obtener rankings + platform |
| POST | `/api/workshop/actions/save` | Guardar acciones seleccionadas |
| GET | `/api/workshop/comparison/{group_id}` | Comparacion completa |

---

## 6. i18n (3 idiomas)

Traduccion completa en EN/ES/PT para:
- 30+ keys de flujo (fases, botones, labels)
- 15 nombres de acciones PEARC
- 15 descripciones de acciones PEARC

---

## 7. Tests Realizados

### 7.1. Backend API Tests (todos pasaron)

```
[OK] Health check: 200
[OK] Workshop municipalities: 200 (10 municipios)
     - Iporanga Q3, gov: 12.40
     - Campinas Q1, gov: 40.90
     - Santos Q1, gov: 42.80
[OK] PEARC actions: 200 (15 acciones)
[OK] Save ranking: 200
[OK] Save actions: 200
[OK] Comparison: 200
     - Spearman: 0.2
     - Kendall: 0.156
     - Action overlap: 100%
     - Position differences: 10 items
     - Suggested actions: 10 items
```

### 7.2. Frontend Build

```
Next.js 14.2.35 - Compiled successfully
Route /workshop: 33.7 kB (First Load: 149 kB)
0 TypeScript errors
1 ESLint warning (pre-existente en MapViewer)
```

---

## 8. Bugs Encontrados y Corregidos (6)

| # | Bug | Solucion |
|---|-----|----------|
| 1 | API endpoints mismatch (frontend usaba rutas incorrectas) | Corregidas 3 funciones handler en workshop/page.tsx |
| 2 | riskSummary retornaba objetos anidados en vez de numeros planos | Backend ahora calcula promedio por categoria |
| 3 | Evidence stars: `Math.round(evidence * 3)` cuando ya era escala 1-3 | Cambiado a `Math.round(avgEvidence)` |
| 4 | actionOverlap se duplicaba (backend ya retorna %) | Removido `* 100` en frontend |
| 5 | Nombres de campos diferentes entre backend y frontend (positionDifferences) | Alineados: userPosition, platformPosition, difference |
| 6 | Boton de ActionsSelector decia "submitRanking" en vez de "viewResults" | Corregido el key de i18n |

---

## 9. Pendientes (Puntos de Adrian)

| Punto | Descripcion | Estado |
|-------|-------------|--------|
| 7 | Red bipartita PEARC (network visualization) | Pendiente |
| 8 | Radar/spider chart por municipio | Pendiente |
| 9 | Comparacion por niveles de vulnerabilidad | Pendiente |
| 1-6 | Positioning, governance audit, IPAM benchmark, profiles | Pendiente (documentado) |
| 11 | Metadata de acciones (costos, tiempos, ejemplos) | Pendiente |

### Proximo paso inmediato:
- Testing end-to-end con `docker-compose up` (backend + frontend juntos)
- Verificar que el CSV tiene los 10 municipios correctos
- Implementar radar chart (punto 8) y red PEARC (punto 7)

---

## 10. Estructura Final de Archivos

```
terrarisk-workshop/
  backend/
    main.py                          [modificado]
    core/
      config.py
      database.py                    [modificado]
      pearc_actions.py               [NUEVO]
      ranking_algorithm.py           [NUEVO]
    api/
      layers.py
      municipalities.py
      groups.py
      workshop_flow.py               [NUEVO]
  frontend/
    messages/
      en.json                        [modificado]
      es.json                        [modificado]
      pt.json                        [modificado]
    src/
      lib/
        types.ts                     [modificado]
        store.ts                     [modificado]
      app/
        workshop/page.tsx            [modificado]
      components/
        workshop/
          WorkshopStepper.tsx        [NUEVO]
          MunicipalityRanking.tsx     [NUEVO]
          ActionsSelector.tsx         [NUEVO]
          RankingComparison.tsx       [NUEVO]
```
