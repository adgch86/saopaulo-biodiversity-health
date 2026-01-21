# ==============================================================================
# Verificar filtro de casos AUTOCTONOS
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Verificando columna TPAUTOCTO y otros filtros\n")
cat("=======================================================================\n\n")

# Leer archivo 2015
filepath <- file.path(DATA_RAW, "DENGBR15.dbc")
df <- read.dbc(filepath)

# Filtrar SP
df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]
cat(sprintf("Total SP 2015: %d\n\n", nrow(df_sp)))

# Verificar valores de TPAUTOCTO
cat("Valores de TPAUTOCTO:\n")
print(table(df_sp$TPAUTOCTO, useNA = "ifany"))

# Verificar valores de CLASSI_FIN
cat("\nValores de CLASSI_FIN:\n")
print(table(df_sp$CLASSI_FIN, useNA = "ifany"))

# Para DIADEMA (351380), probar diferentes filtros
cod_diadema <- "351380"
df_diadema <- df_sp[as.character(df_sp$ID_MN_RESI) == cod_diadema, ]

cat(sprintf("\n\nDIADEMA (cod %s):\n", cod_diadema))
cat(sprintf("Total notificaciones: %d\n", nrow(df_diadema)))

# Solo confirmados
classi <- as.numeric(as.character(df_diadema$CLASSI_FIN))
df_conf <- df_diadema[classi %in% c(5, 10, 11, 12), ]
cat(sprintf("Confirmados: %d\n", nrow(df_conf)))

# Solo autoctonos
auto <- as.numeric(as.character(df_diadema$TPAUTOCTO))
df_auto <- df_diadema[auto == 1, ]
cat(sprintf("Autoctonos: %d\n", nrow(df_auto)))

# Confirmados + Autoctonos
df_conf_auto <- df_conf[as.numeric(as.character(df_conf$TPAUTOCTO)) == 1, ]
cat(sprintf("Confirmados + Autoctonos: %d\n", nrow(df_conf_auto)))

# Probar CRITERIO (criterio de confirmacion)
cat("\nValores de CRITERIO en DIADEMA:\n")
print(table(df_diadema$CRITERIO, useNA = "ifany"))

# Para comparar con Adrian (3993 para 2015)
cat("\n\n=======================================================================\n")
cat("Adrian tiene 3993 para DIADEMA en 2015\n")
cat("Nosotros tenemos diferentes valores segun el filtro\n")
cat("=======================================================================\n")
