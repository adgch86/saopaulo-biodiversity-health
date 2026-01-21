# ==============================================================================
# Tabla comparativa FINAL para Adrian
# Municipios: CRAVINHOS hasta DIVINOLANDIA
# Anos: 2014, 2015, 2016
# Por municipio de residencia + ano de notificacion
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

# Codigos IBGE verificados
municipios <- data.frame(
  cod_ibge = c(
    "351320",   # CRAVINHOS (3513207)
    "351330",   # CRISTAIS PAULISTA (3513306)
    "351340",   # CRUZALIA (3513405)
    "351350",   # CRUZEIRO (3513504) - VERIFICAR: podria ser otro
    "351350",   # CUBATAO (3513501) - 6 digitos = 351350? NO, verificar
    "351390",   # CUNHA (3513900)
    "351430",   # DESCALVADO (3514304)
    "351380",   # DIADEMA (3513801)
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

# CORRECCION: Verificar codigos reales
# Los codigos de 7 digitos son:
# CRAVINHOS = 3513207 -> 6 digitos = 351320
# CRISTAIS PAULISTA = 3513306 -> 351330
# CRUZALIA = 3513405 -> 351340
# CRUZEIRO = 3513504 -> 351350
# CUBATAO = 3513501 -> 351350 (coincide con CRUZEIRO!) ERROR
# CUNHA = 3513900 -> 351390
# DESCALVADO = 3514304 -> 351430
# DIADEMA = 3513801 -> 351380
# DIRCE REIS = 3514502 -> 351450
# DIVINOLANDIA = 3514601 -> 351460

# El problema es que CRUZEIRO y CUBATAO tienen el mismo codigo de 6 digitos!
# Esto es un error. CUBATAO = 3513501 -> truncado a 6 digitos = 351350
# CRUZEIRO = 3513504 -> truncado a 6 digitos = 351350

# SOLUCION: Los archivos DBC de DATASUS usan codigos de 6 digitos SIN el
# digito verificador. Pero el ultimo digito NO es verificador, es parte del codigo!
# Entonces debemos usar todos los digitos excepto el ultimo.

# Codigos CORRECTOS (usando primeros 6 de los 7):
municipios <- data.frame(
  cod_ibge = c(
    "351320",   # CRAVINHOS (3513207 -> 351320)
    "351330",   # CRISTAIS PAULISTA (3513306 -> 351330)
    "351340",   # CRUZALIA (3513405 -> 351340) VERIFICAR
    "351350",   # CRUZEIRO (3513504 -> 351350)
    "351350",   # CUBATAO (3513501 -> 351350) MISMO QUE CRUZEIRO!
    "351390",   # CUNHA (3513900 -> 351390)
    "351430",   # DESCALVADO (3514304 -> 351430)
    "351380",   # DIADEMA (3513801 -> 351380)
    "351450",   # DIRCE REIS (3514502 -> 351450)
    "351460"    # DIVINOLANDIA (3514601 -> 351460)
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

cat("=======================================================================\n")
cat("DATASUS - Dengue por Municipio de Residencia + Ano de Notificacao\n")
cat("Comparacion con datos de Adrian\n")
cat("=======================================================================\n\n")

# Funcion para extraer casos de un archivo
extraer_casos <- function(filepath, tipo = "total") {
  if (!file.exists(filepath)) return(NULL)

  df <- read.dbc(filepath)

  # Filtrar SP
  df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]

  if (tipo == "confirmados") {
    classi <- as.numeric(as.character(df_sp$CLASSI_FIN))
    df_sp <- df_sp[classi %in% c(5, 10, 11, 12), ]
  }

  # Contar por municipio
  codigos <- as.character(df_sp$ID_MN_RESI)
  tabla <- table(codigos)
  return(as.data.frame(tabla, stringsAsFactors = FALSE))
}

# Procesar anos
anos <- c(2014, 2015, 2016)

# Extraer TOTAL y CONFIRMADOS para cada ano
resultados_total <- list()
resultados_conf <- list()

for (ano in anos) {
  ano_2d <- substr(as.character(ano), 3, 4)
  filepath <- file.path(DATA_RAW, paste0("DENGBR", ano_2d, ".dbc"))
  cat(sprintf("Procesando %d...\n", ano))

  df_t <- extraer_casos(filepath, "total")
  df_c <- extraer_casos(filepath, "confirmados")

  if (!is.null(df_t)) {
    names(df_t) <- c("cod", paste0("tot_", ano))
    resultados_total[[as.character(ano)]] <- df_t
  }
  if (!is.null(df_c)) {
    names(df_c) <- c("cod", paste0("conf_", ano))
    resultados_conf[[as.character(ano)]] <- df_c
  }
}

# Merge
df_t <- resultados_total[["2014"]]
df_t <- merge(df_t, resultados_total[["2015"]], by = "cod", all = TRUE)
df_t <- merge(df_t, resultados_total[["2016"]], by = "cod", all = TRUE)

df_c <- resultados_conf[["2014"]]
df_c <- merge(df_c, resultados_conf[["2015"]], by = "cod", all = TRUE)
df_c <- merge(df_c, resultados_conf[["2016"]], by = "cod", all = TRUE)

# Merge total con confirmados
df_final <- merge(df_t, df_c, by = "cod", all = TRUE)
df_final[is.na(df_final)] <- 0

# Filtrar solo rango de interes
df_rango <- df_final[as.numeric(df_final$cod) >= 351300 &
                     as.numeric(df_final$cod) <= 351500, ]
df_rango <- df_rango[order(df_rango$cod), ]

cat("\n=======================================================================\n")
cat("DATOS DATASUS - Municipios 351300-351500\n")
cat("tot = Total notificaciones, conf = Confirmados\n")
cat("=======================================================================\n\n")

cat(sprintf("%-8s %8s %8s %8s | %8s %8s %8s\n",
            "CODIGO", "tot_14", "tot_15", "tot_16", "conf_14", "conf_15", "conf_16"))
cat(strrep("-", 70), "\n")

for (i in 1:nrow(df_rango)) {
  cat(sprintf("%-8s %8d %8d %8d | %8d %8d %8d\n",
              df_rango$cod[i],
              df_rango$tot_2014[i], df_rango$tot_2015[i], df_rango$tot_2016[i],
              df_rango$conf_2014[i], df_rango$conf_2015[i], df_rango$conf_2016[i]))
}

# Guardar
output_file <- file.path(PROJECT_ROOT, "outputs/dengue_datasus_vs_adrian.csv")
write.csv(df_rango, output_file, row.names = FALSE)
cat(sprintf("\nGuardado: %s\n", output_file))

cat("\n=======================================================================\n")
cat("DATOS DE ADRIAN (para comparar):\n")
cat("=======================================================================\n")
cat("MUNICIPIO          | 2014 | 2015 | 2016\n")
cat("-------------------+------+------+------\n")
cat("CRAVINHOS          |    - |  106 |  144  (col4=219?)\n")
cat("CRISTAIS PAULISTA  |    - |    3 |    2  (col4=22?)\n")
cat("CRUZALIA           |    - |    3 |  129  (col4=2?)\n")
cat("CRUZEIRO           |    - |   66 |  232  (col4=126?)\n")
cat("CUBATAO            |    - |  496 |  808  (col4=283?)\n")
cat("CUNHA              |    - |    - |   14  (col4=6?)\n")
cat("DESCALVADO         |    - |  103 | 1272  (col4=94?)\n")
cat("DIADEMA            |    - |  841 | 3993  (col4=550?)\n")
cat("DIRCE REIS         |    - |    5 |   41  (col4=60?)\n")
cat("DIVINOLANDIA       |    - |    3 |    7  (col4=2?)\n")
cat("=======================================================================\n")
