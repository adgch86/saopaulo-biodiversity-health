# Guía de Descarga y Procesamiento de Datos DATASUS

## Estado Actual (2026-01-20)

**50 archivos DBC descargados** en `data/raw/datasus/`:
- Dengue (DENG): 10 archivos (2010-2019) - ~650 MB
- Leptospirose (LEPT): 10 archivos (2010-2019) - ~13 MB
- Malaria (MALA): 10 archivos (2010-2019) - ~1 MB
- Leishmaniose Visceral (LEIV): 10 archivos (2010-2019) - ~6 MB
- Leishmaniose Tegumentar (LTAN): 10 archivos (2010-2019) - ~11 MB

**Pendiente**: Procesar archivos DBC para extraer datos de São Paulo.

---

## Resumen de Enfermedades Disponibles

| Enfermedad | Código PySUS | CID-10 | Sistema | Disponibilidad |
|------------|-------------|--------|---------|----------------|
| **Dengue** | `DENG` | A90-A91 | SINAN | ✅ Disponible |
| **Leptospirose** | `LEPT` | A27 | SINAN | ✅ Disponible |
| **Malária** | `MALA` | B50-B54 | SINAN | ✅ Disponible |
| **Leishmaniose Visceral** | `LEIV` | B55.0 | SINAN | ✅ Disponible |
| **Leishmaniose Tegumentar** | `LTAN` | B55.1-B55.2 | SINAN | ✅ Disponible |
| **Diarrea Aguda (DDA)** | - | A00-A09 | SIVEP-DDA | ⚠️ Solo surtos |

---

## Opción 1: Script Python con PySUS (Recomendado)

### Instalación

```bash
# Instalar PySUS
pip install pysus

# O con conda
conda install -c conda-forge pysus
```

### Ejecución

```bash
cd "C:\Users\arlex\Documents\Adrian David"
python scripts/download_datasus_health.py
```

### Columnas del Dataset Generado

El script genera `data/processed/health_data_SP_2010_2019.csv` con:

| Columna | Descripción |
|---------|-------------|
| `cod_ibge_6` | Código IBGE del municipio (6 dígitos) |
| `year` | Año (2010-2019) |
| `cases_deng` | Casos de dengue |
| `cases_lept` | Casos de leptospirose |
| `cases_mala` | Casos de malaria |
| `cases_leiv` | Casos de leishmaniose visceral |
| `cases_ltan` | Casos de leishmaniose tegumentar |

---

## Opción 2: Descarga Manual via TabNet

### URLs Directas

1. **Dengue**: http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def
2. **Leptospirose**: http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/leptobr.def
3. **Malária**: http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/malabr.def
4. **Leishmaniose Visceral**: http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/leishvbr.def
5. **Leishmaniose Tegumentar**: http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/ltabr.def

### Pasos en TabNet

1. Ir a la URL de la enfermedad deseada
2. **Linha**: Munic Resid (para obtener por municipio)
3. **Coluna**: Ano 1º Sintoma (para obtener por año)
4. **Conteúdo**: Casos confirmados
5. **Períodos Disponíveis**: Seleccionar 2010 a 2019
6. **Seleções Disponíveis**:
   - UF de Residência: **São Paulo**
7. Clic en "Mostra" para ver los datos
8. Exportar a CSV

---

## Opción 3: Secretaria de Saúde do Estado de São Paulo

Para datos más detallados de São Paulo específicamente:

- **URL**: https://saude.sp.gov.br/cve-centro-de-vigilancia-epidemiologica-prof.-alexandre-vranjac/areas-de-vigilancia/doencas-de-transmissao-por-vetores-e-zoonoses/

### Datos disponibles:
- Dengue (casos por municipio, semana epidemiológica)
- Chikungunya
- Zika
- Leishmaniose
- Malária importada

---

## Opción 4: OpenDataSUS (API)

- **URL**: https://opendatasus.saude.gov.br/
- **Dengue Dataset**: https://opendatasus.saude.gov.br/dataset/arboviroses-dengue

### Ventajas:
- Datos abiertos en formato CSV/JSON
- API REST disponible
- Actualizaciones frecuentes

---

## Nota sobre Diarrea (DDA)

La Doença Diarreica Aguda **NO** está en el SINAN regular. Las opciones son:

### 1. SIVEP-DDA (Sistema de Vigilância)
- Solo notifica **surtos**, no casos individuales
- Datos agregados semanales por unidad de salud
- Contactar: vigilancia.dda@saude.gov.br

### 2. SIH (Sistema de Internações Hospitalares)
- Hospitalizaciones por CID A00-A09
- Disponible en: http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sih/cnv/nibr.def
- Seleccionar: Diagnóstico Principal = A00-A09

### 3. SIM (Sistema de Mortalidade)
- Óbitos por diarrea
- CID: A00-A09
- Disponible en: http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sim/cnv/obt10uf.def

---

## Códigos IBGE de Municipios de São Paulo

São Paulo tiene **645 municipios** con códigos IBGE que van de:
- 3500105 (Adamantina) a 3557105 (Votorantim)

El código de 7 dígitos se compone de:
- **35**: Código UF de São Paulo
- **XXXXX**: Código del municipio (5 dígitos)

Para conversión de 6 a 7 dígitos, el 7º dígito es un dígito verificador.

---

## Referencias

1. **PySUS Documentation**: https://pysus.readthedocs.io/
2. **Microdatasus (R)**: https://rfsaldanha.github.io/microdatasus/
3. **DATASUS Portal**: https://datasus.saude.gov.br/
4. **CVE-SP**: https://www.cve.saude.sp.gov.br/

---

*Última actualización: 2026-01-20*
*Science Team - São Paulo Biodiversity & Health Project*
