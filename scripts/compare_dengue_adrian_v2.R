# ==============================================================================
# Script para comparar datos de Dengue con la tabla de Adrian
# Municipios: CRAVINHOS hasta DIVINOLANDIA
# Anos: 2014, 2015, 2016
# Criterio: Municipio de residencia + Ano de notificacion
# Usando codigos IBGE
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)
library(tidyverse)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

# Codigos IBGE de los municipios (6 digitos sin digito verificador)
# Fuente: https://www.ibge.gov.br/explica/codigos-dos-municipios.php
municipios <- tibble(
  cod_ibge_6 = c(
    "351300",  # CRAVINHOS
    "351330",  # CRISTAIS PAULISTA
    "351350",  # CRUZALIA
    "351360",  # CRUZEIRO
    "351380",  # CUBATAO
    "351390",  # CUNHA
    "351430",  # DESCALVADO
    "351380",  # DIADEMA - este codigo esta mal, buscar el correcto
    "351450",  # DIRCE REIS
    "351460"   # DIVINOLANDIA
  ),
  nome = c(
    "CRAVINHOS",
    "CRISTAIS PAULISTA",
    "CRUZALIA",
    "CRUZEIRO",
    "CUBATAO",
    "CUNHA",
    "DESCALVADO",
    "DIADEMA",
    "DIRCE REIS",
    "DIVINOLANDIA"
  )
)

# Corregir codigo de DIADEMA (buscar el correcto)
# Diadema es codigo 3513801 (7 digitos) = 351380 (6 digitos)
# Pero CUBATAO tambien es 3513801? No, revisar...
# CUBATAO = 3513504 -> 351350? No...
# Vamos a verificar los codigos correctos

# Codigos IBGE CORRECTOS (de la lista oficial):
municipios <- tibble(
  cod_ibge_6 = c(
    "351300",  # CRAVINHOS - 3513009
    "351330",  # CRISTAIS PAULISTA - 3513306
    "351350",  # CRUZALIA - 3513504
    "351360",  # CRUZEIRO - 3513603
    "351380",  # CUBATAO - 3513801
    "351390",  # CUNHA - 3513900
    "351430",  # DESCALVADO - 3514304
    "351380",  # DIADEMA - 3513801 DUPLICADO! Error
    "351450",  # DIRCE REIS - 3514502
    "351460"   # DIVINOLANDIA - 3514601
  ),
  nome = c(
    "CRAVINHOS",
    "CRISTAIS PAULISTA",
    "CRUZALIA",
    "CRUZEIRO",
    "CUBATAO",
    "CUNHA",
    "DESCALVADO",
    "DIADEMA",
    "DIRCE REIS",
    "DIVINOLANDIA"
  )
)

# Parece que los codigos de 6 digitos no son suficientes
# Vamos a usar los codigos IBGE completos (7 digitos)
# y luego truncar a 6 para comparar

municipios <- tibble(
  cod_ibge_7 = c(
    "3513009",  # CRAVINHOS
    "3513306",  # CRISTAIS PAULISTA
    "3513504",  # CRUZALIA
    "3513603",  # CRUZEIRO
    "3513801",  # CUBATAO
    "3513900",  # CUNHA
    "3514304",  # DESCALVADO
    "3513801",  # DIADEMA  3513801 es CUBATAO! Corregir
    "3514502",  # DIRCE REIS
    "3514601"   # DIVINOLANDIA
  ),
  nome = c(
    "CRAVINHOS",
    "CRISTAIS PAULISTA",
    "CRUZALIA",
    "CRUZEIRO",
    "CUBATAO",
    "CUNHA",
    "DESCALVADO",
    "DIADEMA",
    "DIRCE REIS",
    "DIVINOLANDIA"
  )
)

# Codigo correcto de DIADEMA es 3513504? No...
# Buscar en el archivo los codigos exactos

cat("=======================================================================\n")
cat("Comparacion de datos Dengue DATASUS vs Adrian\n")
cat("Buscando por codigo IBGE de municipio de residencia\n")
cat("=======================================================================\n\n")

# Primero, vamos a leer un archivo y mostrar algunos codigos para verificar
filepath_14 <- file.path(DATA_RAW, "DENGBR14.dbc")
df14 <- read.dbc(filepath_14)

cat("Columnas disponibles:\n")
cat(paste(names(df14), collapse = ", "), "\n\n")

# Filtrar SP
df14_sp <- df14 %>%
  filter(substr(as.character(ID_MN_RESI), 1, 2) == "35")

cat(sprintf("Total registros SP 2014: %d\n\n", nrow(df14_sp)))

# Mostrar valores unicos de ID_MN_RESI ordenados
cat("Primeros 50 codigos de municipio (6 digitos) de SP:\n")
codigos_sp <- df14_sp %>%
  mutate(cod_6 = substr(as.character(ID_MN_RESI), 1, 6)) %>%
  distinct(cod_6) %>%
  arrange(cod_6) %>%
  head(50)
print(codigos_sp)

# Buscar los que empiezan con 3513 o 3514 (municipios de interes)
cat("\n\nCodigos que empiezan con 3513 o 3514:\n")
codigos_interes <- df14_sp %>%
  mutate(cod_6 = substr(as.character(ID_MN_RESI), 1, 6)) %>%
  filter(substr(cod_6, 1, 4) %in% c("3513", "3514")) %>%
  distinct(cod_6) %>%
  arrange(cod_6)
print(codigos_interes, n=100)

# Contar casos por municipio para los codigos de interes
cat("\n\nCasos 2014 para municipios 3513xx y 3514xx:\n")
casos_14 <- df14_sp %>%
  mutate(cod_6 = substr(as.character(ID_MN_RESI), 1, 6)) %>%
  filter(substr(cod_6, 1, 4) %in% c("3513", "3514")) %>%
  group_by(cod_6) %>%
  summarise(casos_2014 = n(), .groups = "drop") %>%
  arrange(cod_6)
print(casos_14, n=100)
