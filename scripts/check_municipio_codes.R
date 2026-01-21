# ==============================================================================
# Verificar codigos IBGE de municipios de SP
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

# Leer un archivo para buscar municipios con nombre
filepath <- file.path(DATA_RAW, "DENGBR15.dbc")
cat("Leyendo", basename(filepath), "...\n\n")

df <- read.dbc(filepath)

# Ver todas las columnas
cat("Columnas disponibles:\n")
print(names(df))

# Filtrar SP
df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]
cat(sprintf("\nTotal registros SP: %d\n", nrow(df_sp)))

# Buscar si hay alguna columna con nombres
if ("MUNIC_RES" %in% names(df_sp)) {
  cat("\nColumna MUNIC_RES encontrada\n")
  # Mostrar algunos nombres
  munis <- unique(df_sp$MUNIC_RES)
  cat("Primeros 20 municipios:\n")
  print(head(sort(as.character(munis)), 20))
}

# Verificar la columna ID_MUNICIP (municipio de notificacion) vs ID_MN_RESI (municipio de residencia)
cat("\n\nComparando ID_MUNICIP vs ID_MN_RESI:\n")
cat("ID_MUNICIP (notificacion):\n")
print(head(table(df_sp$ID_MUNICIP), 20))

cat("\nID_MN_RESI (residencia):\n")
print(head(table(df_sp$ID_MN_RESI), 20))

# Buscar valores especificos
cat("\n\nBuscando codigos que terminan en 00, 10, 20, etc (secuencia alfabetica):\n")
codigos_resi <- as.character(df_sp$ID_MN_RESI)

# Contar por codigo
tabla <- table(codigos_resi)
df_tabla <- as.data.frame(tabla, stringsAsFactors = FALSE)
names(df_tabla) <- c("codigo", "casos")
df_tabla <- df_tabla[order(df_tabla$codigo), ]

# Mostrar todos los codigos en el rango 351300-351500
cat("\nCodigos en rango 351300-351500:\n")
for (i in 1:nrow(df_tabla)) {
  cod_num <- as.numeric(df_tabla$codigo[i])
  if (!is.na(cod_num) && cod_num >= 351300 && cod_num <= 351500) {
    cat(sprintf("%s: %d casos\n", df_tabla$codigo[i], df_tabla$casos[i]))
  }
}
