# ==============================================================================
# Script para comparar datos de Dengue - SOLO CASOS CONFIRMADOS
# Municipios: CRAVINHOS hasta DIVINOLANDIA
# Anos: 2014, 2015, 2016
# Criterio: Municipio de residencia + Ano de notificacion + Confirmados
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("DATASUS - Dengue CONFIRMADOS por Municipio Residencia + Ano Notificacao\n")
cat("Anos: 2014, 2015, 2016\n")
cat("Filtro: CLASSI_FIN = 10, 11, 12 (Dengue confirmado)\n")
cat("=======================================================================\n\n")

# Funcion para extraer casos CONFIRMADOS por municipio
extraer_casos_confirmados <- function(filepath) {
  if (!file.exists(filepath)) {
    return(NULL)
  }

  df <- read.dbc(filepath)

  # Filtrar SP (codigo empieza con 35)
  df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]

  # Filtrar solo casos CONFIRMADOS
  # CLASSI_FIN: 10=Dengue, 11=Dengue com sinais de alarme, 12=Dengue grave
  # O puede ser 5=Confirmado en versiones antiguas
  if ("CLASSI_FIN" %in% names(df_sp)) {
    classi <- as.numeric(as.character(df_sp$CLASSI_FIN))
    # Valores de confirmado: 10, 11, 12 (nuevo) o 5 (antiguo)
    df_conf <- df_sp[classi %in% c(5, 10, 11, 12), ]
    cat(sprintf("  Confirmados SP: %d de %d\n", nrow(df_conf), nrow(df_sp)))
  } else {
    cat("  AVISO: No hay columna CLASSI_FIN\n")
    df_conf <- df_sp
  }

  # Contar casos por codigo de municipio
  codigos <- as.character(df_conf$ID_MN_RESI)
  tabla <- table(codigos)

  return(as.data.frame(tabla, stringsAsFactors = FALSE))
}

# Procesar los 3 anos
anos <- c(2014, 2015, 2016)
resultados <- list()

for (ano in anos) {
  ano_2d <- substr(as.character(ano), 3, 4)
  filepath <- file.path(DATA_RAW, paste0("DENGBR", ano_2d, ".dbc"))

  cat(sprintf("Procesando %d...\n", ano))

  df_casos <- extraer_casos_confirmados(filepath)
  if (!is.null(df_casos)) {
    names(df_casos) <- c("cod_ibge", paste0("Y", ano))
    resultados[[as.character(ano)]] <- df_casos
  }
}

# Merge de los 3 anos
cat("\nConsolidando datos...\n")

df_final <- resultados[["2014"]]
df_final <- merge(df_final, resultados[["2015"]], by = "cod_ibge", all = TRUE)
df_final <- merge(df_final, resultados[["2016"]], by = "cod_ibge", all = TRUE)

# Reemplazar NA con 0
df_final[is.na(df_final)] <- 0

# Filtrar solo el rango de municipios de interes (351300 - 351500)
df_rango <- df_final[as.numeric(df_final$cod_ibge) >= 351300 &
                     as.numeric(df_final$cod_ibge) <= 351500, ]
df_rango <- df_rango[order(df_rango$cod_ibge), ]

cat("\n=======================================================================\n")
cat("RESULTADOS: Casos CONFIRMADOS - Municipios 351300-351500\n")
cat("=======================================================================\n\n")

cat(sprintf("%-10s %10s %10s %10s\n", "COD_IBGE", "2014", "2015", "2016"))
cat(strrep("-", 45), "\n")

for (i in 1:nrow(df_rango)) {
  cat(sprintf("%-10s %10d %10d %10d\n",
              df_rango$cod_ibge[i],
              df_rango$Y2014[i],
              df_rango$Y2015[i],
              df_rango$Y2016[i]))
}

# Guardar
output_file <- file.path(PROJECT_ROOT, "outputs/dengue/dengue_confirmados_2014_2016.csv")
write.csv(df_rango, output_file, row.names = FALSE)
cat(sprintf("\nGuardado en: %s\n", output_file))

cat("\n=======================================================================\n")
cat("TABLA DE ADRIAN (para comparar):\n")
cat("CRAVINHOS:        -   106   144   (buscar 219 en 2016 en tu version)\n")
cat("CRISTAIS PAULISTA: -    3     2\n")
cat("CRUZALIA:          -    3   129\n")
cat("CRUZEIRO:          -   66   232\n")
cat("CUBATAO:           -  496   808\n")
cat("CUNHA:             -    -    14\n")
cat("DESCALVADO:        -  103 1.272\n")
cat("DIADEMA:           -  841 3.993\n")
cat("DIRCE REIS:        -    5    41\n")
cat("DIVINOLANDIA:      -    3     7\n")
cat("=======================================================================\n")
