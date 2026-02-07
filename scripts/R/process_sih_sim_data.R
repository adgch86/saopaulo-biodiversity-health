# =============================================================================
# Script para procesar datos de SIH (Hospitalizações) y SIM (Mortalidade)
# =============================================================================
#
# Este script procesa archivos DBC de DATASUS y extrae:
# - Hospitalizações por doenças circulatórias (CID-10: I00-I99)
# - Hospitalizações por doenças respiratórias (CID-10: J00-J99)
# - Hospitalizações por efeitos do calor (CID-10: T67.0-T67.9)
# - Óbitos por las mismas causas
#
# Autor: Science Team / Dra. María Santos (Bioestadística)
# Fecha: 2026-01-23
# =============================================================================

# Cargar librerías necesarias
suppressPackageStartupMessages({
  library(read.dbc)
  library(tidyverse)
  library(data.table)
})

# Configuración de paths
# Detectar automáticamente la raíz del proyecto
args <- commandArgs(trailingOnly = FALSE)
script_path <- sub("--file=", "", args[grep("--file=", args)])
if (length(script_path) > 0) {
  project_root <- dirname(dirname(normalizePath(script_path)))
} else {
  project_root <- "C:/Users/arlex/Documents/Adrian David"
}

data_raw_sih <- file.path(project_root, "data", "raw", "datasus", "sih")
data_raw_sim <- file.path(project_root, "data", "raw", "datasus", "sim")
data_processed <- file.path(project_root, "data", "processed")

# Crear directorio de salida si no existe
dir.create(data_processed, recursive = TRUE, showWarnings = FALSE)

# Configuración de CID-10
# Doenças do aparelho circulatório: I00-I99 (Capítulo IX)
# Doenças do aparelho respiratório: J00-J99 (Capítulo X)
# Efeitos do calor e da luz: T67.0-T67.9

# Años de interés
anos <- 2010:2019

# UF São Paulo
uf_sp <- "35"  # Código IBGE de SP

# =============================================================================
# Función para verificar si un CID está en el rango de interés
# =============================================================================
check_cid_circulatorio <- function(cid) {
  # CID I00-I99 (Doenças do aparelho circulatório)
  if (is.na(cid) || nchar(cid) < 3) return(FALSE)
  substr(cid, 1, 1) == "I"
}

check_cid_respiratorio <- function(cid) {
  # CID J00-J99 (Doenças do aparelho respiratório)
  if (is.na(cid) || nchar(cid) < 3) return(FALSE)
  substr(cid, 1, 1) == "J"
}

check_cid_calor <- function(cid) {
  # CID T67 (Efeitos do calor e da luz)
  if (is.na(cid) || nchar(cid) < 3) return(FALSE)
  substr(cid, 1, 3) == "T67"
}

classify_cid <- function(cid) {
  if (is.na(cid) || nchar(cid) < 3) return("outros")
  if (substr(cid, 1, 1) == "I") return("circulatorio")
  if (substr(cid, 1, 1) == "J") return("respiratorio")
  if (substr(cid, 1, 3) == "T67") return("calor")
  return("outros")
}

# Vectorizar la función
classify_cid_vec <- Vectorize(classify_cid)

