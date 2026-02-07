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

**Estado:** DEPLOYED en produccion. Backend + Frontend completos. Tests E2E pasados (11/11 backend, 7/7 frontend).
**URL:** https://terrarisk.arlexperalta.com
**Deploy:** Contabo VPS (161.97.95.132) via Docker Compose

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

## 9. Deploy en Produccion

**Fecha deploy:** 2026-02-05 23:59 (CET)
**Servidor:** Contabo VPS (161.97.95.132)
**URL:** https://terrarisk.arlexperalta.com

```
Verificacion post-deploy:
  Health check:            200 OK
  Workshop municipalities: 10 (todos presentes)
  PEARC actions:           15 (todas las categorias)
  Frontend HTTPS:          200 OK
  Docker containers:       2/2 running (api + frontend)
```

---

## 10. Tests End-to-End Completos

### 10.1. Backend API (11/11 OK)

```
[OK] Health check: 200
[OK] Workshop municipalities: 10 (Iporanga Q3, Campinas Q1, Santos Q1...)
[OK] PEARC actions: 15 (5 categorias)
[OK] Create group
[OK] Save initial ranking (10 positions)
[OK] Get rankings (initial + platform)
     Platform top 3: Sao Joaquim da Barra (1.38), Iporanga (1.04), Francisco Morato (1.00)
[OK] Save revised ranking
[OK] Save selected actions (5)
[OK] Full comparison (Spearman: 0.164, Kendall: 0.111)
[OK] Layers endpoint: 16
[OK] All municipalities: 645
```

### 10.2. Frontend Integration (7/7 OK)

Flujo completo simulando un usuario real a traves del proxy Next.js:

```
Step 1: Create group "Workshop Team Alpha"           [OK]
Step 2: Page loads (16 layers, 645 munis, 10 workshop, 15 actions) [OK]
Step 3: Phase 1 - Initial ranking (SP > Campinas > Santos > ...) [OK]
Step 4: Phase 2 - Buy layer "Gobernanza Riesgo Climatico"  [OK]
Step 5: Phase 3 - Revised ranking (SJB > Iporanga > F.Morato)  [OK]
Step 6: Phase 3 - Select 5 PEARC actions                    [OK]
Step 7: Phase 4 - Comparison results                         [OK]
         Spearman: 0.624 (62%) - MODERATE agreement
         Kendall:  0.467 (47%)
         Action overlap: 80%
         Biggest diff: Cerquilho (user #10 vs platform #4)
```

---

## 11. Pendientes por Implementar (Notas de Adrian)

### PRIORIDAD ALTA (para el workshop Feb 22-26)

#### Punto 7 - Red Bipartita PEARC (Network Visualization)
**Que pidio Adrian:** Visualizar la relacion entre acciones PEARC y dimensiones de riesgo como una red bipartita interactiva.
**Que falta:**
- Componente de visualizacion de red (d3.js o vis-network)
- Nodos izquierda: 15 acciones PEARC (coloreados por categoria)
- Nodos derecha: 14 dimensiones de riesgo
- Aristas: ponderadas por evidencia (1-3), grosor proporcional
- Interactividad: hover para resaltar conexiones, click para filtrar
- Integracion en la Fase 3 (al seleccionar acciones, resaltar sus conexiones)
**Estimacion:** ~4-6 horas de desarrollo
**Impacto:** Alto - permite a los participantes entender visualmente que acciones impactan que riesgos

#### Punto 8 - Radar/Spider Chart por Municipio
**Que pidio Adrian:** Grafico radar con las 5 dimensiones de riesgo (governance, biodiversity, climate, health, social) para cada municipio seleccionado.
**Que falta:**
- Componente RadarChart (recharts o chart.js)
- Mostrar en la Fase 2 al hacer click en un municipio
- Superponer multiples municipios para comparacion
- Normalizar valores a escala 0-100 para comparabilidad
- Opcional: mostrar en Fase 4 junto a la comparacion de rankings
**Estimacion:** ~3-4 horas de desarrollo
**Impacto:** Alto - representacion visual intuitiva del perfil de riesgo

