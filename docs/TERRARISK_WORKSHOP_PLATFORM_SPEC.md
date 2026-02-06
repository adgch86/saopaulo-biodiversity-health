# TerraRisk Workshop Platform - Especificación Completa

**Proyecto**: Adrian David - SEMIL-USP Workshop Platform
**Fecha**: 2026-02-04
**Estado**: Pendiente de implementación
**Deadline**: 22 de febrero 2026 (inicio del workshop)

---

## 1. RESUMEN EJECUTIVO

Crear una plataforma web interactiva para el **Workshop SEMIL-USP** (24-26 febrero 2026) que permita a los participantes explorar datos del nexus **Gobernanza-Biodiversidad-Clima-Salud** de 645 municipios de São Paulo.

### Características principales:
- 16+ mapas temáticos como capas (layers) superpuestas
- Sistema de créditos para "comprar" acceso a capas adicionales
- Generación de mapas bivariados al combinar dos variables
- Interfaz gamificada y entretenida para el workshop

---

## 2. CONTEXTO CIENTÍFICO

### 2.1 El Proyecto
- **Investigador**: Dr. Adrian David González Chaves (PhD Ecología, USP)
- **Datos**: 645 municipios de São Paulo × 104 variables × 10 años
- **Objetivo**: Entender cómo gobernanza, biodiversidad, clima y vulnerabilidad social afectan la salud pública

### 2.2 Hallazgos Clave (para contextualizar los mapas)
1. **Dengue es URBANO**: No responde a cobertura forestal (confundido por urbanización)
2. **Malaria es FORESTAL**: Más bosque = más malaria (trade-off real)
3. **Gobernanza REACTIVA**: Los municipios desarrollan gobernanza DESPUÉS de las crisis
4. **Pobreza domina todo**: Explica 27% de la varianza en gobernanza

### 2.3 Sistema de Cuadrantes
Los municipios se clasifican en 4 cuadrantes según Gobernanza vs Vulnerabilidad:

| Cuadrante | Descripción | Color | Prioridad |
|-----------|-------------|-------|-----------|
| Q1 - Modelo | Alta gobernanza + Baja vulnerabilidad | Verde | Referencia |
| Q2 - Riesgo | Alta gobernanza + Alta vulnerabilidad | Amarillo | Media |
| Q3 - Crítico | Baja gobernanza + Alta vulnerabilidad | Rojo | **URGENTE** |
| Q4 - Potencial | Baja gobernanza + Baja vulnerabilidad | Naranja | Desarrollo |

---

## 3. INVENTARIO DE RECURSOS EXISTENTES

### 3.1 Mapas PNG Estáticos (18 capas disponibles)
**Ubicación**: `outputs/figures/workshop_layers/`

| # | Archivo | Variable | Interpretación |
|---|---------|----------|----------------|
| 01 | `01_Governance_UAI_Climatic_Risk.png` | Gobernanza Climática | Verde = bueno |
| 02 | `02_Governance_UAI_General.png` | Gobernanza General | Verde = bueno |
| 03 | `03_Biodiversity_Species_Richness.png` | Riqueza de Especies | Verde = bueno |
| 04 | `04_Natural_Habitat_Vegetation.png` | Cobertura Forestal | Verde = bueno |
| 05 | `05_Pollination_Deficit.png` | Déficit Polinización | Rojo = malo |
| 06 | `06_Flooding_Risk.png` | Riesgo Inundación | Rojo = malo |
| 07 | `07_Fire_Risk_Index.png` | Riesgo Incendios | Rojo = malo |
| 08 | `08_Hydric_Stress_Risk.png` | Estrés Hídrico | Rojo = malo |
| 09 | `09_Zoonotic_Dengue_Incidence.png` | Incidencia Dengue | Rojo = malo |
| 10 | `10_Water_Pollution_Diarrhea.png` | Incidencia Diarrea | Rojo = malo |
| 11 | `11_Heat_Fire_CV_Mortality.png` | Mortalidad Cardiovascular | Rojo = malo |
| 12 | `12_Heat_Fire_Resp_Hospitalization.png` | Hospitalización Respiratoria | Rojo = malo |
| 13 | `13_Poverty_Percentage.png` | % Pobreza | Rojo = malo |
| 14 | `14_Vulnerability_Index.png` | Índice Vulnerabilidad | Rojo = malo |
| 15 | `15_Rural_Population.png` | % Población Rural | Neutral (azul) |
| 16 | `16_Zoonotic_Leishmaniasis_Incidence.png` | Leishmaniasis | Rojo = malo |
| 16b | `16_Infant_Mortality.png` | Mortalidad Infantil | Rojo = malo |
| 16c | `16_Heat_Mortality.png` | Mortalidad por Calor | Rojo = malo |

