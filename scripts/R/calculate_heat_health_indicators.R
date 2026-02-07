# =============================================================================
# Script para calcular indicadores de salud relacionados con calor
# =============================================================================
#
# Calcula incidencia media y máxima de hospitalizaciones y óbitos para:
# - Doenças do aparelho circulatório (I00-I99)
# - Doenças do aparelho respiratório (J00-J99)
# - Efeitos do calor e da luz (T67)
#
# Autor: Science Team / Dra. María Santos (Bioestadística)
# Fecha: 2026-01-23
# =============================================================================

suppressPackageStartupMessages({
  library(read.dbc)
  library(tidyverse)
  library(data.table)
})

# Configuración de paths
project_root <- "C:/Users/arlex/Documents/Adrian David"
data_raw_sih <- file.path(project_root, "data", "raw", "datasus", "sih")
data_raw_sim <- file.path(project_root, "data", "raw", "datasus", "sim")
data_processed <- file.path(project_root, "data", "processed")

# Clasificación de CID
classify_cid <- function(cid) {
  if (is.na(cid) || nchar(cid) < 3) return("otros")
  if (substr(cid, 1, 1) == "I") return("circulatorio")
  if (substr(cid, 1, 1) == "J") return("respiratorio")
  if (substr(cid, 1, 3) == "T67") return("calor")
  return("otros")
}
classify_cid_vec <- Vectorize(classify_cid)

# =============================================================================
# Cargar datos de población (convertir wide a long)
# =============================================================================
load_population <- function() {
  pop_file <- file.path(data_processed, "populacao_SP_2010_2019.csv")

  if (file.exists(pop_file)) {
    pop_wide <- read_csv(pop_file, show_col_types = FALSE)

    # Convertir a long format
    pop_long <- pop_wide %>%
      select(cod_ibge, starts_with("pop_20")) %>%
      pivot_longer(
        cols = starts_with("pop_"),
        names_to = "ano",
        values_to = "populacao",
        names_prefix = "pop_"
      ) %>%
      mutate(
        ano = as.integer(ano),
        cod_ibge = as.character(cod_ibge)
      )

    return(pop_long)
  }

  return(NULL)
}

# =============================================================================
# Procesar SIH (Hospitalizaciones)
# =============================================================================
process_sih <- function() {
  cat("Procesando archivos SIH...\n")

  sih_files <- list.files(data_raw_sih, pattern = "\\.dbc$", full.names = TRUE, ignore.case = TRUE)

  if (length(sih_files) == 0) {
    cat("No se encontraron archivos SIH\n")
    return(NULL)
  }

  results_list <- list()

  for (file_path in sih_files) {
    file_name <- basename(file_path)

    tryCatch({
      df <- read.dbc(file_path)

      # Filtrar por SP y CID de interés
      if ("MUNIC_RES" %in% names(df) && "DIAG_PRINC" %in% names(df)) {
        df$MUNIC_RES <- as.character(df$MUNIC_RES)
        df$DIAG_PRINC <- as.character(df$DIAG_PRINC)

        df <- df[substr(df$MUNIC_RES, 1, 2) == "35", ]
        df$categoria_cid <- classify_cid_vec(df$DIAG_PRINC)
        df <- df[df$categoria_cid %in% c("circulatorio", "respiratorio", "calor"), ]

        if (nrow(df) > 0) {
          # Extraer año del nombre del archivo
          year_2d <- as.integer(substr(file_name, 5, 6))
          df$ano <- ifelse(year_2d < 50, 2000 + year_2d, 1900 + year_2d)
          df$cod_ibge <- substr(df$MUNIC_RES, 1, 6)

          summary_df <- df %>%
            group_by(cod_ibge, ano, categoria_cid) %>%
            summarise(internacoes = n(), .groups = "drop")

          results_list[[file_name]] <- summary_df
        }
      }
    }, error = function(e) {
      cat(sprintf("Error en %s: %s\n", file_name, e$message))
    })
  }

  if (length(results_list) > 0) {
    all_results <- bind_rows(results_list)
    sih_summary <- all_results %>%
      group_by(cod_ibge, ano, categoria_cid) %>%
      summarise(internacoes = sum(internacoes), .groups = "drop")

    return(sih_summary)
  }

  return(NULL)
}

