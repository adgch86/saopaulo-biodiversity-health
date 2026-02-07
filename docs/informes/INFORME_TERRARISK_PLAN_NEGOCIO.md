# TerraRisk Analytics - Informe de Viabilidad y Plan de Negocios

**Fecha:** 24 de enero de 2026
**Elaborado por:** Equipo AP Digital + Science Team
**Para:** Arlex Peralta y Dr. Adrian David González Chaves

---

## Resumen Ejecutivo

Este informe evalúa la viabilidad de comercializar los análisis territoriales desarrollados por el Science Team como producto/servicio bajo la marca **TerraRisk Analytics**.

### Veredicto General

| Aspecto | Estado | Comentario |
|---------|--------|------------|
| Oportunidad de mercado | ✅ ALTA | Regulaciones ESG 2026 crean demanda |
| Viabilidad técnica | ✅ VIABLE | 60% del backend ya existe |
| Viabilidad legal | ⚠️ PARCIAL | DATASUS bloqueante, resto OK |
| Competencia | ⚠️ ALTA | Agrotools, WayCarbon dominan |
| Recomendación | ✅ PROCEDER | Con ajustes al modelo |

---

## 1. La Oportunidad

### 1.1 Activos Existentes

El proyecto de investigación del Dr. Adrian David ha generado activos comercializables:

| Activo | Descripción | Valor Comercial |
|--------|-------------|-----------------|
| Dataset integrado | 645 municipios × 104 variables | Alto |
| Metodología nexus | Gobernanza-biodiversidad-bienestar | Único en mercado |
| Pipeline de datos | Python scripts automatizados | Reutilizable |
| Mapas interactivos | 6 capas + dashboard | Demo ready |
| Publicación científica | En preparación | Credibilidad |

### 1.2 Mercados Potenciales

| Segmento | Necesidad | Ticket Anual Est. | Urgencia |
|----------|-----------|-------------------|----------|
| Seguros agrícolas | Pricing de pólizas por riesgo territorial | USD 50-150k | Alta (siniestralidad) |
| Agribusiness/ESG | Compliance EUDR, certificaciones | USD 80-200k | Alta (regulación 2025) |
| Gobiernos | Priorización de inversión pública | USD 200-500k | Media |
| Real Estate | Due diligence climática | USD 15-40k | Media |
| Impact Investing | Screening territorial ESG | USD 30-100k | Alta |

### 1.3 Timing Favorable

- **CVM 193 (Brasil):** Reportes ISSB obligatorios desde 2026
- **EUDR (Europa):** Trazabilidad de cadenas productivas 2025
- **COP30 (Belém):** Noviembre 2025, momentum regulatorio
- **BCB 387:** Bancos deben integrar riesgo climático 2025

---

## 2. Análisis Legal

### 2.1 Fuentes de Datos - Viabilidad Comercial

| Fuente | Licencia | Uso Comercial | Riesgo |
|--------|----------|---------------|--------|
| **DATASUS** | CC-BY-NC-SA | ❌ NO PERMITIDO | 🔴 BLOQUEANTE |
| **IBGE** | Datos Abiertos | ✅ SÍ | 🟢 Bajo |
| **MapBiomas** | CC-BY-SA | ✅ SÍ (con atribución) | 🟢 Bajo |
| **Landsat/NASA** | Dominio Público | ✅ SÍ | 🟢 Bajo |
| **Sentinel/ESA** | CC-BY-SA 3.0 IGO | ✅ SÍ (con atribución) | 🟢 Bajo |
| **GBIF** | Mixta | ✅ Filtrar CC0/CC-BY | 🟡 Medio |

### 2.2 Problema Crítico: DATASUS

Los datos de salud (dengue, diarrea, mortalidad) tienen licencia **Non-Commercial**:

> **CC-BY-NC-SA 4.0**: "No puede utilizar el material para fines comerciales"

**Opciones de resolución:**

| Opción | Viabilidad | Tiempo | Riesgo |
|--------|------------|--------|--------|
| A) Solicitar licencia comercial al Ministerio de Salud | Incierta | 3-6 meses | Medio |
| B) Excluir datos de salud del producto | Alta | Inmediato | Bajo |
| C) Modelo híbrido académico-comercial | Alta | Inmediato | Bajo-Medio |