# =============================================================================
# Procesar archivos SIH (Hospitalizações)
# =============================================================================
process_sih_files <- function() {
  cat("\n", paste(rep("=", 70), collapse = ""), "\n")
  cat("PROCESANDO ARCHIVOS SIH (Hospitalizações)\n")
  cat(paste(rep("=", 70), collapse = ""), "\n")

  # Listar archivos DBC de SIH
  sih_files <- list.files(data_raw_sih, pattern = "\\.dbc$", full.names = TRUE, ignore.case = TRUE)
  cat(sprintf("Archivos SIH encontrados: %d\n", length(sih_files)))

  if (length(sih_files) == 0) {
    cat("[ADVERTENCIA] No se encontraron archivos SIH. Ejecute primero download_sih_sim_datasus.py\n")
    return(NULL)
  }

  # Dataframe para acumular resultados
  results_list <- list()

  for (i in seq_along(sih_files)) {
    file_path <- sih_files[i]
    file_name <- basename(file_path)

    cat(sprintf("\n[%d/%d] Procesando %s...\n", i, length(sih_files), file_name))

    tryCatch({
      # Leer archivo DBC
      df <- read.dbc(file_path)
      cat(sprintf("  Registros totales: %s\n", format(nrow(df), big.mark = ",")))

      # Columnas clave en SIH:
      # - MUNIC_RES: Município de residência (6 dígitos IBGE)
      # - DIAG_PRINC: Diagnóstico principal (CID-10)
      # - ANO_CMPT: Año de competência
      # - MES_CMPT: Mes de competência

      # Filtrar solo registros de SP (código empieza con 35)
      if ("MUNIC_RES" %in% names(df)) {
        df$MUNIC_RES <- as.character(df$MUNIC_RES)
        df <- df[substr(df$MUNIC_RES, 1, 2) == "35", ]
        cat(sprintf("  Registros de SP: %s\n", format(nrow(df), big.mark = ",")))
      }

      # Filtrar por CID de interés
      if ("DIAG_PRINC" %in% names(df)) {
        df$DIAG_PRINC <- as.character(df$DIAG_PRINC)
        df$categoria_cid <- classify_cid_vec(df$DIAG_PRINC)

        # Solo mantener CIDs de interés
        df <- df[df$categoria_cid %in% c("circulatorio", "respiratorio", "calor"), ]
        cat(sprintf("  Registros con CID de interés: %s\n", format(nrow(df), big.mark = ",")))

        if (nrow(df) > 0) {
          # Agregar información del año
          if ("ANO_CMPT" %in% names(df)) {
            df$ano <- as.integer(df$ANO_CMPT)
          } else {
            # Extraer año del nombre del archivo (formato: RDSP{AAMM}.dbc)
            year_2d <- as.integer(substr(file_name, 5, 6))
            df$ano <- ifelse(year_2d < 50, 2000 + year_2d, 1900 + year_2d)
          }

          # Agregar código de municipio (6 dígitos)
          df$cod_ibge <- substr(df$MUNIC_RES, 1, 6)

          # Contar hospitalizaciones por municipio, año y categoría
          summary_df <- df %>%
            group_by(cod_ibge, ano, categoria_cid) %>%
            summarise(internacoes = n(), .groups = "drop")

          results_list[[file_name]] <- summary_df
          cat(sprintf("  Municipios únicos: %d\n", length(unique(df$cod_ibge))))
        }
      }
    }, error = function(e) {
      cat(sprintf("  [ERROR] No se pudo procesar: %s\n", e$message))
    })
  }

  # Combinar todos los resultados
  if (length(results_list) > 0) {
    cat("\nCombinando resultados SIH...\n")
    all_results <- bind_rows(results_list)

    # Agregar por municipio, año y categoría (algunos archivos pueden tener duplicados)
    sih_summary <- all_results %>%
      group_by(cod_ibge, ano, categoria_cid) %>%
      summarise(internacoes = sum(internacoes), .groups = "drop")

    cat(sprintf("Total de registros agregados: %s\n", format(nrow(sih_summary), big.mark = ",")))

    return(sih_summary)
  } else {
    return(NULL)
  }
}

