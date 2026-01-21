# ==============================================================================
# Script para procesar archivos DBC de DATASUS - CASOS PROVÁVEIS
# ==============================================================================
#
# Este script aplica el filtro de TABNET para obtener "Casos Prováveis":
# - Excluye casos descartados (CLASSI_FIN según el año)
#
# Criterios de CLASSI_FIN por período:
# - 2007-2013: CLASSI_FIN = 1 es "Confirmado", excluir != 1
# - 2014+: CLASSI_FIN = 5 es "Descartado", excluir = 5
#
# Autor: Science Team
# Fecha: 2026-01-20
# ==============================================================================

# Configurar biblioteca de usuario
.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

# Cargar librerias
library(read.dbc)
library(dplyr)

# Configuracion
PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")
DATA_PROCESSED <- file.path(PROJECT_ROOT, "data/processed")

# Codigo UF de Sao Paulo
UF_SP <- "35"

# ==============================================================================
# Funcion para filtrar casos provaveis (excluir descartados)
# ==============================================================================
filter_casos_provaveis <- function(df, year) {
  # Verificar si existe CLASSI_FIN
  if (!"CLASSI_FIN" %in% names(df)) {
    cat("  AVISO: No existe columna CLASSI_FIN, retornando todos los casos\n")
    return(df)
  }

  # Mostrar distribucion de CLASSI_FIN
  cat("  Distribucion CLASSI_FIN:\n")
  print(table(df$CLASSI_FIN, useNA = "ifany"))

  n_total <- nrow(df)

  if (year < 2014) {
    # Antes de 2014: CLASSI_FIN = 5 era descartado
    # Casos provaveis = todos excepto CLASSI_FIN = 5
    df_filtered <- df[df$CLASSI_FIN != 5 | is.na(df$CLASSI_FIN), ]
    cat(sprintf("  Filtro (año < 2014): excluir CLASSI_FIN = 5\n"))
  } else {
    # 2014+: CLASSI_FIN = 5 es descartado
    # Casos provaveis = todos excepto CLASSI_FIN = 5
    df_filtered <- df[df$CLASSI_FIN != 5 | is.na(df$CLASSI_FIN), ]
    cat(sprintf("  Filtro (año >= 2014): excluir CLASSI_FIN = 5\n"))
  }

  n_filtered <- nrow(df_filtered)
  n_excluded <- n_total - n_filtered

  cat(sprintf("  Total: %d -> Casos provaveis: %d (excluidos: %d)\n",
              n_total, n_filtered, n_excluded))

  return(df_filtered)
}

# ==============================================================================
# Funcion para procesar dengue por año
# ==============================================================================
process_dengue_year <- function(year) {
  filename <- sprintf("DENGBR%02d.dbc", year %% 100)
  filepath <- file.path(DATA_RAW, filename)

  if (!file.exists(filepath)) {
    cat(sprintf("Archivo no encontrado: %s\n", filename))
    return(NULL)
  }

  cat(sprintf("\n=== Procesando %s (año %d) ===\n", filename, year))

  tryCatch({
    # Leer archivo DBC
    df <- read.dbc(filepath)
    cat(sprintf("  Registros totales Brasil: %d\n", nrow(df)))

    # Mostrar columnas disponibles
    cat("  Columnas:", paste(head(names(df), 10), collapse=", "), "...\n")

    # Filtrar Sao Paulo
    mun_col <- if ("ID_MN_RESI" %in% names(df)) "ID_MN_RESI" else "ID_MUNICIP"
    df_sp <- df[substr(as.character(df[[mun_col]]), 1, 2) == UF_SP, ]
    cat(sprintf("  Registros Sao Paulo: %d\n", nrow(df_sp)))

    # Aplicar filtro de casos provaveis
    df_provaveis <- filter_casos_provaveis(df_sp, year)

    # Agregar por municipio
    result <- df_provaveis %>%
      mutate(cod_ibge = substr(as.character(.data[[mun_col]]), 1, 6)) %>%
      group_by(cod_ibge) %>%
      summarise(cases = n(), .groups = "drop") %>%
      mutate(year = year)

    return(result)

  }, error = function(e) {
    cat(sprintf("  Error: %s\n", e$message))
    return(NULL)
  })
}

# ==============================================================================
# MAIN
# ==============================================================================
cat(strrep("=", 70), "\n")
cat("Procesador de CASOS PROVÁVEIS - DATASUS\n")
cat("Filtro: Excluye casos descartados (como TABNET)\n")
cat(strrep("=", 70), "\n")

# Procesar años 2010-2019
all_data <- list()

for (year in 2010:2019) {
  result <- process_dengue_year(year)
  if (!is.null(result)) {
    all_data[[as.character(year)]] <- result
  }
}

# Combinar todos los años
if (length(all_data) > 0) {
  df_final <- bind_rows(all_data)

  # Pivot a formato ancho
  df_wide <- df_final %>%
    tidyr::pivot_wider(
      names_from = year,
      values_from = cases,
      names_prefix = "deng_",
      values_fill = 0
    )

  # Guardar
  output_file <- file.path(DATA_PROCESSED, "dengue_casos_provaveis_SP_2010_2019.csv")
  write.csv(df_wide, output_file, row.names = FALSE)
  cat(sprintf("\n\nArchivo guardado: %s\n", output_file))
  cat(sprintf("Municipios: %d\n", nrow(df_wide)))

  # Mostrar totales por año
  cat("\nTotales estatales (Casos Prováveis):\n")
  for (year in 2010:2019) {
    col <- paste0("deng_", year)
    if (col %in% names(df_wide)) {
      cat(sprintf("  %d: %s casos\n", year, format(sum(df_wide[[col]]), big.mark=",")))
    }
  }
} else {
  cat("No se procesaron datos\n")
}

cat("\nProcesamiento completado.\n")
