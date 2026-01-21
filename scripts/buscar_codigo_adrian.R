# ==============================================================================
# Buscar codigos que coincidan con los valores de Adrian
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Buscando codigos que coincidan con valores de Adrian\n")
cat("=======================================================================\n\n")

# Valores de Adrian para 2015 (columna 2 segun imagen)
valores_adrian <- c(
  CRAVINHOS = 106,
  CRISTAIS_PAULISTA = 3,
  CRUZALIA = 3,
  CRUZEIRO = 66,
  CUBATAO = 496,
  CUNHA = 0,
  DESCALVADO = 103,
  DIADEMA = 841,
  DIRCE_REIS = 5,
  DIVINOLANDIA = 3
)

# Leer archivo 2014 (que seria columna 2 de Adrian)
filepath <- file.path(DATA_RAW, "DENGBR14.dbc")
df <- read.dbc(filepath)

# Filtrar SP
df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]

# Contar por codigo
codigos <- as.character(df_sp$ID_MN_RESI)
tabla <- as.data.frame(table(codigos), stringsAsFactors = FALSE)
names(tabla) <- c("cod", "casos")

cat("Buscando codigos con valores de Adrian en 2014:\n\n")

for (nombre in names(valores_adrian)) {
  v <- valores_adrian[nombre]
  if (v > 0) {
    # Buscar codigos con ese valor exacto
    matches <- tabla[tabla$casos == v, ]
    if (nrow(matches) > 0) {
      cat(sprintf("%s (%d casos): ", nombre, v))
      cat(paste(matches$cod, collapse = ", "), "\n")
    } else {
      # Buscar +/- 10%
      matches <- tabla[abs(tabla$casos - v) <= v * 0.1, ]
      if (nrow(matches) > 0) {
        cat(sprintf("%s (~%d casos +/-10%%): ", nombre, v))
        for (j in 1:nrow(matches)) {
          cat(sprintf("%s(%d) ", matches$cod[j], matches$casos[j]))
        }
        cat("\n")
      }
    }
  }
}

# Buscar DIADEMA especificamente (841 casos en 2014 segun Adrian)
cat("\n\nBuscando DIADEMA (841 casos en 2014):\n")
matches <- tabla[tabla$casos >= 800 & tabla$casos <= 900, ]
print(matches)

# Buscar CUBATAO (496 casos)
cat("\nBuscando CUBATAO (496 casos en 2014):\n")
matches <- tabla[tabla$casos >= 480 & tabla$casos <= 510, ]
print(matches)

cat("\n=======================================================================\n")
