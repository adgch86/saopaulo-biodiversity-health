# Verificar casos confirmados vs totales
.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))
library(read.dbc)

filepath <- "C:/Users/arlex/Documents/Adrian David/data/raw/datasus/DENGBR10.dbc"
df <- read.dbc(filepath)

# Filtrar solo SP por residencia
df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]

cat("=== DENGUE SP 2010 - ANALISIS ===\n\n")
cat("Total casos SP (por residencia):", nrow(df_sp), "\n")

# Verificar CLASSI_FIN (clasificacion final)
cat("\n=== CLASSI_FIN (Clasificacion Final) ===\n")
print(table(df_sp$CLASSI_FIN, useNA = "ifany"))

# Verificar CRITERIO
cat("\n=== CRITERIO ===\n")
print(table(df_sp$CRITERIO, useNA = "ifany"))

# Contar solo confirmados (CLASSI_FIN en 10, 11, 12, 13 = dengue clasico, FHD, etc)
# Segun documentacion SINAN:
# 10 = Dengue
# 11 = Dengue com sinais de alarme
# 12 = Dengue grave
# 13 = Dengue com complicacoes (FHD)
confirmados <- df_sp[df_sp$CLASSI_FIN %in% c(10, 11, 12, 13, "10", "11", "12", "13"), ]
cat("\n=== CONTEO FINAL ===\n")
cat("Total SP residencia:", nrow(df_sp), "\n")
cat("Confirmados (CLASSI_FIN 10-13):", nrow(confirmados), "\n")

# Verificar por municipio especifico: Adamantina
cat("\n=== ADAMANTINA (350010) ===\n")
adam_all <- df_sp[substr(as.character(df_sp$ID_MN_RESI), 1, 6) == "350010", ]
adam_conf <- adam_all[adam_all$CLASSI_FIN %in% c(10, 11, 12, 13, "10", "11", "12", "13"), ]
cat("Total:", nrow(adam_all), "\n")
cat("Confirmados:", nrow(adam_conf), "\n")
cat("Esperado:", 246, "\n")
