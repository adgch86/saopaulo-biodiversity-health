# Brief del Proyecto Adrian David
## Onboarding para Juan "Monti" Cabrera

**Fecha:** Febrero 2026
**Preparado por:** Dante (CEO, Peralta Digital)
**Para:** Monti - Project Coordinator & Business Scout

---

## 1. Resumen Ejecutivo

Este es un proyecto de **investigacion cientifica aplicada** liderado por el **Dr. Adrian David Gonzalez Chaves** (PhD Ecologia, USP Brasil). El objetivo central es analizar como la biodiversidad, el clima, la salud publica y la gobernanza interactuan en los **645 municipios del estado de Sao Paulo, Brasil**, y convertir esos hallazgos en herramientas utiles para la toma de decisiones.

**En una frase:** Datos cientificos sobre riesgo ambiental y salud publica, transformados en productos digitales para gobiernos locales y organizaciones.

**URL de la plataforma:** https://terrarisk.arlexperalta.com

---

## 2. Equipo Actual

| Persona | Rol | Ubicacion |
|---------|-----|-----------|
| **Dr. Adrian David Gonzalez Chaves** | Director Cientifico, Investigador Principal | Sao Paulo, Brasil |
| **Arlex Peralta** | Desarrollo tecnologico (web, APIs, infraestructura) | Remoto |
| **Dante + Science Team** | 6 investigadores IA que asisten en analisis estadistico, GIS, datos, ecologia | Virtual |
| **Monti (tu)** | Project Coordinator + Business Scout | Lisboa, Portugal |

### Sobre Adrian

- PhD en Ecologia (USP, Brasil)
- Especialista en ecologia del paisaje y servicios ecosistemicos
- Cientifico de datos con experiencia en R y analisis cuantitativos
- Experto en polinizacion, conservacion de abejas y agroecosistemas
- Publicaciones en revistas de alto impacto (Functional Ecology, Environmental Research Letters, Journal of Applied Ecology)
- Premio "Outstanding Use of Quantitative Methods" (SCCS New York, 2018)

---

## 3. Proyectos Activos

Hay **2 proyectos cientificos activos** y **1 iniciativa de negocio** en fase de validacion:

### 3.1 Resilient Landscapes (Sao Paulo) - PRINCIPAL

**Titulo completo:** *Resilient Landscapes: Integrating Planetary Health, Nexus Thinking, and Environmental Justice in Sao Paulo's Agrifood Systems*

**Estado:** Framework analitico completado. Preparando publicacion cientifica + Workshop presencial.

**Que se hizo:**
- Dataset integrado de **645 municipios x 112 variables** (salud, biodiversidad, clima, gobernanza, vulnerabilidad social)
- 6 hipotesis (H1-H6) analizadas con modelos estadisticos (SEM, mediacion, moderacion)
- Plataforma web interactiva **TerraRisk** (ver seccion 4)

**Hallazgos principales (para que entiendas el "producto"):**

| Hallazgo | Implicacion de negocio |
|----------|----------------------|
| Ecosistemas biodiversos **reducen** dengue (-45%) y diarrea (-45%) | Argumento para invertir en restauracion ecologica |
| La gobernanza municipal **NO reduce** directamente los riesgos climaticos | Los municipios necesitan herramientas mejores |
| La pobreza **anula** el efecto protector de la gobernanza | Focalizar intervencion en municipios vulnerables |
| Cobertura forestal reduce deficit de polinizacion (-77%) | Valor economico del bosque cuantificable |
| Cada enfermedad tiene su propia "firma" de predictores | Se pueden disenar intervenciones personalizadas por municipio |

**Proximo evento clave:**
- **Workshop SEMIL-USP**: 22-26 de Febrero 2026, Sao Paulo
- TerraRisk sera usado en vivo con participantes reales
- Es la primera validacion publica de la plataforma

### 3.2 Air Pollution & Pollinator Networks - SEGUNDO

**Titulo:** *The invisible threat: Air pollution rewires pollinator networks worldwide*

**PIs:** Dra. Luisa Carvalheiro & Dr. Ruben Alarcon
**Rol de Adrian:** Consultor - Extraccion de datos ambientales
**Presupuesto:** $600 USD ($200/mes x 3 meses, Feb-Abr 2026)

