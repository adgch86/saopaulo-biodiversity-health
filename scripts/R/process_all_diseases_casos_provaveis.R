# ==============================================================================
# Script para procesar TODAS las enfermedades - CASOS PROVÁVEIS
# ==============================================================================
#
# Enfermedades procesadas:
#   - Dengue (DENG)
#   - Leptospirose (LEPT)
#   - Malaria (MALA)
#   - Leishmaniose Visceral (LEIV)
#   - Leishmaniose Tegumentar Americana (LTAN)
#
# Filtro aplicado: CLASSI_FIN != 5 (excluir casos descartados)
# Agrupación: Municipio de residencia x Año de notificación
#
# Autor: Science Team
# Fecha: 2026-01-21
# ==============================================================================

# Configurar biblioteca de usuario
.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

# Cargar librerias
library(read.dbc)
library(dplyr)
library(tidyr)

# Configuracion
PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")
DATA_PROCESSED <- file.path(PROJECT_ROOT, "data/processed")

# Codigo UF de Sao Paulo
UF_SP <- "35"

# Definir enfermedades a procesar
DISEASES <- list(
  dengue = list(prefix = "DENG", name = "Dengue"),
  leptospirose = list(prefix = "LEPT", name = "Leptospirose"),
  malaria = list(prefix = "MALA", name = "Malaria"),
  leish_visceral = list(prefix = "LEIV", name = "Leishmaniose Visceral"),
  leish_tegumentar = list(prefix = "LTAN", name = "Leishmaniose Tegumentar")
)

# ==============================================================================
# Funcion para filtrar casos provaveis (excluir descartados)
# ==============================================================================
filter_casos_provaveis <- function(df, year, disease_name) {
  # Buscar columna de clasificacion final (puede variar el nombre)
  classi_cols <- c("CLASSI_FIN", "CLASSIFICACAO", "CLASS_FIN", "CRITERIO")
  classi_col <- NULL

  for (col in classi_cols) {
    if (col %in% names(df)) {
      classi_col <- col
      break
    }
  }

  if (is.null(classi_col)) {
    cat(sprintf("  [%s] AVISO: No existe columna de clasificacion, retornando todos los casos\n", disease_name))
    cat("  Columnas disponibles:", paste(names(df), collapse=", "), "\n")
    return(list(data = df, has_filter = FALSE))
  }

  # Mostrar distribucion de clasificacion
  cat(sprintf("  [%s] Distribucion %s:\n", disease_name, classi_col))
  print(table(df[[classi_col]], useNA = "ifany"))

  n_total <- nrow(df)

  # Aplicar filtro: excluir casos descartados (generalmente = 5)
  # Casos provaveis = todos excepto descartados
  df_filtered <- df[is.na(df[[classi_col]]) | df[[classi_col]] != 5, ]

  n_filtered <- nrow(df_filtered)
  n_excluded <- n_total - n_filtered
  pct_excluded <- round(100 * n_excluded / n_total, 1)

  cat(sprintf("  [%s] Total: %s -> Provaveis: %s (excluidos: %s = %.1f%%)\n",
              disease_name,
              format(n_total, big.mark=","),
              format(n_filtered, big.mark=","),
              format(n_excluded, big.mark=","),
              pct_excluded))

  return(list(data = df_filtered, has_filter = TRUE))
}

# ==============================================================================
# Funcion para procesar una enfermedad por año
# ==============================================================================
process_disease_year <- function(disease_prefix, disease_name, year) {
  filename <- sprintf("%sBR%02d.dbc", disease_prefix, year %% 100)
  filepath <- file.path(DATA_RAW, filename)

  if (!file.exists(filepath)) {
    cat(sprintf("[%s] Archivo no encontrado: %s\n", disease_name, filename))
    return(NULL)
  }

  cat(sprintf("\n=== %s - %d (%s) ===\n", disease_name, year, filename))

  tryCatch({
    # Leer archivo DBC
    df <- read.dbc(filepath)
    cat(sprintf("  Registros Brasil: %s\n", format(nrow(df), big.mark=",")))

    # Identificar columna de municipio de residencia
    mun_cols <- c("ID_MN_RESI", "ID_MUNICIP", "MUNIC_RES", "MUN_RESID", "COD_MUN_RES")
    mun_col <- NULL

    for (col in mun_cols) {
      if (col %in% names(df)) {
        mun_col <- col
        break
      }
    }

    if (is.null(mun_col)) {
      cat(sprintf("  [%s] ERROR: No se encontro columna de municipio\n", disease_name))
      cat("  Columnas:", paste(head(names(df), 20), collapse=", "), "\n")
      return(NULL)
    }

    cat(sprintf("  Columna municipio: %s\n", mun_col))

    # Filtrar Sao Paulo (codigo UF = 35)
    df[[mun_col]] <- as.character(df[[mun_col]])
    df_sp <- df[substr(df[[mun_col]], 1, 2) == UF_SP, ]
    cat(sprintf("  Registros Sao Paulo: %s\n", format(nrow(df_sp), big.mark=",")))

    if (nrow(df_sp) == 0) {
      return(NULL)
    }

    # Aplicar filtro de casos provaveis
    result_filter <- filter_casos_provaveis(df_sp, year, disease_name)
    df_provaveis <- result_filter$data

    # Agregar por municipio
    result <- df_provaveis %>%
      mutate(cod_ibge = substr(.data[[mun_col]], 1, 6)) %>%
      filter(!is.na(cod_ibge) & cod_ibge != "" & cod_ibge != "350000") %>%  # Excluir codigo ignorado
      group_by(cod_ibge) %>%
      summarise(cases = n(), .groups = "drop") %>%
      mutate(year = year)

    return(result)

  }, error = function(e) {
    cat(sprintf("  [%s] Error: %s\n", disease_name, e$message))
    return(NULL)
  })
}

