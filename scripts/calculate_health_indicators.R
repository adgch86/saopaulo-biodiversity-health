# ==============================================================================
# Cálculo de Indicadores de Salud: Incidencia, Persistencia y Co-presencia
# ==============================================================================
#
# Inspirado en: health_variables.R (Julia)
# Adaptado para: 4 enfermedades (dengue, leptospirose, malaria, leishmaniose)
# Nota: Leishmaniose = Visceral + Tegumentar (agregadas)
#
# Indicadores calculados:
#   1. Persistencia: años con presencia de cada enfermedad (0-10)
#   2. Incidencia media: casos por 100,000 habitantes (promedio 2010-2019)
#   3. Co-presencia: años con 2+ enfermedades presentes simultáneamente
#   4. Co-presencia por pares: años con cada par de enfermedades
#
# Autor: Science Team
# Fecha: 2026-01-21
# ==============================================================================

# Configurar biblioteca de usuario
.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

# Cargar librerías
library(dplyr)
library(tidyr)
library(purrr)

# Configuración
PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_PROCESSED <- file.path(PROJECT_ROOT, "data/processed")

cat("=" , rep("=", 69), "\n", sep="")
cat("CÁLCULO DE INDICADORES DE SALUD\n")
cat("Estado: São Paulo | Período: 2010-2019\n")
cat("Enfermedades: Dengue, Leptospirose, Malaria, Leishmaniose\n")
cat("=", rep("=", 69), "\n\n", sep="")

# ==============================================================================
# 1. CARGAR DATOS DE SALUD
# ==============================================================================
cat("1. Cargando datos de salud...\n")

health_file <- file.path(DATA_PROCESSED, "health_casos_provaveis_SP_2010_2019_regioes.csv")
health <- read.csv(health_file, stringsAsFactors = FALSE)

cat(sprintf("   Municipios: %d\n", nrow(health)))
cat(sprintf("   Columnas: %d\n", ncol(health)))

# ==============================================================================
# 2. COMBINAR LEISHMANIOSE (Visceral + Tegumentar)
# ==============================================================================
cat("\n2. Combinando Leishmaniose Visceral + Tegumentar...\n")

# Crear columnas de leishmaniose combinada para cada año
for (year in 2010:2019) {
  leiv_col <- paste0("leiv_", year)
  ltan_col <- paste0("ltan_", year)
  leish_col <- paste0("leish_", year)

  health[[leish_col]] <- health[[leiv_col]] + health[[ltan_col]]
}

cat("   Columnas leish_2010 a leish_2019 creadas\n")

# ==============================================================================
# 3. DESCARGAR POBLACIÓN DEL IBGE
# ==============================================================================
cat("\n3. Descargando población del IBGE...\n")

# Intentar cargar población si ya existe
pop_file <- file.path(DATA_PROCESSED, "populacao_SP_2010_2019.csv")