**Que es:** Un manuscrito que fue rechazado de *Science* por problemas metodologicos en los datos de contaminacion atmosferica. Adrian fue contratado para rehacer la extraccion de datos con fuentes mas robustas (CAMS/ERA5 en vez de TROPOMI).

**Datos:** 1,468 redes de polinizadores en 6 continentes.

**Estado:** Propuesta enviada, esperando respuesta de Luisa (6 Feb).

### 3.3 TerraRisk Analytics - OPORTUNIDAD DE NEGOCIO

**Esto es lo que mas te interesa para tu rol.**

TerraRisk es la plataforma web que visualiza todos los datos del proyecto Resilient Landscapes. Actualmente es una herramienta academica, pero tiene potencial para convertirse en un **producto SaaS** o servicio de consultoria.

**Clientes potenciales:**
- Municipios de Sao Paulo (645) que necesitan datos para planificacion
- ONGs ambientales que trabajan en conservacion
- Organismos estatales/federales (IBAMA, ICMBio, Secretaria de Meio Ambiente)
- Organizaciones internacionales (OMS, FAO, UNEP) enfocadas en One Health / Planetary Health
- Consultoras ambientales que necesitan datos integrados
- Universidades y centros de investigacion

---

## 4. TerraRisk - La Plataforma

### Stack Tecnico

| Componente | Tecnologia |
|------------|------------|
| Frontend | Next.js 14 + React 18 + Tailwind CSS + Zustand |
| Backend | FastAPI (Python) + SQLite |
| Mapas | Leaflet + react-leaflet |
| Idiomas | Ingles, Espanol, Portugues |
| Deploy | Docker en VPS Contabo |
| URL | https://terrarisk.arlexperalta.com |

### Flujo del Workshop (4 fases)

La plataforma esta disenada como un **workshop interactivo** donde los participantes:

**Fase 1 - Priorizacion Inicial:**
Los participantes reciben 10 municipios y los priorizan segun su percepcion de riesgo (sin datos).

**Fase 2 - Exploracion de Datos:**
Mapa interactivo de Sao Paulo con 16 capas de datos (gobernanza, biodiversidad, clima, salud, social). Los participantes tienen 10 creditos para "comprar" capas y explorar.

**Fase 3 - Revision y Acciones:**
Con los datos explorados, revisan su ranking y seleccionan acciones PEARC (15 acciones en 5 categorias).

**Fase 4 - Resultados y Comparacion:**
Se compara el ranking del participante vs. el ranking de la plataforma (basado en datos). Incluye:
- Correlacion estadistica (Spearman, Kendall)
- Graficos radar por municipio
- Comparacion de vulnerabilidad por cuadrantes
- Metricas de cambio de perspectiva
- Red bipartita acciones-dimensiones

### Datos que Maneja

| Dimension | Ejemplos de Variables |
|-----------|----------------------|
| **Gobernanza** | UAI (Urban Adaptation Index): vivienda, ambiental, alimentacion, movilidad, riesgo climatico |
| **Biodiversidad** | Riqueza de vertebrados, cobertura forestal, deficit de polinizacion |
| **Riesgo Climatico** | Riesgo de inundacion, riesgo de fuego, estres hidrico |
| **Salud** | Dengue, malaria, leptospirosis, leishmaniasis, diarrea, mortalidad cardiovascular, hospitalizaciones respiratorias |
| **Vulnerabilidad Social** | % pobreza, % rural, % poblacion negra, % poblacion indigena |

---

## 5. Tu Rol: Project Coordinator + Business Scout

### Lo que necesitamos de ti

1. **Ordenar el proyecto**
   - Definir un roadmap claro con milestones y deadlines
   - Trackear avances (que esta hecho, que falta, quien hace que)
   - Asegurar que los entregables se cumplen a tiempo
   - Coordinar entre Adrian (ciencia), Arlex (tecnologia) y stakeholders externos

2. **Buscar ofertas y demandas**
   - Identificar grants, convocatorias y fondos para investigacion aplicada
   - Buscar empresas/organizaciones que necesiten datos como los que tenemos
   - Mapear competidores y herramientas similares
   - Identificar conferencias y eventos donde presentar TerraRisk

3. **Definir productos viables**
   - Convertir hallazgos cientificos en propuestas de valor claras
   - Definir MVPs de posibles servicios/productos
   - Estructurar paquetes de consultoria basados en los datos
   - Crear pitch decks o one-pagers para potenciales clientes/partners

