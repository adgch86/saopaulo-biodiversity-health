# ==============================================================================
# Script para comparar datos de Dengue con la tabla de Adrian
# Municipios: CRAVINHOS hasta DIVINOLANDIA
# Anos: 2014, 2015, 2016
# Criterio: Municipio de residencia + Ano de notificacion
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)
library(tidyverse)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Comparacion de datos Dengue DATASUS vs Adrian\n")
cat("=======================================================================\n\n")

# Leer archivo 2014 para explorar estructura
filepath_14 <- file.path(DATA_RAW, "DENGBR14.dbc")
df14 <- read.dbc(filepath_14)

# Filtrar SP
df14_sp <- df14 %>%
  filter(substr(as.character(ID_MN_RESI), 1, 2) == "35")

cat(sprintf("Total registros SP 2014: %d\n", nrow(df14_sp)))

# Mostrar todos los codigos unicos ordenados
cat("\nTodos los codigos de municipio de SP (primeros 100):\n")
codigos_sp <- df14_sp %>%
  mutate(cod = as.character(ID_MN_RESI)) %>%
  count(cod, name = "casos") %>%
  arrange(cod) %>%
  head(100)
print(codigos_sp, n = 100)

# Mostrar rango de codigos
cat("\n\nRango de codigos:\n")
cat("Min:", min(as.numeric(as.character(df14_sp$ID_MN_RESI)), na.rm = TRUE), "\n")
cat("Max:", max(as.numeric(as.character(df14_sp$ID_MN_RESI)), na.rm = TRUE), "\n")

# Buscar codigos especificos basados en la secuencia alfabetica
# CRAVINHOS, CRISTAIS PAULISTA, CRUZALIA, CRUZEIRO, CUBATAO, CUNHA
# DESCALVADO, DIADEMA, DIRCE REIS, DIVINOLANDIA

# Codigos IBGE de SP son 35XXXX donde XXXX es el codigo del municipio
# Segun el orden alfabetico, estos municipios deberian tener codigos consecutivos

# Buscar en el rango 3513xx-3514xx
cat("\n\nBuscando codigos en rango 351300-351500:\n")
codigos_rango <- df14_sp %>%
  mutate(cod = as.numeric(as.character(ID_MN_RESI))) %>%
  filter(cod >= 351300 & cod <= 351500) %>%
  count(cod = as.character(cod), name = "casos_2014") %>%
  arrange(cod)
print(codigos_rango, n = 50)
