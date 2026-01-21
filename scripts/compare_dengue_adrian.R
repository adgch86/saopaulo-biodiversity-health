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

# Municipios a buscar (nombres en mayusculas sin acentos)
municipios_buscar <- c(
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

# Anos a procesar
anos <- c(2014, 2015, 2016)

cat("=======================================================================\n")
cat("Comparacion de datos Dengue DATASUS vs Adrian\n")
cat("Municipio de residencia + Ano de notificacion\n")
cat("=======================================================================\n\n")

# Funcion para normalizar nombres de municipio
normalizar_nome <- function(nome) {
  nome <- toupper(nome)
  nome <- iconv(nome, to = "ASCII//TRANSLIT")
  nome <- trimws(nome)
  return(nome)
}

# Procesar cada ano
resultados <- list()

for (ano in anos) {
  ano_2d <- substr(as.character(ano), 3, 4)
  filepath <- file.path(DATA_RAW, paste0("DENGBR", ano_2d, ".dbc"))

  cat(sprintf("Procesando ano %d (%s)\n", ano, basename(filepath)))

  if (file.exists(filepath)) {
    df <- read.dbc(filepath)
    cat(sprintf("  Total registros Brasil: %d\n", nrow(df)))

    # Mostrar columnas disponibles
    # cat("  Columnas:", paste(names(df), collapse=", "), "\n")

    # Buscar columna de municipio de residencia
    if ("ID_MN_RESI" %in% names(df)) {
      mun_col <- "ID_MN_RESI"
    } else if ("ID_MUNICIP" %in% names(df)) {
      mun_col <- "ID_MUNICIP"
    } else {
      cat("  ERROR: No se encontro columna de municipio\n")
      next
    }

    # Buscar columna de ano de notificacion
    if ("NU_ANO" %in% names(df)) {
      ano_col <- "NU_ANO"
    } else if ("ANO_NOTIF" %in% names(df)) {
      ano_col <- "ANO_NOTIF"
    } else if ("DT_NOTIFIC" %in% names(df)) {
      ano_col <- "DT_NOTIFIC"
    } else {
      cat("  ERROR: No se encontro columna de ano\n")
      next
    }

    cat(sprintf("  Usando columnas: %s (municipio), %s (ano)\n", mun_col, ano_col))

    # Filtrar solo Sao Paulo (codigo empieza con 35)
    df_sp <- df %>%
      filter(substr(as.character(.data[[mun_col]]), 1, 2) == "35")

    cat(sprintf("  Registros Sao Paulo: %d\n", nrow(df_sp)))

    # Buscar columna de nombre del municipio
    nome_cols <- c("NM_MUNICIP", "NM_MN_RESI", "MUNIC_RES")
    nome_col <- NULL
    for (col in nome_cols) {
      if (col %in% names(df_sp)) {
        nome_col <- col
        break
      }
    }

    if (!is.null(nome_col)) {
      # Agregar por nombre de municipio
      df_agg <- df_sp %>%
        mutate(nome_mun = normalizar_nome(as.character(.data[[nome_col]]))) %>%
        filter(nome_mun %in% municipios_buscar) %>%
        group_by(nome_mun) %>%
        summarise(casos = n(), .groups = "drop") %>%
        mutate(ano = ano)

      resultados[[as.character(ano)]] <- df_agg

    } else {
      # No hay columna de nombre, usar codigos IBGE
      cat("  No hay columna de nombre, intentando cargar catalogo IBGE...\n")

      # Cargar catalogo de municipios de SP
      # Codigos IBGE para los municipios buscados (7 digitos)
      codigos_ibge <- c(
        "3513009" = "CRAVINHOS",
        "3513306" = "CRISTAIS PAULISTA",
        "3513504" = "CRUZALIA",
        "3513603" = "CRUZEIRO",
        "3513801" = "CUBATAO",
        "3513900" = "CUNHA",
        "3514304" = "DESCALVADO",
        "3513801" = "DIADEMA",  # Corregir codigo
        "3514502" = "DIRCE REIS",
        "3514601" = "DIVINOLANDIA"
      )

      # Por ahora, mostrar conteo total de SP
      cat("  Sin columna de nombre disponible en este archivo\n")
    }

  } else {
    cat(sprintf("  ERROR: Archivo no encontrado: %s\n", filepath))
  }
  cat("\n")
}

# Mostrar resultados
if (length(resultados) > 0) {
  df_final <- bind_rows(resultados)

  # Pivotar a formato ancho
  df_wide <- df_final %>%
    pivot_wider(
      names_from = ano,
      values_from = casos,
      names_prefix = "Y"
    ) %>%
    arrange(nome_mun)

  cat("\n=======================================================================\n")
  cat("RESULTADOS - Casos de Dengue por municipio de residencia\n")
  cat("=======================================================================\n\n")

  print(df_wide, n = 20)

  # Guardar CSV
  output_file <- file.path(PROJECT_ROOT, "outputs/comparacion_dengue_adrian.csv")
  write.csv(df_wide, output_file, row.names = FALSE)
  cat(sprintf("\nGuardado en: %s\n", output_file))
}

cat("\n=======================================================================\n")
cat("Proceso completado\n")
cat("=======================================================================\n")