# =============================================================================
# Procesar archivos SIM (Mortalidade)
# =============================================================================
process_sim_files <- function() {
  cat("\n", paste(rep("=", 70), collapse = ""), "\n")
  cat("PROCESANDO ARCHIVOS SIM (Mortalidade)\n")
  cat(paste(rep("=", 70), collapse = ""), "\n")

  # Listar archivos DBC de SIM
  sim_files <- list.files(data_raw_sim, pattern = "\\.dbc$", full.names = TRUE, ignore.case = TRUE)
  cat(sprintf("Archivos SIM encontrados: %d\n", length(sim_files)))

  if (length(sim_files) == 0) {
    cat("[ADVERTENCIA] No se encontraron archivos SIM. Ejecute primero download_sih_sim_datasus.py\n")
    return(NULL)
  }

  # Dataframe para acumular resultados
  results_list <- list()

  for (i in seq_along(sim_files)) {
    file_path <- sim_files[i]
    file_name <- basename(file_path)

    cat(sprintf("\n[%d/%d] Procesando %s...\n", i, length(sim_files), file_name))

    tryCatch({
      # Leer archivo DBC
      df <- read.dbc(file_path)
      cat(sprintf("  Registros totales: %s\n", format(nrow(df), big.mark = ",")))

      # Columnas clave en SIM:
      # - CODMUNRES: Código do município de residência (6 dígitos IBGE)
      # - CAUSABAS: Causa básica do óbito (CID-10)
      # - DTOBITO: Data do óbito (formato DDMMAAAA)

      # Filtrar solo registros de SP (código empieza con 35)
      if ("CODMUNRES" %in% names(df)) {
        df$CODMUNRES <- as.character(df$CODMUNRES)
        df <- df[substr(df$CODMUNRES, 1, 2) == "35", ]
        cat(sprintf("  Registros de SP: %s\n", format(nrow(df), big.mark = ",")))
      }

      # Filtrar por CID de interés
      if ("CAUSABAS" %in% names(df)) {
        df$CAUSABAS <- as.character(df$CAUSABAS)
        df$categoria_cid <- classify_cid_vec(df$CAUSABAS)

        # Solo mantener CIDs de interés
        df <- df[df$categoria_cid %in% c("circulatorio", "respiratorio", "calor"), ]
        cat(sprintf("  Registros con CID de interés: %s\n", format(nrow(df), big.mark = ",")))

        if (nrow(df) > 0) {
          # Extraer año del nombre del archivo (formato: DOSP{AAAA}.dbc)
          # o de la fecha de óbito
          if ("DTOBITO" %in% names(df)) {
            df$DTOBITO <- as.character(df$DTOBITO)
            df$ano <- as.integer(substr(df$DTOBITO, 5, 8))
          } else {
            # Extraer del nombre del archivo
            year_str <- substr(file_name, 5, 8)
            df$ano <- as.integer(year_str)
          }

          # Agregar código de municipio (6 dígitos)
          df$cod_ibge <- substr(df$CODMUNRES, 1, 6)

          # Contar óbitos por municipio, año y categoría
          summary_df <- df %>%
            group_by(cod_ibge, ano, categoria_cid) %>%
            summarise(obitos = n(), .groups = "drop")

          results_list[[file_name]] <- summary_df
          cat(sprintf("  Municipios únicos: %d\n", length(unique(df$cod_ibge))))
        }
      }
    }, error = function(e) {
      cat(sprintf("  [ERROR] No se pudo procesar: %s\n", e$message))
    })
  }

  # Combinar todos los resultados
  if (length(results_list) > 0) {
    cat("\nCombinando resultados SIM...\n")
    all_results <- bind_rows(results_list)

    # Agregar por municipio, año y categoría
    sim_summary <- all_results %>%
      group_by(cod_ibge, ano, categoria_cid) %>%
      summarise(obitos = sum(obitos), .groups = "drop")

    cat(sprintf("Total de registros agregados: %s\n", format(nrow(sim_summary), big.mark = ",")))

    return(sim_summary)
  } else {
    return(NULL)
  }
}

