# ==============================================================================
# Investigar formato de codigos en DENGBR10.dbc
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

filepath <- file.path(DATA_RAW, "DENGBR10.dbc")
df <- read.dbc(filepath)

# Filtrar SP
df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]

cat("Primeros 20 codigos de municipio en SP (ID_MN_RESI):\n")
codigos <- head(sort(unique(as.character(df_sp$ID_MN_RESI))), 20)
print(codigos)

cat("\nTipo de la columna ID_MN_RESI:", class(df_sp$ID_MN_RESI), "\n")

cat("\nBuscando codigos que empiezan con 3500:\n")
cod_3500 <- unique(as.character(df_sp$ID_MN_RESI))
cod_3500 <- cod_3500[substr(cod_3500, 1, 4) == "3500"]
print(sort(cod_3500))

cat("\nConteo para primeros municipios de SP:\n")
tabla <- table(as.character(df_sp$ID_MN_RESI))
tabla_df <- as.data.frame(tabla, stringsAsFactors = FALSE)
names(tabla_df) <- c("codigo", "casos")
tabla_df <- tabla_df[order(tabla_df$codigo), ]
print(head(tabla_df, 15))