### 3.2 Mapas Bivariados Existentes
- `bivariate_Governance_vs_Vulnerability_EN.png`
- `bivariate_ClimateRisk_vs_Vulnerability_EN.png`

### 3.3 Datos
- **Dataset principal**: `outputs/municipios_integrado_v8.csv` (645 filas × 104 columnas)
- **Shapefile**: `data/geo/ibge_sp/SP_Municipios_2022.shp`

### 3.4 Variables del Dataset (selección relevante)
```
Identificadores:
- cod_ibge, Municipio, nome_mesorregiao

Gobernanza (UAI):
- UAI_housing, UAI_env, UAI_food, UAI_mob, UAI_Crisk
- idx_gobernanza, idx_gobernanza_100

Biodiversidad:
- mean_species_richness, forest_cover, pol_deficit, idx_biodiv

Clima/Riesgos:
- flooding_risks, hydric_stress_risk, fire_risk_index, idx_clima

Salud:
- incidence_mean_dengue, incidence_mean_leishmaniose
- health_death_circ_mean, health_hosp_resp_mean
- incidence_diarrhea_mean

Social:
- pct_pobreza, pct_rural, pct_preta, pct_indigena
- idx_vulnerabilidad, cuadrante
```

---

## 4. ARQUITECTURA PROPUESTA

### 4.1 Estructura de Directorios

```
terrarisk-workshop/
├── frontend/                    # Next.js / React
│   ├── components/
│   │   ├── MapViewer/          # Visualizador de mapas Leaflet
│   │   ├── LayerSelector/      # Panel de selección de capas
│   │   ├── CreditSystem/       # Sistema de créditos
│   │   ├── BivariateGenerator/ # Generador de mapas bivariados
│   │   └── MunicipalityInfo/   # Panel de información
│   ├── pages/
│   │   ├── index.tsx           # Landing/login grupos
│   │   ├── workshop.tsx        # Interfaz principal
│   │   └── admin.tsx           # Panel de control Adrian
│   └── public/
│       └── maps/               # PNG de las 16 capas
│
├── backend/                     # FastAPI / Python
│   ├── api/
│   │   ├── credits.py          # Gestión de créditos
│   │   ├── maps.py             # Servir mapas y GeoJSON
│   │   └── bivariate.py        # Generar mapas bivariados
│   ├── data/
│   │   ├── municipios.csv      # Dataset principal
│   │   └── geojson/            # Geometrías municipios
│   └── utils/
│       └── map_generator.py    # Lógica de generación de mapas
│
└── docker-compose.yml          # Deployment
```

### 4.2 Stack Tecnológico

| Componente | Tecnología | Justificación |
|------------|------------|---------------|
| Frontend | Next.js + TypeScript | SSR, fácil deploy |
| Mapas | Leaflet + React-Leaflet | Open source, flexible |
| Styling | Tailwind CSS | Rápido, consistente |
| Backend | FastAPI (Python) | Integra con scripts existentes |
| DB | SQLite/JSON | Simple para workshop temporal |
| Deploy | Docker + VPS Contabo | Control total |

---

## 5. FUNCIONALIDADES CORE

### 5.1 MAPA INTERACTIVO BASE
- **Tecnología**: Leaflet.js o Mapbox GL
- **Base**: Mapa de São Paulo con 645 municipios
- **Interactividad**:
  - Hover: Mostrar nombre del municipio + valores
  - Click: Panel lateral con información detallada
  - Zoom: Permitir acercamiento

### 5.2 SELECTOR DE CAPAS (Layer Picker)
```
┌─────────────────────────────────────┐
│ 📊 CAPAS DISPONIBLES                │
├─────────────────────────────────────┤
│ ☑ Capa Base (siempre visible)       │
│                                      │
│ 🔓 GRATIS (incluidas):              │
│   ☐ Gobernanza UAI General          │
│   ☐ Índice Vulnerabilidad           │
│                                      │
│ 💰 CON CRÉDITOS:                    │
│   🔒 Riesgo Inundación (2 créditos) │
│   🔒 Incidencia Dengue (2 créditos) │
│   🔒 Cobertura Forestal (2 créditos)│
│   🔒 % Pobreza (1 crédito)          │
│   ...                               │
│                                      │
│ 💎 Créditos disponibles: 10         │
└─────────────────────────────────────┘
```