# ==============================================================================
# Funcion para procesar una enfermedad completa (todos los años)
# ==============================================================================
process_disease <- function(disease_key) {
  disease <- DISEASES[[disease_key]]
  prefix <- disease$prefix
  name <- disease$name

  cat("\n")
  cat(strrep("=", 70), "\n")
  cat(sprintf("PROCESANDO: %s (%s)\n", name, prefix))
  cat(strrep("=", 70), "\n")

  all_years <- list()

  for (year in 2010:2019) {
    result <- process_disease_year(prefix, name, year)
    if (!is.null(result) && nrow(result) > 0) {
      all_years[[as.character(year)]] <- result
    }
  }

  if (length(all_years) == 0) {
    cat(sprintf("\n[%s] No se encontraron datos\n", name))
    return(NULL)
  }

  # Combinar todos los años
  df_combined <- bind_rows(all_years)

  # Mostrar resumen
  cat(sprintf("\n[%s] Resumen:\n", name))
  totals <- df_combined %>%
    group_by(year) %>%
    summarise(total = sum(cases), municipios = n(), .groups = "drop")
  print(totals)

  return(df_combined)
}

# ==============================================================================
# MAIN - Procesar todas las enfermedades
# ==============================================================================
cat(strrep("=", 70), "\n")
cat("EXTRACTOR DE CASOS PROVÁVEIS - DATASUS SINAN\n")
cat("Estado: São Paulo | Período: 2010-2019\n")
cat("Filtro: Excluye casos descartados (CLASSI_FIN != 5)\n")
cat("Agrupación: Municipio de residencia x Año de notificación\n")
cat(strrep("=", 70), "\n")

# Almacenar resultados por enfermedad
all_diseases <- list()

for (disease_key in names(DISEASES)) {
  result <- process_disease(disease_key)
  if (!is.null(result)) {
    all_diseases[[disease_key]] <- result
  }
}

# ==============================================================================
# Crear dataset consolidado
# ==============================================================================
cat("\n")
cat(strrep("=", 70), "\n")
cat("CONSOLIDANDO DATASET\n")
cat(strrep("=", 70), "\n")

# Convertir cada enfermedad a formato ancho y combinar
create_wide_format <- function(df, disease_key) {
  prefix <- tolower(substr(DISEASES[[disease_key]]$prefix, 1, 4))

  df %>%
    pivot_wider(
      names_from = year,
      values_from = cases,
      names_prefix = paste0(prefix, "_"),
      values_fill = 0
    )
}

# Procesar cada enfermedad
wide_dfs <- list()

for (disease_key in names(all_diseases)) {
  wide_dfs[[disease_key]] <- create_wide_format(all_diseases[[disease_key]], disease_key)
}

# Combinar todas las enfermedades por cod_ibge
if (length(wide_dfs) > 0) {
  df_final <- wide_dfs[[1]]

  if (length(wide_dfs) > 1) {
    for (i in 2:length(wide_dfs)) {
      df_final <- full_join(df_final, wide_dfs[[i]], by = "cod_ibge")
    }
  }

  # Reemplazar NA con 0
  df_final[is.na(df_final)] <- 0

  # Ordenar columnas
  year_cols <- grep("_20", names(df_final), value = TRUE)
  df_final <- df_final %>%
    select(cod_ibge, sort(year_cols))

  # Guardar archivo consolidado
  output_file <- file.path(DATA_PROCESSED, "health_casos_provaveis_SP_2010_2019.csv")
  write.csv(df_final, output_file, row.names = FALSE)

  cat(sprintf("\nArchivo guardado: %s\n", output_file))
  cat(sprintf("Municipios totales: %d\n", nrow(df_final)))
  cat(sprintf("Columnas: %d\n", ncol(df_final)))

  # Resumen por enfermedad y año
  cat("\n")
  cat(strrep("=", 70), "\n")
  cat("RESUMEN: CASOS PROVÁVEIS POR ENFERMEDAD Y AÑO\n")
  cat(strrep("=", 70), "\n")

  for (disease_key in names(DISEASES)) {
    disease <- DISEASES[[disease_key]]
    prefix <- tolower(substr(disease$prefix, 1, 4))
    cols <- grep(paste0("^", prefix, "_"), names(df_final), value = TRUE)

    if (length(cols) > 0) {
      cat(sprintf("\n%s:\n", disease$name))
      for (col in sort(cols)) {
        year <- sub(paste0(prefix, "_"), "", col)
        total <- sum(df_final[[col]], na.rm = TRUE)
        cat(sprintf("  %s: %s casos\n", year, format(total, big.mark=",")))
      }
    }
  }

} else {
  cat("ERROR: No se procesaron datos\n")
}

cat("\n")
cat(strrep("=", 70), "\n")
cat("Procesamiento completado.\n")
cat(strrep("=", 70), "\n")
