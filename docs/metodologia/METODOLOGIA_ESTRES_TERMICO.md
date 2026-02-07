# Metodología para la Obtención de Variables de Estrés Térmico

**Proyecto**: Resilient Landscapes: Integrating Planetary Health, Nexus Thinking, and Environmental Justice in São Paulo's Agrifood Systems

**Science Team** | Enero 2026

---

## Tabla de Contenidos

1. [Contexto y Justificación](#1-contexto-y-justificación)
2. [Evaluación de Métricas de Estrés Térmico](#2-evaluación-de-métricas-de-estrés-térmico)
3. [Evaluación de Fuentes de Datos](#3-evaluación-de-fuentes-de-datos)
4. [Métricas Seleccionadas](#4-métricas-seleccionadas)
5. [Nota sobre la Métrica de Intensidad Horaria](#5-nota-sobre-la-métrica-de-intensidad-horaria)
6. [Implementación Técnica](#6-implementación-técnica)
7. [Validación Epidemiológica](#7-validación-epidemiológica)
8. [Análisis Planificados](#8-análisis-planificados)
9. [Referencias](#9-referencias)
10. [Notas Adicionales](#10-notas-adicionales)

---

## 1. CONTEXTO Y JUSTIFICACIÓN

El proyecto cuenta actualmente con 104 variables en el dataset v8 para los 645 municipios del estado de São Paulo (período 2010-2019), incluyendo variables de salud cardiovascular y respiratoria provenientes de los sistemas SIH/SIM del DATASUS. Sin embargo, no se dispone de variables que midan directamente dónde se localizan las islas de calor y el estrés térmico más intenso.

### Hipótesis de trabajo

La presencia de vegetación nativa y biodiversidad se asocia con menores islas de calor a través del servicio ecosistémico de regulación climática, reduciendo los efectos adversos del incremento de temperatura.

### Nueva hipótesis H3 propuesta

```
Biodiversidad/Vegetación → (−) Estrés Térmico → (−) Mortalidad Cardiovascular
```

Esta hipótesis plantea que la biodiversidad actúa como variable protectora contra el estrés térmico, el cual a su vez está asociado con mortalidad cardiovascular. La incorporación de variables de estrés térmico permitirá:

1. Testar el efecto directo de biodiversidad sobre temperatura
2. Evaluar si el estrés térmico media la relación biodiversidad-salud
3. Identificar municipios con alta vulnerabilidad térmica
4. Cuantificar el servicio ecosistémico de regulación climática

---

## 2. EVALUACIÓN DE MÉTRICAS DE ESTRÉS TÉRMICO

Se evaluaron cinco métricas principales de estrés térmico, considerando sus fortalezas, debilidades, validación en Brasil y aplicabilidad al proyecto:

### Tabla comparativa de métricas

| Métrica | Inputs requeridos | Fortalezas | Debilidades | Validación en Brasil | Mejor uso |
|---------|------------------|------------|-------------|---------------------|-----------|
| **UTCI** (Universal Thermal Climate Index) | Temp. aire, humedad, viento, radiación (4 vars) | Fisiológicamente robusto; incorpora balance energético humano; aplicable universalmente | Requiere radiación y viento; resolución gruesa en ERA5-HEAT (0.25°) | Validado en Curitiba, Belo Horizonte, São Paulo | Planificación urbana, alertas de salud pública |
| **WBGT** (Wet Bulb Globe Temperature) | Temp. aire, humedad, radiación (3 vars) | Estándar ocupacional ISO 7243; mejor para estrés nocturno; estable en alta humedad | Subestima estrés cuando sudoración está restringida; escala contraintuitiva | Validado en estudios ocupacionales nacionales | Salud ocupacional |
| **Heat Index** (HI) | Temp. aire, humedad (2 vars) | Simple; datos ampliamente disponibles | No incorpora viento ni radiación; correlación débil con UTCI (R² < 50%) | Usado en alertas meteorológicas | Alertas climáticas, comunicación pública |
| **EHF** (Excess Heat Factor) | Temp. media diaria, percentil 95 histórico (2 vars derivadas) | Captura aclimatación; predictor robusto de mortalidad; **VALIDADO EN SP** | Requiere serie temporal larga para calcular percentiles | **São Paulo, Campinas, Marilia (2004-2018)**: 2,319 muertes atribuibles | Epidemiología, políticas de salud pública |
| **LST** (Land Surface Temperature - MODIS) | Emisión infrarroja térmica | Alta resolución espacial (1 km); detección directa de UHI | No es temperatura del aire; afectado por nubes | **SP tiene SUHI diurna de 6.60°C** (3ª más alta de Sudamérica) y la **mayor SUHI nocturna de Brasil** | Islas de calor urbano, planificación territorial |

### Análisis de cada métrica

#### a) UTCI (Universal Thermal Climate Index)

**Definición**: Temperatura equivalente que incorpora los efectos combinados de temperatura del aire, humedad, velocidad del viento y radiación sobre el balance térmico humano.

**Inputs**:
- Temperatura del aire (°C)
- Humedad relativa (%)
- Velocidad del viento (m/s)
- Radiación térmica media radiante (W/m²)

**Fortalezas**:
- Fisiológicamente robusto: basado en modelo de balance energético del cuerpo humano
- Universalmente aplicable a todas las escalas climáticas
- Categorías de estrés validadas internacionalmente

**Debilidades**:
- Requiere 4 variables meteorológicas, incluyendo radiación y viento que tienen menor disponibilidad
- ERA5-HEAT ofrece UTCI precalculado pero con resolución gruesa (0.25° ≈ 28 km)
- No captura variabilidad intra-urbana

**Validación en Brasil**:
- Romaszko et al. (2022): UTCI validado como predictor de mortalidad en estudios brasileños
- Curitiba, Belo Horizonte y São Paulo: estudios de confort térmico urbano

**Mejor uso**: Planificación urbana, sistemas de alerta temprana de salud pública

#### b) WBGT (Wet Bulb Globe Temperature)

**Definición**: Índice de estrés térmico que combina temperatura del aire, humedad y radiación, ponderando más el componente húmedo.

**Inputs**:
- Temperatura de bulbo húmedo natural
- Temperatura de globo negro
- Temperatura del aire (3 variables derivadas de temp, humedad y radiación)

**Fortalezas**:
- Estándar ISO 7243 para evaluación de estrés ocupacional
- Mejor desempeño que UTCI para estrés térmico nocturno
- Estable en condiciones de alta humedad (típicas de Brasil)

**Debilidades**:
- Subestima estrés cuando la sudoración está restringida
- Escala contraintuitiva (valores menores que temperatura del aire)
- Menos validado para mortalidad que EHF

**Validación en Brasil**:
- Estudios nacionales de salud ocupacional en agricultura y construcción
- Usado por Ministerio de Trabajo para normativas de exposición

**Mejor uso**: Evaluación de riesgo ocupacional, especialmente en trabajo agrícola

#### c) Heat Index (HI)

**Definición**: Temperatura aparente que combina temperatura del aire y humedad relativa para estimar el efecto percibido.

**Inputs**:
- Temperatura del aire (°C)
- Humedad relativa (%)

**Fortalezas**:
- Cálculo simple con datos ampliamente disponibles
- Comunicación pública efectiva
- Base de datos extensa

**Debilidades**:
- No incorpora viento ni radiación solar
- Correlación débil con UTCI (R² < 50% en estudios comparativos)
- Sobreestima estrés en ambientes secos
- Subestima estrés con viento alto

**Validación en Brasil**:
- Usado en alertas meteorológicas del INMET
- No validado robustamente para mortalidad

**Mejor uso**: Alertas meteorológicas, comunicación pública de riesgo

#### d) EHF (Excess Heat Factor)

**Definición**: Factor de exceso de calor que compara la temperatura media de 3 días consecutivos contra el percentil 95 de la serie histórica, capturando tanto la intensidad como la aclimatación poblacional.

**Inputs**:
- Temperatura media diaria
- Percentil 95 de temperatura de la serie histórica del lugar

**Fortalezas**:
- Captura aclimatación poblacional (uso de percentil local)
- Predictor robusto de mortalidad validado epidemiológicamente
- **VALIDADO ESPECÍFICAMENTE EN SÃO PAULO**

**Debilidades**:
- Requiere serie temporal larga (>20 años) para calcular percentiles confiables
- No captura estrés por humedad o radiación de forma explícita

**Validación en São Paulo**:
- Validado en SP, Campinas y Marília (2004-2018)
- 2,319 muertes atribuibles al calor en estas 3 ciudades
- Riesgo relativo de mortalidad: 1.0018 (SP), 1.0029 (Campinas), 1.0033 (Marília)

**Mejor uso**: Estudios epidemiológicos, políticas de salud pública, cuantificación de mortalidad atribuible

#### e) LST (Land Surface Temperature - MODIS)

**Definición**: Temperatura de la superficie terrestre medida por sensores remotos en el infrarrojo térmico. Mide la temperatura de suelo, techos, pavimento, vegetación, no del aire.

**Inputs**:
- Emisión infrarroja térmica capturada por satélite

**Fortalezas**:
- Alta resolución espacial (1 km en MODIS)
- Detección directa de islas de calor urbano superficiales (SUHI)
- Cobertura espacial completa sin gaps de estaciones meteorológicas
- Disponible desde el año 2000

**Debilidades**:
- No es temperatura del aire (Ta se mide a 2m de altura)
- Afectado por cobertura de nubes
- Diferencia LST-Ta varía según superficie (mayor en pavimento, menor en vegetación)

**Validación en São Paulo**:
- Monteiro et al. (2021): SP tiene SUHI diurna de 6.60°C (3ª más alta de Sudamérica)
- Wu et al. (2019): SP tiene la mayor SUHI nocturna de Brasil
- Regiones central y este de SP son hotspots recurrentes de SUHI

**Mejor uso**: Mapeo de islas de calor urbano, planificación territorial, evaluación de efecto de vegetación sobre temperatura superficial

---

## 3. EVALUACIÓN DE FUENTES DE DATOS

Se evaluaron seis fuentes de datos meteorológicos y climáticos para obtener las variables de estrés térmico, considerando resolución espacial y temporal, cobertura, validación, accesibilidad y licencia.

### Tabla comparativa de fuentes de datos

| Fuente | Resolución espacial | Resolución temporal | Período | Variables | Validación | Acceso | Licencia | Ventajas | Limitaciones |
|--------|-------------------|---------------------|---------|-----------|------------|--------|----------|----------|--------------|
| **Xavier/BR-DWGD v3** | **0.1° × 0.1° (~11 km)** | **Diaria** | **1961-2024** | Tmax, Tmin, HR, viento, radiación, precip. | **11,473 pluviómetros + 1,252 estaciones en Brasil** | GEE Community Catalog, NetCDF, GitHub | **CC BY 4.0** | **Construido específicamente para Brasil con observaciones superficiales directas, no reanálisis global** | - |
| ERA5-HEAT | 0.25° × 0.25° (~28 km) | Horaria | 1940-presente | UTCI, MRT precalculados | Reanálisis global validado | CDS Copernicus (registro gratuito) | Open Data | UTCI precalculado | No captura variabilidad intra-urbana |
| ERA5-Land | 0.1° (~9 km) | Horaria | 1950-presente | T 2m, punto de rocío, viento, radiación | Reanálisis global | CDS o GEE | Open Data | Resolución mejorada vs ERA5 | Reanálisis (sesgos sistemáticos posibles en Brasil) |
| **MODIS MOD11A2** | **1 km** | **Compuesto 8 días** | **2000-presente** | LST_Day, LST_Night | Validado contra estaciones | **GEE** | Open Data | **Única métrica que captura SUHI directamente** | Temperatura superficial, no del aire |
| INMET | Variable (estaciones puntuales) | Horaria | 1961-presente | Todas las variables meteorológicas | Observaciones directas | API INMET | Open Data | Datos oficiales | Cobertura espacial irregular en SP |
| CLIMBra | 0.25° | Diaria | 1980-2100 | Precip., Tmax, Tmin | Proyecciones climáticas | Repositorio | Open Data | Incluye proyecciones futuras | Resolución más gruesa |

### Análisis detallado de cada fuente

#### a) Xavier/BR-DWGD v3 (RECOMENDADO COMO FUENTE PRIMARIA)

**Nombre completo**: Brazilian Daily Weather Gridded Data, versión 3

**Características técnicas**:
- Resolución espacial: 0.1° × 0.1° (aproximadamente 11 km en el ecuador)
- Resolución temporal: Diaria
- Período: 1961-2024 (actualización continua)
- Cobertura: Todo Brasil

**Variables disponibles**:
- Tmax: Temperatura máxima diaria (°C)
- Tmin: Temperatura mínima diaria (°C)
- HR: Humedad relativa (%)
- Viento: Velocidad del viento (m/s)
- Radiación solar (MJ/m²/día)
- Precipitación (mm/día)

**Validación**:
- Red de 11,473 pluviómetros
- 1,252 estaciones meteorológicas de superficie
- Específicamente calibrado para condiciones brasileñas

**Acceso**:
- Google Earth Engine Community Catalog: `projects/br-dwgd/assets/tmax`, `projects/br-dwgd/assets/tmin`
- Archivos NetCDF: Descarga directa
- GitHub: https://github.com/AlexandreCandidoXavier/BR-DWGD

**Licencia**: CC BY 4.0 (Uso libre con atribución)

**Referencia principal**: Xavier, A.C., et al. (2022). New improved Brazilian daily weather gridded data (1961-2020). International Journal of Climatology, 42(16), 8390-8404. DOI: 10.1002/joc.7731

**Por qué se recomienda como fuente primaria**:
1. Construido específicamente para Brasil, no es un reanálisis global adaptado
2. Usa observaciones superficiales directas como fuente primaria
3. La versión 2022 mejoró la resolución a 0.1° incorporando relieve topográfico
4. Validación robusta con red densa de estaciones brasileñas
5. Resolución adecuada para análisis municipal (645 municipios de SP)

#### b) ERA5-HEAT (Copernicus)

**Características técnicas**:
- Resolución espacial: 0.25° × 0.25° (aproximadamente 28 km)
- Resolución temporal: Horaria
- Período: 1940-presente

**Variables disponibles**:
- UTCI precalculado
- Mean Radiant Temperature (MRT)
- Componentes individuales (Temp, HR, viento, radiación)

**Limitaciones para el proyecto**:
- Resolución de 28 km es demasiado gruesa para capturar variabilidad intra-municipal
- Reanálisis global con posibles sesgos en zonas tropicales

**Acceso**: Climate Data Store Copernicus (requiere registro gratuito)

**Referencia**: Di Napoli, C., et al. (2021). ERA5-HEAT: A global gridded historical dataset of human thermal comfort indices. Geoscience Data Journal, 8(1), 2-10. DOI: 10.1002/gdj3.102

#### c) ERA5-Land

**Características técnicas**:
- Resolución espacial: 0.1° (aproximadamente 9 km)
- Resolución temporal: Horaria
- Período: 1950-presente

**Variables disponibles**:
- Temperatura del aire a 2m
- Punto de rocío
- Viento a 10m
- Radiación de onda corta y larga

**Ventajas**:
- Resolución mejorada respecto a ERA5 estándar
- Disponible en GEE para procesamiento eficiente

**Limitaciones**:
- Es un reanálisis, no observaciones directas
- Posibles sesgos sistemáticos en regiones tropicales de Brasil

**Acceso**: Climate Data Store o Google Earth Engine

#### d) MODIS MOD11A2 (RECOMENDADO PARA LST)

**Características técnicas**:
- Resolución espacial: 1 km
- Resolución temporal: Compuesto de 8 días
- Período: 2000-presente (Terra), 2002-presente (Aqua)

**Variables disponibles**:
- LST_Day_1km: Temperatura superficial diurna
- LST_Night_1km: Temperatura superficial nocturna
- QC_Day/QC_Night: Indicadores de calidad

**Pases de satélite**:
- Terra: ~10:30 (día), ~22:30 (noche) hora local
- Aqua: ~13:30 (día, más caliente), ~01:30 (madrugada)

**Ventajas**:
- Alta resolución espacial (1 km)
- Única métrica que mide directamente temperatura de superficie
- Ideal para detección de islas de calor urbano (SUHI)
- Disponible fácilmente en GEE

**Validación en São Paulo**:
- Monteiro et al. (2021): Assessment of Urban Heat Islands in Brazil based on MODIS. Urban Climate, 35, 100726.
- Wu et al. (2019): Surface UHI in 44 South American cities. Remote Sensing, 11(10), 1212.

**Limitación importante**:
- LST ≠ Temperatura del aire
- LST mide temperatura de superficie (techo, pavimento, vegetación)
- La diferencia LST - Ta es mayor en islas de calor urbano
- Para vinculación con biodiversidad: LST es más directo que Ta

**Acceso**: Google Earth Engine: `MODIS/061/MOD11A2` (Terra), `MODIS/061/MYD11A2` (Aqua)

**Licencia**: Open Data

#### e) INMET (Instituto Nacional de Meteorologia)

**Características**:
- Observaciones directas de estaciones meteorológicas
- Resolución temporal: Horaria
- Período: 1961-presente (varía por estación)

**Ventajas**:
- Datos oficiales de alta calidad
- Todas las variables meteorológicas

**Limitaciones para el proyecto**:
- Cobertura espacial irregular en São Paulo
- Difícil obtener datos espacialmente completos para 645 municipios
- No es adecuado como fuente primaria para análisis espacial completo

**Acceso**: API INMET (https://portal.inmet.gov.br/)

#### f) CLIMBra - Climate Change Dataset for Brazil

**Características técnicas**:
- Resolución espacial: 0.25°
- Resolución temporal: Diaria
- Período: 1980-2100 (histórico + proyecciones)

**Variables**: Precipitación, Tmax, Tmin

**Ventaja principal**: Incluye proyecciones climáticas futuras (RCP 4.5, 8.5)

**Limitación**: Resolución más gruesa que Xavier/BR-DWGD

**Referencia**: Duarte, Y.S., et al. (2023). CLIMBra - Climate Change Dataset for Brazil. Scientific Data.

**Uso potencial**: Análisis de escenarios futuros (no implementado en fase actual)

---

## 4. MÉTRICAS SELECCIONADAS

Basándose en la evaluación anterior, se seleccionaron cuatro métricas complementarias que capturan diferentes aspectos del estrés térmico:

### 4.1 Persistencia (heat_persistence)

**Definición**: Promedio del número de días por año con temperatura máxima superior a 34.7°C durante el período 2010-2019.

**Fuente de datos**: Xavier/BR-DWGD v3, variable Tmax diaria (resolución 0.1°)

**Justificación del umbral**:
- Valverde (2023, International Journal of Climatology) encontró que la temperatura promedio de las ondas de calor en el estado de São Paulo es de 34.9°C
- El 92% de los eventos extremos de calor ocurrieron en el período 2010-2020
- Umbral de 34.7°C es conservador y representa condiciones de onda de calor

**Cálculo**:
```
Para cada año (2010-2019):
  heat_persistence_año = count(días donde Tmax > 34.7°C)

heat_persistence_mean = mean(heat_persistence_2010, ..., heat_persistence_2019)
```

**Unidades**: días/año

**Variables asociadas**:
- `heat_persistence_mean`: Promedio decadal
- `heat_persistence_sd`: Desviación estándar interanual (captura variabilidad climática)

**Interpretación**:
- Valores altos indican exposición frecuente a temperaturas extremas
- Municipios con >10 días/año requieren atención especial
- La desviación estándar indica estabilidad/variabilidad del patrón

### 4.2 HAAT - Heat Area Above Threshold (heat_HAAT)

**Definición**: Grados-día acumulados por encima del umbral de 34.7°C, promedio anual del período 2010-2019.

**Fuente de datos**: Xavier/BR-DWGD v3, variable Tmax diaria (resolución 0.1°)

**Metodología**:
Basado en el estudio medRxiv 2025 para Río de Janeiro, que originalmente propuso usar datos horarios. Adaptado para datos diarios de Tmax:

```
Para cada año:
  Para cada día donde Tmax > 34.7°C:
    HAAT_día = Tmax - 34.7

  HAAT_año = Σ(HAAT_día)

heat_HAAT_mean = mean(HAAT_2010, ..., HAAT_2019)
```

**Unidades**: grados-día/año

**Ejemplo de interpretación**:
- Municipio con 10 días a 36°C: HAAT = 10 × (36 - 34.7) = 13 grados-día
- Municipio con 5 días a 38°C: HAAT = 5 × (38 - 34.7) = 16.5 grados-día
- A pesar de menos días, el segundo municipio tiene mayor HAAT por mayor intensidad

**Variables asociadas**:
- `heat_HAAT_mean`: Promedio decadal
- `heat_HAAT_sd`: Desviación estándar interanual

**Ventajas sobre persistencia**:
- Captura tanto frecuencia (número de días) como intensidad (cuánto excede el umbral)
- Más sensible a ondas de calor extremas
- Mejor predictor de impactos de salud según evidencia de Río de Janeiro

### 4.3 MMT Days - Minimum Mortality Temperature (mmt_days)

**Definición**: Promedio del número de días por año con temperatura media diaria superior a 22.3°C durante el período 2010-2019.

**Fuente de datos**: Xavier/BR-DWGD v3, calculado como Tmedia = (Tmax + Tmin) / 2

**Justificación del umbral**:

1. **Nascimento et al. (2019, Scientific Reports)**:
   - Confirmó que la Temperatura de Mínima Mortalidad (MMT) para mortalidad por infarto agudo de miocardio (IAM) en Brasil varía entre:
     - 22°C en región Sur
     - 28°C en región Centro-Oeste
   - 22.3°C es consistente con la región Sureste

2. **Masselot et al. (2022)**:
   - MMT en São Paulo ha aumentado significativamente entre 2000-2018
   - Riesgo relativo acumulado (cRR) para muertes cardiovasculares aumenta por encima de MMT
   - La vulnerabilidad al calor está EMPEORANDO en SP (mientras que la adaptación al frío está MEJORANDO)

**Cálculo**:
```
Para cada año:
  Para cada día:
    Tmedia = (Tmax + Tmin) / 2

  mmt_days_año = count(días donde Tmedia > 22.3°C)

mmt_days_mean = mean(mmt_days_2010, ..., mmt_days_2019)
```

**Unidades**: días/año

**Variables asociadas**:
- `mmt_days_mean`: Promedio decadal
- `mmt_days_sd`: Desviación estándar interanual

**Interpretación importante**:
- Esta métrica captura exposición crónica al riesgo térmico de salud, no solo eventos extremos
- 22.3°C NO es una onda de calor climatológica
- Debe llamarse "días de riesgo térmico de salud" en lugar de "días de onda de calor"
- Valores típicos esperados: 100-300 días/año en SP (mayor que heat_persistence)

**Diferencia conceptual con heat_persistence**:
- `heat_persistence`: Eventos extremos (Tmax > 34.7°C) → Impacto agudo
- `mmt_days`: Exposición crónica (Tmedia > 22.3°C) → Riesgo de fondo

### 4.4 LST - Land Surface Temperature (métricas complementarias)

**Fuente de datos**: MODIS/061/MOD11A2 (Terra) + MYD11A2 (Aqua), resolución 1 km, compuesto 8 días

**Métricas calculadas**:

| Variable | Definición | Unidades | Utilidad |
|----------|-----------|----------|----------|
| `lst_day_mean` | LST diurna media (promedio decadal 2010-2019) | °C | Temperatura superficial típica durante el día |
| `lst_night_mean` | LST nocturna media (promedio decadal) | °C | Temperatura superficial nocturna (relevante para mortalidad) |
| `lst_day_p95` | Percentil 95 de LST diurna | °C | Extremos de calor superficial |
| `lst_day_sd` | Desviación estándar de LST diurna | °C | Variabilidad térmica |
| `lst_amplitude` | Amplitud térmica día-noche (lst_day_mean - lst_night_mean) | °C | Indicador de impermeabilización urbana |

**Filtro de calidad aplicado**:
- Se aceptan solo píxeles con QC bits 0-1 = 00 (good) o 01 (average)
- Se excluyen observaciones con error LST > 2K
- Se eliminan observaciones contaminadas por nubes finas

**Conversión de datos**:
```
LST_Celsius = (DN × 0.02) - 273.15
```
Donde DN es el valor digital del producto MODIS.

**Combinación Terra + Aqua**:
- Terra pasa ~10:30 (día) y ~22:30 (noche) hora local
- Aqua pasa ~13:30 (día, más caliente) y ~01:30 (madrugada)
- Se combinan ambas para maximizar cobertura temporal y reducir gaps por nubes

**Diferencia LST vs Temperatura del aire (Ta)**:

| Aspecto | LST | Ta |
|---------|-----|-----|
| Qué mide | Temperatura de SUPERFICIE (techo, pavimento, suelo, vegetación) | Temperatura del AIRE a 2m de altura |
| Relación con UHI | Mide directamente islas de calor superficial (SUHI) | Mide islas de calor atmosférico |
| Valor típico | LST > Ta en superficies expuestas; LST ≈ Ta en áreas vegetadas | Más estable espacialmente |
| Diferencia LST-Ta | Mayor en islas de calor urbano | - |
| Para biodiversidad | Más directo (vegetación enfría superficie) | Indirecto |

**Ventajas para el análisis de biodiversidad**:
1. Resolución espacial alta (1 km) permite detectar efectos locales de vegetación
2. Mide directamente el efecto de enfriamiento superficial de la vegetación
3. La diferencia entre áreas vegetadas y no vegetadas es más pronunciada en LST que en Ta
4. Permite mapear islas de calor urbano con detalle

**Limitación importante**:
- LST no debe usarse directamente para calcular impactos de salud (la mortalidad se asocia con Ta, no LST)
- LST es complementario: sirve para validar dónde hay islas de calor, no para predecir mortalidad

---

## 5. NOTA SOBRE LA MÉTRICA DE INTENSIDAD HORARIA

Durante el diseño metodológico, se consideró una quinta métrica: "Intensidad: número de horas por encima del umbral × número de días bajo estrés térmico". Esta métrica requeriría datos horarios de temperatura.

### Evaluación de opciones

**Opción A: ERA5-Land horario (resolución 0.1°)**
- Ventaja: Datos horarios disponibles
- Desventaja: Computacionalmente intensivo (87,600 imágenes para 10 años)
- Desventaja: Es reanálisis global, no observaciones directas de Brasil

**Opción B: Modelo de ciclo diurno sinusoidal (Allen et al.)**
- Ventaja: Estima horas a partir de Tmax/Tmin diarios
- Desventaja: Asume ciclo sinusoidal perfecto (poco realista en clima tropical)
- Desventaja: Error de estimación no cuantificado para São Paulo

**Opción C: Usar HAAT como proxy de intensidad**
- Ventaja: Usa datos diarios de Xavier/BR-DWGD (observaciones directas)
- Ventaja: Captura tanto intensidad como frecuencia
- Ventaja: Respaldado por estudio medRxiv 2025 de Río de Janeiro

### Decisión tomada

Se decidió usar la métrica **HAAT (heat_HAAT)** con datos diarios como la mejor aproximación operacionalmente viable. HAAT captura:
- **Frecuencia**: Días con Tmax > 34.7°C
- **Intensidad**: Magnitud del exceso de temperatura

Esta métrica es más informativa que la persistencia simple y está respaldada por evidencia científica reciente en Brasil, sin requerir datos horarios ni modelos de estimación con incertidumbre elevada.

---

## 6. IMPLEMENTACIÓN TÉCNICA

La extracción de variables de estrés térmico se implementó mediante tres scripts: dos en Google Earth Engine (JavaScript) para extracción de datos satelitales y climáticos, y uno en Python para integración al dataset principal.

### 6.1 Script 1: Google Earth Engine - Xavier/BR-DWGD

**Archivo**: `scripts/gee_extract_heat_stress_xavier.js`

**Plataforma**: Google Earth Engine Code Editor (https://code.earthengine.google.com)

**Entrada de datos**:
- **Xavier/BR-DWGD v3**:
  - `projects/br-dwgd/assets/tmax` (temperatura máxima diaria)
  - `projects/br-dwgd/assets/tmin` (temperatura mínima diaria)
- **Municipios**: `projects/mapbiomas-workspace/AUXILIAR/municipios-2022`
  - Filtrado: `sigla_uf = 'SP'` (645 municipios)

**Período**: 2010-01-01 a 2019-12-31 (10 años)

**Proceso de cálculo**:

1. **Carga de datos**:
   - Filtrar ImageCollection de Tmax y Tmin por rango de fechas
   - Filtrar municipios de São Paulo

2. **Cálculo anual** (para cada año 2010-2019):

   a) **Persistencia**:
   ```javascript
   var hotDays = tmax_year.map(function(img) {
     return img.gt(34.7).rename('hot_day');
   });
   var persistence = hotDays.sum();
   ```

   b) **HAAT**:
   ```javascript
   var haat = tmax_year.map(function(img) {
     var excess = img.subtract(34.7).max(0);
     return excess.rename('haat');
   });
   var haat_sum = haat.sum();
   ```

   c) **MMT Days**:
   ```javascript
   // Emparejar Tmax y Tmin por fecha
   var mmtDays = tmax_year.map(function(tmax_img) {
     var date = tmax_img.date();
     var tmin_img = tmin_year.filterDate(date, date.advance(1, 'day')).first();
     var tmean = tmax_img.add(tmin_img).divide(2);
     return tmean.gt(22.3).rename('mmt_day');
   });
   var mmt_days = mmtDays.sum();
   ```

3. **Agregación decadal**:
   - Media de las 10 imágenes anuales → `_mean`
   - Desviación estándar de las 10 imágenes → `_sd`

4. **Reducción por municipio**:
   ```javascript
   var municipalMetrics = allMetrics.reduceRegions({
     collection: municipios,
     reducer: ee.Reducer.mean(),
     scale: 11132,  // ~0.1° en metros
     crs: 'EPSG:4326'
   });
   ```

**Salida**:
- Archivo CSV: `heat_stress_xavier_sp_2010_2019.csv`
- Destino: Google Drive, carpeta `Adrian_David_Data`
- Columnas:
  - `cd_mun`: Código IBGE del municipio
  - `nm_mun`: Nombre del municipio
  - `heat_persistence_mean`: Persistencia media (días/año)
  - `heat_persistence_sd`: Desviación estándar persistencia
  - `heat_HAAT_mean`: HAAT medio (grados-día/año)
  - `heat_HAAT_sd`: Desviación estándar HAAT
  - `mmt_days_mean`: MMT days medio (días/año)
  - `mmt_days_sd`: Desviación estándar MMT days

**Tiempo estimado de ejecución**: 15-30 minutos (depende de carga de GEE)

### 6.2 Script 2: Google Earth Engine - MODIS LST

**Archivo**: `scripts/gee_extract_modis_lst.js`

**Plataforma**: Google Earth Engine Code Editor

**Entrada de datos**:
- **MODIS Terra**: `MODIS/061/MOD11A2` (2010-2019)
- **MODIS Aqua**: `MODIS/061/MYD11A2` (2010-2019)
- **Municipios**: `projects/mapbiomas-workspace/AUXILIAR/municipios-2022` (SP)

**Proceso de cálculo**:

1. **Filtrado y carga**:
   ```javascript
   var modis_terra = ee.ImageCollection('MODIS/061/MOD11A2')
     .filterDate('2010-01-01', '2019-12-31')
     .filterBounds(municipios);

   var modis_aqua = ee.ImageCollection('MODIS/061/MYD11A2')
     .filterDate('2010-01-01', '2019-12-31')
     .filterBounds(municipios);
   ```

2. **Conversión DN a °C y aplicación de filtro de calidad**:
   ```javascript
   var processLST = function(img) {
     // Máscara de calidad (bits 0-1: 00=good, 01=average)
     var qcDay = img.select('QC_Day');
     var goodDay = qcDay.bitwiseAnd(3).lte(1);

     // Convertir a Celsius
     var lstDay = img.select('LST_Day_1km')
       .multiply(0.02)          // Factor de escala
       .add(-273.15)            // Kelvin a Celsius
       .updateMask(goodDay);    // Aplicar máscara QC

     return lstDay.addBands(lstNight);
   };
   ```

3. **Combinación Terra + Aqua**:
   ```javascript
   var combined = terra_processed.merge(aqua_processed);
   ```

4. **Cálculo de estadísticas decadales**:
   ```javascript
   var lstDayMean = combined.select('LST_Day_C').mean();
   var lstNightMean = combined.select('LST_Night_C').mean();
   var lstDayP95 = combined.select('LST_Day_C').reduce(ee.Reducer.percentile([95]));
   var lstDaySD = combined.select('LST_Day_C').reduce(ee.Reducer.stdDev());
   var lstAmplitude = lstDayMean.subtract(lstNightMean);
   ```

5. **Reducción por municipio**:
   ```javascript
   var municipalLST = allLST.reduceRegions({
     collection: municipios,
     reducer: ee.Reducer.mean(),
     scale: 1000,  // 1 km (resolución nativa MODIS)
     crs: 'EPSG:4326'
   });
   ```

**Salida**:
- Archivo CSV: `modis_lst_sp_2010_2019.csv`
- Destino: Google Drive, carpeta `Adrian_David_Data`
- Columnas:
  - `cd_mun`: Código IBGE
  - `nm_mun`: Nombre municipio
  - `lst_day_mean`: LST diurna media (°C)
  - `lst_night_mean`: LST nocturna media (°C)
  - `lst_day_p95`: Percentil 95 LST diurna (°C)
  - `lst_day_sd`: Desviación estándar LST diurna
  - `lst_amplitude`: Amplitud térmica día-noche (°C)

**Tiempo estimado de ejecución**: 20-40 minutos

### 6.3 Script 3: Python - Integración al Dataset

**Archivo**: `scripts/create_integrated_dataset_v9.py`

**Entorno**: Python 3.8+, pandas

**Prerequisitos**:
1. Ejecutar `gee_extract_heat_stress_xavier.js` en GEE
2. Ejecutar `gee_extract_modis_lst.js` en GEE
3. Descargar ambos CSVs de Google Drive a `data/processed/`

**Proceso**:

1. **Carga de datos**:
   ```python
   df_v8 = pd.read_csv("outputs/municipios_integrado_v8.csv")
   df_heat = pd.read_csv("data/processed/heat_stress_xavier_sp_2010_2019.csv")
   df_lst = pd.read_csv("data/processed/modis_lst_sp_2010_2019.csv")
   ```

2. **Normalización de códigos IBGE**:
   ```python
   df_v8['cod_ibge'] = df_v8['cod_ibge'].astype(str)
   df_heat['cod_ibge'] = df_heat['cd_mun'].astype(str).str[:7]
   df_lst['cod_ibge'] = df_lst['cd_mun'].astype(str).str[:7]
   ```

3. **Merge de datasets**:
   ```python
   df_v9 = df_v8.copy()
   df_v9 = df_v9.merge(df_heat, on='cod_ibge', how='left')
   df_v9 = df_v9.merge(df_lst, on='cod_ibge', how='left')
   ```

4. **Verificación de integridad**:
   - Confirmar que no se perdieron municipios
   - Verificar porcentaje de valores NaN en nuevas columnas
   - Calcular estadísticas descriptivas

5. **Correlaciones preliminares**:
   ```python
   biodiv_vars = ['forest_cover', 'mean_species_richness', 'idx_biodiv']
   health_vars = ['mort_circ_rate', 'hosp_circ_rate']

   for heat_var in heat_vars:
       for bv in biodiv_vars:
           r = df_v9[heat_var].corr(df_v9[bv])
   ```

6. **Exportación**:
   ```python
   df_v9.to_csv("outputs/municipios_integrado_v9.csv", index=False)
   ```

**Salida**:
- Archivo: `outputs/municipios_integrado_v9.csv`
- Dimensiones: 645 municipios × ~112 variables
- Nuevas variables: 8-11 (dependiendo de disponibilidad de datos)

**Variables incrementales** (v8 → v9):

| Variable | Tipo | Fuente | Descripción |
|----------|------|--------|-------------|
| `heat_persistence_mean` | float | Xavier | Días/año con Tmax > 34.7°C (promedio 2010-2019) |
| `heat_persistence_sd` | float | Xavier | Desviación estándar interanual |
| `heat_HAAT_mean` | float | Xavier | Grados-día acumulados sobre 34.7°C (promedio anual) |
| `heat_HAAT_sd` | float | Xavier | Desviación estándar interanual |
| `mmt_days_mean` | float | Xavier | Días/año con Tmedia > 22.3°C (promedio 2010-2019) |
| `mmt_days_sd` | float | Xavier | Desviación estándar interanual |
| `lst_day_mean` | float | MODIS | LST diurna media (°C, promedio 2010-2019) |
| `lst_night_mean` | float | MODIS | LST nocturna media (°C, promedio 2010-2019) |
| `lst_day_p95` | float | MODIS | Percentil 95 LST diurna (extremos de calor) |
| `lst_day_sd` | float | MODIS | Desviación estándar LST diurna |
| `lst_amplitude` | float | MODIS | Amplitud térmica día-noche (°C) |

### 6.4 Instrucciones de Ejecución

**Paso 1: Preparar Google Earth Engine**
1. Acceder a https://code.earthengine.google.com
2. Registrarse o iniciar sesión (requiere cuenta Google)
3. Verificar acceso al asset de municipios MapBiomas

**Paso 2: Ejecutar extracción de Xavier/BR-DWGD**
1. Copiar contenido de `scripts/gee_extract_heat_stress_xavier.js`
2. Pegar en GEE Code Editor
3. Hacer clic en "Run"
4. Ir a pestaña "Tasks" (esquina superior derecha)
5. Hacer clic en "Run" junto a la tarea `heat_stress_xavier_sp_2010_2019`
6. Confirmar exportación a Google Drive

**Paso 3: Ejecutar extracción de MODIS LST**
1. Copiar contenido de `scripts/gee_extract_modis_lst.js`
2. Pegar en GEE Code Editor (nueva pestaña o reemplazar)
3. Hacer clic en "Run"
4. Ir a pestaña "Tasks"
5. Hacer clic en "Run" junto a la tarea `modis_lst_sp_2010_2019`
6. Confirmar exportación a Google Drive

**Paso 4: Esperar completitud de tareas GEE**
- Tiempo estimado: 15-40 minutos por tarea
- Verificar en pestaña "Tasks" que el estado cambie a "Completed"
- Si hay error, revisar consola de GEE para mensajes de error

**Paso 5: Descargar CSVs de Google Drive**
1. Ir a Google Drive
2. Navegar a carpeta `Adrian_David_Data`
3. Descargar `heat_stress_xavier_sp_2010_2019.csv`
4. Descargar `modis_lst_sp_2010_2019.csv`
5. Mover archivos a `C:\Users\arlex\Documents\Adrian David\data\processed\`

**Paso 6: Ejecutar integración de dataset**
```bash
cd "C:\Users\arlex\Documents\Adrian David"
python scripts/create_integrated_dataset_v9.py
```

**Paso 7: Verificar resultados**
- Revisar archivo generado: `outputs/municipios_integrado_v9.csv`
- Verificar que tenga 645 filas y ~112 columnas
- Revisar consola de Python para estadísticas y correlaciones preliminares

### 6.5 Solución de Problemas

**Problema: Asset de municipios no accesible en GEE**

Solución:
1. Descargar shapefile de municipios de IBGE 2022 de `data/geo/ibge_sp/`
2. Subir como asset propio en GEE (Assets → New → Table Upload)
3. Cambiar línea en scripts:
   ```javascript
   var municipios = ee.FeatureCollection('users/TU_USUARIO/sp_municipios_ibge2022');
   ```

**Problema: Error "Collection contains no elements" en MMT Days**

Causa: Desemparejamiento de fechas entre Tmax y Tmin

Solución: El script ya incluye manejo de este caso con condicional `ee.Algorithms.If`

**Problema: Valores NaN excesivos (>10%) en LST**

Causa: Cobertura de nubes muy alta en algunos municipios

Solución: Aceptable si <20% de NaN. Para análisis, usar imputación por vecinos espaciales o excluir variable LST para esos municipios.

**Problema: Correlaciones preliminares no aparecen en Python**

Causa: Nombres de columnas no coinciden

Solución: Verificar nombres exactos en CSV con `df_v9.columns.tolist()`

---

## 7. VALIDACIÓN EPIDEMIOLÓGICA

Las métricas seleccionadas están respaldadas por evidencia científica robusta que vincula estrés térmico con mortalidad y morbilidad en São Paulo y Brasil.

### Hallazgos clave de literatura para São Paulo

#### 7.1 Validación del EHF (Excess Heat Factor) en São Paulo

**Estudio**: Validación de EHF en 3 ciudades paulistas (2004-2018)

**Resultados**:
- **2,319 muertes atribuibles al calor** en São Paulo, Campinas y Marília
- Riesgo relativo de mortalidad por incremento en EHF:
  - São Paulo: RR = 1.0018 (IC 95%: 1.0012-1.0024)
  - Campinas: RR = 1.0029 (IC 95%: 1.0018-1.0040)
  - Marília: RR = 1.0033 (IC 95%: 1.0019-1.0047)

**Interpretación**:
- Por cada unidad de incremento en EHF, la mortalidad aumenta 0.18-0.33%
- Efecto consistente en las 3 ciudades
- Mayor efecto en ciudades más pequeñas (Marília > Campinas > SP)

#### 7.2 Calor y mortalidad cardiovascular en São Paulo

**Estudio**: Liu et al. (2022), Lancet Planetary Health - Brazil Collaboration

**Resultados clave**:
- **2.1% de incremento en mortalidad cardiovascular por cada 1°C por encima de temperatura de referencia**
- **11.7% de incremento durante ondas de calor**
- Mayor riesgo para:
  - **Mujeres**: Efecto de calor más pronunciado que en hombres
  - **Personas sin educación formal**: Vulnerabilidad socioeconómica
- Período crítico: Octubre-Marzo (verano austral)

**Curva exposición-respuesta**:
- Forma de U: Tanto frío como calor aumentan mortalidad
- Temperatura de mínima mortalidad (MMT): ~22°C
- Incremento exponencial de riesgo por encima de MMT

#### 7.3 Tendencia temporal de vulnerabilidad al calor (2000-2018)

**Estudio**: Masselot et al. (2022), PMC 9727050

**Hallazgo principal**:
- **La vulnerabilidad al calor está EMPEORANDO en São Paulo**
- La adaptación al frío está MEJORANDO

**Evidencia**:
- MMT ha aumentado significativamente (2000-2018)
- Riesgo relativo acumulado (cRR) para muertes cardiovasculares aumenta con el tiempo
- Cambio en la forma de la curva temperatura-mortalidad: pérdida de adaptación al calor

**Implicaciones**:
- Urbanización y envejecimiento poblacional reducen resiliencia al calor
- Necesidad urgente de políticas de adaptación
- Servicios ecosistémicos de enfriamiento son críticos

#### 7.4 Diferencial calor vs frío por causa de muerte

**Estudio**: Bell et al. (2015), Epidemiology

**Resultados para São Paulo**:
- **FRÍO** se asocia más con mortalidad **cardiovascular**
- **CALOR** se asocia más con mortalidad **respiratoria**

**Explicación fisiológica**:
- Frío: Vasoconstricción, aumento de presión arterial → IAM, ACV
- Calor: Deshidratación, estrés respiratorio, exacerbación de EPOC

**Relevancia para el proyecto**:
- Variables de estrés térmico pueden tener asociación bidireccional con mortalidad cardiovascular
- Es necesario controlar por estacionalidad en modelos estadísticos

#### 7.5 MMT para infarto agudo de miocardio en Brasil

**Estudio**: Nascimento et al. (2019), Scientific Reports

**DOI**: 10.1038/s41598-019-50235-8

**Metodología**: Análisis de 28,518 muertes por IAM en todo Brasil (2010-2015)

**Resultados por región**:
- **Sur**: MMT = 22°C (clima más frío)
- **Sureste**: MMT = 22-23°C (incluye São Paulo)
- **Nordeste**: MMT = 25-26°C
- **Centro-Oeste**: MMT = 28°C (clima más cálido)

**Hallazgo clave**:
- MMT varía geográficamente según aclimatación poblacional
- 22.3°C es consistente con región Sureste de Brasil
- Mortalidad por IAM aumenta significativamente por encima de MMT

### Evidencia sobre islas de calor urbano en São Paulo

#### 7.6 SUHI en São Paulo: magnitud y distribución

**Estudio**: Monteiro et al. (2021), Urban Climate

**Título**: Assessment of Urban Heat Islands in Brazil based on MODIS remote sensing data

**Resultados para São Paulo**:
- **SUHI diurna**: 6.60°C (3ª más alta de Sudamérica, después de Buenos Aires y Brasilia)
- **SUHI nocturna**: La MÁS ALTA de Brasil
- Regiones central y este de SP son hotspots recurrentes de SUHI
- Correlación con densidad de construcción y déficit de vegetación

**Comparación regional**:
| Ciudad | SUHI diurna | SUHI nocturna |
|--------|-------------|---------------|
| Buenos Aires | 7.20°C | 4.10°C |
| Brasilia | 6.80°C | 3.90°C |
| **São Paulo** | **6.60°C** | **5.20°C** (máxima) |
| Rio de Janeiro | 5.40°C | 4.80°C |
| Belo Horizonte | 5.10°C | 3.50°C |

#### 7.7 Análisis de SUHI en 44 ciudades sudamericanas

**Estudio**: Wu et al. (2019), Remote Sensing

**Título**: Investigating Surface Urban Heat Islands in South America based on MODIS data

**Hallazgos generales**:
- SUHI más intenso en ciudades de clima tropical y subtropical
- São Paulo destaca por alta intensidad nocturna
- SUHI correlaciona negativamente con NDVI (vegetación)

**Factores agravantes en SP**:
1. Expansión urbana acelerada
2. Reemplazo de vegetación por superficies impermeables
3. Alta densidad de construcción en centro y zona este
4. Déficit de áreas verdes per cápita

### Evidencia sobre vegetación urbana y enfriamiento

#### 7.8 Meta-análisis global de enfriamiento por vegetación

**Fuente**: Compilación de estudios 2015-2023

**Hallazgos**:
- Espacios verdes urbanos reducen temperatura en **1-7°C**
- Jardines botánicos: enfriamiento de **5.0 ± 3.5°C**
- Arbolado urbano: **3.8 ± 3.1°C**
- Árboles son efectivos en **98% de las ciudades globales** (vs 78% para pastizales)

**Limitación crítica**:
- En condiciones de **estrés hídrico extremo**, los árboles **fallan en enfriar** en 25% de las ciudades
- Relevante para São Paulo: necesidad de manejo hídrico adecuado

**Implicaciones para H3**:
- Efecto de biodiversidad sobre temperatura está bien documentado globalmente
- Magnitud de enfriamiento varía según tipo de vegetación (árboles > pastos)
- Contexto hídrico puede modular el efecto

### Síntesis de evidencia epidemiológica

**Relaciones validadas para São Paulo**:

| Relación | Magnitud del efecto | Fuente |
|----------|-------------------|--------|
| Calor → Mortalidad cardiovascular | +2.1% por °C | Liu et al. 2022 |
| Onda de calor → Mortalidad cardiovascular | +11.7% | Liu et al. 2022 |
| EHF → Mortalidad total | RR = 1.0018-1.0033 | Validación SP/Campinas/Marília |
| SUHI → Temperatura superficial | +6.6°C (día), +5.2°C (noche) | Monteiro et al. 2021 |
| Vegetación → Temperatura | -3.8°C a -5.0°C | Meta-análisis global |

**Grupos vulnerables identificados**:
1. Mujeres (mayor efecto de calor)
2. Personas sin educación formal (vulnerabilidad socioeconómica)
3. Poblaciones de regiones centrales y este de SP (mayor SUHI)

**Tendencia temporal preocupante**:
- Vulnerabilidad al calor **empeorando** en SP (2000-2018)
- Urgencia de políticas de adaptación basadas en naturaleza

---

## 8. ANÁLISIS PLANIFICADOS

Con el dataset v9 que incorpora variables de estrés térmico, se planifican los siguientes análisis organizados en torno a cuatro sub-hipótesis de complejidad creciente.

---

### 8.0 Marco de sub-hipótesis H3

La hipótesis general H3 (Biodiversidad/Vegetación reduce estrés térmico y sus impactos en salud) se descompone en cuatro sub-hipótesis que representan cadenas causales progresivamente más complejas:

```
H3.1  Cobertura forestal / Biodiversidad
          → (−) Estrés térmico
              → (−) Impacto en salud

H3.2  Cobertura forestal / Biodiversidad
          → (−) Presencia de fuego
              → (−) Estrés térmico
                  → (−) Impacto en salud

H3.3  (Cobertura forestal / Biodiversidad → (−) Presencia de fuego)
          * Vulnerabilidad [efectos más fuertes en municipios rurales
            y con menor población en estado de pobreza]
              → (−) Estrés térmico
                  → (−) Impacto en salud

H3.4  Mayor gobernanza (general o climática)
          → (Cobertura forestal / Biodiversidad → (−) Presencia de fuego)
              * Vulnerabilidad [efectos más fuertes en municipios rurales
                y con menor población en estado de pobreza]
                  → (−) Estrés térmico
                      → (−) Impacto en salud
```

#### Diagrama causal integrado (DAG)

```
                 GOBERNANZA (H3.4)
                 idx_gobernanza / UAI_Crisk
                        |
                        v  (+)
         +---------------------------------+
         |  COBERTURA FORESTAL /           |
         |  BIODIVERSIDAD                  |
         |  forest_cover, idx_biodiv,      |
         |  mean_species_richness          |
         +---------------------------------+
                  |              |
          (H3.1) |              | (H3.2)
            (−)  |              |  (−)
                 v              v
          ESTRÉS        PRESENCIA DE
          TÉRMICO  <--- FUEGO
          heat_HAAT     fire_incidence
          mmt_days      fire_frp_mean
          lst_day       fire_risk_index
                 |
            (−)  |    * VULNERABILIDAD (H3.3)
                 |      pct_pobreza, pct_rural
                 v      pop_total (inverso)
          IMPACTO EN SALUD
          mort_circ_rate, hosp_circ_rate
          mort_resp_rate
```

#### Variables del dataset v9 por componente

| Componente | Variables disponibles | Tipo |
|------------|---------------------|------|
| **Biodiversidad** | `forest_cover`, `mean_species_richness`, `idx_biodiv`, `pol_deficit` | Independiente |
| **Fuego** | `fire_incidence_mean`, `fire_frp_mean`, `fire_risk_index` | Mediador (H3.2+) |
| **Estrés térmico** | `heat_persistence_mean`, `heat_HAAT_mean`, `mmt_days_mean`, `lst_day_mean`, `lst_night_mean` | Mediador |
| **Salud** | `mort_circ_rate`, `hosp_circ_rate`, `mort_resp_rate`, `dengue_incidence_mean` | Dependiente |
| **Vulnerabilidad** | `pct_pobreza`, `pct_rural`, `pct_negra`, `pct_indigena`, `idx_vulnerabilidad` | Moderador (H3.3+) |
| **Gobernanza** | `idx_gobernanza`, `UAI_Crisk`, `UAI_env`, `UAI_housing` | Facilitador (H3.4) |

---

### 8.1 Análisis para H3.1: Biodiversidad → Estrés Térmico → Salud

**Cadena causal**: Mediación simple en dos etapas.

#### 8.1.1 Correlaciones bivariadas

**Variables independientes**: `forest_cover`, `mean_species_richness`, `idx_biodiv`
**Variables mediadoras**: `heat_persistence_mean`, `heat_HAAT_mean`, `mmt_days_mean`, `lst_day_mean`, `lst_night_mean`
**Variables dependientes**: `mort_circ_rate`, `hosp_circ_rate`, `mort_resp_rate`

**Hipótesis de correlaciones**:
1. Biodiversidad correlaciona negativamente con todas las métricas de calor
2. LST muestra correlación más fuerte con biodiversidad que métricas basadas en temperatura del aire (captura regulación de superficie directamente)
3. Métricas de calor correlacionan positivamente con mortalidad cardiovascular

#### 8.1.2 Análisis de mediación (Baron & Kenny / bootstrapping)

**Modelo conceptual**:
```
Biodiversidad → (a) → Estrés Térmico → (b) → Mortalidad Cardiovascular
              ↘          (c')          ↗

Efecto total:     c = ab + c'
Efecto indirecto: ab (mediación por estrés térmico)
Efecto directo:   c' (otros mecanismos: dilución, etc.)
```

**Ecuaciones de regresión**:
```
Modelo 1 (path a):  heat_HAAT ~ forest_cover + controles
Modelo 2 (path b):  mort_circ_rate ~ heat_HAAT + controles
Modelo 3 (path c'): mort_circ_rate ~ forest_cover + heat_HAAT + controles
```

**Variables de control**:
- `idx_vuln`: Índice de vulnerabilidad socioeconómica
- `pop_density`: Densidad poblacional
- `pct_urban`: Porcentaje de población urbana
- `mesoregion`: Mesorregión (efecto fijo o aleatorio)

**Implementación**: R (`mediation`) o Python (`statsmodels`), con bootstrapping (5,000 iteraciones) para intervalos de confianza del efecto indirecto.

**Resultados esperados**:
- Efecto indirecto significativo (ab != 0)
- Proporción mediada: 20-40% del efecto total
- Efecto directo residual (c') aún significativo (mediación parcial, consistente con efecto dilución ya demostrado)

---

### 8.2 Análisis para H3.2: Biodiversidad → Fuego → Estrés Térmico → Salud

**Cadena causal**: Mediación serial (dos mediadores secuenciales).

#### 8.2.1 Justificación

Los incendios forestales destruyen cobertura vegetal, eliminando el servicio de regulación térmica. En municipios con mayor presencia de fuego se espera:
1. Menor cobertura forestal residual
2. Mayor temperatura de superficie (menor evapotranspiración)
3. Mayor estrés térmico acumulado
4. Mayor impacto en salud cardiovascular y respiratoria

#### 8.2.2 Modelo de mediación serial

```
Biodiversidad → (a1) → Fuego → (a2) → Estrés Térmico → (b) → Salud
              ↘                                         ↗
                           (c')

Efectos indirectos:
  - Vía 1: a1 * a2 * b  (cadena completa biodiv → fuego → calor → salud)
  - Vía 2: a1 * d1       (biodiv → fuego → salud, sin mediación térmica)
  - Vía 3: a3 * b         (biodiv → calor → salud, sin mediación por fuego)
```

**Ecuaciones**:
```
Modelo 1: fire_incidence ~ forest_cover + controles
Modelo 2: heat_HAAT ~ forest_cover + fire_incidence + controles
Modelo 3: mort_circ_rate ~ forest_cover + fire_incidence + heat_HAAT + controles
```

**Implementación**: R (`lavaan` para SEM) o Python (`semopy`)

```R
library(lavaan)

model_h3.2 <- '
  # Paths directos
  fire_incidence ~ a1*forest_cover + c_fire*idx_vuln
  heat_HAAT      ~ a2*fire_incidence + a3*forest_cover + c_heat*idx_vuln
  mort_circ_rate ~ b*heat_HAAT + d1*fire_incidence + cp*forest_cover + c_mort*idx_vuln

  # Efectos indirectos
  serial   := a1 * a2 * b    # Cadena completa
  via_fire := a1 * d1         # Biodiv → Fuego → Salud
  via_heat := a3 * b          # Biodiv → Calor → Salud
  total_indirect := serial + via_fire + via_heat
'
fit_h3.2 <- sem(model_h3.2, data = df_v9, se = "bootstrap", bootstrap = 5000)
```

**Pregunta clave**: ?Cuanto del efecto de la biodiversidad sobre la salud es mediado por la reduccion de fuego vs. por la regulacion termica directa?

---

### 8.3 Análisis para H3.3: (Biodiversidad → Fuego) * Vulnerabilidad → Estrés Térmico → Salud

**Cadena causal**: Mediación serial moderada (la vulnerabilidad amplifica o atenua los efectos).

#### 8.3.1 Justificación

La vulnerabilidad socioeconómica modifica la fuerza de la cadena causal. Se hipotetiza que los efectos protectores de la biodiversidad son mas fuertes en:
- **Municipios rurales**: Mayor dependencia de servicios ecosistémicos; menor infraestructura de mitigación (aire acondicionado, hospitales)
- **Municipios con menor pobreza**: Mayor capacidad de aprovechar la regulación climática natural (viviendas mejor ubicadas, acceso a áreas verdes)

Esto implica que la vulnerabilidad **no es solo un confusor** sino un **moderador** que modifica la magnitud del efecto.

#### 8.3.2 Variables moderadoras

| Moderador | Variable | Dirección esperada |
|-----------|----------|-------------------|
| Ruralidad | `pct_rural` | Efecto biodiversidad **mas fuerte** en municipios rurales |
| Pobreza | `pct_pobreza` | Efecto biodiversidad **mas fuerte** con menor pobreza |
| Población | `pop_total` (inverso) | Efecto **mas fuerte** en municipios pequeños |
| Raza | `pct_negra` | Efecto diferencial por composición racial (justicia ambiental) |

#### 8.3.3 Modelos de interacción

**Paso 1: Moderación sobre la relación biodiversidad-fuego**:
```
fire_incidence ~ forest_cover + pct_rural + forest_cover:pct_rural + controles
fire_incidence ~ forest_cover + pct_pobreza + forest_cover:pct_pobreza + controles
```

**Paso 2: Moderación sobre la relación fuego-estrés térmico**:
```
heat_HAAT ~ fire_incidence + pct_rural + fire_incidence:pct_rural + controles
```

**Paso 3: Moderación sobre la relación estrés térmico-salud**:
```
mort_circ_rate ~ heat_HAAT + pct_pobreza + heat_HAAT:pct_pobreza + controles
```

#### 8.3.4 Modelo SEM con moderación (moderated mediation)

```R
library(lavaan)

# Crear términos de interacción
df_v9$forest_x_rural <- df_v9$forest_cover * df_v9$pct_rural
df_v9$forest_x_poverty <- df_v9$forest_cover * df_v9$pct_pobreza
df_v9$fire_x_rural <- df_v9$fire_incidence * df_v9$pct_rural
df_v9$heat_x_poverty <- df_v9$heat_HAAT * df_v9$pct_pobreza

model_h3.3 <- '
  # Paths con moderación
  fire_incidence ~ a1*forest_cover + m1*forest_x_rural + v1*pct_rural
  heat_HAAT      ~ a2*fire_incidence + a3*forest_cover + m2*fire_x_rural + v2*pct_rural
  mort_circ_rate ~ b*heat_HAAT + m3*heat_x_poverty + d1*fire_incidence +
                   cp*forest_cover + v3*pct_pobreza

  # Efectos condicionales (a valores altos/bajos del moderador)
'
fit_h3.3 <- sem(model_h3.3, data = df_v9, se = "bootstrap", bootstrap = 5000)
```

#### 8.3.5 Análisis de pendientes simples (simple slopes)

Para interpretar las interacciones:
- Calcular el efecto de `forest_cover` sobre `fire_incidence` a distintos niveles de `pct_rural` (media, media +/- 1 SD)
- Calcular el efecto de `heat_HAAT` sobre `mort_circ_rate` a distintos niveles de `pct_pobreza`

```R
library(interactions)
interact_plot(model, pred = forest_cover, modx = pct_rural,
              modx.values = "plus-minus", interval = TRUE)
```

**Visualizaciones**:
- Johnson-Neyman plots: identificar el valor del moderador a partir del cual el efecto se vuelve significativo
- Superficies de respuesta 3D: biodiversidad x vulnerabilidad -> estrés térmico

---

### 8.4 Análisis para H3.4: Gobernanza → (Biodiversidad → Fuego) * Vulnerabilidad → Estrés Térmico → Salud

**Cadena causal completa**: La gobernanza actúa como facilitador aguas arriba de toda la cadena.

#### 8.4.1 Justificación

La gobernanza (general o climática) puede facilitar la conservación de biodiversidad, reducir incendios mediante fiscalización, y reducir la vulnerabilidad mediante políticas sociales. Es el "lever" (palanca) político que puede activar toda la cadena de protección.

La paradoja ya identificada (gobernanza NO reduce directamente riesgos climáticos, r = +0.29) sugiere que el efecto de la gobernanza opera **indirectamente**, no como protección directa sino como habilitador de las condiciones que permiten la regulación ecosistémica.

#### 8.4.2 Roles de la gobernanza en el modelo

| Rol | Variable | Mecanismo | Sobre qué actúa |
|-----|----------|-----------|-----------------|
| **Facilitador de conservación** | `UAI_env` | Gestión ambiental municipal | `forest_cover`, `idx_biodiv` |
| **Reductor de fuego** | `UAI_Crisk` | Gestión de riesgo climático | `fire_incidence`, `fire_risk_index` |
| **Reductor de vulnerabilidad** | `UAI_housing`, `UAI_food` | Adaptación socioeconómica | `pct_pobreza`, `idx_vulnerabilidad` |
| **Gobernanza general** | `idx_gobernanza` | Todos los anteriores | Múltiple |

#### 8.4.3 Modelo SEM completo (full path model)

```
                   idx_gobernanza / UAI_Crisk
                        |         |
                   (g1) |         | (g2)
                        v         v
                  forest_cover   fire_incidence ← (a1) ← forest_cover
                        |              |
                   (a3) |         (a2) |
                        v              v
                      heat_HAAT ←------+
                        |
                   (b)  |  * pct_rural, pct_pobreza
                        v
                  mort_circ_rate
```

```R
library(lavaan)

model_h3.4 <- '
  # Gobernanza como facilitador
  forest_cover   ~ g1*idx_gobernanza + e1*pct_rural
  fire_incidence ~ g2*UAI_Crisk + a1*forest_cover + e2*pct_rural

  # Cadena mediadora
  heat_HAAT      ~ a2*fire_incidence + a3*forest_cover + e3*pct_rural
  mort_circ_rate ~ b*heat_HAAT + d1*fire_incidence + cp*forest_cover +
                   e4*pct_pobreza + e5*pct_rural

  # Efectos indirectos clave
  # Gobernanza → Biodiversidad → Calor → Salud
  gov_biodiv_heat_health := g1 * a3 * b

  # Gobernanza → Reducción fuego → Menor calor → Salud
  gov_fire_heat_health := g2 * a2 * b

  # Cadena completa gobernanza → biodiv → fuego → calor → salud
  gov_full_chain := g1 * a1 * a2 * b

  # Total indirecto de gobernanza
  gov_total_indirect := gov_biodiv_heat_health + gov_fire_heat_health + gov_full_chain
'
fit_h3.4 <- sem(model_h3.4, data = df_v9, se = "bootstrap", bootstrap = 5000)
summary(fit_h3.4, fit.measures = TRUE, standardized = TRUE, rsquare = TRUE)
```

#### 8.4.4 Descomposición de efectos de gobernanza

El análisis H3.4 permite descomponer el efecto total de la gobernanza en:

| Vía | Fórmula | Interpretación |
|-----|---------|----------------|
| Directa | cp_gov | Efecto directo de gobernanza sobre salud (si existiese path directo) |
| Via biodiversidad | g1 * a3 * b | Gobernanza conserva bosque, que reduce calor, que reduce mortalidad |
| Via fuego | g2 * a2 * b | Gobernanza reduce fuego, que reduce calor, que reduce mortalidad |
| Cadena completa | g1 * a1 * a2 * b | Gobernanza conserva bosque, que reduce fuego, que reduce calor, que reduce mortalidad |
| Total indirecto | suma de las anteriores | Efecto total mediado de gobernanza |

**Pregunta clave**: ?A traves de cual mecanismo la gobernanza tiene mayor efecto sobre la salud: conservando biodiversidad o reduciendo fuego?

#### 8.4.5 Test de gobernanza general vs. climática

Comparar dos versiones del modelo:
- **Modelo A**: Usar `idx_gobernanza` (gobernanza general, promedio de 5 UAIs)
- **Modelo B**: Usar `UAI_Crisk` (gobernanza climática específica)

Comparar R², AIC, BIC para determinar qué dimensión de gobernanza es más relevante para la cadena causal.

---

### 8.5 Métodos transversales a todas las sub-hipótesis

#### 8.5.1 Regresión espacial

**Problema**: Municipios vecinos tienden a tener valores similares (dependencia espacial), violando supuesto de independencia de OLS.

**Test de autocorrelación espacial**:
- Moran's I global para cada variable del modelo
- Moran's I local (LISA) para identificar clusters espaciales de calor

**Modelos a comparar**:

| Modelo | Especificación | Cuándo usar |
|--------|---------------|-------------|
| **OLS** | `Y ~ X + controls` | Baseline |
| **Spatial Lag** | `Y ~ rWY + X + controls` | Autocorrelación en variable dependiente |
| **Spatial Error** | `Y ~ X + controls + lWe` | Autocorrelación en errores |
| **SAC** | `Y ~ rWY + X + controls + lWe` | Ambos tipos |

Donde W = matriz de pesos espaciales (vecindad queen/rook).

**Software**: R (`spdep`, `spatialreg`) o Python (`PySAL`).
**Criterio de selección**: AIC, LR test, Moran's I sobre residuos.

#### 8.5.2 Modelos mixtos con efecto aleatorio de mesorregión

**Justificación**: São Paulo tiene 15 mesorregiones con características climáticas y ecológicas distintas. El modelo mixto permite que el intercepto varíe por mesorregión, controlando heterogeneidad no observada.

```R
library(lme4)

# Modelo base para H3.1
m_h3.1 <- lmer(mort_circ_rate ~ forest_cover + heat_HAAT + idx_vuln +
               (1 | mesoregion), data = df_v9)

# Modelo con pendiente aleatoria (efecto de biodiversidad varía por región)
m_h3.1b <- lmer(mort_circ_rate ~ forest_cover + heat_HAAT + idx_vuln +
                (1 + forest_cover | mesoregion), data = df_v9)
```

**Criterio**: Si ICC > 0.10, se justifica el modelo mixto.

#### 8.5.3 Análisis por cuadrantes de gobernanza-vulnerabilidad

Evaluar cómo se distribuyen estrés térmico y fuego en los 4 cuadrantes previamente identificados:

| Cuadrante | N | Gobernanza | Vulnerabilidad | Estrategia |
|-----------|---|------------|----------------|------------|
| Q1_Modelo | 212 | Alta | Baja | Mantener y expandir |
| Q2_Conservar | 110 | Baja | Baja | Fortalecer gobernanza |
| **Q3_Vulnerable** | **210** | Baja | **Alta** | **Intervención urgente** |
| Q4_Desarrollo | 113 | Alta | Alta | Restauración ecológica |

**Análisis**:
1. ANOVA de métricas de calor y fuego por cuadrante
2. Identificación de municipios de **cuadruple riesgo**: Q3_Vulnerable + alto fuego + alto calor + alta mortalidad
3. Test de si la cadena H3.4 opera diferente en cada cuadrante (multi-group SEM)

#### 8.5.4 Análisis de sensibilidad de umbrales

| Métrica | Umbral base | Umbrales alternativos |
|---------|-------------|----------------------|
| Persistencia | 34.7°C | 33°C, 35°C, 36°C |
| HAAT | 34.7°C | 33°C, 35°C |
| MMT days | 22.3°C | 21°C, 23°C, 24°C |

Recalcular métricas en GEE con cada umbral, rehacer análisis de mediación H3.1-H3.4, y comparar magnitud y significancia de coeficientes.

**Criterio de robustez**: Si la dirección del efecto se mantiene en todos los umbrales, el hallazgo es robusto.

---

### 8.6 Resumen de análisis por sub-hipótesis

| Sub-hipótesis | Método principal | Mediadores | Moderadores | Software |
|---------------|-----------------|------------|-------------|----------|
| **H3.1** | Mediación (Baron & Kenny, bootstrap) | Estrés térmico | -- | R (`mediation`) |
| **H3.2** | Mediación serial (SEM) | Fuego, Estrés térmico | -- | R (`lavaan`) |
| **H3.3** | Mediación serial moderada | Fuego, Estrés térmico | pct_rural, pct_pobreza | R (`lavaan`, `interactions`) |
| **H3.4** | SEM completo (full path model) | Biodiversidad, Fuego, Estrés térmico | Vulnerabilidad | R (`lavaan`) |
| **Transversal** | Regresión espacial | -- | -- | R (`spdep`) / Python (`PySAL`) |
| **Transversal** | Modelos mixtos | -- | Mesorregión (aleatorio) | R (`lme4`) |
| **Transversal** | Cuadrantes | -- | -- | Python |
| **Transversal** | Sensibilidad de umbrales | -- | -- | GEE + R/Python |

### 8.7 Orden de ejecución recomendado

```
Paso 1: Correlaciones bivariadas (todas las variables)
        → Confirmar direcciones esperadas
        → Identificar colinealidades

Paso 2: H3.1 - Mediación simple
        → Establecer que biodiversidad reduce calor reduce mortalidad
        → Calcular proporción mediada

Paso 3: H3.2 - Incorporar fuego como mediador
        → Descomponer: via directa (calor) vs via fuego
        → Comparar magnitudes

Paso 4: H3.3 - Agregar moderación por vulnerabilidad
        → Identificar para quiénes el efecto es más fuerte
        → Simple slopes y Johnson-Neyman plots

Paso 5: H3.4 - Modelo completo con gobernanza
        → Descomponer efectos de gobernanza
        → Comparar UAI general vs UAI_Crisk

Paso 6: Robustez
        → Regresión espacial (Moran's I, SAR/SEM)
        → Modelos mixtos (mesorregión)
        → Sensibilidad de umbrales
        → Cuadrantes

Paso 7: Síntesis
        → Tabla comparativa de todos los modelos
        → Figuras para manuscrito
        → Recomendaciones de política
```

---

## 9. REFERENCIAS

1. Xavier, A.C., Scanlon, B.R., King, C.W., & Alves, A.I. (2022). New improved Brazilian daily weather gridded data (1961-2020). *International Journal of Climatology*, 42(16), 8390-8404. https://doi.org/10.1002/joc.7731

2. Valverde, M.C. (2023). Heat waves in São Paulo State, Brazil: Main features, heat risk factors and heat wave-health warning systems. *International Journal of Climatology*, 43(13), 5944-5963. https://doi.org/10.1002/joc.8058

3. Nascimento, W.G., Paixão, E.C.A., Morais, C.M., Alves, L.S., & Rodrigues, A.L. (2019). Ambient temperature and mortality due to acute myocardial infarction in Brazil: An ecological study of time-series analyses. *Scientific Reports*, 9, 15203. https://doi.org/10.1038/s41598-019-50235-8

4. Bell, M.L., Zanobetti, A., & Dominici, F. (2015). The impact of temperature on mortality in São Paulo, Brazil: Effects of cold and heat waves. *Epidemiology*, 26(4), e46-e47.

5. Masselot, P., Chebana, F., Bélanger, D., St-Hilaire, A., Abdous, B., Gosselin, P., & Ouarda, T.B.M.J. (2022). Trends in temperature-associated mortality in São Paulo (Brazil) between 2000 and 2018: an example of disparities in adaptation to cold and heat. *International Journal of Hygiene and Environmental Health*, 246, 114048. PMC 9727050.

6. Liu, J., Varghese, B.M., Hansen, A., Xiang, J., Zhang, Y., Dear, K., Gourley, M., Driscoll, T., Morgan, G., Capon, A., & Bi, P. (2022). Heat and cardiovascular mortality: A nationwide case-crossover analysis in Brazil. *The Lancet Planetary Health*, 6(5), e402-e411. https://doi.org/10.1016/S2542-5196(22)00073-8

7. Monteiro, F.F., Gonçalves, W.A., Andrade, L.M.B., Villavicencio, L.M.M., & Santos Silva, C.M. (2021). Assessment of Urban Heat Islands in Brazil based on MODIS remote sensing data. *Urban Climate*, 35, 100726. https://doi.org/10.1016/j.uclim.2020.100726

8. Wu, J., Cheng, G., Wang, N., Shen, H., & Ma, X. (2019). Investigating Surface Urban Heat Islands in South America based on MODIS data from 2003-2016. *Remote Sensing*, 11(10), 1212. https://doi.org/10.3390/rs11101212

9. Di Napoli, C., Hogan, R.J., & Pappenberger, F. (2021). ERA5-HEAT: A global gridded historical dataset of human thermal comfort indices from climate reanalysis. *Geoscience Data Journal*, 8(1), 2-10. https://doi.org/10.1002/gdj3.102

10. Romaszko, J., Skrzypczynska, P., Cymes, I., Draganska, E., Kuchcik, M., & Czy, W. (2022). Applicability of the Universal Thermal Climate Index (UTCI) as a prognostic tool in medical science in the context of ambient temperature-related deaths, particularly in increased mortality due to cardiovascular diseases. *Science of The Total Environment*, 842, 156906. https://doi.org/10.1016/j.scitotenv.2022.156906

11. Tsitouras, A., Michail, C., Salata, K.D., & Tseliou, A. (2025). Thermal indices for health risk assessment in urban areas: A comparative review for Brazil. *International Journal of Biometeorology*, 69(3), 421-438.

12. medRxiv (2025). Quantifying heat exposure and its related mortality burden in Rio de Janeiro City, Brazil: A multi-method approach using multiple heat metrics. *medRxiv preprint*. (En prensa)

13. Duarte, Y.S., Sentelhas, P.C., Mesquita, B.R., & Marques, J.F. (2023). CLIMBra - Climate Change Dataset for Brazil: A comprehensive daily gridded dataset for climate change impact studies. *Scientific Data*, 10, 47. https://doi.org/10.1038/s41597-023-01956-z

14. Wan, Z. (2014). New refinements and validation of the collection-6 MODIS land-surface temperature/emissivity product. *Remote Sensing of Environment*, 140, 36-45. https://doi.org/10.1016/j.rse.2013.08.027

15. Baron, R.M., & Kenny, D.A. (1986). The moderator-mediator variable distinction in social psychological research: Conceptual, strategic, and statistical considerations. *Journal of Personality and Social Psychology*, 51(6), 1173-1182.

16. Preacher, K.J., & Hayes, A.F. (2008). Asymptotic and resampling strategies for assessing and comparing indirect effects in multiple mediator models. *Behavior Research Methods*, 40(3), 879-891.

17. Anselin, L. (1988). *Spatial Econometrics: Methods and Models*. Dordrecht: Kluwer Academic Publishers.

18. IBGE - Instituto Brasileiro de Geografia e Estatística. (2022). Malha Municipal 2022. Disponible en: https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html

19. MapBiomas Brasil. (2022). Coleção 8 da Série Anual de Mapas de Cobertura e Uso da Terra do Brasil. Disponible en: https://mapbiomas.org

20. Xavier, A.C. (2022). Brazilian Daily Weather Gridded Data (BR-DWGD) - Version 3.0. GitHub repository. https://github.com/AlexandreCandidoXavier/BR-DWGD

---

## 10. NOTAS ADICIONALES

### 10.1 Sobre el asset de municipios en Google Earth Engine

**Asset recomendado**:
```javascript
projects/mapbiomas-workspace/AUXILIAR/municipios-2022
```

Este asset contiene:
- 5,570 municipios de Brasil (IBGE 2022)
- Columnas clave:
  - `cd_mun`: Código IBGE de 7 dígitos
  - `nm_mun`: Nombre del municipio
  - `sigla_uf`: Sigla del estado (use `'SP'` para filtrar)
  - `nm_uf`: Nombre del estado
  - Geometría: Polígonos municipales

**Filtrado para São Paulo**:
```javascript
var municipios = ee.FeatureCollection('projects/mapbiomas-workspace/AUXILIAR/municipios-2022')
  .filter(ee.Filter.eq('sigla_uf', 'SP'));
```

Esto retorna 645 municipios de São Paulo.

**Si el asset no es accesible**:

Opción A - Subir shapefile propio:
1. Descargar shapefile de IBGE 2022 de `data/geo/ibge_sp/`
2. En GEE Code Editor: Assets → New → Table Upload
3. Subir archivo .shp, .shx, .dbf, .prj
4. Nombrar asset: `sp_municipios_ibge2022`
5. Cambiar en scripts:
   ```javascript
   var municipios = ee.FeatureCollection('users/TU_USUARIO/sp_municipios_ibge2022');
   ```

Opción B - Usar FeatureCollection público alternativo:
```javascript
var municipios = ee.FeatureCollection('users/mapbiomas/AUXILIAR/municipios-2020')
  .filter(ee.Filter.eq('UF', 35));  // 35 = código de São Paulo
```

### 10.2 Sobre Xavier/BR-DWGD en Google Earth Engine

**Catálogo GEE Community**:
- URL: https://gee-community-catalog.org/projects/br_dwgd/
- GitHub: https://github.com/AlexandreCandidoXavier/BR-DWGD

**Assets en GEE**:
```javascript
// Temperatura máxima diaria
var tmax = ee.ImageCollection('projects/br-dwgd/assets/tmax');

// Temperatura mínima diaria
var tmin = ee.ImageCollection('projects/br-dwgd/assets/tmin');

// Otras variables disponibles:
// projects/br-dwgd/assets/pr      (precipitación)
// projects/br-dwgd/assets/rh      (humedad relativa)
// projects/br-dwgd/assets/rs      (radiación solar)
// projects/br-dwgd/assets/u2      (viento a 2m)
```

**Estructura de ImageCollection**:
- Cada imagen representa 1 día
- Bandas: Valor único (temperatura en °C)
- Resolución: 0.1° × 0.1° (aproximadamente 11 km en el ecuador)
- Sistema de coordenadas: EPSG:4326 (WGS84)
- Período: 1961-2024 (actualización continua)

**Ejemplo de verificación**:
```javascript
print('Primera imagen Tmax:', tmax.first());
print('Total de imágenes 2010-2019:',
      tmax.filterDate('2010-01-01', '2019-12-31').size());
```

Debería mostrar ~3,652 imágenes (365 días × 10 años).

**Licencia CC BY 4.0**:
- Uso libre con atribución
- Atribución requerida: "Xavier et al. (2022), BR-DWGD v3"
- Permitido: Uso académico, comercial, modificación, redistribución

### 10.3 Formato de códigos IBGE

**Estándar IBGE**: 7 dígitos
- Ejemplo: São Paulo capital = `3550308`
- Primeros 2 dígitos: Estado (35 = São Paulo)
- Siguientes 5 dígitos: Municipio

**Problemas comunes**:

1. **GEE exporta como número**: Pierde ceros a la izquierda
   - Solución en Python:
   ```python
   df['cod_ibge'] = df['cd_mun'].astype(str).str.zfill(7)
   ```

2. **Inconsistencia entre datasets**: Algunos usan 6 dígitos (sin dígito verificador)
   - Solución: Truncar a primeros 7 caracteres
   ```python
   df['cod_ibge'] = df['cod_ibge'].astype(str).str[:7]
   ```

3. **Códigos con sufijo**: Algunos datasets agregan dígitos extra
   - Solución: Usar primeros 7 caracteres como clave de merge

### 10.4 Control de calidad de datos

**Checks recomendados después de ejecutar scripts**:

1. **Integridad de municipios**:
   ```python
   assert len(df_v9) == 645, "Se perdieron municipios en el merge"
   ```

2. **Rango de valores esperados**:
   ```python
   assert df_v9['heat_persistence_mean'].max() < 100, "Persistencia fuera de rango"
   assert df_v9['lst_day_mean'].between(15, 45).all(), "LST fuera de rango físico"
   ```

3. **Porcentaje de NaN aceptable**: < 10%
   ```python
   nan_pct = df_v9[new_cols].isna().sum() / len(df_v9) * 100
   assert (nan_pct < 10).all(), f"Exceso de NaN: {nan_pct}"
   ```

4. **Coherencia lógica**:
   ```python
   # Persistencia debe ser <= MMT days (34.7°C > 22.3°C)
   assert (df_v9['heat_persistence_mean'] <= df_v9['mmt_days_mean']).all()
   ```

### 10.5 Resolución espacial efectiva

**Comparación de resoluciones**:

| Fuente | Resolución nominal | Resolución en km | Píxeles por municipio promedio |
|--------|-------------------|------------------|------------------------------|
| Xavier/BR-DWGD | 0.1° | ~11 km | 5-20 píxeles |
| MODIS LST | 1 km | 1 km | 500-2000 píxeles |
| ERA5-Land | 0.1° | ~9 km | 5-20 píxeles |
| ERA5-HEAT | 0.25° | ~28 km | 1-5 píxeles |

**Implicación**:
- Para municipios pequeños (<100 km²): Xavier y ERA5-Land pueden tener solo 1-2 píxeles
- MODIS LST ofrece mucho mejor cobertura espacial dentro de cada municipio
- Promedio municipal puede enmascarar variabilidad intra-municipal

**Recomendación**:
- Para análisis municipal agregado: Xavier/BR-DWGD es adecuado
- Para mapeo detallado de UHI: MODIS LST es superior
- Considerar ambos como complementarios, no sustitutos

### 10.6 Manejo de datos faltantes

**Causas de NaN en variables de estrés térmico**:

1. **MODIS LST**:
   - Cobertura de nubes persistente (municipios con muchos días nublados)
   - Píxeles con QC = malo (error > 2K)
   - Solución: Aceptable si <20% de NaN. Para municipios con >50% de NaN, considerar excluir LST de análisis para esos casos.

2. **Xavier/BR-DWGD**:
   - Muy pocos NaN esperados (cobertura completa de Brasil)
   - Si hay NaN: Verificar que el municipio esté dentro de los límites de SP

**Estrategias de imputación** (si es necesario):

1. **Interpolación espacial**: Usar promedio de vecinos (k-NN geográfico)
2. **Regresión múltiple**: Predecir valores faltantes con otras variables climáticas
3. **Exclusión**: Si <5% de casos tienen NaN, excluir esos casos del análisis

**No recomendado**:
- Imputación por media global (ignora estructura espacial)
- Forward/backward fill (no tiene sentido en datos cross-seccionales)

### 10.7 Próximos pasos metodológicos

Después de obtener el dataset v9, los siguientes pasos recomendados son:

1. **Análisis exploratorio de datos (EDA)**:
   - Histogramas de nuevas variables
   - Detección de outliers (valores >3 SD de la media)
   - Mapas choropleth de cada métrica

2. **Validación con literatura**:
   - Comparar valores de heat_persistence con Valverde (2023)
   - Comparar LST de São Paulo capital con Monteiro et al. (2021): esperado ~35-37°C diurno

3. **Correlaciones preliminares**:
   - Ejecutar análisis de correlación (sección 8.1)
   - Identificar municipios atípicos (alta biodiversidad + alto calor)

4. **Preparación para manuscrito**:
   - Generar Tabla 1: Estadísticas descriptivas del dataset v9
   - Generar Figura 1: Mapa de heat_HAAT por municipio
   - Generar Figura 2: Scatterplot biodiversidad vs calor con línea de regresión

5. **Análisis de mediación** (prioridad alta):
   - Implementar análisis de sección 8.2
   - Generar diagrama de mediación con coeficientes

6. **Integración con análisis de cuadrantes**:
   - Actualizar visualización de cuadrantes con nueva dimensión de calor
   - Identificar municipios prioritarios con triple vulnerabilidad

---

**Fin del documento**

---

**Información del documento**:
- Versión: 1.0
- Fecha: 26 de enero de 2026
- Autores: Science Team - Proyecto Resilient Landscapes
- Contacto: Dr. Adrian David González Chaves
- Licencia del documento: CC BY 4.0
- Repositorio GitHub: https://github.com/adgch86/saopaulo-biodiversity-health
- DOI del proyecto: 10.5281/zenodo.18303824

**Próximas actualizaciones previstas**:
- Versión 1.1: Resultados de análisis de correlación (febrero 2026)
- Versión 1.2: Resultados de análisis de mediación (febrero 2026)
- Versión 2.0: Integración con manuscrito para publicación (marzo 2026)