### 5.3 SISTEMA DE CRÉDITOS
- **Créditos iniciales por grupo**: 10
- **Costos por capa**:
  - Variables simples: 1 crédito (pobreza, rural, población negra)
  - Variables complejas: 2 créditos (riesgos, biodiversidad, salud)
  - Índices compuestos: 3 créditos (gobernanza UAI completo)

**Mecánica del juego**:
1. Grupos inician con 10 créditos
2. Seleccionan qué capas "comprar"
3. Una vez compradas, se revelan en el mapa
4. No hay reembolso (decisión estratégica)

### 5.4 MAPAS BIVARIADOS (Feature Estrella)
Cuando el usuario selecciona 2 capas, generar automáticamente un **mapa bivariado**:

```
Capa 1: Gobernanza    +    Capa 2: Vulnerabilidad
         ↓                          ↓
    ┌────────────────────────────────────┐
    │       MAPA BIVARIADO               │
    │                                    │
    │   Cuadrantes con 4 colores:        │
    │   🟢 Q1: Alta Gov + Baja Vuln      │
    │   🟡 Q2: Alta Gov + Alta Vuln      │
    │   🔴 Q3: Baja Gov + Alta Vuln      │
    │   🟠 Q4: Baja Gov + Baja Vuln      │
    │                                    │
    │   + Scatter plot lateral           │
    └────────────────────────────────────┘
```

**Combinaciones predefinidas sugeridas**:
1. Gobernanza × Vulnerabilidad (clásica)
2. Riesgo Climático × Vulnerabilidad
3. Cobertura Forestal × Incidencia Dengue
4. Pobreza × Gobernanza
5. Biodiversidad × Carga de Enfermedad

### 5.5 PANEL DE INFORMACIÓN DE MUNICIPIO
Al hacer click en un municipio:

```
┌─────────────────────────────────────┐
│ 📍 CAMPINAS                         │
│ Región: Metropolitana               │
│ Cuadrante: Q1 (Modelo)              │
├─────────────────────────────────────┤
│ Variables visibles:                 │
│ • Gobernanza UAI: 78/100 🟢         │
│ • Vulnerabilidad: 11.0% 🟢          │
│ • Población: 1.2M habitantes        │
├─────────────────────────────────────┤
│ Variables ocultas: 14               │
│ [Comprar más capas para revelar]    │
└─────────────────────────────────────┘
```

---

## 6. FLUJO DE USUARIO

```
1. INICIO
   ├── Crear grupo (nombre del grupo)
   ├── Recibir 10 créditos
   └── Ver mapa base + 2 capas gratuitas

2. EXPLORACIÓN
   ├── Revisar capas disponibles
   ├── Decidir estrategia ("¿qué quiero saber?")
   └── "Comprar" capas con créditos

3. ANÁLISIS
   ├── Activar capas compradas
   ├── Superponer 2 capas → mapa bivariado
   └── Click en municipios para detalles

4. PRESENTACIÓN
   ├── Cada grupo explica su estrategia
   ├── Muestra qué capas compraron
   └── Conclusiones sobre municipios prioritarios
```

---

## 7. DISEÑO UI/UX

### 7.1 Layout Principal

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER: TerraRisk Workshop | Grupo: [Nombre] | 💎 10 créditos   │
├────────────────────────────────────┬────────────────────────────┤
│                                    │                            │
│                                    │  📊 PANEL DE CAPAS         │
│                                    │  ────────────────          │
│        MAPA INTERACTIVO            │  Gratis:                   │
│        (70% del ancho)             │  ☑ Gobernanza              │
│                                    │  ☑ Vulnerabilidad          │
│                                    │                            │
│                                    │  Con créditos:             │
│                                    │  🔒 Dengue (2)             │
│                                    │  🔒 Bosque (2)             │
│                                    │  ...                       │
│                                    │                            │
│                                    │  ────────────────          │
│                                    │  📍 MUNICIPIO              │
│                                    │  [Info del seleccionado]   │
│                                    │                            │
├────────────────────────────────────┴────────────────────────────┤
│ FOOTER: Leyenda de colores | Escala | Fuente: USP/SEMIL 2026   │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Paleta de Colores