### 2.3 LGPD (Protección de Datos)

**No aplica** a datos agregados por municipio:
- Art. 12 LGPD: Datos anonimizados no son datos personales
- Agregación municipal (miles de habitantes) impide reidentificación
- Precedentes favorables en tribunales brasileños

### 2.4 Requisitos Legales para Operar

| Requisito | Descripción | Costo Est. |
|-----------|-------------|------------|
| Seguro E&O | Errors & Omissions, USD 1-2M cobertura | USD 3-5k/año |
| Disclaimers | En todos los outputs y contratos | Legal fee |
| Atribuciones | MapBiomas, Sentinel, IBGE | Ninguno |
| Términos de uso | Limitación de responsabilidad | Legal fee |

---

## 3. Análisis de Competencia

### 3.1 Competidores Directos

| Competidor | País | Producto | Funding | Clientes | Threat Level |
|------------|------|----------|---------|----------|--------------|
| **Agrotools** | Brasil | Monitoreo geoespacial agro | $21M+ | Cargill, JBS, Itaú, McDonald's | 🔴 Alto |
| **WayCarbon** | Brasil | Consultoría clima/ESG + software MOVE | Santander (80%) | Natura, Braskem, Renner | 🔴 Alto |
| **TerraMagna** | Brasil | Crédito rural + análisis satelital | SoftBank, Maya | Agrogalaxy | 🟡 Medio |
| **Agrosatélite** | Brasil | Deforestación, EUDR compliance | Serasa Experian | Bancos, traders | 🟡 Medio |

### 3.2 Plataformas Gratuitas (Competencia Indirecta)

| Plataforma | Qué ofrece | Gap vs TerraRisk |
|------------|------------|------------------|
| **MapBiomas** | 38 años datos uso suelo, alertas, gratuito | Solo mapeo, no scoring |
| **AdaptaBrasil** | Índices riesgo climático municipal | Gobierno, no comercializable |
| **CDP (2025)** | Datos climáticos 10,000+ empresas gratis | Empresas, no territorial |

### 3.3 Amenaza Big Tech

| Player | Oferta | Riesgo |
|--------|--------|--------|
| AWS | Data Exchange con datasets ESG | 🟡 Medio |
| Microsoft | Cloud for Sustainability | 🟡 Medio |
| Google | Herramientas carbon footprint | 🟡 Medio |

### 3.4 Gap de Mercado (Oportunidad)

**Ningún competidor ofrece:**

1. ✅ **Scoring municipal integrado** (clima + biodiversidad + gobernanza)
2. ✅ **Nexo gobernanza-biodiversidad-bienestar** (metodología Adrian)
3. ✅ **Due diligence climática para real estate** (90%+ pérdidas no aseguradas)
4. ✅ **Análisis de vulnerabilidad social + ambiental integrado**

---

## 4. Plan de Negocios

### 4.1 Producto Propuesto

**TerraRisk Analytics** - Plataforma de inteligencia territorial

| Componente | Descripción | Timeline |
|------------|-------------|----------|
| API de datos | Endpoints REST para consulta de indicadores | MVP: 4-6 semanas |
| Dashboard | Visualización interactiva con mapas | v1: +8 semanas |
| Reportes | PDFs automatizados por municipio/región | MVP: 3 semanas |
| Consultoría | Análisis personalizados | Inmediato |

### 4.2 Stack Tecnológico Recomendado

```
Frontend:  Next.js 14 + TypeScript + Tailwind + Mapbox GL
Backend:   FastAPI (Python) - reutiliza scripts existentes
Database:  PostgreSQL + PostGIS
Cache:     Redis
Auth:      Clerk/Auth.js
Deploy:    Vercel (front) + Railway (API)
```

### 4.3 Pricing Tiers