# =============================================================================
# Procesar SIM (Mortalidad)
# =============================================================================
process_sim <- function() {
  cat("Procesando archivos SIM...\n")

  sim_files <- list.files(data_raw_sim, pattern = "\\.dbc$", full.names = TRUE, ignore.case = TRUE)

  if (length(sim_files) == 0) {
    cat("No se encontraron archivos SIM\n")
    return(NULL)
  }

  results_list <- list()

  for (file_path in sim_files) {
    file_name <- basename(file_path)

    tryCatch({
      df <- read.dbc(file_path)

      if ("CODMUNRES" %in% names(df) && "CAUSABAS" %in% names(df)) {
        df$CODMUNRES <- as.character(df$CODMUNRES)
        df$CAUSABAS <- as.character(df$CAUSABAS)

        df <- df[substr(df$CODMUNRES, 1, 2) == "35", ]
        df$categoria_cid <- classify_cid_vec(df$CAUSABAS)
        df <- df[df$categoria_cid %in% c("circulatorio", "respiratorio", "calor"), ]

        if (nrow(df) > 0) {
          # Extraer año del nombre del archivo
          year_str <- substr(file_name, 5, 8)
          df$ano <- as.integer(year_str)
          df$cod_ibge <- substr(df$CODMUNRES, 1, 6)

          summary_df <- df %>%
            group_by(cod_ibge, ano, categoria_cid) %>%
            summarise(obitos = n(), .groups = "drop")

          results_list[[file_name]] <- summary_df
        }
      }
    }, error = function(e) {
      cat(sprintf("Error en %s: %s\n", file_name, e$message))
    })
  }

  if (length(results_list) > 0) {
    all_results <- bind_rows(results_list)
    sim_summary <- all_results %>%
      group_by(cod_ibge, ano, categoria_cid) %>%
      summarise(obitos = sum(obitos), .groups = "drop")

    return(sim_summary)
  }

  return(NULL)
}

