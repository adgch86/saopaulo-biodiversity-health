# Verificar qué columnas existen en cada archivo DBC

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))
library(read.dbc)

DATA_RAW <- "C:/Users/arlex/Documents/Adrian David/data/raw/datasus"

diseases <- c("LEPT", "MALA", "LEIV", "LTAN")

for (dis in diseases) {
  cat(sprintf("\n=== %s ===\n", dis))
  for (year in c(2012, 2015)) {  # Años con mayores diferencias
    filename <- sprintf("%sBR%02d.dbc", dis, year %% 100)
    filepath <- file.path(DATA_RAW, filename)

    if (file.exists(filepath)) {
      df <- read.dbc(filepath)

      # Verificar columnas de municipio
      mun_cols <- c("ID_MUNICIP", "ID_MN_RESI", "CO_MUN_RES", "MUNRESBR")
      available <- mun_cols[mun_cols %in% names(df)]

      cat(sprintf("\n%s:\n", filename))
      cat(sprintf("  Columnas municipio disponibles: %s\n", paste(available, collapse=", ")))

      # Script original usaría la primera disponible
      if ("ID_MUNICIP" %in% names(df)) {
        cat("  Script original usaría: ID_MUNICIP\n")

        # Contar registros de SP por cada columna
        cat(sprintf("  Registros SP por ID_MUNICIP: %d\n",
                    sum(substr(as.character(df$ID_MUNICIP), 1, 2) == "35", na.rm=TRUE)))

        if ("ID_MN_RESI" %in% names(df)) {
          cat(sprintf("  Registros SP por ID_MN_RESI: %d\n",
                      sum(substr(as.character(df$ID_MN_RESI), 1, 2) == "35", na.rm=TRUE)))
        }
      } else if ("ID_MN_RESI" %in% names(df)) {
        cat("  Script original usaría: ID_MN_RESI\n")
        cat(sprintf("  Registros SP: %d\n",
                    sum(substr(as.character(df$ID_MN_RESI), 1, 2) == "35", na.rm=TRUE)))
      }
    }
  }
}
