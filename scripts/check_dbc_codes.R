# Investigar codigos de municipio
.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))
library(read.dbc)

filepath <- "C:/Users/arlex/Documents/Adrian David/data/raw/datasus/DENGBR10.dbc"
df <- read.dbc(filepath)

cat("=== INVESTIGACION DE CODIGOS ===\n\n")

# Ver ejemplos de ID_MN_RESI
cat("Ejemplos de ID_MN_RESI:\n")
print(head(unique(df$ID_MN_RESI), 20))

# Ver longitud de codigos
cat("\nLongitud de codigos ID_MN_RESI:\n")
print(table(nchar(as.character(df$ID_MN_RESI))))

# Buscar Adamantina especificamente
cat("\n=== BUSCAR ADAMANTINA ===\n")
adam_mask <- grepl("35001", as.character(df$ID_MN_RESI))
cat("Registros con '35001' en ID_MN_RESI:", sum(adam_mask), "\n")

if(sum(adam_mask) > 0) {
  cat("Codigos encontrados:\n")
  print(unique(df$ID_MN_RESI[adam_mask]))
}

# Ver los primeros municipios de SP
cat("\n=== PRIMEROS MUNICIPIOS DE SP ===\n")
sp_codes <- unique(df$ID_MN_RESI[substr(as.character(df$ID_MN_RESI), 1, 2) == "35"])
sp_codes_sorted <- sort(sp_codes)
cat("Primeros 20 codigos de SP:\n")
print(head(sp_codes_sorted, 20))

# Contar casos para primeros municipios
cat("\n=== CASOS PRIMEROS MUNICIPIOS SP (CLASSI_FIN=1) ===\n")
df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]
df_conf <- df_sp[df_sp$CLASSI_FIN == 1, ]

for (i in 1:10) {
  cod <- sp_codes_sorted[i]
  casos <- sum(df_conf$ID_MN_RESI == cod, na.rm = TRUE)
  cat(sprintf("%s: %d casos\n", cod, casos))
}