# =============================================================================
# Calcular indicadores finales
# =============================================================================
calculate_indicators <- function(sih_data, sim_data, pop_data) {
  cat("Calculando indicadores...\n")

  # Lista de municipios de SP (645)
  municipios <- read_csv(file.path(data_processed, "municipios_regioes_SP.csv"), show_col_types = FALSE) %>%
    select(cod_ibge) %>%
    distinct() %>%
    mutate(cod_ibge = as.character(cod_ibge))

  # Crear grid completo de municipios x años x categorías
  anos <- 2010:2019
  categorias <- c("circulatorio", "respiratorio", "calor")

  grid <- expand.grid(
    cod_ibge = municipios$cod_ibge,
    ano = anos,
    stringsAsFactors = FALSE
  )

  # Pivotar SIH
  if (!is.null(sih_data)) {
    sih_wide <- sih_data %>%
      pivot_wider(
        id_cols = c(cod_ibge, ano),
        names_from = categoria_cid,
        values_from = internacoes,
        values_fill = 0,
        names_prefix = "hosp_"
      )

    # Asegurar que existan todas las columnas
    for (cat in categorias) {
      col_name <- paste0("hosp_", cat)
      if (!col_name %in% names(sih_wide)) {
        sih_wide[[col_name]] <- 0
      }
    }
  } else {
    sih_wide <- grid %>%
      mutate(hosp_circulatorio = 0, hosp_respiratorio = 0, hosp_calor = 0)
  }

  # Pivotar SIM
  if (!is.null(sim_data)) {
    sim_wide <- sim_data %>%
      pivot_wider(
        id_cols = c(cod_ibge, ano),
        names_from = categoria_cid,
        values_from = obitos,
        values_fill = 0,
        names_prefix = "obit_"
      )

    for (cat in categorias) {
      col_name <- paste0("obit_", cat)
      if (!col_name %in% names(sim_wide)) {
        sim_wide[[col_name]] <- 0
      }
    }
  } else {
    sim_wide <- grid %>%
      mutate(obit_circulatorio = 0, obit_respiratorio = 0, obit_calor = 0)
  }

  # Combinar todo
  combined <- grid %>%
    left_join(sih_wide, by = c("cod_ibge", "ano")) %>%
    left_join(sim_wide, by = c("cod_ibge", "ano")) %>%
    mutate(across(starts_with("hosp_"), ~replace_na(., 0))) %>%
    mutate(across(starts_with("obit_"), ~replace_na(., 0)))

  # Agregar población
  if (!is.null(pop_data)) {
    combined <- combined %>%
      left_join(pop_data, by = c("cod_ibge", "ano"))

    # Calcular incidencias (por 100,000 habitantes)
    combined <- combined %>%
      mutate(
        inc_hosp_circulatorio = ifelse(populacao > 0, hosp_circulatorio / populacao * 100000, NA),
        inc_hosp_respiratorio = ifelse(populacao > 0, hosp_respiratorio / populacao * 100000, NA),
        inc_hosp_calor = ifelse(populacao > 0, hosp_calor / populacao * 100000, NA),
        inc_obit_circulatorio = ifelse(populacao > 0, obit_circulatorio / populacao * 100000, NA),
        inc_obit_respiratorio = ifelse(populacao > 0, obit_respiratorio / populacao * 100000, NA),
        inc_obit_calor = ifelse(populacao > 0, obit_calor / populacao * 100000, NA)
      )
  }

  # Calcular estadísticas por municipio (media y máxima)
  stats <- combined %>%
    group_by(cod_ibge) %>%
    summarise(
      # Hospitalizaciones - Media
      inc_hosp_circ_media = mean(inc_hosp_circulatorio, na.rm = TRUE),
      inc_hosp_resp_media = mean(inc_hosp_respiratorio, na.rm = TRUE),
      inc_hosp_calor_media = mean(inc_hosp_calor, na.rm = TRUE),
      # Hospitalizaciones - Máxima
      inc_hosp_circ_max = max(inc_hosp_circulatorio, na.rm = TRUE),
      inc_hosp_resp_max = max(inc_hosp_respiratorio, na.rm = TRUE),
      inc_hosp_calor_max = max(inc_hosp_calor, na.rm = TRUE),
      # Óbitos - Media
      inc_obit_circ_media = mean(inc_obit_circulatorio, na.rm = TRUE),
      inc_obit_resp_media = mean(inc_obit_respiratorio, na.rm = TRUE),
      inc_obit_calor_media = mean(inc_obit_calor, na.rm = TRUE),
      # Óbitos - Máxima
      inc_obit_circ_max = max(inc_obit_circulatorio, na.rm = TRUE),
      inc_obit_resp_max = max(inc_obit_respiratorio, na.rm = TRUE),
      inc_obit_calor_max = max(inc_obit_calor, na.rm = TRUE),
      # Totales (valores absolutos)
      total_hosp_circ = sum(hosp_circulatorio, na.rm = TRUE),
      total_hosp_resp = sum(hosp_respiratorio, na.rm = TRUE),
      total_hosp_calor = sum(hosp_calor, na.rm = TRUE),
      total_obit_circ = sum(obit_circulatorio, na.rm = TRUE),
      total_obit_resp = sum(obit_respiratorio, na.rm = TRUE),
      total_obit_calor = sum(obit_calor, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    mutate(across(where(is.numeric), ~ifelse(is.infinite(.), NA, .)))

  return(list(annual = combined, stats = stats))
}

# =============================================================================
# Main
# =============================================================================
main <- function() {
  cat(paste(rep("=", 70), collapse = ""), "\n")
  cat("Cálculo de Indicadores de Salud - Impactos del Calor\n")
  cat(sprintf("Fecha: %s\n", Sys.time()))
  cat(paste(rep("=", 70), collapse = ""), "\n\n")

  # Cargar población
  cat("Cargando datos de población...\n")
  pop_data <- load_population()
  if (!is.null(pop_data)) {
    cat(sprintf("Población cargada: %d registros\n", nrow(pop_data)))
  }

  # Procesar SIH
  sih_data <- process_sih()
  if (!is.null(sih_data)) {
    cat(sprintf("Datos SIH procesados: %d registros\n", nrow(sih_data)))
  }

  # Procesar SIM
  sim_data <- process_sim()
  if (!is.null(sim_data)) {
    cat(sprintf("Datos SIM procesados: %d registros\n", nrow(sim_data)))
  }

  # Calcular indicadores
  results <- calculate_indicators(sih_data, sim_data, pop_data)

  # Guardar resultados
  annual_file <- file.path(data_processed, "health_heat_annual_SP_2010_2019.csv")
  stats_file <- file.path(data_processed, "health_heat_indicators_SP_2010_2019.csv")

  write_csv(results$annual, annual_file)
  write_csv(results$stats, stats_file)

  cat("\n", paste(rep("=", 70), collapse = ""), "\n")
  cat("ARCHIVOS GENERADOS\n")
  cat(paste(rep("=", 70), collapse = ""), "\n")
  cat(sprintf("Datos anuales: %s\n", annual_file))
  cat(sprintf("Indicadores por municipio: %s\n", stats_file))

  # Resumen
  cat("\n", paste(rep("=", 70), collapse = ""), "\n")
  cat("RESUMEN\n")
  cat(paste(rep("=", 70), collapse = ""), "\n")
  cat(sprintf("Municipios: %d\n", nrow(results$stats)))

  # Totales
  cat("\nHospitalizaciones totales (2010-2019):\n")
  cat(sprintf("  - Circulatorias (I00-I99): %s\n", format(sum(results$stats$total_hosp_circ, na.rm = TRUE), big.mark = ",")))
  cat(sprintf("  - Respiratorias (J00-J99): %s\n", format(sum(results$stats$total_hosp_resp, na.rm = TRUE), big.mark = ",")))
  cat(sprintf("  - Efectos del calor (T67): %s\n", format(sum(results$stats$total_hosp_calor, na.rm = TRUE), big.mark = ",")))

  cat("\nÓbitos totales (2010-2019):\n")
  cat(sprintf("  - Circulatorias (I00-I99): %s\n", format(sum(results$stats$total_obit_circ, na.rm = TRUE), big.mark = ",")))
  cat(sprintf("  - Respiratorias (J00-J99): %s\n", format(sum(results$stats$total_obit_resp, na.rm = TRUE), big.mark = ",")))
  cat(sprintf("  - Efectos del calor (T67): %s\n", format(sum(results$stats$total_obit_calor, na.rm = TRUE), big.mark = ",")))

  cat("\nIncidencias promedio (por 100,000 hab):\n")
  cat(sprintf("  - Hosp. Circulatorias media: %.1f\n", mean(results$stats$inc_hosp_circ_media, na.rm = TRUE)))
  cat(sprintf("  - Hosp. Respiratorias media: %.1f\n", mean(results$stats$inc_hosp_resp_media, na.rm = TRUE)))
  cat(sprintf("  - Hosp. Calor media: %.2f\n", mean(results$stats$inc_hosp_calor_media, na.rm = TRUE)))
  cat(sprintf("  - Obit. Circulatorias media: %.1f\n", mean(results$stats$inc_obit_circ_media, na.rm = TRUE)))
  cat(sprintf("  - Obit. Respiratorias media: %.1f\n", mean(results$stats$inc_obit_resp_media, na.rm = TRUE)))
  cat(sprintf("  - Obit. Calor media: %.3f\n", mean(results$stats$inc_obit_calor_media, na.rm = TRUE)))

  return(results)
}

# Ejecutar
result <- main()