# =============================================================================
# Crear dataset final con incidencias
# =============================================================================
create_final_dataset <- function(sih_data, sim_data, pop_data = NULL) {
  cat("\n", paste(rep("=", 70), collapse = ""), "\n")
  cat("CREANDO DATASET FINAL\n")
  cat(paste(rep("=", 70), collapse = ""), "\n")

  # Cargar datos de población si no se proporcionan
  if (is.null(pop_data)) {
    pop_file <- file.path(data_processed, "populacao_SP_2010_2019.csv")
    if (file.exists(pop_file)) {
      pop_data <- read_csv(pop_file, show_col_types = FALSE)
      cat(sprintf("Datos de población cargados: %d registros\n", nrow(pop_data)))
    } else {
      cat("[ADVERTENCIA] No se encontraron datos de población. Las incidencias serán valores absolutos.\n")
    }
  }

  # Pivotar datos de SIH para tener una columna por categoría y año
  if (!is.null(sih_data)) {
    sih_wide <- sih_data %>%
      pivot_wider(
        id_cols = c(cod_ibge, ano),
        names_from = categoria_cid,
        values_from = internacoes,
        values_fill = 0
      ) %>%
      rename_with(~paste0("hosp_", .), -c(cod_ibge, ano))

    cat(sprintf("Datos SIH pivotados: %d filas x %d columnas\n", nrow(sih_wide), ncol(sih_wide)))
  }

  # Pivotar datos de SIM
  if (!is.null(sim_data)) {
    sim_wide <- sim_data %>%
      pivot_wider(
        id_cols = c(cod_ibge, ano),
        names_from = categoria_cid,
        values_from = obitos,
        values_fill = 0
      ) %>%
      rename_with(~paste0("obit_", .), -c(cod_ibge, ano))

    cat(sprintf("Datos SIM pivotados: %d filas x %d columnas\n", nrow(sim_wide), ncol(sim_wide)))
  }

  # Unir SIH y SIM
  if (!is.null(sih_data) && !is.null(sim_data)) {
    combined <- sih_wide %>%
      full_join(sim_wide, by = c("cod_ibge", "ano"))
  } else if (!is.null(sih_data)) {
    combined <- sih_wide
  } else if (!is.null(sim_data)) {
    combined <- sim_wide
  } else {
    cat("[ERROR] No hay datos para combinar\n")
    return(NULL)
  }

  # Reemplazar NA con 0
  combined <- combined %>%
    mutate(across(where(is.numeric), ~replace_na(., 0)))

  # Agregar población y calcular incidencias (por 100,000 habitantes)
  if (!is.null(pop_data)) {
    pop_data$cod_ibge <- as.character(pop_data$cod_ibge)
    combined$cod_ibge <- as.character(combined$cod_ibge)

    combined <- combined %>%
      left_join(pop_data %>% select(cod_ibge, ano, populacao), by = c("cod_ibge", "ano"))

    # Calcular incidencias
    combined <- combined %>%
      mutate(
        # Incidencias de hospitalizaciones
        inc_hosp_circulatorio = ifelse(populacao > 0, hosp_circulatorio / populacao * 100000, NA),
        inc_hosp_respiratorio = ifelse(populacao > 0, hosp_respiratorio / populacao * 100000, NA),
        inc_hosp_calor = ifelse(populacao > 0, hosp_calor / populacao * 100000, NA),
        # Incidencias de óbitos
        inc_obit_circulatorio = ifelse(populacao > 0, obit_circulatorio / populacao * 100000, NA),
        inc_obit_respiratorio = ifelse(populacao > 0, obit_respiratorio / populacao * 100000, NA),
        inc_obit_calor = ifelse(populacao > 0, obit_calor / populacao * 100000, NA)
      )
  }

  cat(sprintf("\nDataset combinado: %d filas x %d columnas\n", nrow(combined), ncol(combined)))

  return(combined)
}