#### Punto 9 - Comparacion por Niveles de Vulnerabilidad
**Que pidio Adrian:** Separar municipios en grupos de alta/baja vulnerabilidad y comparar patrones.
**Que falta:**
- Split de los 10 municipios en 2 grupos segun idx_vulnerabilidad
- Tabla comparativa: promedios de cada dimension por grupo
- Highlight visual de como las acciones PEARC impactan diferente a cada grupo
- Integracion en Fase 4 (seccion adicional en RankingComparison)
**Estimacion:** ~2-3 horas de desarrollo
**Impacto:** Medio-alto - permite entender inequidades

### PRIORIDAD MEDIA (mejoras pre-workshop)

#### Punto 4 - Perfiles de Participantes
**Que pidio Adrian:** Capturar perfil de cada grupo (area de expertise, familiaridad con los temas) al registrarse.
**Que falta:**
- Formulario extendido en la pagina de registro (landing)
- Campos: area profesional, experiencia en gestion ambiental, municipio de origen
- Almacenar en BD y mostrar en panel admin
**Estimacion:** ~2 horas
**Impacto:** Medio - datos utiles para analisis post-workshop

#### Punto 5 - Valor de la Informacion
**Que pidio Adrian:** Metricas sobre cuanto cambia la decision de los participantes despues de ver datos (Phase 1 vs Phase 3).
**Que falta:**
- Endpoint que compare ranking inicial vs revisado automaticamente
- Calcular: cuantas posiciones cambiaron, en que direccion
- Mostrar en panel admin: "grupos que mas cambiaron de opinion"
- Agregar a Fase 4: seccion "Tu cambio de perspectiva"
**Estimacion:** ~2-3 horas
**Impacto:** Medio - metricas clave para la publicacion

#### Punto 6 - Cuanto Pagaron por la Informacion
**Que pidio Adrian:** Analizar que capas compraron los grupos y correlacionar con cambios en ranking.
**Que falta:**
- Panel admin: capas mas compradas, creditos gastados por grupo
- Correlacion: grupos que compraron mas capas cambiaron mas su ranking?
- Visualizacion: heatmap de compras por grupo
**Estimacion:** ~2 horas (parcialmente implementado en admin existente)
**Impacto:** Medio - dato interesante para paper

### PRIORIDAD BAJA (post-workshop o version futura)

#### Punto 1 - Positioning vs Plataformas Existentes
**Que pidio Adrian:** Diferenciar TerraRisk de Adapta Brasil, IPAM, MapBiomas.
**Estado:** Documentado en notas, no requiere desarrollo.

#### Punto 2 - Auditoria de Gobernanza
**Que pidio Adrian:** Funcionalidad para auditar politicas climaticas municipales.
**Estado:** Vision futura, fuera de scope del workshop.

#### Punto 3 - Benchmark IPAM
**Que pidio Adrian:** Investigar IPAM para ideas de UX y datos.
**Estado:** Tarea de research, no de desarrollo.

#### Punto 11 - Metadata Extendida de Acciones
**Que pidio Adrian:** Agregar a cada accion PEARC: costo estimado, tiempo de implementacion, ejemplos en Brasil, fuentes.
**Que falta:**
- Extender el catalogo pearc_actions.py con campos adicionales
- Mostrar en modal expandido al hacer click en una accion
- Links a documentos de referencia
**Estimacion:** ~3-4 horas (la mayoria es curar los datos)
**Impacto:** Bajo para el workshop, alto para version productiva

---

## 12. Roadmap Sugerido Pre-Workshop

```
Semana del 10-14 Feb:
  [ ] Radar chart por municipio (Punto 8) - 3h
  [ ] Red bipartita PEARC (Punto 7) - 5h
  [ ] Comparacion por vulnerabilidad (Punto 9) - 3h

Semana del 17-21 Feb:
  [ ] Perfiles de participantes (Punto 4) - 2h
  [ ] Metricas de cambio de perspectiva (Punto 5) - 3h
  [ ] Testing con datos reales + QA visual
  [ ] Deploy final pre-workshop

22-26 Feb: WORKSHOP SEMIL-USP
```

**Total estimado:** ~16-20 horas de desarrollo para features completos

---

## 13. Estructura Final de Archivos

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
