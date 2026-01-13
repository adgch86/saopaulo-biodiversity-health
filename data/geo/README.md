# Datos Geograficos

## Shapefiles NO incluidos en Git

| Archivo | Tamano | Descripcion |
|---------|--------|-------------|
| praArlex.shp | 8.8 MB | Geometria de municipios de Sao Paulo |
| praArlex.dbf | 117 KB | Atributos |
| praArlex.shx | 1.6 KB | Indice espacial |
| praArlex.prj | 151 B | Proyeccion (SIRGAS 2000) |

## Fuente

IBGE - Instituto Brasileiro de Geografia e Estatistica
https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html

## Proyeccion

SIRGAS 2000 (EPSG:4674)

## Uso

```python
import geopandas as gpd

# Cargar shapefile
gdf = gpd.read_file('data/geo/shapefiles/praArlex.shp')
print(gdf.crs)  # SIRGAS 2000
```
