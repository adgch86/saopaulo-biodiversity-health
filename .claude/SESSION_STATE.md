# Adrian David - Estado de Sesion

> Este archivo se actualiza AUTOMATICAMENTE al final de cada sesion de Claude Code.
> El workspace principal (Arlex Peralta) lo lee al iniciar sesion.

## Ultima Sesion

**Fecha:** 2026-02-07
**Estado general:** Carpeta reorganizada completamente. Estructura limpia, sync a Drive verificado.

### Lo que se hizo hoy

1. **Reorganizacion completa de la carpeta Adrian David**
   - **Basura eliminada:** `nul`, `src/` vacio, PDF duplicado en Papers, PDF comprimido duplicado en docs, `temp_output.txt`
   - **scripts/** reorganizado en 5 subcarpetas:
     - `analisis/` (15 scripts activos H1-H6)
     - `datos/` (10 scripts de creacion/procesamiento datasets)
     - `visualizacion/` (10 scripts de mapas, dashboards, graficos)
     - `utils/` (16 scripts de sync, automation, helpers)
     - `R/` (12 scripts de R activos)
   - **37 scripts viejos** archivados en `Adrian David - Archivo/scripts_old/`
   - **outputs/** reorganizado: 61 CSVs sueltos distribuidos en subcarpetas tematicas:
     - `dataset/` (municipios_integrado.csv - sin version en nombre)
     - `correlaciones/` (12 CSVs)
     - `modelos/` (26 CSVs - h1_*, modelos_mixtos_*, etc.)
     - `dengue/` (6 CSVs)
     - `clasificacion/` (15 CSVs + TXTs)
     - Subcarpetas H1-H6, figures/, dashboard_mockups/ sin cambios
   - **5 outputs viejos** archivados (v5, v6, v7 del dataset + WhatsApp)
   - **docs/** reorganizado en 5 subcarpetas: `informes/`, `metodologia/`, `negocio/`, `workshop/`, `sesiones/`
   - **notebooks/** renombrado a **presentaciones/** (no tenia .ipynb, solo PPTX/DOCX)
   - **Paths actualizados** en 24 scripts (Python + R) para apuntar a nuevas rutas
   - **sync_to_drive.ps1** actualizado: exclusion de `.next` agregada, bug de args duplicados corregido

2. **Sync a Google Drive verificado**
   - Todas las subcarpetas: 100% match local = Drive
   - Limpieza de Drive: 190 archivos sueltos borrados (ya en subcarpetas)
   - `node_modules/` (~25k archivos) y `.next/` (~1.8k archivos) borrados del Drive
   - Carpeta `notebooks/` vieja borrada del Drive
   - Papers/ tiene 163 en Drive vs 2 local (Adrian sube directo al Drive, correcto)

### Estructura nueva

```
Adrian David/
├── admin/                (32 archivos - becas, CVs)
├── data/                 (2.7GB - NO sync a Drive)
├── docs/
│   ├── informes/         (7)
│   ├── metodologia/      (5)
│   ├── negocio/          (4)
│   ├── workshop/         (7)
│   └── sesiones/         (1)
├── outputs/
│   ├── dataset/          (municipios_integrado.csv)
│   ├── correlaciones/    (12)
│   ├── modelos/          (26)
│   ├── dengue/           (6)
│   ├── clasificacion/    (15)
│   ├── h1-h6_*/          (por hipotesis)
│   ├── figures/          (127 PNGs)
│   └── dashboard_mockups/
├── Papers/               (2 local, 163 en Drive)
├── presentaciones/       (antes notebooks/)
├── scripts/
│   ├── analisis/         (15)
│   ├── datos/            (10)
│   ├── visualizacion/    (10)
│   ├── utils/            (16)
│   └── R/                (12)
├── terrarisk-workshop/   (app Next.js+FastAPI)
└── [archivos .md raiz]
```

### Archivo externo

`C:\Users\arlex\Documents\Adrian David - Archivo\`
- `scripts_old/` - 37 versiones viejas
- `outputs_old/` - 5 archivos (v5, v6, v7 + backup v8 + WhatsApp)
- `docs_old/` - 1 archivo (INFORME V3)

### Pendiente (para workshop Feb 22-26)

- [x] Red bipartita PEARC network (punto 7)
- [x] Radar chart por municipio (punto 8)
- [x] Comparacion por vulnerabilidad (punto 9)
- [x] Perfiles de participantes (punto 4)
- [x] Metricas cambio de perspectiva (punto 5)
- [x] Quitar etiquetas Q1-Q4
- [x] Adaptar UI a telefono
- [x] Reorganizar carpeta proyecto
- [x] Sync a Drive limpio
- [ ] Testing con datos reales + QA visual
- [ ] Deploy final pre-workshop (validacion completa)

### Proximos pasos

1. Testing con datos reales + QA visual (probar flujo completo en movil)
2. Validacion final pre-workshop

### Proyectos activos

1. **Air Pollution & Pollinator Networks** - tabla enviada a Luisa (6 Feb), esperando respuesta
2. **Resilient Landscapes (Sao Paulo)** - Workshop SEMIL-USP Feb 22-26
   - TerraRisk Workshop: TODOS los features implementados, UI responsive, deployed
   - Carpeta reorganizada y sincronizada con Drive
   - Pendiente: testing con datos reales + QA visual