| Elemento | Color | Hex |
|----------|-------|-----|
| Positivo/Bueno | Verde | #2E7D32 |
| Medio | Amarillo | #FFC107 |
| Negativo/Malo | Rojo | #C62828 |
| Neutral | Azul | #1565C0 |
| Background | Gris claro | #F5F5F5 |
| Accent | Púrpura | #7B1FA2 |

### 7.3 Estilo Visual
- **Minimalista científico**: Limpio, datos claros, sin distracciones
- **Gamificación sutil**: Créditos como "monedas", sonidos al desbloquear
- **Responsive**: Funcionar en proyector del workshop (16:9) y tablets

---

## 8. API ENDPOINTS

### 8.1 Endpoints Backend (FastAPI)

```python
# Groups / Credits
GET  /api/groups                    # Lista grupos
POST /api/groups                    # Crear grupo
GET  /api/groups/{id}               # Detalle de grupo
GET  /api/groups/{id}/credits       # Ver créditos
POST /api/groups/{id}/purchase      # Comprar capa

# Layers / Maps
GET  /api/layers                    # Lista de capas disponibles
GET  /api/layers/{id}               # Detalle de una capa
GET  /api/layers/{id}/image         # PNG de la capa
GET  /api/layers/{id}/geojson       # GeoJSON con datos

# Bivariate Maps
POST /api/bivariate                 # Generar mapa bivariado
     Body: { layer1_id, layer2_id }
     Returns: { image_url, stats }

# Municipalities
GET  /api/municipalities            # Lista de municipios
GET  /api/municipalities/{code}     # Datos de un municipio
GET  /api/municipalities/search     # Buscar por nombre

# Admin
GET  /api/admin/stats               # Estadísticas de uso
POST /api/admin/reset/{group_id}    # Resetear créditos
GET  /api/admin/export              # Exportar datos del workshop
```

### 8.2 Modelos de Datos

```typescript
// Grupo
interface Group {
  id: string;
  name: string;
  credits: number;
  purchasedLayers: string[];
  createdAt: Date;
}

// Capa
interface Layer {
  id: string;
  name: string;
  nameEN: string;
  description: string;
  cost: number;
  category: 'governance' | 'biodiversity' | 'climate' | 'health' | 'social';
  isPositive: boolean; // true = verde es bueno
  imageUrl: string;
  variable: string; // nombre en el CSV
}

// Municipio
interface Municipality {
  code: string;
  name: string;
  region: string;
  population: number;
  quadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4';
  values: Record<string, number>;
}
```

---

## 9. CONFIGURACIÓN DE CAPAS

