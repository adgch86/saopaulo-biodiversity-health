# ==============================================================================
# Script para procesar archivos DBC de DATASUS
# ==============================================================================
#
# Este script lee los archivos DBC descargados del FTP de DATASUS,
# filtra los datos de Sao Paulo y genera un dataset consolidado.
#
# Requisitos:
#   install.packages("microdatasus")
#   install.packages("tidyverse")
#   install.packages("data.table")
#
# Autor: Science Team
# Fecha: 2026-01-20
# ==============================================================================

# Configurar biblioteca de usuario
.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

# Cargar librerias
library(read.dbc)
library(tidyverse)
library(data.table)

# Configuracion
PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")
DATA_PROCESSED <- file.path(PROJECT_ROOT, "data/processed")

# Codigo UF de Sao Paulo
UF_SP <- "35"
YEARS <- 2010:2019

# Enfermedades a procesar
DISEASES <- list(
  DENG = "Dengue",
  LEPT = "Leptospirose",
  MALA = "Malaria",
  LEIV = "Leishmaniose_Visceral",
  LTAN = "Leishmaniose_Tegumentar"
)

# ==============================================================================
# Funcion para procesar un archivo DBC
# ==============================================================================
process_dbc_file <- function(filepath) {
  cat(sprintf("Procesando: %s\n", basename(filepath)))

  tryCatch({
    # Leer archivo DBC usando read.dbc
    df <- read.dbc(filepath)

    cat(sprintf("  Registros totales: %d\n", nrow(df)))
    # Retornar dataframe
    return(df)
  }, error = function(e) {
    cat(sprintf("  Error: %s\n", e$message))
    return(NULL)
  })
}

# ==============================================================================
# Funcion para filtrar datos de Sao Paulo
# ==============================================================================
filter_sao_paulo <- function(df) {
  # Columnas posibles para codigo de municipio
  mun_cols <- c("ID_MUNICIP", "ID_MN_RESI", "CO_MUN_RES", "MUNRESBR")

  for (col in mun_cols) {
    if (col %in% names(df)) {
      # Filtrar por codigo que empiece con 35 (Sao Paulo)
      df <- df %>%
        filter(substr(as.character(.data[[col]]), 1, 2) == UF_SP)

      cat(sprintf("  Filtrado por %s: %d registros de SP\n", col, nrow(df)))
      return(df)
    }
  }

  cat("  AVISO: No se encontro columna de municipio\n")
  return(df)
}

# ==============================================================================
# Funcion para agregar casos por municipio y ano
# ==============================================================================
aggregate_cases <- function(df, disease_code) {
  # Columnas posibles
  mun_cols <- c("ID_MUNICIP", "ID_MN_RESI", "CO_MUN_RES", "MUNRESBR")
  year_cols <- c("NU_ANO", "ANO_NOTIF", "DT_NOTIFIC")

  mun_col <- NULL
  year_col <- NULL

  # Encontrar columna de municipio
  for (col in mun_cols) {
    if (col %in% names(df)) {
      mun_col <- col
      break
    }
  }

  # Encontrar columna de ano
  for (col in year_cols) {
    if (col %in% names(df)) {
      year_col <- col
      break
    }
  }

  if (is.null(mun_col) || is.null(year_col)) {
    cat("  AVISO: No se encontraron columnas necesarias\n")
    return(NULL)
  }

  # Agregar
  result <- df %>%
    mutate(
      cod_ibge = substr(as.character(.data[[mun_col]]), 1, 6),
      year = if(year_col == "DT_NOTIFIC") {
        substr(as.character(.data[[year_col]]), 1, 4)
      } else {
        as.character(.data[[year_col]])
      }
    ) %>%
    group_by(cod_ibge, year) %>%
    summarise(cases = n(), .groups = "drop") %>%
    rename_with(~ paste0("cases_", tolower(disease_code)), cases)

  return(result)
}

# ==============================================================================
# Funcion principal
# ==============================================================================
main <- function() {
  cat(strrep("=", 70), "\n")
  cat("Procesador de archivos DBC de DATASUS\n")
  cat("Science Team - Sao Paulo Biodiversity & Health Project\n")
  cat(strrep("=", 70), "\n\n")

  all_data <- list()

  for (disease_code in names(DISEASES)) {
    cat(sprintf("\n--- Procesando %s (%s) ---\n",
                DISEASES[[disease_code]], disease_code))

    disease_data <- list()

    for (year in YEARS) {
      year_2d <- substr(as.character(year), 3, 4)
      filename <- sprintf("%sBR%s.dbc", disease_code, year_2d)
      filepath <- file.path(DATA_RAW, filename)

      if (file.exists(filepath)) {
        df <- process_dbc_file(filepath)

        if (!is.null(df) && nrow(df) > 0) {
          # Filtrar Sao Paulo
          df_sp <- filter_sao_paulo(df)

          if (nrow(df_sp) > 0) {
            # Agregar por municipio
            df_agg <- aggregate_cases(df_sp, disease_code)

            if (!is.null(df_agg)) {
              disease_data[[as.character(year)]] <- df_agg
            }
          }
        }
      } else {
        cat(sprintf("  Archivo no encontrado: %s\n", filename))
      }
    }

    if (length(disease_data) > 0) {
      all_data[[disease_code]] <- bind_rows(disease_data)
    }
  }

  # Consolidar todos los datos
  cat("\n--- Consolidando datos ---\n")

  if (length(all_data) > 0) {
    # Crear base con todos los municipios de SP y anos
    all_munis <- unique(unlist(lapply(all_data, function(x) x$cod_ibge)))

    base <- expand.grid(
      cod_ibge = all_munis,
      year = as.character(YEARS),
      stringsAsFactors = FALSE
    )

    # Merge con cada enfermedad
    for (disease_code in names(all_data)) {
      base <- left_join(base, all_data[[disease_code]],
                       by = c("cod_ibge", "year"))
    }

    # Reemplazar NA con 0
    case_cols <- grep("^cases_", names(base), value = TRUE)
    base[case_cols][is.na(base[case_cols])] <- 0

    # Guardar
    output_file <- file.path(DATA_PROCESSED, "health_data_SP_2010_2019.csv")
    write.csv(base, output_file, row.names = FALSE)

    cat(sprintf("\nDataset guardado: %s\n", output_file))
    cat(sprintf("Municipios: %d\n", length(unique(base$cod_ibge))))
    cat(sprintf("Anos: %d\n", length(unique(base$year))))
    cat(sprintf("Total registros: %d\n", nrow(base)))

    cat("\nCasos por enfermedad:\n")
    for (col in case_cols) {
      cat(sprintf("  %s: %d\n", col, sum(base[[col]])))
    }
  } else {
    cat("No se procesaron datos\n")
  }

  cat("\n", strrep("=", 70), "\n")
  cat("Proceso completado\n")
}

# Ejecutar
main()