| Tier | Target | Precio/mes | Incluye |
|------|--------|------------|---------|
| **Básico** | Prefeituras, ONGs | USD 1,500-2,500 | 1 municipio, 20 variables, reportes trimestrales |
| **Pro** | Secretarías, consultoras | USD 8,000-15,000 | 50 municipios, API, reportes mensuales |
| **Enterprise** | Estados, bancos | USD 25,000-50,000 | Estado completo, API ilimitada, white-label |
| **Custom** | Proyectos especiales | USD 50-200k one-time | Expansión países, modelos predictivos |

### 4.4 Proyección Financiera Año 1

| Concepto | Valor |
|----------|-------|
| **Inversión Fase 1 (6 meses)** | USD 148,000 |
| Equipo (2.3 FTE) | USD 111,000 |
| Infraestructura | USD 4,800 |
| Marketing/BD | USD 9,000 |
| Legal/Admin | USD 4,800 |
| Buffer 15% | USD 18,400 |

| Proyección Revenue | Valor |
|--------------------|-------|
| Clientes target Y1 | 15-24 |
| MRR objetivo M12 | USD 100-170k |
| ARR objetivo Y1 | USD 500k-800k |
| Break-even | Mes 10-12 |
| Margen bruto | 65-70% |

### 4.5 Equipo Requerido (Fase 1)

| Rol | Dedicación | Costo/mes |
|-----|------------|-----------|
| Dr. Adrian (Chief Scientist) | 30% | USD 3,000 |
| Data Scientist | 100% | USD 6,500 |
| Frontend Developer | 50% | USD 3,500 |
| Sales/BD | 50% | USD 2,500 |
| PM/Coordinación | Variable | USD 3,000 |
| **Total** | 2.3 FTE | **USD 18,500** |

---

## 5. Análisis de Riesgos

### 5.1 Matriz de Riesgos

| Riesgo | Probabilidad | Impacto | Deal Breaker | Mitigación |
|--------|--------------|---------|--------------|------------|
| DATASUS no autoriza comercial | Alta | Crítico | **SÍ** | Excluir o solicitar licencia |
| MapBiomas commoditiza datos | Alta | Alto | Parcial | Diferenciar con análisis |
| Calidad datos DATASUS | Media | Alto | No | Validación cruzada |
| Big Tech entra gratis | Media | Crítico | **SÍ** | Especialización vertical |
| Litigio por datos erróneos | Baja | Alto | No | Seguro E&O + disclaimers |
| Dependencia Dr. Adrian | Baja | Alto | No | Adrian es socio |

### 5.2 Casos de Fracaso en el Sector

| Patrón | Ejemplo | Lección |
|--------|---------|---------|
| Datos commoditizados | Startups vs CDP gratis | No competir en datos raw |
| Growth insostenible | Climate startups 2020-2021 | Validar antes de escalar |
| Sin market fit | 60% startups fracasan | Hablar con clientes primero |
| Big Tech absorbe | Consolidación ESG 2018-2020 | Partnership o nicho |

---

## 6. Escenarios Estratégicos

### Escenario A: Producto SIN Datos de Salud

| Aspecto | Evaluación |
|---------|------------|
| Producto | Riesgo climático + biodiversidad + gobernanza |
| Viabilidad legal | ✅ 100% |
| Diferenciación | 🟡 Reducida (compite con MapBiomas) |
| Mercado | Agro, Real Estate, ESG funds |
| Recomendación | Viable pero limitado |

### Escenario B: Producto CON Licencia DATASUS

| Aspecto | Evaluación |
|---------|------------|
| Producto | Nexo completo (clima + salud + biodiv + gobernanza) |
| Viabilidad legal | ⚠️ Requiere autorización |
| Diferenciación | ✅ ÚNICA en el mercado |
| Mercado | Gobiernos, Salud pública, Impact investing |
| Recomendación | Ideal si se obtiene licencia |

### Escenario C: Modelo Híbrido Académico-Comercial (RECOMENDADO)

| Aspecto | Evaluación |
|---------|------------|
| Estructura | Adrian publica (NC), TerraRisk vende consultoría |
| Viabilidad legal | ✅ Defendible |
| Diferenciación | ✅ Alta (credibilidad científica) |
| Escalabilidad | 🟡 Limitada inicialmente |
| Recomendación | **Mejor opción corto plazo** |