if (file.exists(pop_file)) {
  cat("   Archivo de población encontrado, cargando...\n")
  pop_data <- read.csv(pop_file, stringsAsFactors = FALSE)
} else {
  cat("   Descargando de IBGE API...\n")

  # API do IBGE - Población estimada por municipio
  # Nota: La API de IBGE tiene límites, usaremos estimación promedio

  # Por ahora, usaremos población del Censo 2010 + estimaciones
  # En una versión futura, integrar con API de población

  tryCatch({
    # Intentar descargar del IBGE
    url <- "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2010|2011|2012|2013|2014|2015|2016|2017|2018|2019/variaveis/9324?localidades=N6[N3[35]]"

    response <- httr::GET(url)

    if (httr::status_code(response) == 200) {
      json_data <- httr::content(response, as = "text", encoding = "UTF-8")
      pop_json <- jsonlite::fromJSON(json_data)

      # Procesar datos
      resultados <- pop_json[[1]]$resultados[[1]]$series

      pop_list <- lapply(resultados, function(x) {
        cod_ibge <- substr(x$localidade$id, 1, 6)
        nome <- x$localidade$nome
        pop_values <- x$serie

        data.frame(
          cod_ibge = cod_ibge,
          nome_municipio = nome,
          pop_2010 = as.numeric(pop_values$`2010`),
          pop_2011 = as.numeric(pop_values$`2011`),
          pop_2012 = as.numeric(pop_values$`2012`),
          pop_2013 = as.numeric(pop_values$`2013`),
          pop_2014 = as.numeric(pop_values$`2014`),
          pop_2015 = as.numeric(pop_values$`2015`),
          pop_2016 = as.numeric(pop_values$`2016`),
          pop_2017 = as.numeric(pop_values$`2017`),
          pop_2018 = as.numeric(pop_values$`2018`),
          pop_2019 = as.numeric(pop_values$`2019`),
          stringsAsFactors = FALSE
        )
      })

      pop_data <- bind_rows(pop_list)
      write.csv(pop_data, pop_file, row.names = FALSE)
      cat(sprintf("   Población descargada: %d municipios\n", nrow(pop_data)))

    } else {
      stop("Error en API")
    }

  }, error = function(e) {
    cat("   AVISO: No se pudo descargar población. Usando estimación.\n")
    cat("   Para incidencia precisa, agregar archivo de población manualmente.\n")

    # Crear estimación basada en casos (placeholder)
    pop_data <<- NULL
  })
}

# ==============================================================================
# 4. PREPARAR DATOS EN FORMATO LARGO
# ==============================================================================
cat("\n4. Preparando datos en formato largo...\n")

# Definir las 4 enfermedades
disease_vars <- c("dengue", "leptospirose", "malaria", "leishmaniose")
disease_prefixes <- c("deng", "lept", "mala", "leish")

# Convertir a formato largo
health_long <- health %>%
  select(cod_ibge, nome_municipio, cod_microrregiao, nome_microrregiao,
         cod_mesorregiao, nome_mesorregiao,
         starts_with("deng_"), starts_with("lept_"),
         starts_with("mala_"), starts_with("leish_")) %>%
  pivot_longer(
    cols = c(starts_with("deng_"), starts_with("lept_"),
             starts_with("mala_"), starts_with("leish_")),
    names_to = c("disease", "year"),
    names_pattern = "([a-z]+)_(\\d{4})",
    values_to = "cases"
  ) %>%
  mutate(
    year = as.integer(year),
    disease = case_when(
      disease == "deng" ~ "dengue",
      disease == "lept" ~ "leptospirose",
      disease == "mala" ~ "malaria",
      disease == "leish" ~ "leishmaniose"
    )
  )

cat(sprintf("   Registros en formato largo: %d\n", nrow(health_long)))

# ==============================================================================
# 5. CALCULAR PERSISTENCIA (años con presencia de cada enfermedad)
# ==============================================================================
cat("\n5. Calculando persistencia...\n")

# Presencia/ausencia por año
health_bin <- health_long %>%
  mutate(present = ifelse(cases > 0, 1, 0))

# Persistencia: suma de años con presencia (0-10)
persistence <- health_bin %>%
  group_by(cod_ibge, nome_municipio, disease) %>%
  summarise(persist_years = sum(present, na.rm = TRUE), .groups = "drop") %>%
  pivot_wider(
    names_from = disease,
    values_from = persist_years,
    names_prefix = "persist_"
  )

cat(sprintf("   Municipios con persistencia calculada: %d\n", nrow(persistence)))

# Mostrar resumen
cat("\n   Distribución de persistencia (años con casos):\n")
for (dis in disease_vars) {
  col <- paste0("persist_", dis)
  mean_val <- mean(persistence[[col]], na.rm = TRUE)
  cat(sprintf("   - %s: media = %.1f años\n", dis, mean_val))
}

# ==============================================================================
# 6. CALCULAR INCIDENCIA (si hay datos de población)
# ==============================================================================
cat("\n6. Calculando incidencia...\n")