# =============================================================================
# Calcular estadísticas por municipio
# =============================================================================
calculate_municipality_stats <- function(combined_data) {
  cat("\n", paste(rep("=", 70), collapse = ""), "\n")
  cat("CALCULANDO ESTADÍSTICAS POR MUNICIPIO\n")
  cat(paste(rep("=", 70), collapse = ""), "\n")

  # Columnas de incidencia
  inc_cols <- grep("^inc_", names(combined_data), value = TRUE)

  if (length(inc_cols) == 0) {
    # Si no hay incidencias, usar valores absolutos
    cat("Usando valores absolutos (sin datos de población)\n")
    inc_cols <- grep("^hosp_|^obit_", names(combined_data), value = TRUE)
  }

  # Calcular media y máxima por municipio para cada variable
  stats_list <- list()

  for (col in inc_cols) {
    col_data <- combined_data %>%
      group_by(cod_ibge) %>%
      summarise(
        !!paste0(col, "_media") := mean(.data[[col]], na.rm = TRUE),
        !!paste0(col, "_max") := max(.data[[col]], na.rm = TRUE),
        .groups = "drop"
      )
    stats_list[[col]] <- col_data
  }

  # Combinar todas las estadísticas
  final_stats <- stats_list[[1]]
  for (i in 2:length(stats_list)) {
    final_stats <- final_stats %>%
      left_join(stats_list[[i]], by = "cod_ibge")
  }

  cat(sprintf("Estadísticas calculadas para %d municipios\n", nrow(final_stats)))

  return(final_stats)
}

# =============================================================================
# Main
# =============================================================================
main <- function() {
  cat(paste(rep("=", 70), collapse = ""), "\n")
  cat("DATASUS - Procesamiento de datos SIH y SIM\n")
  cat("Science Team - São Paulo Biodiversity & Health Project\n")
  cat(sprintf("Fecha: %s\n", Sys.time()))
  cat(paste(rep("=", 70), collapse = ""), "\n")

  # Procesar SIH
  sih_data <- process_sih_files()

  # Procesar SIM
  sim_data <- process_sim_files()

  # Crear dataset combinado
  combined <- create_final_dataset(sih_data, sim_data)

  if (!is.null(combined)) {
    # Guardar dataset anual
    output_file_annual <- file.path(data_processed, "health_sih_sim_annual_SP_2010_2019.csv")
    write_csv(combined, output_file_annual)
    cat(sprintf("\n[OK] Dataset anual guardado: %s\n", output_file_annual))

    # Calcular estadísticas por municipio
    stats <- calculate_municipality_stats(combined)

    # Guardar estadísticas
    output_file_stats <- file.path(data_processed, "health_sih_sim_stats_SP_2010_2019.csv")
    write_csv(stats, output_file_stats)
    cat(sprintf("[OK] Estadísticas guardadas: %s\n", output_file_stats))

    # Resumen
    cat("\n", paste(rep("=", 70), collapse = ""), "\n")
    cat("RESUMEN FINAL\n")
    cat(paste(rep("=", 70), collapse = ""), "\n")
    cat(sprintf("Municipios procesados: %d\n", length(unique(combined$cod_ibge))))
    cat(sprintf("Años: %s\n", paste(range(combined$ano), collapse = "-")))

    if ("hosp_circulatorio" %in% names(combined)) {
      cat(sprintf("\nHospitalizaciones totales:\n"))
      cat(sprintf("  - Circulatórias (I00-I99): %s\n", format(sum(combined$hosp_circulatorio, na.rm = TRUE), big.mark = ",")))
      cat(sprintf("  - Respiratórias (J00-J99): %s\n", format(sum(combined$hosp_respiratorio, na.rm = TRUE), big.mark = ",")))
      cat(sprintf("  - Calor (T67): %s\n", format(sum(combined$hosp_calor, na.rm = TRUE), big.mark = ",")))
    }

    if ("obit_circulatorio" %in% names(combined)) {
      cat(sprintf("\nÓbitos totales:\n"))
      cat(sprintf("  - Circulatórias (I00-I99): %s\n", format(sum(combined$obit_circulatorio, na.rm = TRUE), big.mark = ",")))
      cat(sprintf("  - Respiratórias (J00-J99): %s\n", format(sum(combined$obit_respiratorio, na.rm = TRUE), big.mark = ",")))
      cat(sprintf("  - Calor (T67): %s\n", format(sum(combined$obit_calor, na.rm = TRUE), big.mark = ",")))
    }

    return(list(annual = combined, stats = stats))
  } else {
    cat("\n[ERROR] No se pudieron procesar los datos\n")
    return(NULL)
  }
}

# Ejecutar
if (!interactive()) {
  result <- main()
}