```json
{
  "layers": [
    {
      "id": "governance_uai",
      "name": "Gobernanza UAI General",
      "nameEN": "General Governance (UAI)",
      "variable": "idx_gobernanza_100",
      "cost": 0,
      "category": "governance",
      "isPositive": true,
      "image": "02_Governance_UAI_General.png"
    },
    {
      "id": "vulnerability",
      "name": "Índice de Vulnerabilidad",
      "nameEN": "Vulnerability Index",
      "variable": "idx_vulnerabilidad",
      "cost": 0,
      "category": "social",
      "isPositive": false,
      "image": "14_Vulnerability_Index.png"
    },
    {
      "id": "dengue",
      "name": "Incidencia de Dengue",
      "nameEN": "Dengue Incidence",
      "variable": "incidence_mean_dengue",
      "cost": 2,
      "category": "health",
      "isPositive": false,
      "image": "09_Zoonotic_Dengue_Incidence.png"
    },
    {
      "id": "forest_cover",
      "name": "Cobertura Forestal",
      "nameEN": "Forest Cover",
      "variable": "forest_cover",
      "cost": 2,
      "category": "biodiversity",
      "isPositive": true,
      "image": "04_Natural_Habitat_Vegetation.png"
    },
    {
      "id": "poverty",
      "name": "Porcentaje de Pobreza",
      "nameEN": "Poverty Percentage",
      "variable": "pct_pobreza",
      "cost": 1,
      "category": "social",
      "isPositive": false,
      "image": "13_Poverty_Percentage.png"
    },
    {
      "id": "flooding",
      "name": "Riesgo de Inundación",
      "nameEN": "Flooding Risk",
      "variable": "flooding_risks",
      "cost": 2,
      "category": "climate",
      "isPositive": false,
      "image": "06_Flooding_Risk.png"
    },
    {
      "id": "fire_risk",
      "name": "Riesgo de Incendios",
      "nameEN": "Fire Risk Index",
      "variable": "fire_risk_index",
      "cost": 2,
      "category": "climate",
      "isPositive": false,
      "image": "07_Fire_Risk_Index.png"
    },
    {
      "id": "species_richness",
      "name": "Riqueza de Especies",
      "nameEN": "Species Richness",
      "variable": "mean_species_richness",
      "cost": 2,
      "category": "biodiversity",
      "isPositive": true,
      "image": "03_Biodiversity_Species_Richness.png"
    },
    {
      "id": "cv_mortality",
      "name": "Mortalidad Cardiovascular",
      "nameEN": "Cardiovascular Mortality",
      "variable": "health_death_circ_mean",
      "cost": 2,
      "category": "health",
      "isPositive": false,
      "image": "11_Heat_Fire_CV_Mortality.png"
    },
    {
      "id": "resp_hosp",
      "name": "Hospitalización Respiratoria",
      "nameEN": "Respiratory Hospitalization",
      "variable": "health_hosp_resp_mean",
      "cost": 2,
      "category": "health",
      "isPositive": false,
      "image": "12_Heat_Fire_Resp_Hospitalization.png"
    },
    {
      "id": "diarrhea",
      "name": "Incidencia de Diarrea",
      "nameEN": "Diarrhea Incidence",
      "variable": "incidence_diarrhea_mean",
      "cost": 2,
      "category": "health",
      "isPositive": false,
      "image": "10_Water_Pollution_Diarrhea.png"
    },
    {
      "id": "leishmaniasis",
      "name": "Leishmaniasis",
      "nameEN": "Leishmaniasis Incidence",
      "variable": "incidence_mean_leishmaniose",
      "cost": 2,
      "category": "health",
      "isPositive": false,
      "image": "16_Zoonotic_Leishmaniasis_Incidence.png"
    },
    {
      "id": "rural",
      "name": "Población Rural",
      "nameEN": "Rural Population",
      "variable": "pct_rural",
      "cost": 1,
      "category": "social",
      "isPositive": null,
      "image": "15_Rural_Population.png"
    },
    {
      "id": "hydric_stress",
      "name": "Estrés Hídrico",
      "nameEN": "Hydric Stress Risk",
      "variable": "hydric_stress_risk",
      "cost": 2,
      "category": "climate",
      "isPositive": false,
      "image": "08_Hydric_Stress_Risk.png"
    },
    {
      "id": "pollination",
      "name": "Déficit de Polinización",
      "nameEN": "Pollination Deficit",
      "variable": "pol_deficit",
      "cost": 2,
      "category": "biodiversity",
      "isPositive": false,
      "image": "05_Pollination_Deficit.png"
    },
    {
      "id": "climate_governance",
      "name": "Gobernanza Climática",
      "nameEN": "Climate Risk Governance",
      "variable": "UAI_Crisk",
      "cost": 3,
      "category": "governance",
      "isPositive": true,
      "image": "01_Governance_UAI_Climatic_Risk.png"
    }
  ]
}
```

---

## 10. PANEL DE ADMINISTRADOR

### 10.1 Funcionalidades
- Ver estado de todos los grupos
- Resetear créditos de un grupo
- Ver qué capas ha comprado cada grupo
- Exportar estadísticas de uso
- Proyectar el mapa de cualquier grupo en pantalla grande

### 10.2 Mockup Admin