if (!is.null(pop_data) && nrow(pop_data) > 0) {

  # Convertir población a formato largo
  pop_long <- pop_data %>%
    select(cod_ibge, starts_with("pop_")) %>%
    pivot_longer(
      cols = starts_with("pop_"),
      names_to = "year",
      names_prefix = "pop_",
      values_to = "population"
    ) %>%
    mutate(
      cod_ibge = as.character(cod_ibge),
      year = as.integer(year)
    )

  # Merge con datos de salud
  health_with_pop <- health_long %>%
    mutate(cod_ibge = as.character(cod_ibge)) %>%
    left_join(pop_long, by = c("cod_ibge", "year"))

  # Calcular incidencia por 100,000 habitantes
  incidence <- health_with_pop %>%
    mutate(
      incidence = ifelse(population > 0, (cases / population) * 100000, NA)
    ) %>%
    group_by(cod_ibge, nome_municipio, disease) %>%
    summarise(
      incidence_mean = mean(incidence, na.rm = TRUE),
      incidence_max = max(incidence, na.rm = TRUE),
      total_cases = sum(cases, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    mutate(
      incidence_mean = ifelse(is.nan(incidence_mean), 0, incidence_mean),
      incidence_max = ifelse(is.infinite(incidence_max), 0, incidence_max)
    )

  # Pivotar a formato ancho
  incidence_wide <- incidence %>%
    pivot_wider(
      names_from = disease,
      values_from = c(incidence_mean, incidence_max, total_cases),
      names_glue = "{.value}_{disease}"
    )

  cat(sprintf("   Incidencia calculada para %d municipios\n", nrow(incidence_wide)))

} else {
  cat("   AVISO: Sin datos de población. Calculando solo casos totales.\n")

  # Solo calcular casos totales
  incidence_wide <- health_long %>%
    group_by(cod_ibge, nome_municipio, disease) %>%
    summarise(total_cases = sum(cases, na.rm = TRUE), .groups = "drop") %>%
    pivot_wider(
      names_from = disease,
      values_from = total_cases,
      names_prefix = "total_cases_"
    )
}

# ==============================================================================
# 7. CALCULAR CO-PRESENCIA (años con 2+ enfermedades)
# ==============================================================================
cat("\n7. Calculando co-presencia...\n")

# Crear tabla ancha de presencia/ausencia por año
presence_wide <- health_bin %>%
  select(cod_ibge, nome_municipio, year, disease, present) %>%
  pivot_wider(
    names_from = disease,
    values_from = present,
    values_fill = 0
  )

# Contar enfermedades presentes por municipio-año
copresence <- presence_wide %>%
  rowwise() %>%
  mutate(n_diseases = sum(c_across(all_of(disease_vars)))) %>%
  ungroup() %>%
  group_by(cod_ibge, nome_municipio) %>%
  summarise(
    copresence_years = sum(n_diseases >= 2),  # Años con 2+ enfermedades
    copresence_3plus = sum(n_diseases >= 3),  # Años con 3+ enfermedades
    copresence_all4 = sum(n_diseases == 4),   # Años con todas las 4
    .groups = "drop"
  )

cat(sprintf("   Municipios con co-presencia calculada: %d\n", nrow(copresence)))
cat(sprintf("   - Con 2+ enfermedades algún año: %d (%.1f%%)\n",
            sum(copresence$copresence_years > 0),
            100 * sum(copresence$copresence_years > 0) / nrow(copresence)))

# ==============================================================================
# 8. CALCULAR CO-PRESENCIA POR PARES
# ==============================================================================
cat("\n8. Calculando co-presencia por pares de enfermedades...\n")

disease_pairs <- combn(disease_vars, 2, simplify = FALSE)

pairwise_list <- map(disease_pairs, function(pair) {
  a <- pair[1]
  b <- pair[2]
  pair_name <- paste(a, b, sep = "_")

  presence_wide %>%
    group_by(cod_ibge, nome_municipio) %>%
    summarise(
      !!pair_name := sum(.data[[a]] == 1 & .data[[b]] == 1, na.rm = TRUE),
      .groups = "drop"
    )
})

# Combinar todas las columnas de pares
pairwise_copresence <- reduce(pairwise_list, left_join, by = c("cod_ibge", "nome_municipio"))

cat(sprintf("   Pares calculados: %d\n", length(disease_pairs)))
for (pair in disease_pairs) {
  pair_name <- paste(pair, collapse = "_")
  mean_val <- mean(pairwise_copresence[[pair_name]], na.rm = TRUE)
  cat(sprintf("   - %s: media = %.1f años\n", pair_name, mean_val))
}

# ==============================================================================
# 9. JUNTAR TODO EN DATASET FINAL
# ==============================================================================
cat("\n9. Consolidando dataset final...\n")

# Obtener info de regiones del dataset original
region_info <- health %>%
  select(cod_ibge, nome_municipio, cod_microrregiao, nome_microrregiao,
         cod_mesorregiao, nome_mesorregiao) %>%
  mutate(cod_ibge = as.character(cod_ibge))

# Juntar todas las tablas
health_indicators <- region_info %>%
  left_join(persistence %>% mutate(cod_ibge = as.character(cod_ibge)) %>%
              select(-nome_municipio), by = "cod_ibge") %>%
  left_join(incidence_wide %>% mutate(cod_ibge = as.character(cod_ibge)) %>%
              select(-nome_municipio), by = "cod_ibge") %>%
  left_join(copresence %>% mutate(cod_ibge = as.character(cod_ibge)) %>%
              select(-nome_municipio), by = "cod_ibge") %>%
  left_join(pairwise_copresence %>% mutate(cod_ibge = as.character(cod_ibge)) %>%
              select(-nome_municipio), by = "cod_ibge")

cat(sprintf("   Municipios en dataset final: %d\n", nrow(health_indicators)))
cat(sprintf("   Columnas totales: %d\n", ncol(health_indicators)))

# ==============================================================================
# 10. GUARDAR RESULTADOS
# ==============================================================================
cat("\n10. Guardando resultados...\n")

output_file <- file.path(DATA_PROCESSED, "health_indicators_SP_2010_2019.csv")
write.csv(health_indicators, output_file, row.names = FALSE)
cat(sprintf("    Archivo guardado: %s\n", output_file))

# ==============================================================================
# 11. RESUMEN FINAL
# ==============================================================================
cat("\n")
cat("=", rep("=", 69), "\n", sep="")
cat("RESUMEN DE INDICADORES CALCULADOS\n")
cat("=", rep("=", 69), "\n", sep="")

cat("\nPERSISTENCIA (años con casos, 0-10):\n")
for (dis in disease_vars) {
  col <- paste0("persist_", dis)
  cat(sprintf("  %s: min=%d, max=%d, media=%.1f\n",
              dis,
              min(health_indicators[[col]], na.rm = TRUE),
              max(health_indicators[[col]], na.rm = TRUE),
              mean(health_indicators[[col]], na.rm = TRUE)))
}

cat("\nCO-PRESENCIA:\n")
cat(sprintf("  Años con 2+ enfermedades: media=%.1f\n",
            mean(health_indicators$copresence_years, na.rm = TRUE)))
cat(sprintf("  Años con 3+ enfermedades: media=%.1f\n",
            mean(health_indicators$copresence_3plus, na.rm = TRUE)))
cat(sprintf("  Años con 4 enfermedades: media=%.1f\n",
            mean(health_indicators$copresence_all4, na.rm = TRUE)))

cat("\nCASOS TOTALES (2010-2019):\n")
for (dis in disease_vars) {
  col <- paste0("total_cases_", dis)
  if (col %in% names(health_indicators)) {
    total <- sum(health_indicators[[col]], na.rm = TRUE)
    cat(sprintf("  %s: %s casos\n", dis, format(total, big.mark = ",")))
  }
}

cat("\n")
cat("=", rep("=", 69), "\n", sep="")
cat("Proceso completado.\n")
cat("=", rep("=", 69), "\n", sep="")
