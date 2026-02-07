# ==============================================================================
# Probar filtro TABNET: excluir descartados (1), inconclusivos (8) y NA
# Municipios CRAVINHOS-DIVINOLANDIA, Anos 2014-2016
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("DATASUS - Filtro estilo TABNET (excluir descartados/inconclusivos)\n")
cat("Anos: 2014, 2015, 2016\n")
cat("=======================================================================\n\n")

# Funcion: excluir CLASSI_FIN = 1 (descartado), 8 (inconclusivo) y NA
extraer_confirmados_tabnet <- function(filepath) {
  if (!file.exists(filepath)) return(NULL)

  df <- read.dbc(filepath)
  df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]

  classi <- as.numeric(as.character(df_sp$CLASSI_FIN))
  # Excluir: 1 (descartado), 8 (inconclusivo), NA
  df_filt <- df_sp[!classi %in% c(1, 8) & !is.na(classi), ]

  codigos <- as.character(df_filt$ID_MN_RESI)
  tabla <- table(codigos)
  return(as.data.frame(tabla, stringsAsFactors = FALSE))
}

anos <- c(2014, 2015, 2016)
resultados <- list()

for (ano in anos) {
  ano_2d <- substr(as.character(ano), 3, 4)
  filepath <- file.path(DATA_RAW, paste0("DENGBR", ano_2d, ".dbc"))
  cat(sprintf("Procesando %d...\n", ano))

  df_casos <- extraer_confirmados_tabnet(filepath)
  if (!is.null(df_casos)) {
    names(df_casos) <- c("cod", paste0("Y", ano))
    resultados[[as.character(ano)]] <- df_casos
  }
}

df_final <- resultados[["2014"]]
df_final <- merge(df_final, resultados[["2015"]], by = "cod", all = TRUE)
df_final <- merge(df_final, resultados[["2016"]], by = "cod", all = TRUE)
df_final[is.na(df_final)] <- 0

# Filtrar rango 351300-351500
df_rango <- df_final[as.numeric(df_final$cod) >= 351300 &
                     as.numeric(df_final$cod) <= 351500, ]
df_rango <- df_rango[order(df_rango$cod), ]

cat("\n=======================================================================\n")
cat("RESULTADOS - Confirmados (excluyendo 1, 8, NA)\n")
cat("=======================================================================\n\n")

cat(sprintf("%-10s %10s %10s %10s\n", "CODIGO", "2014", "2015", "2016"))
cat(strrep("-", 45), "\n")

for (i in 1:nrow(df_rango)) {
  cat(sprintf("%-10s %10d %10d %10d\n",
              df_rango$cod[i],
              df_rango$Y2014[i],
              df_rango$Y2015[i],
              df_rango$Y2016[i]))
}

cat("\n=======================================================================\n")
cat("DATOS DE ADRIAN (columnas 2014, 2015, 2016):\n")
cat("CRAVINHOS:         - | 106 | 144 | 219\n")
cat("DIADEMA:           - | 841 | 3993 | 550\n")
cat("=======================================================================\n")
