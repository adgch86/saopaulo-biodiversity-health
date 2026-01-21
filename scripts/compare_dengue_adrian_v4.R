# ==============================================================================
# Script para comparar datos de Dengue con la tabla de Adrian
# Municipios: CRAVINHOS hasta DIVINOLANDIA
# Anos: 2014, 2015, 2016
# Criterio: Municipio de residencia + Ano de notificacion
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Comparacion de datos Dengue DATASUS vs Adrian\n")
cat("=======================================================================\n\n")

# Codigos IBGE oficiales de los municipios de interes
# Segun IBGE: https://www.ibge.gov.br/cidades-e-estados
# Los codigos son de 7 digitos, pero en DATASUS usan 6 (sin digito verificador)

# Codigos de 6 digitos (IBGE sin digito verificador):
codigos_interes <- c(
  "351300",  # CRAVINHOS
  "351330",  # CRISTAIS PAULISTA
  "351350",  # CRUZALIA
  "351360",  # CRUZEIRO
  "351380",  # CUBATAO
  "351390",  # CUNHA
  "351430",  # DESCALVADO
  "351380",  # DIADEMA ??? revisar
  "351450",  # DIRCE REIS
  "351460"   # DIVINOLANDIA
)

# Leer archivo 2014
cat("Leyendo DENGBR14.dbc...\n")
filepath_14 <- file.path(DATA_RAW, "DENGBR14.dbc")
df14 <- read.dbc(filepath_14)

# Filtrar SP y ver estructura de los codigos
df14_sp <- df14[substr(as.character(df14$ID_MN_RESI), 1, 2) == "35", ]
cat(sprintf("Registros SP 2014: %d\n\n", nrow(df14_sp)))

# Contar casos por municipio
cat("Contando casos por municipio...\n")
codigos <- as.character(df14_sp$ID_MN_RESI)
tabla <- table(codigos)

# Convertir a data frame
df_tabla <- as.data.frame(tabla, stringsAsFactors = FALSE)
names(df_tabla) <- c("codigo", "casos_2014")
df_tabla <- df_tabla[order(df_tabla$codigo), ]

# Mostrar primeros 100 codigos
cat("\nPrimeros 100 municipios de SP (ordenados por codigo):\n")
cat(sprintf("%-8s %10s\n", "Codigo", "Casos"))
cat(strrep("-", 20), "\n")
for (i in 1:min(100, nrow(df_tabla))) {
  cat(sprintf("%-8s %10d\n", df_tabla$codigo[i], df_tabla$casos_2014[i]))
}

# Buscar codigos en rango 351300-351500
cat("\n\nMunicipios en rango 351300-351500:\n")
cat(sprintf("%-8s %10s\n", "Codigo", "Casos"))
cat(strrep("-", 20), "\n")
for (i in 1:nrow(df_tabla)) {
  cod_num <- as.numeric(df_tabla$codigo[i])
  if (!is.na(cod_num) && cod_num >= 351300 && cod_num <= 351500) {
    cat(sprintf("%-8s %10d\n", df_tabla$codigo[i], df_tabla$casos_2014[i]))
  }
}

cat("\n=======================================================================\n")