### Tus ventajas competitivas para este rol

| Tu experiencia | Aplicacion aqui |
|---------------|-----------------|
| Product Owner en Telecom Argentina | Definir backlogs, priorizar features, roadmaps |
| Technical Product Owner | Entender la viabilidad tecnica de los productos |
| Jira/Asana/MS Projects | Herramientas de gestion ya las dominas |
| Puente negocio-tecnico | Traducir ciencia en lenguaje de mercado |
| Portugues funcional + vives en Lisboa | Conexion directa con mercado portugues/brasileno |
| Ingles C2 | Acceso a grants y oportunidades internacionales |

---

## 6. Contexto Financiero

| Concepto | Valor |
|----------|-------|
| Ingresos actuales del proyecto | $600 USD (consultoria Air Pollution, unico contrato activo) |
| Inversion en infraestructura | ~$10/mes (VPS Contabo) |
| Modelo actual | Academico (sin monetizacion directa de TerraRisk) |
| Potencial estimado | Por definir (esto es parte de tu trabajo) |

---

## 7. Oportunidades Identificadas (para explorar)

Estas son ideas preliminares que necesitan validacion:

### Corto plazo (1-3 meses)
- **Consultoria a municipios de SP**: Reportes personalizados de riesgo por municipio
- **Workshops pagados**: Replicar el workshop SEMIL en otras universidades/instituciones
- **Datos como servicio**: API de datos integrados para investigadores

### Mediano plazo (3-6 meses)
- **TerraRisk SaaS**: Dashboard con suscripcion para gestores municipales
- **Grants de investigacion**: Horizon Europe, FAPESP, CNPq
- **Expansion geografica**: Replicar el modelo a otros estados de Brasil o paises

### Largo plazo (6-12 meses)
- **Certificacion de sostenibilidad**: Herramienta para que municipios midan su desempeno
- **Partnership con ONGs**: Datos para reportes de impacto
- **Spin-off academico**: Empresa de base tecnologica vinculada a USP

---

## 8. Archivos y Recursos Clave

| Recurso | Ubicacion |
|---------|-----------|
| Plataforma TerraRisk | https://terrarisk.arlexperalta.com |
| Codigo fuente | `C:\Users\arlex\Documents\Adrian David\` |
| Contexto cientifico detallado | `.claude/SCIENCE_TEAM_CONTEXT.md` |
| Datos y metodologia | `.claude/DATA_METHODOLOGY.md` |
| Catalogo de 47 papers | `.claude/PAPERS_LIBRARY.md` |
| Dataset principal | `outputs/municipios_integrado_v9.csv` |
| Figuras y outputs | `outputs/` (H1-H6 + workshop layers) |
| Proyecto Air Pollution | `G:\My Drive\Adrian David\Air pollution project\` |

---

## 9. Proximos Pasos Inmediatos

### Para el Workshop (22-26 Feb) - URGENTE

- [ ] Testing de TerraRisk con datos reales + QA visual
- [ ] Deploy final pre-workshop (validacion completa)
- [ ] Preparar materiales de soporte para participantes

### Para Monti (primera semana)

- [ ] Revisar esta documentacion y la plataforma (https://terrarisk.arlexperalta.com)
- [ ] Llamada de kickoff con Adrian y Arlex para alinear expectativas
- [ ] Definir herramientas de gestion a usar (Jira, Notion, Trello, etc.)
- [ ] Crear primer borrador de roadmap del proyecto (post-workshop)
- [ ] Investigacion inicial: grants y convocatorias abiertas en el area

### Para Monti (primer mes)

- [ ] Mapear stakeholders potenciales (municipios, ONGs, organismos)
- [ ] Analisis competitivo: herramientas similares a TerraRisk
- [ ] Propuesta de modelo de negocio v1 (como monetizar)
- [ ] Identificar al menos 3 oportunidades concretas de ingresos

---

## 10. Contactos

| Persona | Email | Rol |
|---------|-------|-----|
| Arlex Peralta | *(solicitar a Arlex)* | Tech Lead, infraestructura |
| Dr. Adrian David | *(solicitar a Adrian)* | Director Cientifico |
| Dra. Luisa Carvalheiro | *(via Adrian)* | PI Air Pollution project |

---

*Bienvenido al equipo, Monti. Tienes las skills exactas que este proyecto necesita para pasar de investigacion pura a impacto real.*
