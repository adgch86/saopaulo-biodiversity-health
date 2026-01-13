# Datos Crudos

## Archivos NO incluidos en Git

Por razones de tamano, los siguientes archivos no estan en el repositorio:

| Archivo | Tamano | Registros | Descripcion |
|---------|--------|-----------|-------------|
| 645_sin_salud.csv | 55 MB | 645 | Municipios con datos ambientales |
| 187_con_salud.csv | 19 MB | 187 | Municipios con datos epidemiologicos |

## Como obtener los datos

### Opcion A: Contactar al autor
Solicitar los archivos directamente al autor del proyecto.

### Opcion B: Descargar de fuentes originales

1. **AdaptaBrasil MCTI** (UAI, riesgos climaticos)
   - https://adaptabrasil.mcti.gov.br/
   - Sistema de Informacoes e Analises sobre Impactos das Mudancas Climaticas

2. **DATASUS** (datos epidemiologicos)
   - http://tabnet.datasus.gov.br/
   - Morbidade Hospitalar do SUS

3. **IBGE** (datos demograficos)
   - https://www.ibge.gov.br/
   - Censo Demografico

## Estructura esperada

Despues de obtener los datos, colocarlos en esta carpeta:

```
data/raw/
├── 645_sin_salud.csv
├── 187_con_salud.csv
└── README.md (este archivo)
```

## Descripcion de Variables

Ver `docs/metadata.xlsx` para definiciones completas de todas las variables.
