# ==============================================================================
# Script FINAL para comparar datos de Dengue con la tabla de Adrian
# Municipios: CRAVINHOS hasta DIVINOLANDIA
# Anos: 2014, 2015, 2016
# Criterio: Municipio de residencia (ID_MN_RESI) + Ano de notificacion (NU_ANO)
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("DATASUS - Dengue por Municipio de Residencia + Ano de Notificacao\n")
cat("Anos: 2014, 2015, 2016\n")
cat("=======================================================================\n\n")

# Codigos IBGE de 6 digitos de los municipios de interes
# Basado en la tabla oficial IBGE (ordenados alfabeticamente)
# Fuente: ftp.ibge.gov.br y verificacion cruzada con datos

# Los codigos de SP son 35XXXX donde XXXX es secuencial alfabetico
# Segun datos del IBGE:
municipios <- data.frame(
  cod_ibge = c(
    "351320",   # CRAVINHOS (3513207)
    "351330",   # CRISTAIS PAULISTA (3513306)
    "351340",   # CRUZALIA (3513405)
    "351350",   # CRUZEIRO (3513504)
    "351380",   # CUBATAO (3513801)
    "351390",   # CUNHA (3513900)
    "351430",   # DESCALVADO (3514304)
    "351380",   # DIADEMA - PENDIENTE VERIFICAR
    "351450",   # DIRCE REIS (3514502)
    "351460"    # DIVINOLANDIA (3514601)
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
  ),
  stringsAsFactors = FALSE
)

# Nota: DIADEMA tiene codigo 3513801 pero CUBATAO tambien?
# Esto no es correcto. Vamos a verificar buscando TODOS los codigos en el rango

# Funcion para extraer casos por municipio de un archivo DBC
extraer_casos <- function(filepath) {
  if (!file.exists(filepath)) {
    return(NULL)
  }

  df <- read.dbc(filepath)

  # Filtrar SP (codigo empieza con 35)
  df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]

  # Contar casos por codigo de municipio
  codigos <- as.character(df_sp$ID_MN_RESI)
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

  df_casos <- extraer_casos(filepath)
  if (!is.null(df_casos)) {
    names(df_casos) <- c("cod_ibge", paste0("Y", ano))
    resultados[[as.character(ano)]] <- df_casos
    cat(sprintf("  Total municipios SP: %d\n", nrow(df_casos)))
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
cat("RESULTADOS: Municipios en rango 351300-351500\n")
cat("Dengue - Notificaciones por municipio de residencia\n")
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

# Guardar a CSV
output_file <- file.path(PROJECT_ROOT, "outputs/dengue_comparacion_2014_2016.csv")
write.csv(df_rango, output_file, row.names = FALSE)
cat(sprintf("\nGuardado en: %s\n", output_file))

cat("\n=======================================================================\n")
cat("NOTA: Comparar estos codigos con la tabla de Adrian para identificar\n")
cat("      cual codigo corresponde a cada municipio\n")
cat("=======================================================================\n")