```
┌─────────────────────────────────────────────────────────────────┐
│ 🔒 ADMIN: Dr. Adrian González                                   │
├─────────────────────────────────────────────────────────────────┤
│ GRUPOS ACTIVOS                                                  │
│ ────────────────────────────────────────────────────────────    │
│ │ Grupo          │ Créditos │ Capas    │ Acciones           │  │
│ │ Investigadores │    4     │ 6/16     │ [Ver] [Reset]      │  │
│ │ Policy-makers  │    7     │ 3/16     │ [Ver] [Reset]      │  │
│ │ Técnicos       │    2     │ 8/16     │ [Ver] [Reset]      │  │
│ │ Estudiantes    │   10     │ 2/16     │ [Ver] [Reset]      │  │
│ ────────────────────────────────────────────────────────────    │
│                                                                 │
│ ESTADÍSTICAS                                                    │
│ • Capa más comprada: Incidencia Dengue (4 grupos)              │
│ • Capa menos comprada: Mortalidad Infantil (0 grupos)          │
│ • Promedio créditos restantes: 5.75                            │
│                                                                 │
│ [📺 Proyectar grupo seleccionado]                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. GAMIFICACIÓN

### 11.1 Elementos de Juego
- **Feedback visual**: Animación al desbloquear capa (brillo, sonido sutil)
- **Progress bar**: "Has desbloqueado 6/16 capas"
- **Achievements opcionales**:
  - 🏆 "Explorador" - Desbloquear 5+ capas
  - 🎯 "Estratega" - Crear 3 mapas bivariados
  - 🔍 "Detective" - Ver información de 50+ municipios

### 11.2 Momentos de Sorpresa
- Al combinar Bosque + Dengue: Popup explicando la paradoja urbana
- Al combinar Gobernanza + Riesgo: Popup sobre gobernanza reactiva
- Al ver Q3 (crítico): Highlight especial de "municipios prioritarios"

---

## 12. DEPLOYMENT

### 12.1 Docker Compose

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
    depends_on:
      - api

  api:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
      - ./frontend/public/maps:/app/maps

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - api
```

### 12.2 Servidor
- **VPS Contabo** (ya disponible)
- Docker Compose para frontend + backend
- Nginx como reverse proxy
- SSL con Let's Encrypt

### 12.3 Dominio Sugerido
- `terrarisk.arlexperalta.com` o
- `workshop.adriandavid.science`

---

## 13. TIMELINE SUGERIDO

| Fase | Duración | Entregables |
|------|----------|-------------|
| **1. Setup** | 2-3 días | Proyecto base, Docker, CI/CD |
| **2. Backend** | 3-4 días | API endpoints, generador bivariados |
| **3. Frontend** | 4-5 días | UI completa, sistema de créditos |
| **4. Integración** | 2 días | Testing, ajustes |
| **5. Deploy** | 1 día | Producción en Contabo |
| **Total** | ~2 semanas | Plataforma lista |

**Deadline**: Antes del 22 de febrero 2026 (inicio del workshop)

---

## 14. ARCHIVOS DE REFERENCIA

| Archivo | Ubicación | Contenido |
|---------|-----------|-----------|
| Dataset principal | `outputs/municipios_integrado_v8.csv` | 645 municipios × 104 variables |
| Mapas PNG | `outputs/figures/workshop_layers/*.png` | 18 capas temáticas |
| Mapas bivariados | `outputs/figures/workshop_layers/bivariate_*.png` | 2 mapas ejemplo |
| Shapefile | `data/geo/ibge_sp/SP_Municipios_2022.shp` | Geometrías municipios |
| Script mapas | `scripts/create_workshop_layers.py` | Lógica de generación |
| Script bivariados | `scripts/create_bivariate_maps_EN.py` | Lógica bivariados |
| Contexto científico | `.claude/SCIENCE_TEAM_CONTEXT.md` | Documentación completa |

---

## 15. COMANDOS PARA INICIAR DESARROLLO

```bash
# Cuando estés listo para comenzar:

# 1. Ir al directorio del proyecto
cd "C:\Users\arlex\Documents\Adrian David"

# 2. Comando para Claude Code
# "Implementa el backend de TerraRisk según docs/TERRARISK_WORKSHOP_PLATFORM_SPEC.md"
# o
# "Implementa el frontend de TerraRisk según docs/TERRARISK_WORKSHOP_PLATFORM_SPEC.md"
```

---

## 16. CHECKLIST PRE-DESARROLLO

- [x] Acceso a dataset CSV (645 municipios × 104 variables)
- [x] 18 PNG de workshop_layers disponibles
- [x] Shapefile de municipios accesible
- [ ] Dominio configurado
- [ ] VPS Contabo preparado para deploy
- [ ] Contacto con Dr. Adrian para dudas científicas

---

*Documento preparado para handoff a equipo de desarrollo*
*Febrero 2026*