---

## 7. Recomendaciones y Próximos Pasos

### 7.1 Decisiones Requeridas (Arlex + Adrian)

| Pregunta | Opción A | Opción B |
|----------|----------|----------|
| ¿Incluir datos de salud? | Sí (buscar licencia) | No (producto reducido) |
| ¿Estructura legal? | Unidad de AP Digital | Empresa separada |
| ¿Modelo de negocio? | SaaS puro | Híbrido académico-comercial |
| ¿Estrategia competitiva? | Competir directo | Partnership/white-label |

### 7.2 Acciones Inmediatas (Semana 1-2)

| Prioridad | Acción | Responsable | Deadline |
|-----------|--------|-------------|----------|
| 🔴 1 | Email formal a DATASUS sobre licencia comercial | Adrian | 7 días |
| 🔴 2 | Mapear gaps exactos vs MapBiomas | Equipo técnico | 7 días |
| 🟡 3 | 5 llamadas de validación con clientes potenciales | Valeria/Arlex | 14 días |
| 🟡 4 | Consulta abogado LGPD Brasil | Elena | 14 días |
| 🟢 5 | Cotización seguro E&O | Elena | 14 días |

### 7.3 Roadmap Propuesto

```
SEMANA 1-2: Validación Legal y Comercial
├── Email DATASUS
├── Llamadas clientes
└── Consulta legal

SEMANA 3-6: MVP (si validación positiva)
├── API básica con datos permitidos
├── Dashboard con mapas existentes
└── 1-2 pilotos pagos

SEMANA 7-12: Iteración
├── Feedback de pilotos
├── Expansión a más estados
└── Definir estructura legal final

MES 4-6: Escala
├── Lanzamiento comercial
├── Equipo completo
└── Marketing activo
```

---

## 8. Conclusión

**TerraRisk Analytics es viable** con las siguientes condiciones:

1. ✅ **Resolver el tema DATASUS** antes de invertir en desarrollo
2. ✅ **Diferenciar con análisis**, no competir en datos raw
3. ✅ **Validar demanda real** con 5-10 clientes antes de construir
4. ✅ **Modelo híbrido** académico-comercial como estrategia inicial

**El activo más valioso no son los datos (públicos), sino:**
- La metodología de análisis nexus de Adrian
- La credibilidad científica (publicaciones)
- La integración única de variables que nadie más ofrece

**Recomendación final:** Proceder con cautela. Invertir 2 semanas en validación legal y comercial antes de comprometer recursos significativos.

---

## Anexos

### A. Fuentes Consultadas

**Legales:**
- DATASUS - Ministério da Saúde (CC-BY-NC-SA 4.0)
- Decreto 8.777/2016 - Política de Dados Abertos
- LGPD - Lei 13.709/2018, Artículo 12
- IBGE Termos de Uso
- MapBiomas Terms of Use
- Copernicus Sentinel Open Licence

**Competencia:**
- Agrotools (agrotools.com.br)
- WayCarbon (waycarbon.com)
- TerraMagna (terramagna.com.br)
- MapBiomas (brasil.mapbiomas.org)

**Regulatorio:**
- CVM Resolution 193 (ISSB Brasil 2026)
- BCB Resolution 387 (Riesgo climático)
- EUDR - EU Deforestation Regulation

### B. Contactos Clave

| Entidad | Para qué | Contacto sugerido |
|---------|----------|-------------------|
| DATASUS | Licencia comercial | datasus@saude.gov.br |
| MapBiomas | Partnership potencial | contato@mapbiomas.org |
| CNseg | Hub Inteligencia Climática | Portal institucional |
| ANPD | Consulta LGPD | Canales oficiales |

### C. Archivos de Referencia

- `outputs/municipios_integrado_v8.csv` - Dataset actual
- `scripts/analisis_nexus_gobernanza_biodiversidad_v1.py` - Metodología
- `.claude/SCIENCE_TEAM_CONTEXT.md` - Contexto del proyecto científico

---

*Informe preparado por el equipo de AP Digital en colaboración con el Science Team.*
*Versión 1.0 - 24 de enero de 2026*
